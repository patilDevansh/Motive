import pytest

from src.llm.parsing import parse_intent_response


def test_parse_valid_json():
    response = """
    {
        "exploration_preference": "exploratory",
        "popularity_preference": "niche",
        "requested_brand": null,
        "min_price": null,
        "max_price": null,
        "use_case": null,
        "priority_features": null,
        "avoid_features": null,
        "supported_preferences": [
            "exploration_preference",
            "popularity_preference"
        ],
        "unverifiable_constraints": []
    }
    """

    intent = parse_intent_response(response)

    assert intent.exploration_preference == "exploratory"
    assert intent.popularity_preference == "niche"



def test_parse_json_code_fence():
    response = (
        "```json\n"
        "{\n"
        '    "exploration_preference": "familiar",\n'
        '    "popularity_preference": null,\n'
        '    "supported_preferences": [\n'
        '        "exploration_preference"\n'
        "    ],\n"
        '    "unverifiable_constraints": []\n'
        "}\n"
        "```"
    )

    intent = parse_intent_response(response)

    assert intent.exploration_preference == "familiar"
    assert intent.popularity_preference is None


def test_invalid_json():
    response = "This is definitely not JSON."

    with pytest.raises(
        ValueError,
        match="invalid JSON"
    ):
        parse_intent_response(response)


def test_invalid_schema():
    response = """
    {
        "exploration_preference": "extremely_random",
        "popularity_preference": null
    }
    """

    with pytest.raises(ValueError):
        parse_intent_response(response)