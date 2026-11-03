from pprint import pprint

from src.llm.anthropic_provider import (
    AnthropicProvider
)

from src.llm.evaluation import (
    evaluate_intent_parser
)

from tests.fixtures.intent_challenge_cases import (
    INTENT_CHALLENGE_CASES
)


provider = AnthropicProvider()

result = evaluate_intent_parser(
    provider,
    INTENT_CHALLENGE_CASES
)

print("\nANTHROPIC CHALLENGE SET")
print("=" * 40)

print(
    "Overall field accuracy:",
    round(
        result["overall_field_accuracy"],
        4
    )
)

print(
    "Correct fields:",
    result["total_correct_fields"]
)

print(
    "Expected fields:",
    result["total_expected_fields"]
)

print("\nFAILED FIELDS")
print("=" * 40)

for case in result["cases"]:

    if not case["success"]:
        print("\nERROR:")
        print(case["text"])
        print(case["error"])
        continue

    wrong_fields = {
        name: info
        for name, info
        in case["fields"].items()
        if not info["correct"]
    }

    if wrong_fields:
        print("\nPrompt:")
        print(case["text"])

        pprint(
            wrong_fields
        )