"""Health check endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthStatus
from app.services.ai.engine import AIEngine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthStatus, summary="Health check")
@router.get("/", response_model=HealthStatus, summary="Health check", include_in_schema=False)
def health_check(db: Session = Depends(get_db)) -> HealthStatus:
    db_ok = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = "disconnected"

    ai_engine = AIEngine()

    return HealthStatus(
        status="healthy" if db_ok == "connected" else "degraded",
        version="1.0.0",
        database=db_ok,
        ai_provider=ai_engine.provider_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
