from src.intent import UserIntent


intent = UserIntent(
    use_case="travel",
    price_sensitivity="high",
    priority_features=["durability"],
    avoid_features=["bulky"],
    exploration_preference="balanced"
)

print(intent.to_dict())