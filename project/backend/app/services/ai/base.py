"""Abstract AI provider interface.

Every AI provider (mock, local LLM, future cloud) implements this interface.
The key design principle: providers receive only an ``AnalyticalContext`` —
aggregated, sanitized metadata — never raw data.
"""

from __future__ import annotations

import abc

from app.schemas.ai import AIInterpretation, AnalyticalContext


class AIProvider(abc.ABC):
    """Abstract interface for AI interpretation providers."""

    name: str = "base"

    @abc.abstractmethod
    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        """Produce an AI interpretation from a sanitized analytical context."""
        ...
