from src.intent import UserIntent
from src.recommender import Recommender


def test_known_user_with_familiar_intent():

    recommender = Recommender()

    intent = UserIntent(
        exploration_preference="familiar"
    )

    result = recommender.recommend(
        user_id=1150086,
        k=5,
        intent=intent
    )

    assert len(result) == 5

    assert (
        result["source"]
        == "tree_reranker_with_intent"
    ).all()


def test_known_user_with_exploratory_intent():

    recommender = Recommender()

    intent = UserIntent(
        exploration_preference="exploratory"
    )

    result = recommender.recommend(
        user_id=1150086,
        k=5,
        intent=intent
    )

    assert len(result) == 5

    assert (
        result["source"]
        == "tree_reranker_with_intent"
    ).all()