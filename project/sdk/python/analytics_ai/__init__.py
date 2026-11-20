"""Open Analytics AI — Official Python SDK.

One-line client to send data, run statistical analytics, detect causality,
compare periods, and retrieve decision-oriented AI executive reports.
"""

from .client import AnalyticsClient, AnalyticsError

__version__ = "0.1.0"
__all__ = ["AnalyticsClient", "AnalyticsError"]
