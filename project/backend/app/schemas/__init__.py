"""Re-export all schemas for convenient importing."""

from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.schemas.analytics import (
    AnalysisDetailResponse,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisResult,
    AnalysisRunRead,
    AnomalyResult,
    DataValidationResult,
    InsightRead,
    SummaryResult,
    TrendResult,
    ValidationIssue,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    ApplicationWithKey,
)
from app.schemas.common import HealthStatus, PaginatedResponse
from app.schemas.dataset import (
    DatasetCreate,
    DatasetFieldCreate,
    DatasetFieldRead,
    DatasetRead,
    DatasetUpdate,
)

__all__ = [
    "AIInterpretation",
    "AnalyticalContext",
    "AnalysisDetailResponse",
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisResult",
    "AnalysisRunRead",
    "AnomalyResult",
    "ApplicationCreate",
    "ApplicationRead",
    "ApplicationUpdate",
    "ApplicationWithKey",
    "DataValidationResult",
    "DatasetCreate",
    "DatasetFieldCreate",
    "DatasetFieldRead",
    "DatasetRead",
    "DatasetUpdate",
    "HealthStatus",
    "InsightRead",
    "PaginatedResponse",
    "SummaryResult",
    "TrendResult",
    "ValidationIssue",
]
