from pprint import pprint

from src.llm.anthropic_provider import AnthropicProvider


provider = AnthropicProvider()

intent = provider.parse_intent(
    "I want something less obvious "
    "than what I normally choose, "
    "and not too mainstream."
)

pprint(intent.to_dict())