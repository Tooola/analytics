"""Anomaly detection — Z-score and Isolation Forest methods."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.services.analytics.base import BaseAnalyticsService

# Scikit-learn is an optional dependency at import time — guard it.
try:
    from sklearn.ensemble import IsolationForest
    _HAS_SKLEARN = True
except ImportError:  # pragma: no cover
    _HAS_SKLEARN = False


class AnomalyService(BaseAnalyticsService):
    analysis_type = "anomaly"

    #: Z-score threshold above which a point is flagged.
    Z_THRESHOLD = 3.0

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        numeric_fields = [
            f for f in fields
            if f["technical_type"] in ("integer", "float")
        ]
        results: list[dict[str, Any]] = []

        for f in numeric_fields:
            col = f["name"]
            if col not in df.columns:
                continue
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 4:
                continue

            anomalies = self._detect_zscore(series, col)
            results.append(anomalies)

        return {"anomaly": results}

    def _detect_zscore(self, series: pd.Series, col: str) -> dict[str, Any]:
        """Flag points whose Z-score exceeds the threshold."""
        mean = float(series.mean())
        std = float(series.std())

        if std == 0:
            return {
                "column": col,
                "anomalies": [],
                "count": 0,
                "method": "zscore",
            }

        z_scores = (series - mean) / std
        anomaly_mask = z_scores.abs() > self.Z_THRESHOLD
        anomalies: list[dict[str, Any]] = []

        for idx in series[anomaly_mask].index:
            val = float(series.loc[idx])
            z = float(z_scores.loc[idx])
            anomalies.append({
                "row": int(idx),
                "value": round(val, 4),
                "z_score": round(z, 4),
            })

        return {
            "column": col,
            "anomalies": anomalies,
            "count": len(anomalies),
            "method": "zscore",
        }
