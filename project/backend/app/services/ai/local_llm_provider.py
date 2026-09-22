"""Local LLM provider — stub for future Ollama / llama.cpp integration.

This provider is intentionally NOT implemented in V1. It exists to show the
integration point and the contract the future implementation must satisfy.
When ready, replace the ``interpret`` body with a call to the local LLM
(see README for setup instructions).
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider

logger = get_logger(__name__)


class LocalLLMProvider(AIProvider):
    name = "local_llm"

    def __init__(self, base_url: str = "", model: str = "") -> None:
        self.base_url = base_url
        self.model = model

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        """Future implementation will call a local LLM via HTTP.

        Planned flow:
        1. Build a prompt from ``context`` (which contains NO raw data).
        2. POST to ``{base_url}/api/generate`` (Ollama) or equivalent.
        3. Parse the LLM response into structured findings/recommendations.

        For now, log a warning and return a placeholder.
        """
        logger.warning(
            "LocalLLMProvider is not yet implemented — returning placeholder. "
            "Set AI_PROVIDER=mock in .env to use the mock provider."
        )
        return AIInterpretation(
            provider=self.name,
            summary=(
                "Local LLM integration is not yet configured. "
                "This is a placeholder response."
            ),
            key_findings=["Local LLM provider not implemented in V1."],
            recommendations=[
                "Configure Ollama or llama.cpp and update LocalLLMProvider "
                "to enable real AI interpretation."
            ],
            confidence=0.0,
        )
