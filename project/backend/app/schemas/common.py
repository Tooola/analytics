"""Pydantic schemas for health checks and common responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator


def _ensure_utc(value: Any) -> Any:
    """Re-attach UTC to naive datetimes.

    SQLite stores DATETIME without tzinfo, so values written as aware UTC
    (models._utcnow) come back naive. Normalising at the API boundary makes
    every timestamp serialise with +00:00, like /health does (PLAN.md S2).
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            # Written as aware UTC (models._utcnow) — SQLite dropped the tag.
            return value.replace(tzinfo=timezone.utc)
        # Already aware: normalise so every API timestamp serialises as UTC.
        return value.astimezone(timezone.utc)
    return value


#: datetime that is always timezone-aware (UTC) in API responses.
UTCDateTime = Annotated[datetime, BeforeValidator(_ensure_utc)]


class HealthStatus(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    database: str  # "connected", "disconnected"
    ai_provider: str
    timestamp: str


class PaginatedResponse(BaseModel):
    """Generic pagination wrapper."""
    items: list
    total: int
    skip: int
    limit: int
