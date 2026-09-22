"""Analytics endpoint — the core analysis flow."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key
from app.core.database import get_db
from app.core.logging import get_logger
from app.models import Application
from app.repositories.analysis_repo import AnalysisRunRepository
from app.repositories.application_repo import ApplicationRepository
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.analytics import (
    AnalysisDetailResponse,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisRunRead,
    InsightRead,
)
from app.services.ai.engine import AIEngine
from app.services.analytics.engine import AnalyticsEngine
from app.services.insights.engine import InsightEngine

router = APIRouter(tags=["analytics"])
logger = get_logger(__name__)


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(
    body: AnalysisRequest,
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

    # Generate insights
    insight_engine = InsightEngine()
    insight_dicts = insight_engine.generate(results, dataset_name=dataset.name)
    run_repo.add_insights(run, insight_dicts)

    # AI interpretation (optional)
    ai_text = None
    if body.include_ai:
        ai_engine = AIEngine()
        context = ai_engine.build_context(
            application=body.application,
            dataset=body.dataset,
            row_count=len(body.data),
            analysis_results=results,
            insights=insight_dicts,
        )
        ai_result = ai_engine.interpret(context)
        ai_text = ai_result.model_dump_json()

    # Persist results
    run_repo.complete_run(run, results, ai_interpretation=ai_text)

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
    limit: int = 50,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> list[AnalysisRunRead]:
    """List recent analysis runs for the authenticated application only."""
    run_repo = AnalysisRunRepository(db)
    runs = run_repo.list_by_application(authed_app.id, limit=limit)
    return [AnalysisRunRead.model_validate(r) for r in runs]
