"""Forecast analysis service — trend extrapolation with confidence intervals."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.analytics.base import BaseAnalyticsService


class ForecastService(BaseAnalyticsService):
    analysis_type = "forecast"

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        num_cols = [
            f["name"]
            for f in fields
            if f["technical_type"] in ("integer", "float") and f["name"] in df.columns
        ]
        results: list[dict[str, Any]] = []

        horizon = 3  # Default forecast horizon (periods into the future)

        for col in num_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 3:
                continue

            n = len(series)
            x = np.arange(n)
            y = series.values.astype(float)

            res = stats.linregress(x, y)
            slope = float(res.slope) if not np.isnan(res.slope) else 0.0
            intercept = float(res.intercept) if not np.isnan(res.intercept) else float(y.mean())
            std_err = float(res.stderr) if res.stderr and not np.isnan(res.stderr) else float(np.std(y))

            predictions: list[dict[str, Any]] = []
            for step in range(1, horizon + 1):
                future_x = n - 1 + step
                pred_val = slope * future_x + intercept
                margin = 1.96 * std_err * np.sqrt(1 + 1 / n + ((future_x - x.mean()) ** 2) / np.sum((x - x.mean()) ** 2)) if np.sum((x - x.mean()) ** 2) > 0 else 1.96 * std_err
                predictions.append({
                    "period": step,
                    "predicted_value": round(float(pred_val), 4),
                    "lower_bound": round(float(pred_val - margin), 4),
                    "upper_bound": round(float(pred_val + margin), 4),
                })

            direction = "up" if slope > 0 else ("down" if slope < 0 else "stable")

            results.append({
                "column": col,
                "horizon": horizon,
                "predictions": predictions,
                "trend_direction": direction,
                "slope": round(slope, 4),
            })

        return {"forecast": results}
