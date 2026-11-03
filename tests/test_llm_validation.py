import pytest

from src.llm.validation import (
    validate_intent_payload
)


def test_valid_intent_payload():

    payload = {
        "exploration_preference":
            "exploratory",

        "popularity_preference":
            "niche",

        "requested_brand":
            "Sony",

        "min_price":
            None,

        "max_price":
            300,

        "use_case":
            "travel",

        "priority_features":
            ["durability"],

        "avoid_features":
            ["bulky"],

        "supported_preferences": [
            "exploration_preference",
            "popularity_preference"
        ],

        "unverifiable_constraints": [
            "requested_brand",
            "max_price",
            "use_case",
            "priority_features",
            "avoid_features"
        ]
    }

    intent = validate_intent_payload(
        payload
    )

    assert (
        intent.exploration_preference
        == "exploratory"
    )

    assert (
        intent.popularity_preference
        == "niche"
    )

    assert (
        intent.max_price
        == 300.0
    )


def test_invalid_exploration_value():

    payload = {
        "exploration_preference":
            "crazy_mode",

        "popularity_preference":
            None
    }

    with pytest.raises(ValueError):
        validate_intent_payload(
            payload
        )


def test_invalid_price_range():

    payload = {
        "exploration_preference":
            None,

        "popularity_preference":
            None,

        "min_price":
            500,

        "max_price":
            100
    }

    with pytest.raises(ValueError):
        validate_intent_payload(
            payload
        )


def test_unsupported_field_cannot_be_supported():

    payload = {
        "exploration_preference":
            None,

        "popularity_preference":
            None,

        "supported_preferences": [
            "requested_brand"
        ]
    }

    with pytest.raises(ValueError):
        validate_intent_payload(
            payload
        )