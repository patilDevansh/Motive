from src.intent import UserIntent


def test_user_intent_to_dict():

    intent = UserIntent(
        exploration_preference="exploratory",
        popularity_preference="niche",

        requested_brand="Bose",
        max_price=250.0,

        use_case="travel",

        priority_features=[
            "durability"
        ],

        avoid_features=[
            "bulky"
        ],

        supported_preferences=[
            "exploration_preference",
            "popularity_preference"
        ],

        unverifiable_constraints=[
            "requested_brand",
            "max_price",
            "use_case",
            "priority_features",
            "avoid_features"
        ]
    )

    data = intent.to_dict()

    assert (
        data["exploration_preference"]
        == "exploratory"
    )

    assert (
        data["popularity_preference"]
        == "niche"
    )

    assert (
        data["requested_brand"]
        == "Bose"
    )

    assert (
        data["max_price"]
        == 250.0
    )

    assert (
        "exploration_preference"
        in data["supported_preferences"]
    )

    assert (
        "requested_brand"
        in data["unverifiable_constraints"]
    )