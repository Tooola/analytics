"""Analytics endpoint — the core analysis flow."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key, require_dashboard_user, optional_dashboard_user
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.ratelimit import limiter
from app.models import Application, User
from app.repositories.analysis_repo import AnalysisRunRepository
from app.repositories.application_repo import ApplicationRepository
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.analytics import (
    AnalysisDetailResponse,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisRunRead,
    DataValidationResult,
    InsightRead,
    JoinAlignment,
    MultiAnalysisRequest,
    MultiAnalysisResponse,
)
from app.schemas.comparison import (
    CompareResponse,
    MultiPeriodCompareRequest,
    MultiPeriodCompareResponse,
    QuickCompareRequest,
    StepComparison,
)
from app.services.ai.business_context import build_business_context
from app.services.ai.engine import AIEngine
from app.services.analytics.auto_selector import auto_select_analyses
from app.services.analytics.comparator import PeriodComparator
from app.services.analytics.cross_correlation import cross_correlate_ex
from app.services.analytics.engine import AnalyticsEngine
from app.services.analytics.grouped import build_grouped, grouped_context_line
from app.services.analytics.synthesis import build_synthesis
from app.services.insights.engine import InsightEngine

router = APIRouter(tags=["analytics"])
logger = get_logger(__name__)


# ─── Quick Analyze (no dataset registration required) ──────────────────────────

class QuickAnalyzeRequest(BaseModel):
    """Quick-test endpoint — auto-infers field types from the data.

    For admin/dashboard testing only: skip the application + dataset registration
    step and get instant analysis results from raw JSON.
    """
    data: list[dict[str, Any]]
    analysis: list[str] = ["auto"]
    group_by: str | None = None  # categorical column to cut measures by
    include_ai: bool = False
    language: str = "fr"  # "fr" | "en"
    label: str = "quick-test"  # optional label shown in results


def _infer_fields(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Auto-detect column types from the first few rows of data."""
    if not data:
        return []
    all_keys: set[str] = set()
    for row in data:
        all_keys.update(row.keys())

    fields = []
    for key in all_keys:
        # Sample non-null values
        samples = [row[key] for row in data if row.get(key) is not None][:10]
        if not samples:
            t = "string"
        elif all(isinstance(v, bool) for v in samples):
            t = "boolean"
        elif all(isinstance(v, int) for v in samples):
            t = "integer"
        elif all(isinstance(v, (int, float)) for v in samples):
            t = "float"
        else:
            # Try to detect real date strings (YYYY-MM-DD or ISO-8601)
            first_val = str(samples[0]).strip()
            is_date = False
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    datetime.strptime(first_val, fmt)
                    is_date = True
                    break
                except ValueError:
                    pass
            if not is_date:
                try:
                    datetime.fromisoformat(first_val)
                    is_date = True
                except ValueError:
                    pass

            t = "date" if is_date else "string"
        fields.append({
            "name": key,
            "technical_type": t,
            "semantic_type": "date" if t == "date" else ("quantity" if t in ("integer", "float") else "category"),
            "required": False,
        })
    return fields


