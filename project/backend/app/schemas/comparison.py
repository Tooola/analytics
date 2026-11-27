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
    language: str = "fr"


class CompareResponse(BaseModel):
    """Executive evolution report between two periods."""
    success: bool = True
    label: str
    period_a_label: str
    period_b_label: str
    period_a_rows: int
    period_b_rows: int
    executive_summary: str = ""
    improved: list[MetricEvolution] = Field(default_factory=list)
    degraded: list[MetricEvolution] = Field(default_factory=list)
    stable: list[MetricEvolution] = Field(default_factory=list)
    vigilance_points: list[VigilancePoint] = Field(default_factory=list)
    comparative_metrics: list[dict[str, Any]] = Field(default_factory=list)
    ai_interpretation: str | None = None
    ai_status: str | None = None


class MultiPeriodCompareRequest(BaseModel):
    """Request to compare 2 to 10 sequential periods (e.g. 3 or 4 months)."""
    periods: list[PeriodData] = Field(..., min_length=2, max_length=10)
    label: str = "comparatif-multi-periodes"
    include_ai: bool = True
    language: str = "fr"


class StepComparison(BaseModel):
    from_label: str
    to_label: str
    improved_count: int
    degraded_count: int
    vigilance_count: int
    report: CompareResponse


class MultiPeriodCompareResponse(BaseModel):
    success: bool = True
    label: str
    periods_count: int
    period_labels: list[str]
    global_trajectory: str
    steps: list[StepComparison]
    ai_interpretation: str | None = None
    ai_status: str | None = None
