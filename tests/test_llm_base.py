import pytest

from src.llm.base import LLMProvider


def test_llm_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        LLMProvider()