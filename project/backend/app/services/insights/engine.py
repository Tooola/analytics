"""Insight engine — transforms analytical results into structured insights.

Each generator examines one type of analysis result and produces human-readable
insights with severity, confidence, and actionable descriptions.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class InsightEngine:
    """Converts analysis results into a list of insight dictionaries."""

    def generate(
        self,
        analysis_results: dict[str, Any],
        dataset_name: str = "",
    ) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []

        if "summary" in analysis_results:
            insights.extend(self._from_summary(analysis_results["summary"]))

        if "trend" in analysis_results:
            insights.extend(self._from_trend(analysis_results["trend"]))

        if "anomaly" in analysis_results:
            insights.extend(self._from_anomaly(analysis_results["anomaly"]))

        logger.info("Generated %d insights for dataset '%s'", len(insights), dataset_name)
        return insights

    def _from_summary(self, summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for s in summaries:
            col = s.get("column", "data")
            insights.append({
                "type": "trend",
                "severity": "low",
                "title": f"{col} summary statistics",
                "description": (
                    f"{col}: count={s['count']}, mean={s.get('mean')}, "
                    f"median={s.get('median')}, min={s.get('min')}, "
                    f"max={s.get('max')}, std={s.get('std')}"
                ),
                "metric": col,
                "confidence": 1.0,
            })
        return insights

    def _from_trend(self, trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for t in trends:
            col = t.get("column", "metric")
            change = t.get("change_pct")
            direction = t.get("direction", "stable")

            if change is None:
                continue

            abs_change = abs(change)
            if abs_change > 20:
                severity = "high"
            elif abs_change > 5:
                severity = "medium"
            else:
                severity = "low"

            if direction == "up":
                title = f"{col} increased by {abs_change}%"
                desc = f"{col} increased by {abs_change}% compared with the previous period."
                itype = "opportunity"
            elif direction == "down":
                title = f"{col} decreased by {abs_change}%"
                desc = f"{col} decreased by {abs_change}% compared with the previous period."
                itype = "risk"
            else:
                title = f"{col} is stable"
                desc = f"{col} remained stable with a change of {abs_change}%."
                itype = "trend"
                severity = "low"

            insights.append({
                "type": itype,
                "severity": severity,
                "title": title,
                "description": desc,
                "metric": col,
                "value": change,
                "unit": "%",
                "confidence": 0.9,
            })
        return insights

    def _from_anomaly(self, anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for a in anomalies:
            col = a.get("column", "metric")
            count = a.get("count", 0)
            if count == 0:
                continue

            severity = "high" if count > 3 else "medium"
            insights.append({
                "type": "anomaly",
                "severity": severity,
                "title": f"{count} anomaly/anomalies detected in {col}",
                "description": (
                    f"{count} data point(s) in '{col}' deviate significantly "
                    f"from the normal range (method: {a.get('method', 'zscore')})."
                ),
                "metric": col,
                "value": float(count),
                "unit": "count",
                "confidence": 0.85,
            })
        return insights
