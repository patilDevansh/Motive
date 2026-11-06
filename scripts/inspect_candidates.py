from src.artifacts import load_artifacts
from src.content import ContentRecommender
from src.popularity import PopularityRecommender
from src.routing import UserRouter
from src.candidates import CandidateGenerator


artifacts = load_artifacts()

content_model = ContentRecommender(
    normalized_item_matrix=artifacts["normalized_item_matrix"],
    item_ids=artifacts["item_ids"],
    item_to_index=artifacts["item_to_index"],
    content_neighbors=artifacts["content_neighbors"]
)

popularity_model = PopularityRecommender(
    weighted_popularity=artifacts["weighted_popularity"]
)

router = UserRouter(
    user_history_count=artifacts["user_history_count"]
)

generator = CandidateGenerator(
    content_model=content_model,
    popularity_model=popularity_model,
    router=router,
    user_item_strength=artifacts["user_item_strength"]
)


candidates = generator.generate(
    user_id=1150086,
    n_candidates=20
)

print("\n--- ESTABLISHED USER CANDIDATES ---")
print(candidates.to_string(index=False))

print("\n--- FEATURE SUMMARY ---")
print(
    candidates[
        [
            "content_score",
            "max_content_similarity",
            "history_support_count",
            "popularity_score",
            "user_history_count"
        ]
    ].describe()
)