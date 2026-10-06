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

            # Prediction interval (PLAN.md S1):
            # - sigma = residual std error sqrt(SSE/(n-2)). linregress.stderr
            #   is the error of the SLOPE, not of the fit — using it produced
            #   bands unrelated to the actual scatter.
            # - t-critical (df = n-2) instead of a fixed 1.96: for small n the
            #   normal approximation badly understates the interval.
            fitted = slope * x + intercept
            sse = float(np.sum((y - fitted) ** 2))
            dof = n - 2  # >= 1: series shorter than 3 points are skipped above
            sigma = float(np.sqrt(sse / dof))
            t_crit = float(stats.t.ppf(0.975, dof))
            sxx = float(np.sum((x - x.mean()) ** 2))

            predictions: list[dict[str, Any]] = []
            for step in range(1, horizon + 1):
                future_x = n - 1 + step
                pred_val = slope * future_x + intercept
                # ± t·sigma·sqrt(1 + 1/n + (x0-x̄)²/Sxx): prediction interval
                # for a NEW observation (leading 1) — strictly widening with
                # the horizon.
                if sxx > 0:
                    se = sigma * np.sqrt(1.0 / n + ((future_x - x.mean()) ** 2) / sxx + 1.0)
                else:  # pragma: no cover — x = arange(n) always has spread
                    se = sigma
                margin = t_crit * se
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
