"""Analytics endpoint — the core analysis flow."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.ratelimit import limiter
from app.models import Application
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
from app.services.ai.business_context import build_business_context
from app.services.ai.engine import AIEngine
from app.services.analytics.cross_correlation import cross_correlate_ex
from app.services.analytics.engine import AnalyticsEngine
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
    analysis: list[str] = ["summary", "trend", "anomaly"]
    include_ai: bool = False
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
            # Try to detect date strings
            str_samples = [str(v) for v in samples]
            if any(c in str_samples[0] for c in ("-", "/")) and len(str_samples[0]) >= 8:
                t = "date"
            else:
                t = "string"
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
    analytics_engine = AnalyticsEngine()
    _, results = analytics_engine.analyze(
        data=body.data,
        fields=field_defs,
        analysis_types=body.analysis,
    )

    insight_engine = InsightEngine()
    insight_dicts = insight_engine.generate(results, dataset_name=body.label)

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
            # Sandbox: no tenant app exists — say so in the business context.
            context = context.model_copy(
                update={
                    "business_context": (
                        f"Banc d'essai rapide — libellé « {body.label} ». "
                        "Aucune application enregistrée : contexte métier non déclaré."
                    )
                }
            )
            ai_result = ai_engine.interpret(context)
            ai_text = ai_result.model_dump_json()
        except Exception as exc:
            logger.warning("Quick analyze AI failed: %s", exc)

    return {
        "success": True,
        "label": body.label,
        "row_count": len(body.data),
        "fields_inferred": field_defs,
        "results": results,
        "insights": insight_dicts,
        "ai_interpretation": ai_text,
        "ai_status": _ai_status(body.include_ai, ai_text),
    }




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
    validation, results = analytics_engine.analyze(
        data=body.data,
        fields=field_defs,
        analysis_types=analysis_type_strs,
    )

    # Create the analysis run record
    run_repo = AnalysisRunRepository(db)
    run = run_repo.create_run(
        application_id=app.id,
        dataset_id=dataset.id,
        analysis_types=analysis_type_strs,
        row_count=len(body.data),
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

    # Insights + AI + persistence. Any crash here marks the run "failed"
    # instead of leaving it stuck in "running" forever (PLAN.md S8).
    ai_text = None
    try:
        insight_engine = InsightEngine()
        insight_dicts = insight_engine.generate(results, dataset_name=dataset.name)
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
                context = context.model_copy(
                    update={
                        "business_context": build_business_context(
                            app.name, app.description, [_dataset_context_dict(dataset)]
                        )
                    }
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
        validation, res = analytics_engine.analyze(
            data=payload,
            fields=fields_by_slug[slug],
            analysis_types=analysis_type_strs,
        )
        validations[slug] = validation

        run = run_repo.create_run(
            application_id=app.id,
            dataset_id=datasets[slug].id,
            analysis_types=analysis_type_strs,
            row_count=len(payload),
        )
        analysis_ids[slug] = run.id

        if not validation.valid:
            run_repo.fail_run(run, "Data validation failed")
            failed.add(slug)
            continue

        # Insights + persistence. A crash here marks THIS run failed
        # instead of leaking it as "running" (PLAN.md S8 contract).
        try:
            insight_dicts = insight_engine.generate(res, dataset_name=datasets[slug].name)
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
                context = context.model_copy(
                    update={
                        "business_context": build_business_context(
                            app.name,
                            app.description,
                            [
                                _dataset_context_dict(datasets[s])
                                for s in body.datasets
                                if s in datasets
                            ],
                        )
                    }
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
