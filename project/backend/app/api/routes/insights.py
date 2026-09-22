"""Insights listing endpoint — authenticated and scoped to the calling application."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key
from app.core.database import get_db
from app.models import Application
from app.repositories.analysis_repo import AnalysisRunRepository, InsightRepository
from app.schemas.analytics import InsightRead

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=list[InsightRead])
def list_insights(
    run_id: str | None = Query(None, description="Filter by analysis run ID"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> list[InsightRead]:
    """List insights for the authenticated application.

    If `run_id` is provided, the run is verified to belong to the
    authenticated application before returning its insights.
    """
    repo = InsightRepository(db)

    if run_id:
        # Verify the requested run belongs to the authenticated application.
        run_repo = AnalysisRunRepository(db)
        run = run_repo.get_with_insights(run_id)
        if run is None or run.application_id != authed_app.id:
            # Return 404 (not 403) to avoid leaking the existence of other apps' runs.
            raise HTTPException(status_code=404, detail="Analysis run not found")
        insights = repo.list_by_run(run_id)
    else:
        insights = repo.list_by_application(authed_app.id, limit=limit)

    return [InsightRead.model_validate(i) for i in insights]
