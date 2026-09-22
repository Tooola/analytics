"""Smart Analytical AI provider — provides detailed interpretations, recommendations, and actionable solution proposals.
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
                findings.append(f"Metric '{col}' exhibits significant upward acceleration (+{change}% growth).")
            elif direction == "down" and change is not None:
                findings.append(f"Metric '{col}' shows a contraction of {change}% over the analyzed period.")

        # Cross-metric financial & operational analysis
        rev_change = trend_cols.get("revenue", (None, None))[1]
        cost_change = trend_cols.get("cost", (None, None))[1]
        qty_change = trend_cols.get("quantity", (None, None))[1]

        if rev_change is not None and cost_change is not None:
            if rev_change > cost_change:
                net_gain = round(rev_change - cost_change, 2)
                findings.append(f"Revenue growth (+{rev_change}%) outpaces cost expansion (+{cost_change}%), resulting in a net margin expansion of +{net_gain}%.")
                recommendations.append("Capitalize on high-margin product lines to accelerate overall profitability.")
                action_plan.append("Immediate: Allocate additional marketing budget to the top-performing products.")
            else:
                margin_drag = round(cost_change - rev_change, 2)
                findings.append(f"Cost expansion (+{cost_change}%) exceeds revenue growth (+{rev_change}%), causing a margin compression of -{margin_drag}%.")
                recommendations.append("Audit operational cost drivers and renegotiate supplier pricing to protect operating margins.")
                action_plan.append("Immediate: Conduct a cost structure review to eliminate low-margin expense items.")

        if qty_change is not None and qty_change > 50:
            recommendations.append(f"Sales volume surge (+{qty_change}%) requires inventory optimization to prevent stockouts.")
            action_plan.append("Short-Term: Adjust reorder thresholds and secure supply chain agreements.")

        # Summarize anomalies
        anomaly_count = sum(a.get("count", 0) for a in context.anomalies)
        if anomaly_count:
            findings.append(f"Detected {anomaly_count} statistical anomaly/anomalies requiring operational verification.")
            recommendations.append("Investigate high-variance data points for potential billing errors or exceptional spikes.")
            action_plan.append("Short-Term: Set up automated threshold alerts to flag future data spikes in real time.")

        # Fallbacks if default metrics missing
        if not findings:
            findings.append("Data metrics remain within baseline variance parameters.")
            recommendations.append("Establish automated periodic monitoring to detect emerging trends early.")
            action_plan.append("Long-Term: Expand data collection timeline for multi-month trend analysis.")

        if not action_plan:
            action_plan.append("1. Immediate: Validate data accuracy with underlying source transactions.")
            action_plan.append("2. Short-Term: Benchmark unit prices against market competitors.")
            action_plan.append("3. Long-Term: Establish monthly KPI targets based on current growth trends.")

        risk_level = "High" if anomaly_count > 3 or (cost_change and rev_change and cost_change > rev_change + 20) else "Low"

        summary = (
            f"Analytical interpretation of {context.row_count} records from "
            f"'{context.application}/{context.dataset}': Identified {len(findings)} key analytical trend(s) "
            f"and {len(recommendations)} strategic recommendation(s)."
        )

        return AIInterpretation(
            provider=self.name,
            summary=summary,
            key_findings=findings,
            recommendations=recommendations,
            action_plan=action_plan,
            risk_assessment=f"Risk Level: {risk_level}. Operational stability maintained.",
            confidence=0.88,
        )
