"""Insight engine — transforms analytical results into business-oriented insights.

Each generator examines one type of analysis result and produces human-readable,
business-analyst-style insights in French — readable by executives, not just
data scientists. Severity, confidence, and actionable descriptions included.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.utils.humanize import humanize_column

logger = get_logger(__name__)


class InsightEngine:
    """Converts analysis results into a list of business-friendly insight dicts."""

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

        if "causality" in analysis_results:
            insights.extend(self._from_causality(analysis_results["causality"]))

        logger.info("Generated %d insights for dataset '%s'", len(insights), dataset_name)
        return insights

    def _from_summary(self, summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for s in summaries:
            col = s.get("column", "indicateur")
            label = humanize_column(col)
            mean = s.get("mean")
            median = s.get("median")
            mn = s.get("min")
            mx = s.get("max")
            count = s.get("count", 0)

            if mean is None:
                continue

            # Detect skew between mean and median (business interpretation)
            skew_note = ""
            if median is not None and mean != 0:
                ratio = abs(mean - median) / abs(mean)
                if ratio > 0.2:
                    if mean > median:
                        skew_note = (
                            f" La moyenne ({mean:,.2f}) est nettement supérieure à la médiane ({median:,.2f}), "
                            "ce qui indique que quelques valeurs élevées tirent l'indicateur vers le haut."
                        )
                    else:
                        skew_note = (
                            f" La moyenne ({mean:,.2f}) est inférieure à la médiane ({median:,.2f}), "
                            "ce qui suggère des valeurs basses atypiques dans le jeu de données."
                        )

            desc = (
                f"Sur {count:,} enregistrements analysés, la valeur moyenne de **{label}** est de **{mean:,.2f}** "
                f"(médiane : {median:,.2f}, min : {mn}, max : {mx}).{skew_note}"
            )

            insights.append({
                "type": "trend",
                "severity": "low",
                "title": f"Vue d'ensemble — {label}",
                "description": desc,
                "metric": label,
                "confidence": 1.0,
            })
        return insights

    def _from_trend(self, trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for t in trends:
            col = t.get("column", "indicateur")
            label = humanize_column(col)
            change = t.get("change_pct")
            direction = t.get("direction", "stable")
            is_sig = t.get("is_significant", True)
            periods = t.get("periods", 0)

            if change is None:
                continue

            abs_change = abs(change)
            if abs_change > 20:
                severity = "high"
            elif abs_change > 5:
                severity = "medium"
            else:
                severity = "low"

            period_str = f" sur {periods} périodes" if periods else ""

            if direction == "up":
                title = f"Progression de +{abs_change:.1f}% sur {label}"
                desc = f"{label} progresse de +{abs_change:.1f}%{period_str}. Trajectoire positive confirmée sur la période."
                itype = "opportunity"
            elif direction == "down":
                title = f"Recul de -{abs_change:.1f}% sur {label}"
                desc = f"{label} diminue de -{abs_change:.1f}%{period_str}. Vigilance opérationnelle conseillée pour anticiper un impact."
                itype = "risk"
            else:
                title = f"Stabilité sur {label}"
                desc = f"{label} demeure constant{period_str} (variation de {abs_change:.1f}%). Aucune rupture d'activité."
                itype = "trend"
                severity = "low"

            confidence = 0.95 if is_sig else 0.60
            insights.append({
                "type": itype,
                "severity": severity,
                "title": title,
                "description": desc,
                "metric": label,
                "value": change,
                "unit": "%",
                "confidence": confidence,
            })
        return insights

    def _from_anomaly(self, anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for a in anomalies:
            col = a.get("column", "indicateur")
            label = humanize_column(col)
            raw_count = a.get("count", 0)
            if raw_count == 0:
                continue

            anomaly_items = a.get("anomalies", [])
            if anomaly_items and any("confidence_score" in item for item in anomaly_items):
                valid_items = [item for item in anomaly_items if item.get("confidence_score", 1.0) >= 0.66]
                count = len(valid_items)
            else:
                valid_items = anomaly_items
                count = raw_count

            if count == 0:
                continue

            severity = "high" if count > 3 else "medium"

            reason = a.get("reason")
            rec = a.get("recommendation")
            if reason and rec:
                desc = f"Comportement atypique constaté sur {label} : {reason} Action conseillée : {rec}"
            else:
                desc = f"Comportement atypique constaté sur {label}. À auditer pour vérifier toute anomalie ponctuelle ou erreur de saisie."

            title = f"Point d'attention sur {label}"

            insights.append({
                "type": "anomaly",
                "severity": severity,
                "title": title,
                "description": desc,
                "metric": label,
                "value": float(count),
                "unit": "count",
                "confidence": 0.85,
            })
        return insights

    def _from_correlation(self, correlations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for c in correlations:
            col1 = c.get("column1", "")
            col2 = c.get("column2", "")
            label1 = humanize_column(col1)
            label2 = humanize_column(col2)
            coeff = c.get("coefficient", 0.0)

            abs_r = abs(coeff)
            if abs_r < 0.4:
                continue

            # Strength levels — used for both wording and severity.
            if abs_r >= 0.8:
                strength = "strong"
                strength_label = "forte"
            elif abs_r >= 0.6:
                strength = "moderate"
                strength_label = "modérée"
            else:
                strength = "weak"
                strength_label = "faible"

            if coeff > 0:
                itype = "opportunity"
                title = f"Lien positif entre {label1} et {label2}"
                desc = (
                    f"Une relation positive est observée entre "
                    f"**{label1}** et **{label2}** : lorsque l'un progresse, l'autre augmente également."
                )
            else:
                itype = "risk"
                title = f"Relation inverse entre {label1} et {label2}"
                desc = (
                    f"Une relation inverse est observée entre "
                    f"**{label1}** et **{label2}** : "
                    f"lorsque {label1} augmente, {label2} tend à diminuer."
                )

            insights.append({
                "type": itype,
                "severity": {"strong": "high", "moderate": "medium"}.get(strength, "low"),
                "title": title,
                "description": desc,
                "metric": f"{label1} vs {label2}",
                "value": float(coeff),
                "confidence": 0.90,
            })
        return insights

    def _from_causality(self, causality_drivers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for d in causality_drivers:
            target = d.get("target", "")
            driver = d.get("driver", "")
            rel = d.get("relationship_type", "synchronous")
            explanation = d.get("explanation", "")

            if rel == "synchronous":
                title = f"Effet moteur : {driver} tire {target}"
                itype = "opportunity"
            elif rel == "opposite":
                title = f"Impact divergent entre {target} et {driver}"
                itype = "risk"
            else:
                title = f"Contributeur clé : {driver}"
                itype = "trend"

            insights.append({
                "type": itype,
                "severity": "medium",
                "title": title,
                "description": explanation,
                "metric": target,
                "confidence": 0.95,
            })
        return insights

    def _from_distribution(self, distributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for d in distributions:
            col = d.get("column", "indicateur")
            label = humanize_column(col)
            skew = d.get("skewness", 0.0)
            if abs(skew) > 1.0:
                if skew > 0:
                    direction_text = "concentrée sur les petites valeurs avec une longue queue vers les valeurs élevées"
                    impact = (
                        f"Quelques enregistrements à valeurs très élevées tirent la moyenne vers le haut. "
                        f"Privilégier la médiane comme indicateur de référence pour {label}."
                    )
                else:
                    direction_text = "concentrée sur les valeurs élevées avec une queue vers les faibles valeurs"
                    impact = (
                        f"La distribution de {label} est dominée par des valeurs hautes. "
                        "Des valeurs basses atypiques peuvent indiquer des anomalies ou des cas spéciaux."
                    )

                insights.append({
                    "type": "recommendation",
                    "severity": "low",
                    "title": f"Répartition asymétrique sur {label}",
                    "description": (
                        f"Les valeurs de {label} sont {direction_text}. "
                        f"{impact}"
                    ),
                    "metric": label,
                    "value": float(skew),
                    "confidence": 0.85,
                })
        return insights

    def _from_forecast(self, forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for f in forecasts:
            col = f.get("column", "indicateur")
            label = humanize_column(col)
            direction = f.get("trend_direction", "stable")
            horizon = f.get("horizon", 3)
            preds = f.get("predictions", [])
            if not preds:
                continue

            last_pred = preds[-1].get("predicted_value")
            if last_pred is None:
                continue

            dir_label = {
                "up": "à la hausse",
                "down": "à la baisse",
                "stable": "stable",
            }.get(direction, "stable")

            desc = f"Projection estimée {dir_label} à court terme ({last_pred:,.2f} attendu à l'horizon {horizon} périodes)."

            insights.append({
                "type": "forecast",
                "severity": "medium",
                "title": f"Projection {dir_label} pour {label}",
                "description": desc,
                "metric": label,
                "value": float(last_pred),
                "confidence": 0.80,
            })
        return insights
