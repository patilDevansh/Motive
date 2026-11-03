from src.intent import UserIntent
from src.recommender import Recommender


def test_recommender_with_evidence():

    recommender = Recommender()

    intent = UserIntent(
        exploration_preference="familiar",
        popularity_preference="popular",
        unverifiable_constraints=[
            "requested_brand",
            "max_price"
        ]
    )

    result = (
        recommender
        .recommend_with_evidence(
            user_id=1150086,
            k=5,
            intent=intent
        )
    )

    assert (
        result["segment"]
        == "established"
    )

    assert (
        len(
            result[
                "recommendations"
            ]
        )
        == 5
    )

    assert (
        len(
            result[
                "evidence"
            ]
        )
        == 5
    )

    first_evidence = (
        result[
            "evidence"
        ][0]
    )

    assert (
        "reasons"
        in first_evidence
    )

    assert (
        "intent_used"
        in first_evidence
    )

    assert (
        "unverifiable_constraints"
        in first_evidence
    )