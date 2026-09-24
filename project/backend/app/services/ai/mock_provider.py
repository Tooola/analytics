"""Smart Analytical AI provider — provides detailed interpretations, recommendations, and actionable solution proposals in French.
"""

from __future__ import annotations

from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider


class MockAIProvider(AIProvider):
    name = "mock"

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        findings: list[str] = []
        recommendations: list[str] = []
        action_plan: list[str] = []

        trend_cols = {}
        for t in context.trends:
            col = t.get("column", "metric")
            direction = t.get("direction", "stable")
            change = t.get("change_pct")
            trend_cols[col] = (direction, change)

            if direction == "up" and change is not None:
                findings.append(f"L'indicateur '{col}' affiche une hausse soutenue de +{change:.1f}%.")
            elif direction == "down" and change is not None:
                findings.append(f"L'indicateur '{col}' enregistre une baisse de {change:.1f}% sur la période.")

        # Cross-metric financial & operational analysis
        rev_change = trend_cols.get("revenue", (None, None))[1]
        cost_change = trend_cols.get("cost", (None, None))[1]
        qty_change = trend_cols.get("quantity", (None, None))[1]

        if rev_change is not None and cost_change is not None:
            if rev_change > cost_change:
                net_gain = round(rev_change - cost_change, 2)
                findings.append(f"La croissance du chiffre d'affaires (+{rev_change}%) surpasse l'évolution des coûts (+{cost_change}%), générant un gain de marge nette de +{net_gain}%.")
                recommendations.append("Prioriser la commercialisation des gammes à forte marge pour amplifier la rentabilité globale.")
                action_plan.append("🔴 IMMÉDIAT (< 7 jours) : Réallouer le budget d'acquisition sur les catégories de produits les plus rentables.")
            else:
                margin_drag = round(cost_change - rev_change, 2)
                findings.append(f"La progression des charges (+{cost_change}%) est supérieure à celle des revenus (+{rev_change}%), provoquant une compression de marge de -{margin_drag}%.")
                recommendations.append("Mener un audit ciblé sur les postes de coûts d'exploitation et négocier les tarifs fournisseurs.")
                action_plan.append("🔴 IMMÉDIAT (< 7 jours) : Geler temporairement les dépenses non essentielles et réviser la structure de coûts.")

        if qty_change is not None and qty_change > 30:
            recommendations.append(f"La forte hausse des volumes (+{qty_change}%) nécessite un ajustement des niveaux de stock pour éviter toute rupture.")
            action_plan.append("🟡 COURT TERME (1-4 semaines) : Réajuster les seuils de réapprovisionnement et sécuriser les contrats logistiques.")

        # Summarize anomalies
        anomaly_count = sum(a.get("count", 0) for a in context.anomalies)
        if anomaly_count:
            findings.append(f"{anomaly_count} anomalie(s) statistique(s) détectée(s) nécessitant une vérification opérationnelle.")
            recommendations.append("Analyser les points de données atypiques pour écarter tout risque de saisie ou d'erreur de facturation.")
            action_plan.append("🟡 COURT TERME (1-4 semaines) : Mettre en place des alertes automatisées de seuil en temps réel.")

        if not findings:
            findings.append(f"Les indicateurs clés de l'application '{context.application}' restent stables dans la plage nominale.")
            recommendations.append("Maintenir le suivi périodique automatisé pour anticiper les variations saisonnières.")

        if not action_plan:
            action_plan.append("🔴 IMMÉDIAT (< 7 jours) : Valider l'intégrité des flux de données sources avec l'équipe technique.")
            action_plan.append("🟡 COURT TERME (1-4 semaines) : Établir des objectifs de KPI mensuels basés sur les tendances observées.")
            action_plan.append("🟢 LONG TERME (> 1 mois) : Automatiser la génération de rapports décisionnels hebdomadaires.")

        risk_level = "Élevé" if anomaly_count > 3 or (cost_change and rev_change and cost_change > rev_change + 15) else "Faible"

        app_name = context.application.capitalize()
        dataset_name = context.dataset.replace("-", " ").capitalize()
        summary = (
            f"Analyse décisionnelle de {context.row_count} enregistrements du dataset '{dataset_name}' ({app_name}) : "
            f"Détection de {len(findings)} constat(s) stratégique(s) et formulation de {len(recommendations)} recommandation(s) à haut ROI."
        )

        return AIInterpretation(
            provider=self.name,
            summary=summary,
            key_findings=findings,
            recommendations=recommendations,
            action_plan=action_plan,
            risk_assessment=f"Niveau de risque : {risk_level}. Stabilité opérationnelle sous contrôle.",
            confidence=0.92,
        )

