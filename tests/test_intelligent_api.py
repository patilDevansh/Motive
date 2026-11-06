from fastapi.testclient import TestClient

import api.main as api_main

from src.intent import UserIntent


client = TestClient(
    api_main.app
)


class FakeAnthropicProvider:

    def parse_intent(
        self,
        user_text
    ):
        return UserIntent(
            exploration_preference=
                "exploratory",

            popularity_preference=
                "niche",

            supported_preferences=[
                "exploration_preference",
                "popularity_preference"
            ],

            unverifiable_constraints=[]
        )


class FakeUnsupportedProvider:

    def parse_intent(
        self,
        user_text
    ):
        return UserIntent(
            requested_brand="Sony",

            max_price=300.0,

            use_case="travel",

            supported_preferences=[],

            unverifiable_constraints=[
                "requested_brand",
                "max_price",
                "use_case"
            ]
        )


def test_intelligent_recommendation(
    monkeypatch
):
    monkeypatch.setattr(
        api_main,
        "AnthropicProvider",
        FakeAnthropicProvider
    )

    response = client.post(
        "/recommend/intelligent",
        json={
            "user_id": 1150086,
            "query": (
                "Show me something unusual "
                "and not widely chosen."
            ),
            "k": 5
        }
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["segment"]
        == "established"
    )

    assert (
        data[
            "parsed_intent"
        ][
            "exploration_preference"
        ]
        == "exploratory"
    )

    assert (
        data[
            "parsed_intent"
        ][
            "popularity_preference"
        ]
        == "niche"
    )

    assert (
        len(
            data[
                "recommendations"
            ]
        )
        == 5
    )

    assert (
        len(
            data[
                "evidence"
            ]
        )
        == 5
    )

    assert (
        len(
            data[
                "explanations"
            ]
        )
        == 5
    )


def test_intelligent_unverifiable_constraints(
    monkeypatch
):
    monkeypatch.setattr(
        api_main,
        "AnthropicProvider",
        FakeUnsupportedProvider
    )

    response = client.post(
        "/recommend/intelligent",
        json={
            "user_id": 1150086,

            "query": (
                "I want Sony products "
                "under $300 for travel."
            ),

            "k": 3
        }
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "unverifiable_constraints"
        ]
        == [
            "requested_brand",
            "max_price",
            "use_case"
        ]
    )

    explanation = (
        data[
            "explanations"
        ][0][
            "explanation"
        ]
    )

    assert (
        "brand"
        in explanation
    )

    assert (
        "price limit"
        in explanation
    )

    assert (
        "intended use"
        in explanation
    )

    assert (
        "requested_brand"
        not in explanation
    )