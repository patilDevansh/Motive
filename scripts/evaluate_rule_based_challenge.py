from pprint import pprint

from src.llm.evaluation import evaluate_intent_parser
from src.llm.rule_based_provider import RuleBasedProvider
from tests.fixtures.intent_challenge_cases import (
    INTENT_CHALLENGE_CASES
)


provider = RuleBasedProvider()

result = evaluate_intent_parser(
    provider,
    INTENT_CHALLENGE_CASES
)

print("\nRULE-BASED CHALLENGE SET")
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
        print("\nERROR:", case["text"])
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