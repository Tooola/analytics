"""Insight engine — transforms analytical results into business-oriented insights.

Each generator examines one type of analysis result and produces human-readable,
business-analyst-style insights in French — readable by executives, not just
data scientists. Severity, confidence, and actionable descriptions included.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger

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

        logger.info("Generated %d insights for dataset '%s'", len(insights), dataset_name)
        return insights

    def _from_summary(self, summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for s in summaries:
            col = s.get("column", "indicateur")
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
                f"Sur {count:,} enregistrements analysés, la valeur moyenne de **{col}** est de **{mean:,.2f}** "
                f"(médiane : {median:,.2f}, min : {mn}, max : {mx}).{skew_note}"
            )

            insights.append({
                "type": "trend",
                "severity": "low",
                "title": f"Vue d'ensemble — {col}",
                "description": desc,
                "metric": col,
                "confidence": 1.0,
            })
        return insights

    def _from_trend(self, trends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for t in trends:
            col = t.get("column", "indicateur")
            change = t.get("change_pct")
            direction = t.get("direction", "stable")
            is_sig = t.get("is_significant", True)
            first = t.get("first_value")
            last = t.get("last_value")
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
                title = f"📈 Hausse de {abs_change:.1f}% sur {col}"
                desc = (
                    f"**{col}** est en progression de **+{abs_change:.1f}%**{period_str}"
                )
                if first is not None and last is not None:
                    desc += f" (de {first:,.2f} à {last:,.2f})."
                else:
                    desc += "."
                if is_sig:
                    desc += " Cette tendance est statistiquement confirmée — elle reflète une dynamique réelle, pas du bruit."
                else:
                    desc += " La variation reste dans les marges de fluctuation habituelles."
                itype = "opportunity"
            elif direction == "down":
                title = f"📉 Baisse de {abs_change:.1f}% sur {col}"
                desc = (
                    f"**{col}** est en recul de **-{abs_change:.1f}%**{period_str}"
                )
                if first is not None and last is not None:
                    desc += f" (de {first:,.2f} à {last:,.2f})."
                else:
                    desc += "."
                if is_sig:
                    desc += " Tendance confirmée — une attention particulière est recommandée."
                else:
                    desc += " Variation modérée sans signal d'alerte fort."
                itype = "risk"
            else:
                title = f"⚖️ Stabilité de {col}"
                desc = (
                    f"**{col}** reste stable{period_str} avec une variation de {abs_change:.1f}% "
                    "— aucun signal de rupture détecté."
                )
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
            col = a.get("column", "indicateur")
            raw_count = a.get("count", 0)
            if raw_count == 0:
                continue

            anomaly_items = a.get("anomalies", [])
            # Filter low confidence anomalies if ensemble consensus scores are present
            if anomaly_items and any("confidence_score" in item for item in anomaly_items):
                valid_items = [item for item in anomaly_items if item.get("confidence_score", 1.0) >= 0.66]
                count = len(valid_items)
            else:
                valid_items = anomaly_items
                count = raw_count

            if count == 0:
                continue

            severity = "high" if count > 3 else "medium"
            plural = "s" if count > 1 else ""

            # Build a short description of the anomalous values
            value_examples = ""
            for item in valid_items[:3]:
                val = item.get("value")
                row = item.get("row")
                z = item.get("z_score")
                if val is not None:
                    z_str = f", écart-type : {z:+.1f}σ" if z is not None else ""
                    row_str = f"enregistrement #{row}" if row is not None else "enregistrement"
                    value_examples += f"\n  • {row_str} — valeur : **{val:,.2f}**{z_str}"

            desc = (
                f"**{count} valeur{plural} atypique{plural}** détectée{plural} dans **{col}** "
                f"par analyse multi-méthodes (IQR + MAD{' + Isolation Forest' if count >= 15 else ''})."
            )
            if value_examples:
                desc += f"\n\nValeur{plural} concernée{plural} :{value_examples}"
            desc += (
                "\n\n*Recommandation :* Vérifier si ces enregistrements correspondent à des erreurs de saisie, "
                "des événements exceptionnels ou des données valides hors norme."
            )

            insights.append({
                "type": "anomaly",
                "severity": severity,
                "title": f"⚠️ {count} anomalie{plural} détectée{plural} sur {col}",
                "description": desc,
                "metric": col,
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
            coeff = c.get("coefficient", 0.0)
            strength = c.get("strength", "moderate")

            abs_r = abs(coeff)
            if abs_r >= 0.7:
                strength_label = "forte"
            elif abs_r >= 0.4:
                strength_label = "modérée"
            else:
                strength_label = "faible"

            if coeff > 0:
                itype = "opportunity"
                title = f"🔗 Lien positif entre {col1} et {col2} (r={coeff:.2f})"
                desc = (
                    f"Une **corrélation {strength_label} positive** (r = {coeff:.2f}) est observée entre "
                    f"**{col1}** et **{col2}**. "
                    f"Lorsque {col1} augmente, {col2} tend à augmenter également. "
                )
                if abs_r >= 0.7:
                    desc += "Ce lien est suffisamment fort pour guider des décisions opérationnelles."
            else:
                itype = "risk"
                title = f"🔗 Relation inverse entre {col1} et {col2} (r={coeff:.2f})"
                desc = (
                    f"Une **corrélation {strength_label} négative** (r = {coeff:.2f}) est observée entre "
                    f"**{col1}** et **{col2}**. "
                    f"Lorsque {col1} augmente, {col2} tend à diminuer. "
                )

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
            col = d.get("column", "indicateur")
            skew = d.get("skewness", 0.0)
            if abs(skew) > 1.0:
                if skew > 0:
                    direction_text = "concentrée sur les petites valeurs avec une longue queue vers les valeurs élevées"
                    impact = (
                        f"Quelques enregistrements à valeurs très élevées tirent la moyenne vers le haut. "
                        f"Privilégier la médiane comme indicateur de référence pour {col}."
                    )
                else:
                    direction_text = "concentrée sur les valeurs élevées avec une queue vers les faibles valeurs"
                    impact = (
                        f"La distribution de {col} est dominée par des valeurs hautes. "
                        "Des valeurs basses atypiques peuvent indiquer des anomalies ou des cas spéciaux."
                    )

                insights.append({
                    "type": "recommendation",
                    "severity": "low",
                    "title": f"📊 Distribution asymétrique de {col}",
                    "description": (
                        f"La distribution de **{col}** est {direction_text} (skewness = {skew:.2f}). "
                        f"{impact}"
                    ),
                    "metric": col,
                    "value": float(skew),
                    "confidence": 0.85,
                })
        return insights

    def _from_forecast(self, forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for f in forecasts:
            col = f.get("column", "indicateur")
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
            }.get(direction, "incertaine")

            desc = (
                f"La projection de **{col}** sur les **{horizon} prochaines périodes** indique une tendance **{dir_label}**. "
                f"Valeur projetée à l'horizon {horizon} : **{last_pred:,.2f}**. "
                "Ces prévisions sont basées sur la régression linéaire des données historiques — "
                "elles sont indicatives et doivent être interprétées en contexte opérationnel."
            )

            insights.append({
                "type": "forecast",
                "severity": "medium",
                "title": f"🔮 Prévision {col} — tendance {dir_label}",
                "description": desc,
                "metric": col,
                "value": float(last_pred),
                "confidence": 0.80,
            })
        return insights