@router.post("/analyze/quick")
@limiter.limit("30/minute")
def quick_analyze(
    body: QuickAnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_dashboard_user),
) -> dict[str, Any]:
    """Run analysis on raw JSON data without pre-registered application or dataset.

    Designed for admin dashboard testing: paste any JSON array, get instant
    results. Field types are auto-inferred from the data.
    """
    if not body.data:
        raise HTTPException(status_code=422, detail="data must not be empty")
    if len(body.data) > 10_000:
        raise HTTPException(status_code=422, detail="Max 10 000 rows per request")

    field_defs = _infer_fields(body.data)
    analysis_types = body.analysis
    if "auto" in analysis_types:
        analysis_types = auto_select_analyses(body.data, field_defs)

    analytics_engine = AnalyticsEngine()
    _, results = analytics_engine.analyze(
        data=body.data,
        fields=field_defs,
        analysis_types=analysis_types,
        language=body.language,
    )

    # Segment analysis (opt-in group_by): attached to results — the
    # InsightEngine only reads known types, so it ignores the extra key.
    # Soft-fail contract: a crash here never sinks the statistics.
    if body.group_by:
        try:
            results["grouped"] = build_grouped(
                body.data, field_defs, body.group_by
            )
        except Exception as exc:
            logger.warning(
                "Segment analysis failed (group_by=%s): %s", body.group_by, exc
            )

    insight_engine = InsightEngine()
    insight_dicts = insight_engine.generate(results, dataset_name=body.label, language=body.language)

    ai_text = None
    if body.include_ai:
        try:
            ai_engine = AIEngine()
            context = ai_engine.build_context(
                application=body.label,
                dataset=body.label,
                row_count=len(body.data),
                analysis_results=results,
                insights=insight_dicts,
            )
            # Quick test: pas d'app enregistrée — on donne les noms de colonnes
            # inférés pour que l'IA puisse déduire le domaine automatiquement.
            inferred_cols = ", ".join(f["name"] for f in field_defs) if field_defs else "non spécifiées"
            business_context = (
                f"Banc d'essai rapide (sans application enregistrée). "
                f"Colonnes détectées automatiquement : {inferred_cols}. "
                f"Libellé du test : « {body.label} »."
            )
            segments_line = grouped_context_line(results.get("grouped"))
            if segments_line:
                business_context += " " + segments_line
            context = context.model_copy(
                update={"business_context": business_context, "language": body.language}
            )
            ai_result = ai_engine.interpret(context)
            ai_text = ai_result.model_dump_json()
        except Exception as exc:
            logger.warning("Quick analyze AI failed: %s", exc)

    # Persist in DB so ALL dashboard admins see this run in their history
    run_id = None
    try:
        from app.services.dashboard_auth import ensure_system_quick_test_entities
        sys_app_id, sys_ds_id = ensure_system_quick_test_entities(db)
        run_repo = AnalysisRunRepository(db)
        op_name = current_user.username if current_user else "Admin"
        run = run_repo.create_run(
            application_id=sys_app_id,
            dataset_id=sys_ds_id,
            analysis_types=analysis_types,
            row_count=len(body.data),
            operator_username=op_name,
        )
        run_repo.add_insights(run, insight_dicts)
        results_with_meta = dict(results)
        results_with_meta["label"] = body.label
        run_repo.complete_run(run, results_with_meta, ai_interpretation=ai_text)
        run_id = run.id
    except Exception as exc:
        logger.warning("Could not persist quick test run in DB: %s", exc)

    return {
        "id": run_id,
        "success": True,
        "label": body.label,
        "row_count": len(body.data),
        "fields_inferred": field_defs,
        "results": results,
        "insights": insight_dicts,
        "ai_interpretation": ai_text,
        "ai_status": _ai_status(body.include_ai, ai_text),
    }


@router.post("/analyze/quick/compare", response_model=CompareResponse)
@limiter.limit("30/minute")
def quick_compare(
    body: QuickCompareRequest,
    request: Request,
) -> CompareResponse:
    """Compare two periods (Period A vs Period B) without dataset registration.

    Categorizes metrics into:
    - What improved (Améliorations)
    - What degraded (Dégradations)
    - New points of attention (Vigilance)
    Provides an executive comparative narrative without mathematical/correlation jargon.
    """
    if not body.period_a.data or not body.period_b.data:
        raise HTTPException(status_code=422, detail="Both period_a and period_b data must not be empty")

    comparator = PeriodComparator()
    report = comparator.compare(
        period_a_label=body.period_a.label,
        period_a_data=body.period_a.data,
        period_b_label=body.period_b.label,
        period_b_data=body.period_b.data,
        label=body.label,
        language=body.language,
    )

    ai_text = None
    if body.include_ai:
        try:
            ai_engine = AIEngine()
            context = ai_engine.build_comparison_context(
                label=body.label,
                period_a_label=body.period_a.label,
                period_b_label=body.period_b.label,
                period_a_rows=len(body.period_a.data),
                period_b_rows=len(body.period_b.data),
                improved=report.improved,
                degraded=report.degraded,
                vigilance_points=report.vigilance_points,
                executive_summary=report.executive_summary,
                language=body.language,
            )
            ai_result = ai_engine.interpret(context)
            ai_text = ai_result.model_dump_json()
        except Exception as exc:
            logger.warning("Comparison AI interpretation failed: %s", exc)

    report.ai_interpretation = ai_text
    report.ai_status = _ai_status(body.include_ai, ai_text)
    return report


