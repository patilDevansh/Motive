from src.artifacts import load_artifacts
from src.popularity import PopularityRecommender


artifacts = load_artifacts()

popularity_model = PopularityRecommender(
    weighted_popularity=artifacts[
        "weighted_popularity"
    ]
)

result = popularity_model.recommend(k=10)

print(result)