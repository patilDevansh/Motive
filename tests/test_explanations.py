from src.explanations import (
    GroundedExplanationGenerator
)

from src.intent import UserIntent


def test_grounded_explanation():

    evidence = [
        {
            "itemid": 123,

            "score": 0.75,

            "reasons": [
                {
                    "type":
                        "content_similarity",

                    "value":
                        0.82
                },

                {
                    "type":
                        "covisitation",

                    "value":
                        25.0
                }
            ],

            "intent_used": [
                "exploration_preference"
            ],

            "unverifiable_constraints": [
                "requested_brand",
                "max_price"
            ]
        }
    ]

    intent = UserIntent(
        exploration_preference=
            "exploratory",

        requested_brand=
            "Sony",

        max_price=
            300,

        supported_preferences=[
            "exploration_preference"
        ],

        unverifiable_constraints=[
            "requested_brand",
            "max_price"
        ]
    )

    generator = (
        GroundedExplanationGenerator()
    )

    result = generator.generate(
        evidence,
        intent=intent
    )

    assert len(result) == 1

    explanation = result[0][
        "explanation"
    ]

    assert (
        "similar to products"
        in explanation
    )

    assert (
        "behavioral relationship"
        in explanation
    )

    assert (
        "less familiar items"
        in explanation
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
        "requested_brand"
        not in explanation
    )

    assert (
        "max_price"
        not in explanation
    )