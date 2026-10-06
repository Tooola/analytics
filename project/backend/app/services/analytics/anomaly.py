"""Multi-method robust anomaly detection (IQR + Modified Z-Score/MAD + Isolation Forest)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.services.analytics.base import BaseAnalyticsService

try:
    from sklearn.ensemble import IsolationForest
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False


class AnomalyService(BaseAnalyticsService):
    analysis_type = "anomaly"

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

            anomalies = self._detect_consensus(series, col)
            results.append(anomalies)

        return {"anomaly": results}

    def _detect_consensus(self, series: pd.Series, col: str) -> dict[str, Any]:
        n = len(series)
        iqr_flags = set(self._detect_iqr(series))
        mad_flags = set(self._detect_mad(series))
        iforest_ran = _HAS_SKLEARN and n >= 15
        iforest_flags = set(self._detect_iforest(series)) if iforest_ran else set()

        # Confidence = votes / methods EXECUTED (PLAN.md S4). Dividing by 3
        # while Isolation Forest was skipped capped every small-n score at
        # 0.67 (barely above the insights filter) instead of 1.0 for a
        # unanimous two-method consensus.
        executed = 3 if iforest_ran else 2

        mean = float(series.mean())
        std = float(series.std()) if len(series) > 1 else 0.0

        confirmed_anomalies: list[dict[str, Any]] = []
        for idx in series.index:
            votes = sum([idx in iqr_flags, idx in mad_flags, idx in iforest_flags])
            min_votes = 2 if (n >= 15 and _HAS_SKLEARN) else 1
            if votes >= min_votes:
                val = float(series.loc[idx])
                z_score = round(float((val - mean) / std), 4) if std != 0 else 0.0
                detected_methods = [
                    m for m, active in [("iqr", idx in iqr_flags), ("mad", idx in mad_flags), ("iforest", idx in iforest_flags)]
                    if active
                ]
                confirmed_anomalies.append({
                    "row": int(idx),
                    "value": round(val, 4),
                    "z_score": z_score,
                    "confidence_score": round(votes / executed, 2),
                    "detected_by": detected_methods,
                })

        return {
            "column": col,
            "anomalies": confirmed_anomalies,
            "count": len(confirmed_anomalies),
            "method": "ensemble (iqr + mad + isolation_forest)",
        }

    @staticmethod
    def _detect_iqr(series: pd.Series) -> list[int]:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return []
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return list(series[(series < lower_bound) | (series > upper_bound)].index)

    @staticmethod
    def _detect_mad(series: pd.Series) -> list[int]:
        median = series.median()
        mad = (series - median).abs().median()
        if mad == 0:
            return []
        # Modified Z-score = 0.6745 * |x - median| / MAD
        mod_z = 0.6745 * (series - median).abs() / mad
        return list(series[mod_z > 3.5].index)

    @staticmethod
    def _detect_iforest(series: pd.Series) -> list[int]:
        X = series.values.reshape(-1, 1)
        clf = IsolationForest(contamination=0.05, random_state=42)
        preds = clf.fit_predict(X)
        return list(series[preds == -1].index)

