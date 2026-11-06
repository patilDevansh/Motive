from dataclasses import asdict
from typing import Any, Dict, List

from src.intent import UserIntent


def compare_expected_fields(
    actual: UserIntent,
    expected: Dict[str, Any]
) -> Dict[str, Any]:
    actual_dict = asdict(actual)

    field_results = {}

    correct = 0
    total = 0

    for field, expected_value in expected.items():

        actual_value = actual_dict.get(field)

        is_correct = (
            actual_value == expected_value
        )

        field_results[field] = {
            "expected": expected_value,
            "actual": actual_value,
            "correct": is_correct
        }

        total += 1

        if is_correct:
            correct += 1

    accuracy = (
        correct / total
        if total > 0
        else 0.0
    )

    return {
        "correct_fields": correct,
        "total_fields": total,
        "field_accuracy": accuracy,
        "fields": field_results
    }


def evaluate_intent_parser(
    provider,
    cases: List[Dict[str, Any]]
):
    results = []

    total_correct = 0
    total_fields = 0

    for case in cases:

        text = case["text"]
        expected = case["expected"]

        try:
            actual = provider.parse_intent(
                text
            )

            comparison = (
                compare_expected_fields(
                    actual,
                    expected
                )
            )

            total_correct += (
                comparison[
                    "correct_fields"
                ]
            )

            total_fields += (
                comparison[
                    "total_fields"
                ]
            )

            results.append({
                "text": text,
                "success": True,
                "actual": actual.to_dict(),
                **comparison
            })

        except Exception as exc:

            total_fields += len(
                expected
            )

            results.append({
                "text": text,
                "success": False,
                "error": str(exc),
                "field_accuracy": 0.0
            })

    overall_accuracy = (
        total_correct / total_fields
        if total_fields > 0
        else 0.0
    )

    return {
        "overall_field_accuracy":
            overall_accuracy,

        "total_correct_fields":
            total_correct,

        "total_expected_fields":
            total_fields,

        "cases": results
    }