@router.post("/analyze/quick/compare/multi", response_model=MultiPeriodCompareResponse)
@limiter.limit("30/minute")
def quick_compare_multi(
    body: MultiPeriodCompareRequest,
    request: Request,
) -> MultiPeriodCompareResponse:
    """Compare N sequential periods (2, 3, 4... up to 10 periods).

    For each step (i -> i+1), executes the PeriodComparator and aggregates
    a global trajectory assessment.
    """
    periods = body.periods
    comparator = PeriodComparator()
    steps: list[StepComparison] = []
    total_improved = 0
    total_degraded = 0

    for i in range(len(periods) - 1):
        p_a = periods[i]
        p_b = periods[i + 1]
        step_report = comparator.compare(
            period_a_label=p_a.label,
            period_a_data=p_a.data,
            period_b_label=p_b.label,
            period_b_data=p_b.data,
            label=f"{p_a.label} → {p_b.label}",
            language=body.language,
        )
        total_improved += len(step_report.improved)
        total_degraded += len(step_report.degraded)
        steps.append(
            StepComparison(
                from_label=p_a.label,
                to_label=p_b.label,
                improved_count=len(step_report.improved),
                degraded_count=len(step_report.degraded),
                vigilance_count=len(step_report.vigilance_points),
                report=step_report,
            )
        )

    if total_improved > total_degraded * 1.5:
        trajectory = "Amélioration globale et soutenue sur la séquence observée."
    elif total_degraded > total_improved * 1.5:
        trajectory = "Dégradation progressive nécessitant une action corrective prioritaire."
    else:
        trajectory = "Dynamique contrastée avec des progressions sectorielles et des vigilances persistantes."

    return MultiPeriodCompareResponse(
        label=body.label,
        periods_count=len(periods),
        period_labels=[p.label for p in periods],
        global_trajectory=trajectory,
        steps=steps,
        ai_interpretation=None,
        ai_status=_ai_status(body.include_ai, None),
    )




