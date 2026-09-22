"""Pydantic schemas for health checks and common responses."""

from __future__ import annotations

from pydantic import BaseModel


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
