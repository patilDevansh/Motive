import pandas as pd

from src.reranker import TreeReranker


def test_tree_reranker():

    reranker = TreeReranker()

    candidates = pd.DataFrame({
        "itemid": [1, 2, 3],

        "content_score": [
            10.0,
            20.0,
            5.0
        ],

        "max_content_similarity": [
            0.8,
            0.9,
            0.4
        ],

        "history_support_count": [
            1,
            2,
            1
        ],

        "covisitation_score": [
            5.0,
            20.0,
            1.0
        ],

        "max_covisitation_score": [
            5.0,
            10.0,
            1.0
        ],

        "covisitation_support_count": [
            1,
            2,
            1
        ],

        "popularity_score": [
            10.0,
            50.0,
            5.0
        ],

        "user_history_count": [
            10,
            10,
            10
        ],

        "segment": [
            "established",
            "established",
            "established"
        ],

        "log_popularity": [
            2.397895,
            3.931826,
            1.791759
        ],

        "multi_history_support": [
            0,
            1,
            0
        ],

        "avg_content_support": [
            10.0,
            10.0,
            5.0
        ],

        "log_covisitation_score": [
            1.791759,
            3.044522,
            0.693147
        ],

        "multi_covisitation_support": [
            0,
            1,
            0
        ],

        "avg_covisitation_support": [
            5.0,
            10.0,
            1.0
        ]
    })

    result = reranker.rerank(
        candidates,
        k=2
    )

    assert len(result) == 2

    assert (
        "reranker_score"
        in result.columns
    )

    assert result[
        "reranker_score"
    ].is_monotonic_decreasing

    assert result[
        "itemid"
    ].is_unique