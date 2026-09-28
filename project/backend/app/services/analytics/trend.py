"""Trend analysis using OLS Linear Regression & R-squared statistics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.analytics.base import BaseAnalyticsService


class TrendService(BaseAnalyticsService):
    analysis_type = "trend"
    MIN_R2_THRESHOLD = 0.25  # Rejeter les tendances non significatives (bruit)

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        date_field = self._find_date_field(fields)
        numeric_fields = [
            f for f in fields
            if f["technical_type"] in ("integer", "float")
        ]
        results: list[dict[str, Any]] = []

        if date_field and date_field in df.columns:
            df = df.copy()
            df[date_field] = pd.to_datetime(df[date_field], errors="coerce")
            df = df.dropna(subset=[date_field]).sort_values(date_field)

        for f in numeric_fields:
            col = f["name"]
            if col not in df.columns:
                continue
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 2:
                continue

            x = np.arange(len(series))
            y = series.values.astype(float)

            # Linear regression: y = slope * x + intercept
            res = stats.linregress(x, y)
            slope = float(res.slope) if not np.isnan(res.slope) else 0.0
            r_squared = float(res.rvalue ** 2) if not np.isnan(res.rvalue) else 0.0
            p_value = float(res.pvalue) if not np.isnan(res.pvalue) else 1.0

            first_val = float(y[0])
            last_val = float(y[-1])

            if first_val != 0:
                change_pct = round(((last_val - first_val) / abs(first_val)) * 100, 2)
            else:
                change_pct = round((slope * len(series) / abs(y.mean())) * 100, 2) if y.mean() != 0 else 0.0

            is_significant = bool(p_value < 0.05 and r_squared >= self.MIN_R2_THRESHOLD)

            # Determine direction based on statistical significance or clear slope
            if is_significant:
                direction = "up" if slope > 0 else "down"
            elif len(series) < 5 and change_pct is not None and abs(change_pct) > 1:
                direction = "up" if change_pct > 1 else ("down" if change_pct < -1 else "stable")
            else:
                direction = "stable"

            results.append({
                "column": col,
                "change_pct": change_pct,
                "direction": direction,
                "slope": round(slope, 4),
                "r_squared": round(r_squared, 4),
                "p_value": round(p_value, 4),
                "first_value": round(first_val, 4),
                "last_value": round(last_val, 4),
                "periods": len(series),
                "is_significant": is_significant,
            })

        return {"trend": results}

    @staticmethod
    def _find_date_field(fields: list[dict[str, Any]]) -> str | None:
        for f in fields:
            if f["technical_type"] in ("date", "datetime"):
                return f["name"]
        return None

