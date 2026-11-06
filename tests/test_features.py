import pandas as pd

from src.features import FeatureBuilder


def test_feature_builder():

    candidates = pd.DataFrame({
        "itemid": [1, 2],

        "content_score": [10.0, 20.0],
        "max_content_similarity": [0.8, 0.9],
        "history_support_count": [1, 2],

        "covisitation_score": [0.0, 20.0],
        "max_covisitation_score": [0.0, 10.0],
        "covisitation_support_count": [0, 2],

        "popularity_score": [0.0, 100.0],

        "user_history_count": [5, 5],

        "segment": [
            "established",
            "established"
        ]
    })

    builder = FeatureBuilder()

    features = builder.build(
        candidates
    )

    # --------------------------------------------------
    # Existing derived features
    # --------------------------------------------------

    assert (
        "log_popularity"
        in features.columns
    )

    assert (
        "multi_history_support"
        in features.columns
    )

    assert (
        "avg_content_support"
        in features.columns
    )

    assert (
        features.loc[
            0,
            "multi_history_support"
        ]
        == 0
    )

    assert (
        features.loc[
            1,
            "multi_history_support"
        ]
        == 1
    )

    assert (
        features.loc[
            0,
            "avg_content_support"
        ]
        == 10.0
    )

    assert (
        features.loc[
            1,
            "avg_content_support"
        ]
        == 10.0
    )

    # --------------------------------------------------
    # New co-visitation derived features
    # --------------------------------------------------

    assert (
        "log_covisitation_score"
        in features.columns
    )

    assert (
        "multi_covisitation_support"
        in features.columns
    )

    assert (
        "avg_covisitation_support"
        in features.columns
    )

    assert (
        features.loc[
            0,
            "multi_covisitation_support"
        ]
        == 0
    )

    assert (
        features.loc[
            1,
            "multi_covisitation_support"
        ]
        == 1
    )

    assert (
        features.loc[
            0,
            "avg_covisitation_support"
        ]
        == 0.0
    )

    assert (
        features.loc[
            1,
            "avg_covisitation_support"
        ]
        == 10.0
    )