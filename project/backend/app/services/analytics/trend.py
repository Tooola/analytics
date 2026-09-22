"""Trend analysis — period-over-period change and growth rate."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.analytics.base import BaseAnalyticsService


class TrendService(BaseAnalyticsService):
    analysis_type = "trend"

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

            first_val = float(series.iloc[0])
            last_val = float(series.iloc[-1])

            if first_val != 0:
                change_pct = round(((last_val - first_val) / abs(first_val)) * 100, 2)
            else:
                change_pct = None

            if change_pct is None:
                direction = "stable"
            elif change_pct > 1:
                direction = "up"
            elif change_pct < -1:
                direction = "down"
            else:
                direction = "stable"

            results.append({
                "column": col,
                "change_pct": change_pct,
                "direction": direction,
                "first_value": round(first_val, 4),
                "last_value": round(last_val, 4),
                "periods": len(series),
            })

        return {"trend": results}

    @staticmethod
    def _find_date_field(fields: list[dict[str, Any]]) -> str | None:
        for f in fields:
            if f["technical_type"] in ("date", "datetime"):
                return f["name"]
        return None
