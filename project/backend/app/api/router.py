"""API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import analytics, applications, datasets, health, insights

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(applications.router)
api_router.include_router(datasets.router)
api_router.include_router(analytics.router)
api_router.include_router(insights.router)
