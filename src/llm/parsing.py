import json

from src.intent import UserIntent
from src.llm.validation import (
    validate_intent_payload
)


def parse_intent_response(
    response_text: str
) -> UserIntent:
    """
    Convert raw LLM JSON output into
    a validated UserIntent.
    """

    if not isinstance(response_text, str):
        raise TypeError(
            "LLM response must be a string."
        )

    cleaned = response_text.strip()

    # Handle accidental Markdown code fences.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    try:
        payload = json.loads(cleaned)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(
            "LLM response must be a JSON object."
        )

    return validate_intent_payload(
        payload
    )