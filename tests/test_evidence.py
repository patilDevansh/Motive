import pandas as pd

from src.evidence import (
    RecommendationEvidenceBuilder
)

from src.intent import UserIntent


def test_evidence_builder():

    candidates = pd.DataFrame({
        "itemid": [123],

        "score": [0.75],

        "max_content_similarity": [
            0.82
        ],

        "history_support_count": [
            3
        ],

        "covisitation_score": [
            25.0
        ],

        "covisitation_support_count": [
            2
        ],

        "popularity_score": [
            40.0
        ]
    })

    intent = UserIntent(
        exploration_preference=
            "familiar",

        popularity_preference=
            "popular",

        unverifiable_constraints=[
            "requested_brand",
            "max_price"
        ]
    )

    builder = (
        RecommendationEvidenceBuilder()
    )

    result = builder.build(
        candidates,
        intent=intent
    )

    assert len(result) == 1

    item = result[0]

    assert item["itemid"] == 123

    assert (
        "exploration_preference"
        in item["intent_used"]
    )

    assert (
        "popularity_preference"
        in item["intent_used"]
    )

    assert (
        "requested_brand"
        in item[
            "unverifiable_constraints"
        ]
    )

    reason_types = {
        reason["type"]
        for reason in item["reasons"]
    }

    assert (
        "content_similarity"
        in reason_types
    )

    assert (
        "covisitation"
        in reason_types
    )

    assert (
        "popularity"
        in reason_types
    )