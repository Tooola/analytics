"""Abstract base class for all analytics services.

Each analysis type is a self-contained class with a single ``run`` method.
The AnalyticsEngine dispatches to the appropriate service(s) based on the
requested analysis types.
"""

from __future__ import annotations

import abc
from typing import Any

import pandas as pd


class BaseAnalyticsService(abc.ABC):
    """Base class for a single analysis type."""

    #: The AnalysisType enum value this service handles.
    analysis_type: str = ""

    @abc.abstractmethod
    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        """Run the analysis on *df* and return a serializable result dict.

        *fields* is the list of dataset field definitions (name, technical_type,
        semantic_type, etc.) so the service can pick relevant columns.
        """
        ...
