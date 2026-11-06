from pprint import pprint

from src.llm.anthropic_provider import (
    AnthropicProvider
)

from src.llm.rule_based_provider import (
    RuleBasedProvider
)

from src.llm.evaluation import (
    evaluate_intent_parser
)

from tests.fixtures.intent_final_holdout import (
    INTENT_FINAL_HOLDOUT
)


def print_result(
    name,
    result
):
    print(
        f"\n{name}"
    )

    print("=" * 50)

    print(
        "Overall field accuracy:",
        round(
            result[
                "overall_field_accuracy"
            ],
            4
        )
    )

    print(
        "Correct fields:",
        result[
            "total_correct_fields"
        ]
    )

    print(
        "Expected fields:",
        result[
            "total_expected_fields"
        ]
    )

    successful_cases = sum(
        1
        for case in result["cases"]
        if case["success"]
    )

    total_cases = len(
        result["cases"]
    )

    print(
        "Schema-valid cases:",
        f"{successful_cases}/{total_cases}"
    )

    print(
        "\nFAILED FIELDS / ERRORS"
    )

    print("-" * 50)

    had_failure = False

    for case in result["cases"]:

        if not case["success"]:
            had_failure = True

            print(
                "\nERROR:"
            )

            print(
                case["text"]
            )

            print(
                case["error"]
            )

            continue

        wrong_fields = {
            name: info
            for name, info
            in case[
                "fields"
            ].items()
            if not info[
                "correct"
            ]
        }

        if wrong_fields:
            had_failure = True

            print(
                "\nPrompt:"
            )

            print(
                case["text"]
            )

            pprint(
                wrong_fields
            )

    if not had_failure:
        print(
            "\nNo failures."
        )


print(
    "\nFINAL FROZEN HOLDOUT"
)

print(
    "=" * 50
)

rule_provider = (
    RuleBasedProvider()
)

rule_result = (
    evaluate_intent_parser(
        rule_provider,
        INTENT_FINAL_HOLDOUT
    )
)

print_result(
    "RULE-BASED PARSER",
    rule_result
)


anthropic_provider = (
    AnthropicProvider()
)

anthropic_result = (
    evaluate_intent_parser(
        anthropic_provider,
        INTENT_FINAL_HOLDOUT
    )
)

print_result(
    "ANTHROPIC PARSER",
    anthropic_result
)