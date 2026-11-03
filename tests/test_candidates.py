from src.artifacts import load_artifacts
from src.content import ContentRecommender
from src.popularity import PopularityRecommender
from src.routing import UserRouter
from src.candidates import CandidateGenerator


artifacts = load_artifacts()


content_model = ContentRecommender(
    normalized_item_matrix=artifacts[
        "normalized_item_matrix"
    ],
    item_ids=artifacts[
        "item_ids"
    ],
    item_to_index=artifacts[
        "item_to_index"
    ],
    content_neighbors=artifacts[
        "content_neighbors"
    ]
)


popularity_model = PopularityRecommender(
    weighted_popularity=artifacts[
        "weighted_popularity"
    ]
)


router = UserRouter(
    user_history_count=artifacts[
        "user_history_count"
    ]
)


generator = CandidateGenerator(
    content_model=content_model,
    popularity_model=popularity_model,
    router=router,
    user_item_strength=artifacts[
        "user_item_strength"
    ]
)


def test_established_candidate_generation():

    candidates = generator.generate(
        user_id=1150086,
        n_candidates=100
    )

    assert len(candidates) <= 100
    assert len(candidates) > 0

    assert candidates["itemid"].is_unique

    required_columns = {
        "itemid",
        "content_score",
        "max_content_similarity",
        "history_support_count",
        "popularity_score",
        "user_history_count",
        "segment"
    }

    assert required_columns.issubset(
        candidates.columns
    )


def test_new_user_candidate_generation():

    candidates = generator.generate(
        user_id=999999999,
        n_candidates=100
    )

    assert len(candidates) == 100

    assert (
        candidates["segment"]
        == "new_user"
    ).all()

def test_known_user_has_multiple_candidate_signals():

    candidates = generator.generate(
        user_id=1150086,
        n_candidates=100,
        popularity_candidates=30
    )

    assert len(candidates) > 0

    assert (
        candidates["popularity_score"] > 0
    ).any()

    assert (
        candidates["content_score"] > 0
    ).any()