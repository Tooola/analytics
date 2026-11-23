"""Smart Analytical AI provider — provides detailed interpretations, recommendations, and actionable solution proposals in French.
"""

from __future__ import annotations

from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider


class MockAIProvider(AIProvider):
    name = "mock"

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        is_en = getattr(context, "language", "fr") == "en"
        findings: list[str] = []
        recommendations: list[str] = []
        action_plan: list[str] = []

        trend_cols = {}
        for t in context.trends:
            col = t.get("column", "metric")
            direction = t.get("direction", "stable")
            change = t.get("change_pct")
            trend_cols[col] = (direction, change)

            if is_en:
                if direction == "up" and change is not None:
                    findings.append(f"Metric '{col}' shows a steady increase of +{change:.1f}%.")
                elif direction == "down" and change is not None:
                    findings.append(f"Metric '{col}' records a decrease of {change:.1f}% over the period.")
            else:
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
                if is_en:
                    findings.append(f"Revenue growth (+{rev_change}%) outpaces cost growth (+{cost_change}%), generating a net margin gain of +{net_gain}%.")
                    recommendations.append("Prioritize marketing high-margin lines to boost overall profitability.")
                    action_plan.append("Immediate Priority (< 7 days): Reallocate acquisition budget to the most profitable product categories.")
                else:
                    findings.append(f"La croissance du chiffre d'affaires (+{rev_change}%) surpasse l'évolution des coûts (+{cost_change}%), générant un gain de marge nette de +{net_gain}%.")
                    recommendations.append("Prioriser la commercialisation des gammes à forte marge pour amplifier la rentabilité globale.")
                    action_plan.append("Priorité Immédiate (< 7 jours) : Réallouer le budget d'acquisition sur les catégories de produits les plus rentables et ajuster les objectifs commerciaux.")
            else:
                margin_drag = round(cost_change - rev_change, 2)
                if is_en:
                    findings.append(f"Expense growth (+{cost_change}%) exceeds revenue growth (+{rev_change}%), causing a margin compression of -{margin_drag}%.")
                    recommendations.append("Conduct an audit on operating cost lines and negotiate supplier pricing.")
                    action_plan.append("Immediate Priority (< 7 days): Temporarily freeze non-essential expenses and review operating cost structure.")
                else:
                    findings.append(f"La progression des charges (+{cost_change}%) est supérieure à celle des revenus (+{rev_change}%), provoquant une compression de marge de -{margin_drag}%.")
                    recommendations.append("Mener un audit ciblé sur les postes de coûts d'exploitation et négocier les tarifs fournisseurs.")
                    action_plan.append("Priorité Immédiate (< 7 jours) : Geler temporairement les dépenses non essentielles et réviser la structure de coûts d'exploitation.")

        if qty_change is not None and qty_change > 30:
            if is_en:
                recommendations.append(f"The sharp increase in volumes (+{qty_change}%) requires stock adjustments to avoid shortages.")
                action_plan.append("Short Term (1-4 weeks): Readjust replenishment thresholds and secure carrier contracts.")
            else:
                recommendations.append(f"La forte hausse des volumes (+{qty_change}%) nécessite un ajustement des niveaux de stock pour éviter toute rupture.")
                action_plan.append("Court Terme (1-4 semaines) : Réajuster les seuils de réapprovisionnement et sécuriser les contrats logistiques avec les transporteurs.")

        # Summarize anomalies
        anomaly_count = sum(a.get("count", 0) for a in context.anomalies)
        if anomaly_count:
            if is_en:
                findings.append("Anomalies and atypical patterns observed on key indicators requiring operational verification.")
                recommendations.append("Review isolated entries to verify fluctuations and rule out data entry errors.")
                action_plan.append("Medium Term (> 1 month): Implement automated threshold alerts and train operations teams.")
            else:
                findings.append("Anomalies et comportements atypiques constatés sur certains indicateurs clés nécessitant une vérification opérationnelle.")
                recommendations.append("Contrôler les enregistrements isolés pour confirmer la réalité des variations et écarter toute erreur de saisie.")
                action_plan.append("Moyen Terme (> 1 mois) : Mettre en place des alertes automatisées de seuil et former les équipes opérationnelles.")

        if not findings:
            if is_en:
                findings.append(f"Key indicators for '{context.application}' remain stable within nominal range.")
                recommendations.append("Maintain periodic tracking to anticipate seasonal changes.")
            else:
                findings.append(f"Les indicateurs clés de l'application '{context.application}' restent stables dans la plage nominale.")
                recommendations.append("Maintenir le suivi périodique automatisé pour anticiper les variations saisonnières.")

        if not action_plan:
            if is_en:
                action_plan.append("🔴 IMMEDIATE (< 7 days): Validate source data pipeline integrity with the engineering team.")
                action_plan.append("🟡 SHORT TERM (1-4 weeks): Establish monthly KPI targets based on observed trends.")
                action_plan.append("🟢 LONG TERM (> 1 month): Automate weekly executive reporting generation.")
            else:
                action_plan.append("🔴 IMMÉDIAT (< 7 jours) : Valider l'intégrité des flux de données sources avec l'équipe technique.")
                action_plan.append("🟡 COURT TERME (1-4 semaines) : Établir des objectifs de KPI mensuels basés sur les tendances observées.")
                action_plan.append("🟢 LONG TERME (> 1 mois) : Automatiser la génération de rapports décisionnels hebdomadaires.")

        risk_level = ("High" if is_en else "Élevé") if anomaly_count > 3 or (cost_change and rev_change and cost_change > rev_change + 15) else ("Low" if is_en else "Faible")

        app_name = context.application.capitalize()
        dataset_name = context.dataset.replace("-", " ").capitalize()
        if is_en:
            summary = (
                f"Executive analysis of {context.row_count} records from dataset '{dataset_name}' ({app_name}): "
                f"Identified {len(findings)} strategic finding(s) and {len(recommendations)} high-ROI recommendation(s)."
            )
            risk_text = f"Risk level: {risk_level}. Operational stability under control."
        else:
            summary = (
                f"Analyse décisionnelle de {context.row_count} enregistrements du dataset '{dataset_name}' ({app_name}) : "
                f"Détection de {len(findings)} constat(s) stratégique(s) et formulation de {len(recommendations)} recommandation(s) à haut ROI."
            )
            risk_text = f"Niveau de risque : {risk_level}. Stabilité opérationnelle sous contrôle."

        return AIInterpretation(
            provider=self.name,
            summary=summary,
            key_findings=findings,
            recommendations=recommendations,
            action_plan=action_plan,
            risk_assessment=risk_text,
            confidence=0.92,
        )

