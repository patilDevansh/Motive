from src.artifacts import load_artifacts
from src.content import ContentRecommender


artifacts = load_artifacts()

content_model = ContentRecommender(
    normalized_item_matrix=artifacts[
        "normalized_item_matrix"
    ],
    item_ids=artifacts["item_ids"],
    item_to_index=artifacts["item_to_index"],
    content_neighbors=artifacts[
        "content_neighbors"
    ]
)

result = content_model.get_similar_items(
    460429,
    k=5
)

print(result)