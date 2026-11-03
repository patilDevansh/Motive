from src.artifacts import load_artifacts

artifacts = load_artifacts()

print(artifacts.keys())
print(artifacts["normalized_item_matrix"].shape)
print(len(artifacts["content_neighbors"]))
print(artifacts["user_item_strength"].shape)