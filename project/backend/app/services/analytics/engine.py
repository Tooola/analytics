"""Analytics engine — orchestrates analysis services.

This is the main entry point for running analyses. It:
1. Validates incoming data against the dataset schema.
2. Converts the data to a pandas DataFrame.
3. Dispatches to the requested analysis services.
4. Returns a unified result dict.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.core.logging import get_logger
from app.models import AnalysisType
from app.schemas.analytics import DataValidationResult
from app.services.analytics.anomaly import AnomalyService
from app.services.analytics.base import BaseAnalyticsService
from app.services.analytics.summary import SummaryService
from app.services.analytics.trend import TrendService
from app.services.analytics.validator import DataValidator

logger = get_logger(__name__)


class AnalyticsEngine:
    """Orchestrates data validation and analysis dispatch."""

    def __init__(self) -> None:
        self._validator = DataValidator()
        self._services: dict[str, BaseAnalyticsService] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        for svc in (SummaryService(), TrendService(), AnomalyService()):
            self.register(svc)

    def register(self, service: BaseAnalyticsService) -> None:
        """Register a custom analysis service."""
        self._services[service.analysis_type] = service
        logger.debug("Registered analytics service: %s", service.analysis_type)

    def validate(
        self,
        data: list[dict[str, Any]],
        fields: list[dict[str, Any]],
    ) -> DataValidationResult:
        return self._validator.validate(data, fields)

    def analyze(
        self,
        data: list[dict[str, Any]],
        fields: list[dict[str, Any]],
        analysis_types: list[str],
    ) -> tuple[DataValidationResult, dict[str, Any]]:
        """Validate data, then run requested analyses.

        Returns (validation_result, analysis_results).
        If validation fails, analysis_results is empty.
        """
        validation = self.validate(data, fields)
        if not validation.valid:
            return validation, {}

        df = pd.DataFrame(data)
        field_dicts = [self._field_to_dict(f) for f in fields]
        results: dict[str, Any] = {}

        for atype in analysis_types:
            svc = self._services.get(atype)
            if svc is None:
                logger.warning("Unknown analysis type: %s", atype)
                continue
            logger.info("Running analysis: %s", atype)
            partial = svc.run(df, field_dicts)
            results.update(partial)

        return validation, results

    @staticmethod
    def _field_to_dict(field: Any) -> dict[str, Any]:
        """Accept either a DatasetField ORM obj or a plain dict."""
        if isinstance(field, dict):
            return {
                "name": field["name"],
                "technical_type": field["technical_type"]
                if isinstance(field["technical_type"], str)
                else field["technical_type"].value,
                "semantic_type": field.get("semantic_type"),
                "unit": field.get("unit"),
                "required": field.get("required", True),
            }
        return {
            "name": field.name,
            "technical_type": field.technical_type.value,
            "semantic_type": field.semantic_type,
            "unit": field.unit,
            "required": field.required,
        }
