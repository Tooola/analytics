"""Period comparator service — compares Period A vs Period B.

Computes changes between two time windows (e.g. Month M vs M-1, Year N vs N-1),
categorizing movements into:
- Ce qui s'est amélioré (improved)
- Ce qui s'est dégradé (degraded)
- Nouveaux points de vigilance (vigilance_points)

Follows the zero-technical-jargon constraint: natural, business-ready French.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.core.logging import get_logger
from app.schemas.comparison import CompareResponse, MetricEvolution, VigilancePoint
from app.services.analytics.anomaly import AnomalyService
from app.utils.humanize import humanize_column

logger = get_logger(__name__)

# Keywords identifying indicators where an INCREASE is a degradation / risk
_NEGATIVE_METRIC_KEYWORDS = (
    "cout", "coût", "depense", "dépense", "rupture", "chomage", "chômage",
    "delai", "délai", "perte", "reclamation", "réclamation", "retard",
    "incident", "panne", "dechet", "déchet", "charge", "defaut", "défaut",
    "retour", "rejet", "gaspillage", "litige"
)


def _is_inverted_polarity(col_name: str) -> bool:
    """Returns True if higher values represent worse business performance."""
    low = col_name.lower()
    return any(kw in low for kw in _NEGATIVE_METRIC_KEYWORDS)


def _extract_numeric_series(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    """Extract numeric columns and their valid float values."""
    series: dict[str, list[float]] = {}
    for r in rows:
        for k, v in r.items():
            if v is None or v == "":
                continue
            try:
                val = float(v)
                series.setdefault(k, []).append(val)
            except (ValueError, TypeError):
                continue
    return series


class PeriodComparator:
    """Compares two datasets representing distinct time periods."""

    def __init__(self) -> None:
        self.anomaly_service = AnomalyService()

    def compare(
        self,
        period_a_label: str,
        period_a_data: list[dict[str, Any]],
        period_b_label: str,
        period_b_data: list[dict[str, Any]],
        label: str = "comparatif-temporel",
    ) -> CompareResponse:
        logger.info(
            "Comparing '%s' (%d rows) vs '%s' (%d rows)",
            period_a_label, len(period_a_data),
            period_b_label, len(period_b_data),
        )

        series_a = _extract_numeric_series(period_a_data)
        series_b = _extract_numeric_series(period_b_data)

        common_cols = sorted(set(series_a.keys()) & set(series_b.keys()))

        improved: list[MetricEvolution] = []
        degraded: list[MetricEvolution] = []
        stable: list[MetricEvolution] = []

        for col in common_cols:
            vals_a = series_a[col]
            vals_b = series_b[col]
            if not vals_a or not vals_b:
                continue

            mean_a = sum(vals_a) / len(vals_a)
            mean_b = sum(vals_b) / len(vals_b)

            if abs(mean_a) > 1e-9:
                change_pct = round(((mean_b - mean_a) / abs(mean_a)) * 100, 1)
            else:
                change_pct = round((mean_b - mean_a) * 100, 1) if mean_b != 0 else 0.0

            inverted = _is_inverted_polarity(col)
            label_col = humanize_column(col)

            # Determine direction & status
            if abs(change_pct) < 3.0:
                direction = "stable"
                status = "stable"
                explanation = f"Stabilité confirmée sur {label_col} (variation minime de {change_pct:+.1f}%)."
                stable.append(MetricEvolution(
                    metric=col,
                    label=label_col,
                    direction=direction,
                    change_pct=change_pct,
                    status=status,
                    explanation=explanation,
                ))
            elif change_pct > 0:
                direction = "up"
                if inverted:
                    status = "degraded"
                    explanation = f"Hausse défavorable de {change_pct:+.1f}% sur {label_col} par rapport à {period_a_label}."
                    degraded.append(MetricEvolution(
                        metric=col,
                        label=label_col,
                        direction=direction,
                        change_pct=change_pct,
                        status=status,
                        explanation=explanation,
                    ))
                else:
                    status = "improved"
                    explanation = f"Progression positive de {change_pct:+.1f}% sur {label_col} par rapport à {period_a_label}."
                    improved.append(MetricEvolution(
                        metric=col,
                        label=label_col,
                        direction=direction,
                        change_pct=change_pct,
                        status=status,
                        explanation=explanation,
                    ))
            else:  # change_pct < 0
                direction = "down"
                if inverted:
                    status = "improved"
                    explanation = f"Diminution favorable de {abs(change_pct):.1f}% sur {label_col} par rapport à {period_a_label}."
                    improved.append(MetricEvolution(
                        metric=col,
                        label=label_col,
                        direction=direction,
                        change_pct=change_pct,
                        status=status,
                        explanation=explanation,
                    ))
                else:
                    status = "degraded"
                    explanation = f"Recul de {abs(change_pct):.1f}% sur {label_col} par rapport à {period_a_label}."
                    degraded.append(MetricEvolution(
                        metric=col,
                        label=label_col,
                        direction=direction,
                        change_pct=change_pct,
                        status=status,
                        explanation=explanation,
                    ))

        # Detect new anomalies in period B
        vigilance_points: list[VigilancePoint] = []
        try:
            fields = [{"name": c, "technical_type": "float"} for c in common_cols]
            df_a = pd.DataFrame(period_a_data)
            df_b = pd.DataFrame(period_b_data)
            anom_res_a = self.anomaly_service.run(df_a, fields).get("anomaly", [])
            anom_res_b = self.anomaly_service.run(df_b, fields).get("anomaly", [])

            anom_map_a = {item["column"]: item.get("count", 0) for item in anom_res_a if isinstance(item, dict)}
            for item_b in anom_res_b:
                if not isinstance(item_b, dict):
                    continue
                col_b = item_b.get("column", "")
                count_b = item_b.get("count", 0)
                count_a = anom_map_a.get(col_b, 0)
                if count_b > 0 and count_b > count_a:
                    label_col = humanize_column(col_b)
                    vigilance_points.append(VigilancePoint(
                        metric=col_b,
                        label=label_col,
                        severity="high" if count_b > 2 else "medium",
                        description=(
                            f"Variation inhabituelle constatée sur {label_col} en {period_b_label}, "
                            f"non observée sur la période de référence. À auditer pour vérifier la stabilité opérationnelle."
                        )
                    ))
        except Exception as exc:
            logger.warning("Anomaly check during comparison failed: %s", exc)

        # Build natural executive summary
        summary_parts = [
            f"Bilan d'évolution entre « {period_a_label} » et « {period_b_label} »."
        ]
        if improved:
            col_names = ", ".join(m.label for m in improved[:3])
            summary_parts.append(f"{len(improved)} indicateur(s) en nette amélioration ({col_names}).")
        if degraded:
            col_names = ", ".join(m.label for m in degraded[:3])
            summary_parts.append(f"{len(degraded)} indicateur(s) en repli ({col_names}).")
        if vigilance_points:
            summary_parts.append(f"{len(vigilance_points)} nouveau(x) point(s) de vigilance opérationnelle.")
        elif not degraded:
            summary_parts.append("Dynamique d'ensemble favorable sans détérioration constatée.")

        return CompareResponse(
            success=True,
            label=label,
            period_a_label=period_a_label,
            period_b_label=period_b_label,
            period_a_rows=len(period_a_data),
            period_b_rows=len(period_b_data),
            improved=improved,
            degraded=degraded,
            stable=stable,
            vigilance_points=vigilance_points,
            executive_summary=" ".join(summary_parts),
        )
