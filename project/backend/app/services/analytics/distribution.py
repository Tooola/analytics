"""Distribution analysis — skewness, kurtosis, percentiles, and Shapiro-Wilk test."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.analytics.base import BaseAnalyticsService


class DistributionService(BaseAnalyticsService):
    analysis_type = "distribution"

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        num_cols = [
            f["name"]
            for f in fields
            if f["technical_type"] in ("integer", "float") and f["name"] in df.columns
        ]
        results: list[dict[str, Any]] = []

        for col in num_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 3:
                continue

            arr = series.values.astype(float)
            skew_val = float(stats.skew(arr))
            kurt_val = float(stats.kurtosis(arr))

            quantiles = series.quantile([0.10, 0.25, 0.50, 0.75, 0.90]).to_dict()

            if 3 <= len(series) <= 5000:
                shapiro_res = stats.shapiro(arr)
                shapiro_p = float(shapiro_res.pvalue)
                is_normal = bool(shapiro_p >= 0.05)
            else:
                shapiro_p = None
                is_normal = None

            results.append({
                "column": col,
                "skewness": round(skew_val, 4) if not np.isnan(skew_val) else 0.0,
                "kurtosis": round(kurt_val, 4) if not np.isnan(kurt_val) else 0.0,
                "percentiles": {
                    "p10": round(float(quantiles.get(0.10, 0.0)), 4),
                    "p25": round(float(quantiles.get(0.25, 0.0)), 4),
                    "p50": round(float(quantiles.get(0.50, 0.0)), 4),
                    "p75": round(float(quantiles.get(0.75, 0.0)), 4),
                    "p90": round(float(quantiles.get(0.90, 0.0)), 4),
                },
                "shapiro_p_value": round(shapiro_p, 4) if shapiro_p is not None and not np.isnan(shapiro_p) else None,
                "is_normal": is_normal,
                "count": len(series),
            })

        return {"distribution": results}
