"""Pydantic schemas for AI interpretation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyticalContext(BaseModel):
    """Sanitized context passed to AI providers — no raw data, only statistics.

    This object is the ONLY thing an AI provider ever sees. It contains
    aggregated metrics, trends, anomalies, and insights — never individual
    rows or sensitive raw values.
    """

    application: str
    dataset: str
    row_count: int = 0
    summary: list[dict[str, Any]] = Field(default_factory=list)
    trends: list[dict[str, Any]] = Field(default_factory=list)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    insights: list[dict[str, Any]] = Field(default_factory=list)
    business_context: str | None = None


class AIInterpretation(BaseModel):
    provider: str
    summary: str
    key_findings: list[str] = []
    recommendations: list[str] = []
    action_plan: list[str] = []
    risk_assessment: str | None = None
    confidence: float = 1.0
    raw: dict[str, Any] | None = None
