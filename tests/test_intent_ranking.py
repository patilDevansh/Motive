import pandas as pd

from src.intent import UserIntent
from src.intent_ranking import IntentRankingAdjuster


def test_popular_intent_adjustment():

    candidates = pd.DataFrame({
        "itemid": [1, 2],
        "max_content_similarity": [
            0.5,
            0.5
        ],
        "history_support_count": [
            1,
            1
        ],
        "popularity_score": [
            100.0,
            10.0
        ]
    })

    intent = UserIntent(
        popularity_preference="popular"
    )

    adjuster = IntentRankingAdjuster()

    result = adjuster.adjust(
        candidates,
        intent
    )

    assert (
        result.loc[
            0,
            "intent_adjustment"
        ]
        >
        result.loc[
            1,
            "intent_adjustment"
        ]
    )


def test_niche_intent_adjustment():

    candidates = pd.DataFrame({
        "itemid": [1, 2],
        "max_content_similarity": [
            0.5,
            0.5
        ],
        "history_support_count": [
            1,
            1
        ],
        "popularity_score": [
            100.0,
            10.0
        ]
    })

    intent = UserIntent(
        popularity_preference="niche"
    )

    adjuster = IntentRankingAdjuster()

    result = adjuster.adjust(
        candidates,
        intent
    )

    assert (
        result.loc[
            1,
            "intent_adjustment"
        ]
        >
        result.loc[
            0,
            "intent_adjustment"
        ]
    )