@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("20/minute")
def analyze(
    body: AnalysisRequest,
    request: Request,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> AnalysisResponse:
    """Run analysis on submitted data.

    Flow:
    1. Resolve application + dataset by slug.
    2. Validate the incoming data against the dataset schema.
    3. Run requested analyses (summary, trend, anomaly, ...).
    4. Generate insights from the results.
    5. Optionally, generate an AI interpretation.
    6. Persist everything and return the response.
    """
    # Verify the authenticated app matches the requested slug
    if authed_app.slug != body.application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match the requested application",
        )

    app_repo = ApplicationRepository(db)
    dataset_repo = DatasetRepository(db)

    app = app_repo.get_by_slug(body.application)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")

    dataset = dataset_repo.get_by_slug(app.id, body.dataset)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Build field definitions for validation/analysis
    field_defs = [
        {
            "name": f.name,
            "technical_type": f.technical_type.value,
            "semantic_type": f.semantic_type,
            "unit": f.unit,
            "required": f.required,
        }
        for f in dataset.fields
    ]

    analytics_engine = AnalyticsEngine()
    analysis_type_strs = [a.value for a in body.analysis]
    if "auto" in analysis_type_strs:
        analysis_type_strs = auto_select_analyses(body.data, field_defs)
    validation, results = analytics_engine.analyze(
        data=body.data,
        fields=field_defs,
        analysis_types=analysis_type_strs,
        language=body.language,
    )

    # Create the analysis run record
    run_repo = AnalysisRunRepository(db)
    run = run_repo.create_run(
        application_id=app.id,
        dataset_id=dataset.id,
        analysis_types=analysis_type_strs,
        row_count=len(body.data),
        operator_username=authed_app.name,
    )

    if not validation.valid:
        run_repo.fail_run(run, "Data validation failed")
        return AnalysisResponse(
            success=False,
            analysis_id=run.id,
            application=body.application,
            dataset=body.dataset,
            validation=validation,
        )

    # Segment analysis (opt-in group_by): after validation, attached to
    # results — insights ignore the extra key, persistence carries it.
    # Soft-fail contract: a segment cut never sinks the run.
    if body.group_by:
        try:
            results["grouped"] = build_grouped(
                body.data, field_defs, body.group_by
            )
        except Exception as exc:
            logger.warning(
                "Segment analysis failed (group_by=%s): %s", body.group_by, exc
            )

    # Insights + AI + persistence. Any crash here marks the run "failed"
    # instead of leaving it stuck in "running" forever (PLAN.md S8).
    ai_text = None
    try:
        insight_engine = InsightEngine()
        insight_dicts = insight_engine.generate(results, dataset_name=dataset.name, language=body.language)
        run_repo.add_insights(run, insight_dicts)

        # AI interpretation (optional)
        if body.include_ai:
            try:
                ai_engine = AIEngine()
                context = ai_engine.build_context(
                    application=body.application,
                    dataset=body.dataset,
                    row_count=len(body.data),
                    analysis_results=results,
                    insights=insight_dicts,
                )
                # Tenant's own words (descriptions, units, semantics): each app
                # gets ITS context, rebuilt per request — engine.py untouched.
                business_context = build_business_context(
                    app.name, app.description, [_dataset_context_dict(dataset)]
                )
                segments_line = grouped_context_line(results.get("grouped"))
                if segments_line:
                    business_context += " " + segments_line
                context = context.model_copy(
                    update={"business_context": business_context, "language": body.language}
                )
                ai_result = ai_engine.interpret(context)
                ai_text = ai_result.model_dump_json()
            except Exception as exc:
                # Same contract as /analyze/quick: analysis stands on its own,
                # a provider failure must not sink the run (results kept,
                # ai_status reports the degradation instead).
                logger.warning("AI interpretation failed for run %s: %s", run.id, exc)

        # Persist results
        run_repo.complete_run(run, results, ai_interpretation=ai_text)
    except Exception as exc:
        logger.exception("Post-processing failed for run %s", run.id)
        run_repo.fail_run(run, f"Post-processing failed: {exc}")
        return AnalysisResponse(
            success=False,
            analysis_id=run.id,
            application=body.application,
            dataset=body.dataset,
            validation=validation,
            results=results,
            # Requested but nothing delivered in THIS response.
            ai_status=_ai_status(body.include_ai, None),
        )

    # Load insights from DB for response
    db.refresh(run)
    insight_reads = [InsightRead.model_validate(i) for i in run.insights]

    return AnalysisResponse(
        success=True,
        analysis_id=run.id,
        application=body.application,
        dataset=body.dataset,
        validation=validation,
        results=results,
        insights=insight_reads,
        ai_interpretation=ai_text,
        ai_status=_ai_status(body.include_ai, ai_text),
    )


# ─── Shared helpers ──────────────────────────────────────────────────────────


def _dataset_context_dict(dataset) -> dict[str, Any]:
    """ORM Dataset → plain dict for build_business_context (units, semantics)."""
    return {
        "name": dataset.name,
        "slug": dataset.slug,
        "description": dataset.description,
        "fields": [
            {
                "name": f.name,
                "technical_type": f.technical_type.value,
                "semantic_type": f.semantic_type,
                "unit": f.unit,
                "description": f.description,
            }
            for f in dataset.fields
        ],
    }


