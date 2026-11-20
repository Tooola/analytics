"""Causality and variance drivers service.

Explains *why* metrics vary by identifying dominant relationships between
variables and key segment contributors in plain French without theoretical
mathematical jargon (no 'r=0.92', no 'p-value', no correlation coefficients).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.core.logging import get_logger
from app.services.analytics.base import BaseAnalyticsService
from app.utils.humanize import humanize_column

logger = get_logger(__name__)


class CausalityService(BaseAnalyticsService):
    analysis_type = "causality"

    def run(self, df: pd.DataFrame, fields: list[dict[str, Any]]) -> dict[str, Any]:
        """Identify key drivers of variance in plain business language."""
        if df.empty or len(df) < 4:
            return {"causality": []}

        # 1. Identify numeric columns
        numeric_cols = [
            c for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() > 1
        ]

        # 2. Identify potential segment / categorical columns
        cat_cols = [
            c for c in df.columns
            if c not in numeric_cols and 1 < df[c].nunique() <= 25
        ]

        drivers: list[dict[str, Any]] = []
        seen_pairs: set[frozenset[str]] = set()

        # A. Driver analysis through strong synchronicity / opposition
        if len(numeric_cols) >= 2:
            try:
                corr_matrix = df[numeric_cols].corr(method="pearson")
                pairs: list[tuple[str, str, float]] = []

                for i, col1 in enumerate(numeric_cols):
                    for j, col2 in enumerate(numeric_cols):
                        if i >= j:
                            continue
                        val = corr_matrix.loc[col1, col2]
                        if not np.isnan(val) and abs(val) >= 0.65:
                            pairs.append((col1, col2, float(val)))

                # Sort by absolute strength
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                for col1, col2, r in pairs[:4]:
                    pair_key = frozenset([col1, col2])
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    label1 = humanize_column(col1)
                    label2 = humanize_column(col2)

                    if r > 0:
                        rel_type = "synchronous"
                        explanation = (
                            f"Les variations de {label1} sont directement synchronisées avec "
                            f"{label2} : lorsque l'un progresse, l'autre suit naturellement la même dynamique."
                        )
                    else:
                        rel_type = "opposite"
                        explanation = (
                            f"Une dynamique inverse s'exerce entre {label1} et {label2} : "
                            f"la progression de l'un s'accompagne systématiquement d'un tassement de l'autre."
                        )

                    drivers.append({
                        "target": label1,
                        "driver": label2,
                        "relationship_type": rel_type,
                        "explanation": explanation,
                    })
            except Exception as exc:
                logger.warning("Causality numeric correlation failed: %s", exc)

        # B. Segment contribution analysis (drivers by category/segment)
        if cat_cols and numeric_cols:
            try:
                for cat in cat_cols[:2]:
                    cat_label = humanize_column(cat)
                    for num in numeric_cols[:3]:
                        num_label = humanize_column(num)
                        # Group by category and compute share
                        grouped = df.groupby(cat)[num].sum().abs()
                        total = grouped.sum()
                        if total > 0:
                            top_cat = grouped.idxmax()
                            top_share = grouped.max() / total
                            if top_share >= 0.35 and len(grouped) >= 2:
                                share_pct = round(top_share * 100)
                                drivers.append({
                                    "target": num_label,
                                    "driver": f"{top_cat} ({cat_label})",
                                    "relationship_type": "segment_contribution",
                                    "explanation": (
                                        f"Le segment « {top_cat} » ({cat_label}) constitue le moteur principal "
                                        f"de {num_label}, concentrant environ {share_pct}% du volume total."
                                    ),
                                })
            except Exception as exc:
                logger.warning("Causality segment contribution failed: %s", exc)

        return {"causality": drivers[:6]}
