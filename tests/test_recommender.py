from src.recommender import Recommender


def test_new_user():
    recommender = Recommender()

    result = recommender.recommend(
        999999999,
        k=5
    )

    assert len(result) == 5

    assert (
        result["source"]
        == "weighted_popularity_cold_start"
    ).all()


def test_low_history_user():
    recommender = Recommender()

    result = recommender.recommend(
        1,
        k=5
    )

    assert len(result) == 5

    assert (
        result["source"]
        == "tree_reranker"
    ).all()

    assert (
        result["score"]
        .is_monotonic_decreasing
    )


def test_established_user():
    recommender = Recommender()

    result = recommender.recommend(
        1150086,
        k=5
    )

    assert len(result) == 5

    assert (
        result["source"]
        == "tree_reranker"
    ).all()

    assert (
        result["score"]
        .is_monotonic_decreasing
    )


def test_recommendations_are_unique():
    recommender = Recommender()

    result = recommender.recommend(
        1150086,
        k=10
    )

    assert result[
        "itemid"
    ].is_unique