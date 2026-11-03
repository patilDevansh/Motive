from src.intent import UserIntent
from src.llm.evaluation import (
    compare_expected_fields,
    evaluate_intent_parser
)


class FakeProvider:

    def parse_intent(
        self,
        user_text
    ):
        if "different" in user_text:
            return UserIntent(
                exploration_preference=
                    "exploratory"
            )

        return UserIntent()


def test_compare_expected_fields():

    actual = UserIntent(
        exploration_preference=
            "exploratory",

        popularity_preference=
            "niche"
    )

    expected = {
        "exploration_preference":
            "exploratory",

        "popularity_preference":
            "niche"
    }

    result = compare_expected_fields(
        actual,
        expected
    )

    assert (
        result["field_accuracy"]
        == 1.0
    )

    assert (
        result["correct_fields"]
        == 2
    )


def test_evaluate_intent_parser():

    cases = [
        {
            "text": (
                "Show me something different."
            ),
            "expected": {
                "exploration_preference":
                    "exploratory"
            }
        },

        {
            "text": "Recommend something.",
            "expected": {
                "exploration_preference":
                    None
            }
        }
    ]

    provider = FakeProvider()

    result = evaluate_intent_parser(
        provider,
        cases
    )

    assert (
        result[
            "overall_field_accuracy"
        ]
        == 1.0
    )

    assert (
        len(
            result["cases"]
        )
    )

    assert (
        result["total_correct_fields"]
        == 2
    )

    assert (
        result["total_expected_fields"]
        == 2
    )
    