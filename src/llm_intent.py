import json
import os

from openai import OpenAI

from src.intent import UserIntent


class LLMIntentParser:
    def __init__(self, model="gpt-5.6-luna"):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )

        self.model = model

    def parse(self, text: str) -> UserIntent:

        if not text or not text.strip():
            return UserIntent()

        prompt = f"""
You extract structured shopping intent.

Return ONLY valid JSON with exactly these fields:

{{
  "use_case": string or null,
  "price_sensitivity": "low", "medium", "high", or null,
  "priority_features": array of strings,
  "avoid_features": array of strings,
  "exploration_preference": "familiar", "balanced", "exploratory", or null
}}

Rules:
- Do not invent preferences.
- Only extract information explicitly stated or strongly implied.
- Keep feature phrases short.
- If information is unknown, use null or [].
- Do not recommend products.

User request:
{text}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        raw_text = response.output_text

        data = json.loads(
            raw_text
        )

        return UserIntent(
            use_case=data.get(
                "use_case"
            ),
            price_sensitivity=data.get(
                "price_sensitivity"
            ),
            priority_features=data.get(
                "priority_features"
            ) or [],
            avoid_features=data.get(
                "avoid_features"
            ) or [],
            exploration_preference=data.get(
                "exploration_preference"
            )
        )