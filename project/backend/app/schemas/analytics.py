"""Pydantic schemas for the analytics API — analysis requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.models import AnalysisStatus, AnalysisType, InsightSeverity, InsightType


# ─── Data validation ───────────────────────────────────


class ValidationIssue(BaseModel):
    field: str
    error: str
    row: int | None = None


class DataValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationIssue] = []
    row_count: int = 0


# ─── Analysis request ──────────────────────────────────

# Maximum number of data rows accepted per analysis request.
# This protects against memory exhaustion on very large payloads.
MAX_DATA_ROWS = 10_000


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown fields

    application: str = Field(
        ...,
        description="Application slug",
        min_length=1,
        max_length=255,
        validation_alias=AliasChoices("application", "application_slug"),
    )
    dataset: str = Field(
        ...,
        description="Dataset slug",
        min_length=1,
        max_length=255,
        validation_alias=AliasChoices("dataset", "dataset_slug"),
    )
    analysis: list[AnalysisType] = Field(..., min_length=1)
    data: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=MAX_DATA_ROWS,
        description=f"Data rows to analyse (max {MAX_DATA_ROWS} rows per request).",
    )
    include_ai: bool = False

    @field_validator("application", "dataset")
    @classmethod
    def slug_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


# ─── Analysis results ──────────────────────────────────


class SummaryResult(BaseModel):
    count: int
    mean: float | None = None
    median: float | None = None
    min: float | None = None
    max: float | None = None
    std: float | None = None
    column: str | None = None


class TrendResult(BaseModel):
    column: str
    change_pct: float | None = None
    direction: str  # "up", "down", "stable"
    first_value: float | None = None
    last_value: float | None = None
    periods: int = 0


class AnomalyResult(BaseModel):
    column: str
    anomalies: list[dict[str, Any]] = []
    count: int = 0
    method: str = "zscore"


class AnalysisResult(BaseModel):
    summary: list[SummaryResult] | None = None
    trend: list[TrendResult] | None = None
    anomaly: list[AnomalyResult] | None = None


class InsightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: InsightType
    severity: InsightSeverity
    title: str
    description: str
    metric: str | None = None
    value: float | None = None
    unit: str | None = None
    confidence: float = 1.0


class AnalysisRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    dataset_id: str
    analysis_types: str
    status: AnalysisStatus
    row_count: int | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    application: str
    dataset: str
    validation: DataValidationResult
    results: AnalysisResult | None = None
    insights: list[InsightRead] = []
    ai_interpretation: str | None = None


class AnalysisDetailResponse(AnalysisResponse):
    created_at: datetime
    completed_at: datetime | None = None
    status: AnalysisStatus
