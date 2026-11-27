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
from app.schemas.analytics import DataValidationResult
from app.services.analytics.anomaly import AnomalyService
from app.services.analytics.base import BaseAnalyticsService
from app.services.analytics.causality import CausalityService
from app.services.analytics.correlation import CorrelationService
from app.services.analytics.distribution import DistributionService
from app.services.analytics.forecast import ForecastService
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
        for svc in (
            SummaryService(),
            TrendService(),
            AnomalyService(),
            CorrelationService(),
            DistributionService(),
            ForecastService(),
            CausalityService(),
        ):
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
        language: str = "fr",
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

        # Parallel dispatch across independent analytical services
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import inspect

        def _run_single(atype: str) -> tuple[str, dict[str, Any] | None]:
            svc = self._services.get(atype)
            if svc is None:
                logger.warning("Unknown analysis type: %s", atype)
                return atype, None
            try:
                sig = inspect.signature(svc.run)
                if "language" in sig.parameters:
                    res = svc.run(df, field_dicts, language=language)
                else:
                    res = svc.run(df, field_dicts)
                return atype, res
            except Exception:
                logger.exception("Analysis service crashed: %s", atype)
                return atype, None

        if len(analysis_types) > 1:
            with ThreadPoolExecutor(max_workers=min(4, len(analysis_types))) as executor:
                futures = [executor.submit(_run_single, atype) for atype in analysis_types]
                for f in as_completed(futures):
                    _, partial = f.result()
                    if partial:
                        results.update(partial)
        else:
            for atype in analysis_types:
                _, partial = _run_single(atype)
                if partial:
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
