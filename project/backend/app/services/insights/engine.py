"""Insight engine — transforms analytical results into business-oriented insights.

Each generator examines one type of analysis result and produces human-readable,
business-analyst-style insights in French or English — readable by executives,
not just data scientists. Severity, confidence, and actionable descriptions included.
"""

from __future__ import annotations

import json
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
        language: str = "fr",
    ) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        is_en = language.lower() == "en"

        if "summary" in analysis_results:
            insights.extend(self._from_summary(analysis_results["summary"], is_en=is_en))

        if "trend" in analysis_results:
            insights.extend(self._from_trend(analysis_results["trend"], is_en=is_en))

        if "anomaly" in analysis_results:
            insights.extend(self._from_anomaly(analysis_results["anomaly"], is_en=is_en))

        if "correlation" in analysis_results:
            insights.extend(self._from_correlation(analysis_results["correlation"], is_en=is_en))

        if "distribution" in analysis_results:
            insights.extend(self._from_distribution(analysis_results["distribution"], is_en=is_en))

        if "forecast" in analysis_results:
            insights.extend(self._from_forecast(analysis_results["forecast"], is_en=is_en))

        if "causality" in analysis_results:
            insights.extend(self._from_causality(analysis_results["causality"], is_en=is_en))

        logger.info("Generated %d insights for dataset '%s' (lang=%s)", len(insights), dataset_name, language)
        return insights

    def _from_summary(self, summaries: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
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
                    if is_en:
                        if mean > median:
                            skew_note = (
                                f" The average ({mean:,.2f}) is notably higher than the median ({median:,.2f}), "
                                "indicating that a few high values are pulling the metric upward."
                            )
                        else:
                            skew_note = (
                                f" The average ({mean:,.2f}) is lower than the median ({median:,.2f}), "
                                "suggesting atypically low values in the dataset."
                            )
                    else:
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

            if is_en:
                desc = (
                    f"Out of {count:,} records analyzed, the average value of **{label}** is **{mean:,.2f}** "
                    f"(median: {median:,.2f}, min: {mn}, max: {mx}).{skew_note}"
                )
                title = f"Overview — {label}"
            else:
                desc = (
                    f"Sur {count:,} enregistrements analysés, la valeur moyenne de **{label}** est de **{mean:,.2f}** "
                    f"(médiane : {median:,.2f}, min : {mn}, max : {mx}).{skew_note}"
                )
                title = f"Vue d'ensemble — {label}"

            insights.append({
                "type": "trend",
                "severity": "low",
                "title": title,
                "description": desc,
                "metric": label,
                "confidence": 1.0,
                "evidence": json.dumps({
                    "analysis_type": "summary",
                    "column": col,
                    "metric_label": label,
                    "count": count,
                    "mean": mean,
                    "median": median,
                    "min": mn,
                    "max": mx,
                    "std": s.get("std"),
                }),
            })
        return insights

    def _from_trend(self, trends: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
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

            if is_en:
                period_str = f" across {periods} periods" if periods > 1 else ""
                if direction == "up":
                    title = f"Growth of +{abs_change:.1f}% on {label}"
                    desc = f"{label} increased by +{abs_change:.1f}%{period_str}. Confirmed positive trajectory over the period."
                    itype = "opportunity"
                elif direction == "down":
                    title = f"Decline of -{abs_change:.1f}% on {label}"
                    desc = f"{label} decreased by -{abs_change:.1f}%{period_str}. Operational vigilance advised to mitigate impact."
                    itype = "risk"
                else:
                    title = f"Stability on {label}"
                    desc = f"{label} remains constant{period_str} (variation of {abs_change:.1f}%). No operational disruption."
                    itype = "trend"
                    severity = "low"
            else:
                period_str = f" sur {periods} périodes" if periods > 1 else ""
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
                "evidence": json.dumps({
                    "analysis_type": "trend",
                    "column": col,
                    "metric_label": label,
                    "direction": direction,
                    "change_pct": change,
                    "periods": periods,
                    "is_significant": is_sig,
                    "slope": t.get("slope"),
                }),
            })
        return insights

    def _from_anomaly(self, anomalies: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
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
                count = raw_count

            if count == 0:
                continue

            severity = "high" if count > 3 else "medium"
            reason = a.get("reason")
            rec = a.get("recommendation")

            if is_en:
                if reason and rec:
                    desc = f"Atypical behavior detected on {label}: {reason} Recommended action: {rec}"
                else:
                    desc = f"Notable atypical variance observed on {label}. Requires operational adjustment on the related process."
                title = f"Attention point on {label} ({count} anomal{'ies' if count > 1 else 'y'})"
            else:
                if reason and rec:
                    desc = f"Comportement atypique constaté sur {label} : {reason} Action conseillée : {rec}"
                else:
                    desc = f"Variation atypique notable constatée sur {label}. Nécessite un ajustement opérationnel sur le processus associé."
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

    def _from_correlation(self, correlations: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
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

            if abs_r >= 0.8:
                strength = "strong"
            elif abs_r >= 0.6:
                strength = "moderate"
            else:
                strength = "weak"

            if is_en:
                if coeff > 0:
                    itype = "opportunity"
                    title = f"Positive link between {label1} and {label2}"
                    desc = f"A positive correlation is observed between **{label1}** and **{label2}**: as one grows, the other tends to increase as well."
                else:
                    itype = "risk"
                    title = f"Inverse relationship between {label1} and {label2}"
                    desc = f"An inverse relationship is observed between **{label1}** and **{label2}**: when {label1} increases, {label2} tends to decrease."
            else:
                if coeff > 0:
                    itype = "opportunity"
                    title = f"Lien positif entre {label1} et {label2}"
                    desc = f"Une relation positive est observée entre **{label1}** et **{label2}** : lorsque l'un progresse, l'autre augmente également."
                else:
                    itype = "risk"
                    title = f"Relation inverse entre {label1} et {label2}"
                    desc = f"Une relation inverse est observée entre **{label1}** et **{label2}** : lorsque {label1} augmente, {label2} tend à diminuer."

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

    def _from_causality(self, causality_drivers: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for d in causality_drivers:
            target = d.get("target", "")
            driver = d.get("driver", "")
            rel = d.get("relationship_type", "synchronous")
            explanation = d.get("explanation", "")

            if is_en:
                if rel == "synchronous":
                    title = f"Key driver: {driver} drives {target}"
                    itype = "opportunity"
                elif rel == "opposite":
                    title = f"Divergent impact between {target} and {driver}"
                    itype = "risk"
                else:
                    title = f"Primary contributor: {driver}"
                    itype = "trend"
            else:
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

    def _from_distribution(self, distributions: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for d in distributions:
            col = d.get("column", "indicateur")
            label = humanize_column(col)
            skew = d.get("skewness", 0.0)
            if abs(skew) > 1.0:
                if is_en:
                    if skew > 0:
                        direction_text = "skewed toward lower values with a long tail of high values"
                        impact = f"A few very high values pull the mean upward. Prefer the median as the benchmark indicator for {label}."
                    else:
                        direction_text = "skewed toward high values with a tail of low values"
                        impact = f"The distribution of {label} is dominated by high values. Atypically low values may indicate operational anomalies."
                    title = f"Asymmetric distribution on {label}"
                    desc = f"Values for {label} are {direction_text}. {impact}"
                else:
                    if skew > 0:
                        direction_text = "concentrée sur les petites valeurs avec une longue queue vers les valeurs élevées"
                        impact = f"Quelques enregistrements à valeurs très élevées tirent la moyenne vers le haut. Privilégier la médiane comme indicateur de référence pour {label}."
                    else:
                        direction_text = "concentrée sur les valeurs élevées avec une queue vers les faibles valeurs"
                        impact = f"La distribution de {label} est dominée par des valeurs hautes. Des valeurs basses atypiques peuvent indiquer des anomalies ou des cas spéciaux."
                    title = f"Répartition asymétrique sur {label}"
                    desc = f"Les valeurs de {label} sont {direction_text}. {impact}"

                insights.append({
                    "type": "recommendation",
                    "severity": "low",
                    "title": title,
                    "description": desc,
                    "metric": label,
                    "value": float(skew),
                    "confidence": 0.85,
                })
        return insights

    def _from_forecast(self, forecasts: list[dict[str, Any]], is_en: bool = False) -> list[dict[str, Any]]:
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

            if is_en:
                dir_label = {"up": "upward", "down": "downward", "stable": "stable"}.get(direction, "stable")
                desc = f"Short-term projection estimated {dir_label} ({last_pred:,.2f} expected over {horizon} periods)."
                title = f"{dir_label.capitalize()} projection for {label}"
            else:
                dir_label = {"up": "à la hausse", "down": "à la baisse", "stable": "stable"}.get(direction, "stable")
                desc = f"Projection estimée {dir_label} à court terme ({last_pred:,.2f} attendu à l'horizon {horizon} périodes)."
                title = f"Projection {dir_label} pour {label}"

            insights.append({
                "type": "forecast",
                "severity": "medium",
                "title": title,
                "description": desc,
                "metric": label,
                "value": float(last_pred),
                "confidence": 0.80,
            })
        return insights
