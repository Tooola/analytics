"""Schemas for temporal comparison (Period A vs Period B).

Allows comparing two distinct periods (Month M vs M-1, Year N vs N-1)
without manual file merging, producing executive evolution assessments:
- What improved
- What degraded
- New points of attention
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class PeriodData(BaseModel):
    """Payload representing one time period."""
    label: str = Field(..., description="E.g. 'Mois M-1', 'Octobre 2026', 'Année N-1'")
    data: list[dict[str, Any]] = Field(..., description="Array of records for this period")


class MetricEvolution(BaseModel):
    """Evolution of a single numeric indicator between Period A and Period B."""
    metric: str
    label: str
    direction: Literal["up", "down", "stable"]
    change_pct: float | None = None
    status: Literal["improved", "degraded", "stable"]
    explanation: str


class VigilancePoint(BaseModel):
    """Anomalies or risks that appeared or worsened in Period B."""
    metric: str
    label: str
    severity: Literal["high", "medium", "low"] = "medium"
    description: str


class QuickCompareRequest(BaseModel):
    """Request to compare two periods in quick test mode."""
    period_a: PeriodData
    period_b: PeriodData
    label: str = "comparatif-temporel"
    include_ai: bool = True


class CompareResponse(BaseModel):
    """Executive evolution report between two periods."""
    success: bool
    label: str
    period_a_label: str
    period_b_label: str
    period_a_rows: int
    period_b_rows: int
    improved: list[MetricEvolution] = Field(default_factory=list)
    degraded: list[MetricEvolution] = Field(default_factory=list)
    stable: list[MetricEvolution] = Field(default_factory=list)
    vigilance_points: list[VigilancePoint] = Field(default_factory=list)
    executive_summary: str = ""
    ai_interpretation: str | None = None
    ai_status: str | None = None
