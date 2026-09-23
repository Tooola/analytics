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
DEFAULT_MODEL = "llama-3.3-70b-versatile"


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
                arrow = "↑" if direction == "up" else ("↓" if direction == "down" else "→")
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
                anomaly_desc += f"  - {a.get('column', '?')}: {cnt} anomalie(s) détectée(s) (méthode: {a.get('method', 'IQR')})\n"
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
        for s in context.summary[:8]:  # Limiter pour ne pas surcharger
            col = s.get("column", "?")
            mean = s.get("mean")
            std = s.get("std")
            mn = s.get("min")
            mx = s.get("max")
            if mean is not None:
                stats_desc += f"  - {col}: moy={mean:.2f}, écart-type={std:.2f if std else '?'}, min={mn}, max={mx}\n"

        return f"""Tu es un expert en Business Intelligence et analyse de données, mandaté pour produire un rapport analytique professionnel.

## Contexte de l'analyse
- **Application analysée** : {context.application}
- **Dataset** : {context.dataset}
- **Nombre d'enregistrements** : {context.row_count:,} lignes
- **Contexte métier** : {context.business_context or "Analyse générale de performance opérationnelle"}

## Données analytiques collectées

### Statistiques descriptives :
{stats_desc or "  - Données non disponibles.\n"}

### Tendances identifiées :
{trends_desc or "  - Aucune tendance significative.\n"}

### Anomalies détectées :
{anomaly_desc}

### Insights générés :
{insights_desc}

## Tes instructions

Produis un rapport analytique complet, structuré et actionnable. Tu dois :
1. Interpréter les données dans le contexte spécifique de l'application "{context.application}"
2. Formuler des recommandations CONCRÈTES et PERTINENTES pour ce type de métier
3. Identifier les risques opérationnels et financiers potentiels
4. Proposer un plan d'action priorisé (Immédiat / Court terme / Long terme)

Réponds UNIQUEMENT en JSON strict (pas de markdown, pas de balises ```) avec cette structure exacte :
{{
  "summary": "Résumé exécutif de 2-3 phrases présentant les conclusions clés de l'analyse.",
  "key_findings": [
    "Constat 1 précis avec chiffres",
    "Constat 2 précis avec chiffres",
    "Constat 3 précis avec chiffres",
    "Constat 4 (si pertinent)",
    "Constat 5 (si pertinent)"
  ],
  "recommendations": [
    "Recommandation stratégique 1 contextualisée à {context.application}",
    "Recommandation stratégique 2",
    "Recommandation stratégique 3",
    "Recommandation stratégique 4 (si pertinent)"
  ],
  "action_plan": [
    "🔴 IMMÉDIAT (< 7 jours) : Action prioritaire à prendre maintenant",
    "🟡 COURT TERME (1-4 semaines) : Action de consolidation",
    "🟢 LONG TERME (> 1 mois) : Initiative stratégique"
  ],
  "risk_assessment": "Niveau de risque [Faible/Modéré/Élevé/Critique] — Justification concise des risques identifiés et impact potentiel."
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
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un analyste BI expert. Tu produis uniquement du JSON valide, "
                        "sans markdown ni commentaires. Tes analyses sont en français, "
                        "précises, chiffrées et actionnables."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
        }

        try:
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
            if resp.status_code != 200:
                logger.error(
                    "Groq API returned status %s: %s", resp.status_code, resp.text[:500]
                )
                from app.services.ai.mock_provider import MockAIProvider
                return MockAIProvider().interpret(context)

            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"].strip()

            # Nettoyage si markdown JSON
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            parsed = json.loads(raw_text)
            return AIInterpretation(
                provider=f"groq ({self.model})",
                summary=parsed.get("summary", "Analyse complétée avec succès."),
                key_findings=parsed.get("key_findings", []),
                recommendations=parsed.get("recommendations", []),
                action_plan=parsed.get("action_plan", []),
                risk_assessment=parsed.get("risk_assessment", "Évaluation des risques complétée."),
                confidence=0.93,
                raw={"usage": data.get("usage", {}), "model": self.model},
            )
        except json.JSONDecodeError as e:
            logger.error("Groq JSON decode error: %s | raw: %s", e, raw_text[:300])
            from app.services.ai.mock_provider import MockAIProvider
            return MockAIProvider().interpret(context)
        except Exception as e:
            logger.error("Groq API call failed: %s", e)
            from app.services.ai.mock_provider import MockAIProvider
            return MockAIProvider().interpret(context)
