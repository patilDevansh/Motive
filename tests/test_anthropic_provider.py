import pytest

from src.llm.anthropic_provider import (
    AnthropicProvider
)


def test_anthropic_provider_requires_key(
    monkeypatch
):
    monkeypatch.delenv(
        "ANTHROPIC_API_KEY",
        raising=False
    )

    with pytest.raises(RuntimeError):
        AnthropicProvider()