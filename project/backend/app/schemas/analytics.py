"""Pydantic schemas for the analytics API — analysis requests and responses."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models import AnalysisStatus, AnalysisType, InsightSeverity, InsightType
from app.schemas.common import UTCDateTime

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
    group_by: str | None = Field(
        default=None,
        max_length=255,
        description=(
            "Categorical column to cut every numeric measure by (product, "
            "region…). Omitted = today's behaviour; an absent column soft-"
            "fails (results.grouped carries an explanatory note)."
        ),
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


class CorrelationResult(BaseModel):
    column1: str
    column2: str
    coefficient: float
    p_value: float
    strength: str
    relationship: str


class DistributionResult(BaseModel):
    column: str
    skewness: float
    kurtosis: float
    percentiles: dict[str, float]
    shapiro_p_value: float | None = None
    is_normal: bool | None = None
    count: int


class ForecastResult(BaseModel):
    column: str
    horizon: int
    predictions: list[dict[str, Any]]
    trend_direction: str
    slope: float


# ─── Segment analysis (group_by) ────────────────────────────

class GroupedMetric(BaseModel):
    """One numeric measure inside one segment (summary vocabulary + sum/share)."""

    count: int
    mean: float
    median: float
    min: float
    max: float
    std: float
    sum: float
    # segment sum / total sum over the segmented rows (None when total = 0).
    share: float | None = None


class GroupedSegment(BaseModel):
    segment: str
    rank: int
    row_count: int
    metrics: dict[str, GroupedMetric] = {}


class GroupedResult(BaseModel):
    """Numeric measures cut by one categorical column (request's group_by).

    ``ranked_by`` = first declared numeric column; segments come sorted by its
    descending total. Soft contract: absent column / no usable value →
    ``segments: []`` with an explanatory French ``note`` — never a hard error.
    """

    group_by: str
    ranked_by: str | None = None
    segment_count: int = 0
    segments: list[GroupedSegment] = []
    note: str | None = None


class AnalysisResult(BaseModel):
    summary: list[SummaryResult] | None = None
    trend: list[TrendResult] | None = None
    anomaly: list[AnomalyResult] | None = None
    correlation: list[CorrelationResult] | None = None
    distribution: list[DistributionResult] | None = None
    forecast: list[ForecastResult] | None = None
    # Present only when the request set group_by (additive — null otherwise).
    grouped: GroupedResult | None = None



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
    created_at: UTCDateTime
    completed_at: UTCDateTime | None = None


class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    application: str
    dataset: str
    validation: DataValidationResult
    results: AnalysisResult | None = None
    insights: list[InsightRead] = []
    ai_interpretation: str | None = None
    # None = IA non demandée ; "ok" = interprétation livrée ;
    # "error" = demandée mais le fournisseur n'a rien rendu (résultats seuls).
    ai_status: Literal["ok", "error"] | None = None


class AnalysisDetailResponse(AnalysisResponse):
    created_at: UTCDateTime
    completed_at: UTCDateTime | None = None
    status: AnalysisStatus


# ─── Consolidated multi-dataset analysis ─────────────────

# Maximum number of datasets analysed in one consolidated pass.
MAX_MULTI_DATASETS = 10


class MultiAnalysisRequest(BaseModel):
    """One request, N datasets — the consolidated analysis entry point.

    Every dataset of ONE application is validated, analysed, persisted and
    returned under its own slug; on top of that the endpoint computes the
    links BETWEEN datasets (aligned on ``join_key``) and a decision-oriented
    synthesis. Payload keys must match ``datasets`` exactly.
    """

    model_config = ConfigDict(extra="forbid")

    application: str = Field(
        ...,
        description="Application slug",
        min_length=1,
        max_length=255,
        validation_alias=AliasChoices("application", "application_slug"),
    )
    datasets: list[str] = Field(
        ...,
        min_length=1,
        max_length=MAX_MULTI_DATASETS,
        description=(
            "Dataset slugs to analyse together "
            f"(1..{MAX_MULTI_DATASETS}, unique, same application)."
        ),
    )
    analysis: list[AnalysisType] = Field(..., min_length=1)
    payloads: dict[str, list[dict[str, Any]]] = Field(
        ...,
        description="Data rows keyed by dataset slug — must match `datasets` exactly.",
    )
    join_key: str | None = Field(
        default=None,
        max_length=255,
        description=(
            "Common column aligning rows across datasets (e.g. 'mois'). "
            "When omitted, per-dataset analysis still runs but cross-dataset "
            "correlations are skipped (no safe way to align rows)."
        ),
    )
    join_granularity: Literal["auto", "exact", "day", "month"] = Field(
        default="auto",
        description=(
            "How join_key values meet across datasets. 'auto' (default) "
            "normalizes date-parseable keys to month so a day-grain dataset "
            "aligns with a month-grain one; 'exact' keeps raw strings "
            "strictly equal; 'day'/'month' force the normalization. "
            "Non-date keys always keep raw equality."
        ),
    )
    group_by: str | None = Field(
        default=None,
        max_length=255,
        description=(
            "Categorical column to cut numeric measures by, per dataset. "
            "Applied to the datasets that declare the column; the others get "
            "an empty `grouped` block with an explanatory note (soft-fail)."
        ),
    )
    include_ai: bool = False

    @field_validator("application")
    @classmethod
    def slug_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()

    @field_validator("datasets")
    @classmethod
    def datasets_clean(cls, v: list[str]) -> list[str]:
        cleaned = [d.strip() for d in v]
        if any(not d for d in cleaned):
            raise ValueError("dataset slugs must not be blank")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("dataset slugs must be unique")
        return cleaned

    @field_validator("join_key")
    @classmethod
    def join_key_blank_is_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip() or None

    @model_validator(mode="after")
    def payloads_match_datasets(self) -> "MultiAnalysisRequest":
        wanted = set(self.datasets)
        got = set(self.payloads)
        if wanted != got:
            parts = []
            missing = sorted(wanted - got)
            extra = sorted(got - wanted)
            if missing:
                parts.append(f"missing payload(s) for: {', '.join(missing)}")
            if extra:
                parts.append(f"unknown payload key(s): {', '.join(extra)}")
            raise ValueError("; ".join(parts))
        for slug, rows in self.payloads.items():
            if not rows:
                raise ValueError(f"payload for '{slug}' must not be empty")
            if len(rows) > MAX_DATA_ROWS:
                raise ValueError(
                    f"payload for '{slug}' exceeds {MAX_DATA_ROWS} rows"
                )
        return self


class CrossCorrelationResult(BaseModel):
    """A statistically significant link BETWEEN two datasets."""

    dataset1: str
    column1: str
    dataset2: str
    column2: str
    coefficient: float
    p_value: float
    strength: str  # "strong" (|r| >= 0.7) | "moderate"
    relationship: str  # "positive" | "negative"


class JoinAlignment(BaseModel):
    """How join_key values actually met between datasets (never silent).

    ``granularity`` is what was APPLIED (``requested`` is what the client
    asked for — 'auto' resolves to one of exact/day/month); ``note`` explains
    the outcome in French when normalization kicked in or alignment is
    partial, ``None`` when every key met exactly as sent.
    """

    join_key: str
    requested: str = "auto"
    granularity: str = "exact"
    keys_by_dataset: dict[str, int] = {}
    aligned_keys: int = 0
    note: str | None = None


class ConsolidatedSynthesis(BaseModel):
    """Decision block computed across all datasets of one run."""

    datasets_analyzed: int
    total_rows: int
    join_key: str | None = None
    trends: dict[str, str] = {}  # slug -> "up" | "down" | "stable"
    # slug -> display name (polished prose only; structured fields keep slugs)
    dataset_names: dict[str, str] = {}
    divergent: bool = False
    top_links: list[CrossCorrelationResult] = []
    risks: list[str] = []
    verdict: str = "equilibre"  # "positif" | "equilibre" | "tension" | "surveiller"
    summary: str = ""
    # Join facts (grain applied + keys that met) — informational, never
    # steers the verdict. See JoinAlignment for the shape.
    alignment: dict[str, Any] | None = None


class MultiAnalysisResponse(BaseModel):
    success: bool
    application: str
    datasets: list[str]
    join_key: str | None = None
    validations: dict[str, DataValidationResult] = {}
    results: dict[str, AnalysisResult] = {}
    insights: dict[str, list[InsightRead]] = {}
    cross_correlations: list[CrossCorrelationResult] = []
    synthesis: ConsolidatedSynthesis | None = None
    # Grain applied to join_key + how many keys met — absent when join_key
    # is omitted (nothing attempted, not "no alignment found").
    join_alignment: JoinAlignment | None = None
    ai_interpretation: str | None = None
    # None = IA non demandée/non tentée ; "ok" = interprétation livrée ;
    # "error" = demandée mais le fournisseur n'a rien rendu.
    ai_status: Literal["ok", "error"] | None = None
    # One analysis run per dataset (history stays per-dataset).
    analysis_ids: dict[str, str] = {}
