"""Google Gemini AI Provider — uses Google AI Studio Free API Key.

Provides deep AI interpretation, strategic recommendations, risk assessment,
and concrete solution action plans.
"""

from __future__ import annotations

import json
import requests

from app.core.logging import get_logger
from app.schemas.ai import AIInterpretation, AnalyticalContext
from app.services.ai.base import AIProvider

logger = get_logger(__name__)


class GeminiAIProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key
        self.model = model

    def interpret(self, context: AnalyticalContext) -> AIInterpretation:
        if not self.api_key:
            logger.warning("Gemini API key is missing. Falling back to structured provider.")
            from app.services.ai.mock_provider import MockAIProvider
            return MockAIProvider().interpret(context)

        prompt = f"""
You are an expert business intelligence and data analytics AI.
Analyze the following aggregated analytical context from application '{context.application}' and dataset '{context.dataset}':

- Dataset Record Count: {context.row_count}
- Summary Statistics: {json.dumps(context.summary)}
- Identified Trends: {json.dumps(context.trends)}
- Identified Anomalies: {json.dumps(context.anomalies)}
- Generated Insights: {json.dumps(context.insights)}

Provide your response in strict JSON format with the following keys:
1. "summary": A concise 2-sentence executive summary of the overall analysis.
2. "key_findings": A list of 3-5 specific bullet points detailing key trends, metrics, or anomalies.
3. "recommendations": A list of 3-4 strategic advice items based on the data.
4. "action_plan": A list of 3-4 concrete, step-by-step solution proposals (Immediate, Short-Term, Long-Term).
5. "risk_assessment": A 1-sentence risk level and operational evaluation.

Response must be pure JSON only without markdown formatting.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                logger.error("Gemini API returned status %s: %s", resp.status_code, resp.text)
                from app.services.ai.mock_provider import MockAIProvider
                return MockAIProvider().interpret(context)

            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean markdown JSON formatting if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            parsed = json.loads(raw_text)
            return AIInterpretation(
                provider=f"gemini ({self.model})",
                summary=parsed.get("summary", "Analysis completed successfully."),
                key_findings=parsed.get("key_findings", []),
                recommendations=parsed.get("recommendations", []),
                action_plan=parsed.get("action_plan", []),
                risk_assessment=parsed.get("risk_assessment", "Risk evaluation complete."),
                confidence=0.95,
                raw=data,
            )
        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            from app.services.ai.mock_provider import MockAIProvider
            return MockAIProvider().interpret(context)
