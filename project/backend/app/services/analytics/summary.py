"""Descriptive statistics — count, mean, median, min, max, std."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.analytics.base import BaseAnalyticsService


class SummaryService(BaseAnalyticsService):
    analysis_type = "summary"

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
            if series.empty:
                continue
            results.append({
                "column": col,
                "count": int(series.count()),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "std": round(float(series.std()), 4) if series.count() > 1 else 0.0,
            })

        return {"summary": results}
