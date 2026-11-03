from src.intent import UserIntent


def test_user_intent_schema():

    intent = UserIntent(
        exploration_preference="exploratory",
        popularity_preference="niche",

        requested_brand="Sony",

        min_price=100,
        max_price=300,

        use_case="travel",

        priority_features=[
            "battery life",
            "portability"
        ],

        avoid_features=[
            "heavy"
        ],

        supported_preferences=[
            "exploration_preference",
            "popularity_preference"
        ],

        unverifiable_constraints=[
            "requested_brand",
            "min_price",
            "max_price",
            "use_case",
            "priority_features",
            "avoid_features"
        ]
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
        intent.requested_brand
        == "Sony"
    )

    assert (
        intent.min_price
        == 100
    )

    assert (
        intent.max_price
        == 300
    )

    assert (
        intent.use_case
        == "travel"
    )

    assert (
        "battery life"
        in intent.priority_features
    )

    assert (
        "heavy"
        in intent.avoid_features
    )

    assert (
        "exploration_preference"
        in intent.supported_preferences
    )

    assert (
        "requested_brand"
        in intent.unverifiable_constraints
    )