def _ai_status(
    include_ai: bool, ai_text: str | None, attempted: bool = True
) -> str | None:
    """Honest AI status carried by the response.

    ``None`` = not requested (or not attempted — validation failed, dataset
    rejected), ``"ok"`` = interpretation delivered, ``"error"`` = requested
    but the provider returned nothing: the statistical results stand on their
    own and the client can SEE the degradation instead of a silent null.
    """
    if not include_ai or not attempted:
        return None
    return "ok" if ai_text else "error"


# ─── Consolidated multi-dataset analysis ─────────────────────────────────────


def _merge_results_for_ai(
    results_by_dataset: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Flatten per-dataset results into one dict for the AI context.

    Every entry is tagged with the dataset it came from so the provider can
    talk about departments/sources by name. Originals are never mutated —
    they feed the response untouched.
    """
    merged: dict[str, list[dict[str, Any]]] = {}
    for slug, res in results_by_dataset.items():
        for key, entries in res.items():
            bucket = merged.setdefault(key, [])
            for entry in entries or []:
                if isinstance(entry, dict):
                    tagged = dict(entry)
                    tagged["dataset"] = slug
                    bucket.append(tagged)
    return merged


def _insights_for_ai(
    insights_by_dataset: dict[str, list[InsightRead]],
    synthesis: dict[str, Any],
) -> list[dict[str, Any]]:
    """All per-dataset insights + the consolidated synthesis as one extra entry,
    in the same dict shape InsightEngine.generate() produces."""
    keys = ("type", "severity", "title", "description", "metric", "confidence")
    flat: list[dict[str, Any]] = [
        {k: dumped[k] for k in keys}
        for slug in insights_by_dataset
        for dumped in (
            insight.model_dump(mode="json")
            for insight in insights_by_dataset[slug]
        )
    ]
    flat.append({
        "type": "recommendation",
        "severity": {"surveiller": "high", "tension": "medium"}.get(
            synthesis.get("verdict", ""), "low"
        ),
        "title": "Synthèse consolidée multi-jeux",
        "description": synthesis.get("summary", ""),
        "metric": "consolidated",
        "confidence": 0.9,
    })
    return flat


@router.post("/analyze/multi", response_model=MultiAnalysisResponse)
@limiter.limit(lambda: f"{settings.analyze_multi_per_minute}/minute")
def analyze_multi(
    body: MultiAnalysisRequest,
    request: Request,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> MultiAnalysisResponse:
    """Analyse SEVERAL datasets of this application in ONE pass.

    Each dataset keeps its own validation, results, insights and analysis
    run (history stays per-dataset). On top of that the response carries
    the consolidated layer:
    - cross_correlations: links BETWEEN datasets, aligned on ``join_key``,
    - synthesis: one decision narrative (trends, divergence, risks, verdict),
    - ai_interpretation (optional): the AI reads the whole picture at once.
    """
    if authed_app.slug != body.application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match the requested application",
        )

    app_repo = ApplicationRepository(db)
    dataset_repo = DatasetRepository(db)

    app = app_repo.get_by_slug(body.application)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Resolve every slug INSIDE the authenticated application — a slug that
    # belongs to another tenant is simply "not found" here (isolation).
    datasets: dict[str, Any] = {}
    for slug in body.datasets:
        dataset = dataset_repo.get_by_slug(app.id, slug)
        if dataset is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{slug}' not found for this application",
            )
        datasets[slug] = dataset

    fields_by_slug: dict[str, list[dict[str, Any]]] = {
        slug: [
            {
                "name": f.name,
                "technical_type": f.technical_type.value,
                "semantic_type": f.semantic_type,
                "unit": f.unit,
                "required": f.required,
            }
            for f in dataset.fields
        ]
        for slug, dataset in datasets.items()
    }

    analytics_engine = AnalyticsEngine()
    insight_engine = InsightEngine()
    run_repo = AnalysisRunRepository(db)
    analysis_type_strs = [a.value for a in body.analysis]

    validations: dict[str, DataValidationResult] = {}
    results: dict[str, dict[str, Any]] = {}
    insights: dict[str, list[InsightRead]] = {}
    analysis_ids: dict[str, str] = {}
    ai_insights: list[dict[str, Any]] = []
    failed: set[str] = set()

    for slug in body.datasets:
        payload = body.payloads[slug]
        slug_analysis_types = (
            auto_select_analyses(payload, fields_by_slug[slug])
            if "auto" in analysis_type_strs
            else analysis_type_strs
        )
        validation, res = analytics_engine.analyze(
            data=payload,
            fields=fields_by_slug[slug],
            analysis_types=slug_analysis_types,
            language=body.language,
        )
        validations[slug] = validation

        run = run_repo.create_run(
            application_id=app.id,
            dataset_id=datasets[slug].id,
            analysis_types=slug_analysis_types,
            row_count=len(payload),
            operator_username=authed_app.name,
        )
        analysis_ids[slug] = run.id

        if not validation.valid:
            run_repo.fail_run(run, "Data validation failed")
            failed.add(slug)
            continue

        # Segment analysis (opt-in group_by): same column per dataset that
        # declares it — the others simply stay ungrouped. Soft-fail.
        if body.group_by:
            try:
                res["grouped"] = build_grouped(
                    payload, fields_by_slug[slug], body.group_by
                )
            except Exception as exc:
                logger.warning(
                    "Segment analysis failed for %s (group_by=%s): %s",
                    slug,
                    body.group_by,
                    exc,
                )

        # Insights + persistence. A crash here marks THIS run failed
        # instead of leaking it as "running" (PLAN.md S8 contract).
        try:
            insight_dicts = insight_engine.generate(res, dataset_name=datasets[slug].name, language=body.language)
            run_repo.add_insights(run, insight_dicts)
            run_repo.complete_run(run, res)
            results[slug] = res
            ai_insights.extend(insight_dicts)
            db.refresh(run)
            insights[slug] = [InsightRead.model_validate(i) for i in run.insights]
        except Exception as exc:
            logger.exception("Multi post-processing failed for dataset %s", slug)
            run_repo.fail_run(run, f"Post-processing failed: {exc}")
            failed.add(slug)

    all_valid = not failed

    cross_links: list[dict[str, Any]] = []
    synthesis: dict[str, Any] | None = None
    join_alignment: dict[str, Any] | None = None
    ai_text: str | None = None

    if all_valid:
        row_counts = {slug: len(body.payloads[slug]) for slug in body.datasets}
        cross_links, join_alignment = cross_correlate_ex(
            body.payloads,
            fields_by_slug,
            body.join_key,
            requested=body.join_granularity,
        )
        synthesis = build_synthesis(
            results,
            cross_links,
            row_counts,
            join_key=body.join_key,
            alignment=join_alignment,
            dataset_names={
                s: datasets[s].name for s in body.datasets if s in datasets
            },
            language=body.language,
        )

        if body.include_ai:
            try:
                ai_engine = AIEngine()
                context = ai_engine.build_context(
                    application=body.application,
                    dataset=", ".join(body.datasets),
                    row_count=sum(row_counts.values()),
                    analysis_results=_merge_results_for_ai(results),
                    insights=_insights_for_ai(insights, synthesis),
                )
                business_context = build_business_context(
                    app.name,
                    app.description,
                    [
                        _dataset_context_dict(datasets[s])
                        for s in body.datasets
                        if s in datasets
                    ],
                )
                for s in body.datasets:
                    segments_line = grouped_context_line(
                        (results.get(s) or {}).get("grouped")
                    )
                    if segments_line:
                        business_context += f" [{s}] {segments_line}"
                context = context.model_copy(
                    update={"business_context": business_context, "language": body.language}
                )
                ai_result = ai_engine.interpret(context)
                ai_text = ai_result.model_dump_json()
            except Exception as exc:
                # Same contract as /analyze/quick: analysis stands on its
                # own, a provider failure must not sink the whole run.
                logger.warning("Multi-analysis AI interpretation failed: %s", exc)

    return MultiAnalysisResponse(
        success=all_valid,
        application=body.application,
        datasets=body.datasets,
        join_key=body.join_key,
        validations=validations,
        results=results,
        insights=insights,
        cross_correlations=cross_links,
        synthesis=synthesis,
        join_alignment=(
            JoinAlignment.model_validate(join_alignment)
            if join_alignment is not None
            else None
        ),
        ai_interpretation=ai_text,
        ai_status=_ai_status(body.include_ai, ai_text, attempted=all_valid),
        analysis_ids=analysis_ids,
    )


@router.get("/analysis/{run_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    run_id: str,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> AnalysisDetailResponse:
    """Retrieve a specific analysis run.

    Returns 404 (not 403) when the run belongs to another application, to
    avoid confirming the existence of another application's resources.
    """
    run_repo = AnalysisRunRepository(db)
    run = run_repo.get_with_insights(run_id)

    # Return 404 whether run is missing OR belongs to another app
    if run is None or run.application_id != authed_app.id:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    app_repo = ApplicationRepository(db)
    dataset_repo = DatasetRepository(db)
    app = app_repo.get(run.application_id)
    dataset = dataset_repo.get(run.dataset_id)

    results = json.loads(run.result) if run.result else None
    insights = [InsightRead.model_validate(i) for i in run.insights]

    return AnalysisDetailResponse(
        success=run.status == "completed",
        analysis_id=run.id,
        application=app.slug if app else "",
        dataset=dataset.slug if dataset else "",
        validation={"valid": True, "errors": [], "row_count": run.row_count or 0},
        results=results,
        insights=insights,
        ai_interpretation=run.ai_interpretation,
        created_at=run.created_at,
        completed_at=run.completed_at,
        status=run.status,
    )


@router.get("/analysis", response_model=list[AnalysisRunRead])
def list_analyses(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0, description="Rows to skip — pagination cursor"),
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> list[AnalysisRunRead]:
    """List recent analysis runs for the authenticated application only."""
    run_repo = AnalysisRunRepository(db)
    runs = run_repo.list_by_application(authed_app.id, limit=limit, skip=skip)
    return [AnalysisRunRead.model_validate(r) for r in runs]


@router.get("/analysis/admin/all", response_model=list[dict[str, Any]])
def list_all_analyses_admin(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_dashboard_user),
) -> list[dict[str, Any]]:
    """List all analysis runs across all applications for the dashboard operator."""
    run_repo = AnalysisRunRepository(db)
    app_repo = ApplicationRepository(db)
    dataset_repo = DatasetRepository(db)

    runs = run_repo.list_recent(limit=limit)
    out = []
    for r in runs:
        app = app_repo.get(r.application_id)
        dataset = dataset_repo.get(r.dataset_id)
        label = None
        if r.result:
            try:
                parsed_res = json.loads(r.result) if isinstance(r.result, str) else r.result
                if isinstance(parsed_res, dict):
                    label = parsed_res.get("label")
            except Exception:
                pass
        out.append({
            "id": r.id,
            "label": label,
            "application_name": app.name if app else "Test Rapide",
            "application_slug": app.slug if app else "quick-test",
            "dataset_name": dataset.name if dataset else "Données brutes",
            "dataset_slug": dataset.slug if dataset else "data",
            "analysis_types": r.analysis_types,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "row_count": r.row_count,
            "operator_username": r.operator_username or "Admin",
            "created_at": r.created_at.isoformat(),
            "has_ai": bool(r.ai_interpretation),
            "result": r.result,
            "ai_interpretation": r.ai_interpretation,
        })
    return out
