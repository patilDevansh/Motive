import os

from anthropic import Anthropic

from src.llm.base import LLMProvider
from src.llm.parsing import parse_intent_response
from src.llm.prompts import (
    INTENT_SYSTEM_PROMPT,
    build_intent_prompt,
)


class AnthropicProvider(LLMProvider):

    def __init__(
        self,
        model: str = "claude-sonnet-5"
    ):
        self.api_key = os.getenv(
            "ANTHROPIC_API_KEY"
        )

        if not self.api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set."
            )

        self.model = model

        self.client = Anthropic(
            api_key=self.api_key
        )

    def parse_intent(
        self,
        user_text: str
    ):
        response_text = (
            self._call_intent_model(
                user_text
            )
        )

        return parse_intent_response(
            response_text
        )

    def generate_explanation(
        self,
        recommendation_evidence,
        intent=None
    ):
        raise NotImplementedError(
            "Grounded Anthropic explanation "
            "generation is not wired yet."
        )

    def _call_intent_model(
        self,
        user_text: str
    ) -> str:

        prompt = build_intent_prompt(
            user_text
        )

        response = (
            self.client.messages.create(
                model=self.model,
                max_tokens=700,
                system=INTENT_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        )

        text_parts = []

        for block in response.content:
            if getattr(
                block,
                "type",
                None
            ) == "text":
                text_parts.append(
                    block.text
                )

        if not text_parts:
            raise RuntimeError(
                "Anthropic returned no text."
            )

        return "\n".join(
            text_parts
        ).strip()