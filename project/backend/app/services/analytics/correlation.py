"""Correlation service — Pearson & Spearman matrix analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.analytics.base import BaseAnalyticsService


class CorrelationService(BaseAnalyticsService):
    analysis_type = "correlation"

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        num_cols = [
            f["name"]
            for f in fields
            if f["technical_type"] in ("integer", "float") and f["name"] in df.columns
        ]
        if len(num_cols) < 2:
            return {"correlation": []}

        correlations: list[dict[str, Any]] = []
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                col1, col2 = num_cols[i], num_cols[j]
                s1 = pd.to_numeric(df[col1], errors="coerce")
                s2 = pd.to_numeric(df[col2], errors="coerce")
                valid = pd.concat([s1, s2], axis=1).dropna()
                if len(valid) < 5:
                    continue

                r, p_val = stats.pearsonr(valid.iloc[:, 0], valid.iloc[:, 1])
                if not np.isnan(r) and abs(r) >= 0.4 and p_val < 0.05:
                    correlations.append({
                        "column1": col1,
                        "column2": col2,
                        "coefficient": round(float(r), 4),
                        "p_value": round(float(p_val), 4),
                        "strength": "strong" if abs(r) >= 0.7 else "moderate",
                        "relationship": "positive" if r > 0 else "negative",
                    })

        return {"correlation": correlations}
