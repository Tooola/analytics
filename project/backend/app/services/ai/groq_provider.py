"""Groq AI Provider — uses Groq Cloud API (LLaMA 3 / Mixtral ultra-fast).

Génère des interprétations profondes, des recommandations stratégiques,
une évaluation des risques et un plan d'action concret, entièrement
contextualisés selon l'application et le dataset analysés.
Réponses en français, format rapport professionnel.
"""

from __future__ import annotations

import json
import requests

from app.core.logging import get_logger
from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider

logger = get_logger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]


class GroqAIProvider(AIProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key
        self.model = model

    def _build_prompt(self, context: AnalyticalContext) -> str:
        """Construit un prompt riche et contextualisé selon l'application/dataset."""

        # Résumé des tendances détectées
        trends_desc = ""
        for t in context.trends:
            col = t.get("column", "?")
            direction = t.get("direction", "stable")
            change = t.get("change_pct")
            if change is not None:
                arrow = "↑" if direction in ("up", "increasing") else ("↓" if direction in ("down", "decreasing") else "→")
                trends_desc += f"  - {col}: {arrow} {change:+.1f}%\n"
            else:
                trends_desc += f"  - {col}: {direction}\n"

        # Résumé des anomalies
        anomaly_desc = ""
        total_anomalies = 0
        for a in context.anomalies:
            cnt = a.get("count", 0)
            total_anomalies += cnt
            if cnt:
                anomaly_desc += f"  - {a.get('column', '?')}: {cnt} anomalie(s) détectée(s) (méthode: {a.get('method', 'Z-score/IQR')})\n"
                for item in a.get("anomalies", [])[:3]:
                    val = item.get("value")
                    reason = item.get("reason", "")
                    row = item.get("row")
                    anomaly_desc += f"    * Ligne {row if row is not None else '?'}: valeur={val} ({reason})\n"
        if not anomaly_desc:
            anomaly_desc = "  - Aucune anomalie significative détectée.\n"

        # Résumé des insights
        insights_desc = ""
        for ins in context.insights:
            insights_desc += f"  - [{ins.get('severity', 'info').upper()}] {ins.get('title', '')}: {ins.get('description', '')}\n"
        if not insights_desc:
            insights_desc = "  - Pas d'insights supplémentaires.\n"

        # Stats de base
        stats_desc = ""
        for s in context.summary[:8]:
            col = s.get("column", "?")
            mean = s.get("mean")
            std = s.get("std")
            mn = s.get("min")
            mx = s.get("max")
            if mean is not None:
                std_str = f"{std:.2f}" if std is not None else "?"
                stats_desc += f"  - {col}: moyenne={mean:.2f}, écart-type={std_str}, min={mn}, max={mx}\n"

        return f"""Tu es un analyste BI et Data Scientist senior, chargé d'évaluer la performance opérationnelle et financière d'une entreprise.

## Contexte de l'analyse
- **Application analysée** : {context.application}
- **Dataset** : {context.dataset}
- **Nombre d'enregistrements** : {context.row_count:,} lignes
- **Contexte métier** : {context.business_context or "Analyse approfondie de performance opérationnelle et détection d'anomalies"}

## Données analytiques synthétisées

### Statistiques descriptives :
{stats_desc or "  - Données non disponibles.\n"}

### Tendances identifiées :
{trends_desc or "  - Aucune tendance significative.\n"}

### Anomalies détectées :
{anomaly_desc}

### Insights générés :
{insights_desc}

## Tes instructions

Rédige un rapport analytique complet, hautement détaillé, chiffré et actionnable. 
1. Interprète précisément les chiffres et variations dans le contexte métier de l'application "{context.application}".
2. Explique l'impact des anomalies et des tendances sur les opérations et la rentabilité.
3. Formule des recommandations stratégiques concrètes à fort ROI.
4. Établis un plan d'action opérationnel priorisé.

Réponds UNIQUEMENT sous forme d'un objet JSON strict avec cette structure exacte :
{{
  "summary": "Résumé exécutif synthétique de 3 à 4 phrases résumant la situation et les enjeux majeurs.",
  "key_findings": [
    "Constat 1 détaillé avec chiffres précis (valeurs, %, écarts)",
    "Constat 2 détaillé avec chiffres précis",
    "Constat 3 détaillé avec chiffres précis",
    "Constat 4 détaillé"
  ],
  "recommendations": [
    "Recommandation stratégique 1 adaptée au secteur de {context.application}",
    "Recommandation stratégique 2",
    "Recommandation stratégique 3",
    "Recommandation stratégique 4"
  ],
  "action_plan": [
    "🔴 IMMÉDIAT (< 7 jours) : Action urgente prioritaire",
    "🟡 COURT TERME (1-4 semaines) : Action d'optimisation",
    "🟢 LONG TERME (> 1 mois) : Transformation stratégique"
  ],
  "risk_assessment": "Évaluation synthétique du niveau de risque (Faible / Modéré / Élevé / Critique) avec justification détaillée des impacts opérationnels et financiers."
}}"""

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        if not self.api_key:
            logger.warning("Groq API key manquante. Bascule sur le MockProvider.")
            from app.services.ai.mock_provider import MockAIProvider
            return MockAIProvider().interpret(context)

        prompt = self._build_prompt(context)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        
        last_error = None
        for current_model in models_to_try:
            payload = {
                "model": current_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Tu es un analyste BI et Data Scientist expert. Tu réponds UNIQUEMENT "
                            "en JSON strict, sans bloc de code markdown, sans texte explicatif additionnel."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"},
            }

            try:
                logger.info("Tentative d'appel Groq AI avec le modèle : %s", current_model)
                resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
                if resp.status_code != 200:
                    logger.warning(
                        "Groq API (modèle %s) status %s: %s", current_model, resp.status_code, resp.text[:300]
                    )
                    last_error = f"HTTP {resp.status_code}"
                    continue

                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

                parsed = json.loads(raw_text)

                # Formatage du plan d'action si retourné sous forme d'objets
                raw_action_plan = parsed.get("action_plan", [])
                action_plan_list: list[str] = []
                if isinstance(raw_action_plan, list):
                    for item in raw_action_plan:
                        if isinstance(item, dict):
                            priority = item.get("priority", "Immédiiat")
                            action = item.get("action", item.get("title", ""))
                            detail = item.get("detail", item.get("description", ""))
                            action_plan_list.append(f"• [{priority}] {action}: {detail}".strip(": "))
                        else:
                            action_plan_list.append(str(item))
                elif isinstance(raw_action_plan, str):
                    action_plan_list = [raw_action_plan]

                # Formatage de l'évaluation du risque si retournée sous forme d'objet
                raw_risk = parsed.get("risk_assessment")
                if isinstance(raw_risk, dict):
                    risk_str = " | ".join(f"{k}: {v}" for k, v in raw_risk.items())
                else:
                    risk_str = str(raw_risk) if raw_risk else "Évaluation des risques complétée."

                logger.info("Interprétation Groq AI générée avec succès via %s", current_model)
                return AIInterpretation(
                    provider=f"groq ({current_model})",
                    summary=parsed.get("summary", "Analyse complétée avec succès."),
                    key_findings=parsed.get("key_findings", []),
                    recommendations=parsed.get("recommendations", []),
                    action_plan=action_plan_list,
                    risk_assessment=risk_str,
                    confidence=0.96,
                    raw={"usage": data.get("usage", {}), "model": current_model},
                )
            except json.JSONDecodeError as e:
                logger.error("Groq JSON decode error (%s): %s", current_model, e)
                last_error = f"JSONDecodeError: {e}"
            except Exception as e:
                logger.error("Groq call failed (%s): %s", current_model, e)
                last_error = str(e)

        logger.error("Tous les modèles Groq ont échoué. Dernier message: %s. Bascule sur MockProvider.", last_error)
        from app.services.ai.mock_provider import MockAIProvider
        return MockAIProvider().interpret(context)
