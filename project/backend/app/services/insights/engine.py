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

        if "correlation" in analysis_results:
            insights.extend(self._from_correlation(analysis_results["correlation"]))

        if "distribution" in analysis_results:
            insights.extend(self._from_distribution(analysis_results["distribution"]))

        if "forecast" in analysis_results:
            insights.extend(self._from_forecast(analysis_results["forecast"]))

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
            is_sig = t.get("is_significant", True)

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

            confidence = 0.95 if is_sig else 0.60
            insights.append({
                "type": itype,
                "severity": severity,
                "title": title,
                "description": desc,
                "metric": col,
                "value": change,
                "unit": "%",
                "confidence": confidence,
            })
        return insights

    def _from_anomaly(self, anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for a in anomalies:
            col = a.get("column", "metric")
            raw_count = a.get("count", 0)
            if raw_count == 0:
                continue

            anomaly_items = a.get("anomalies", [])
            # Filter low confidence anomalies if ensemble consensus scores are present
            if anomaly_items and any("confidence_score" in item for item in anomaly_items):
                valid_items = [item for item in anomaly_items if item.get("confidence_score", 1.0) >= 0.66]
                count = len(valid_items)
            else:
                count = raw_count

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

    def _from_correlation(self, correlations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for c in correlations:
            col1 = c.get("column1")
            col2 = c.get("column2")
            coeff = c.get("coefficient", 0.0)
            strength = c.get("strength", "moderate")
            rel = c.get("relationship", "positive")

            if rel == "positive":
                itype = "opportunity"
                title = f"Strong positive correlation between {col1} and {col2}"
                desc = f"Variables {col1} and {col2} are strongly co-varying (r={coeff})."
            else:
                itype = "risk"
                title = f"Inverse relationship between {col1} and {col2}"
                desc = f"Variable {col1} moves inversely to {col2} (r={coeff})."

            insights.append({
                "type": itype,
                "severity": "medium" if strength == "moderate" else "high",
                "title": title,
                "description": desc,
                "metric": f"{col1}_vs_{col2}",
                "value": float(coeff),
                "confidence": 0.90,
            })
        return insights

    def _from_distribution(self, distributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for d in distributions:
            col = d.get("column")
            skew = d.get("skewness", 0.0)
            if abs(skew) > 1.0:
                direction = "right-skewed (positive tail)" if skew > 0 else "left-skewed (negative tail)"
                insights.append({
                    "type": "recommendation",
                    "severity": "low",
                    "title": f"Asymmetric distribution detected in {col}",
                    "description": f"The distribution of {col} is significantly {direction} with skewness of {skew}.",
                    "metric": col,
                    "value": float(skew),
                    "confidence": 0.85,
                })
        return insights

    def _from_forecast(self, forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for f in forecasts:
            col = f.get("column")
            direction = f.get("trend_direction", "stable")
            horizon = f.get("horizon", 3)
            preds = f.get("predictions", [])
            if not preds:
                continue

            last_pred = preds[-1].get("predicted_value")
            insights.append({
                "type": "forecast",
                "severity": "medium",
                "title": f"Forecast for {col}: trend expected {direction}",
                "description": f"Predicted value for {col} in {horizon} periods is estimated at {last_pred}.",
                "metric": col,
                "value": float(last_pred) if last_pred is not None else None,
                "confidence": 0.80,
            })
        return insights
