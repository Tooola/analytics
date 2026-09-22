"""AI engine — factory and orchestrator for AI providers.

Selects the configured provider and builds the AnalyticalContext that gets
passed to it. The context is built from analysis results — never from raw data.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider
from app.services.ai.local_llm_provider import LocalLLMProvider
from app.services.ai.mock_provider import MockAIProvider

logger = get_logger(__name__)


class AIEngine:
    """Builds analytical contexts and dispatches to the configured AI provider."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        if provider is not None:
            self._provider = provider
        elif settings.ai_provider == "gemini" and settings.gemini_api_key:
            from app.services.ai.gemini_provider import GeminiAIProvider
            self._provider = GeminiAIProvider(api_key=settings.gemini_api_key)
        elif settings.ai_provider == "local_llm":
            self._provider = LocalLLMProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
            )
        else:
            self._provider = MockAIProvider()

        logger.info("AI provider: %s", self._provider.name)

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def build_context(
        self,
        application: str,
        dataset: str,
        row_count: int,
        analysis_results: dict[str, Any],
        insights: list[dict[str, Any]],
    ) -> AnalyticalContext:
        """Build a sanitized AnalyticalContext from analysis results.

        No raw data rows are included — only aggregated statistics,
        trends, anomalies, and generated insights.
        """
        return AnalyticalContext(
            application=application,
            dataset=dataset,
            row_count=row_count,
            summary=analysis_results.get("summary", []),
            trends=analysis_results.get("trend", []),
            anomalies=analysis_results.get("anomaly", []),
            insights=insights,
        )

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        return self._provider.interpret(context)
