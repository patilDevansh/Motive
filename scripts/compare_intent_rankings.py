from src.intent import UserIntent
from src.recommender import Recommender


recommender = Recommender()

user_id = 1150086


familiar_intent = UserIntent(
    exploration_preference="familiar"
)

exploratory_intent = UserIntent(
    exploration_preference="exploratory"
)


familiar = recommender.recommend(
    user_id=user_id,
    k=10,
    intent=familiar_intent
)

exploratory = recommender.recommend(
    user_id=user_id,
    k=10,
    intent=exploratory_intent
)


print("\n--- FAMILIAR ---")
print(familiar)

print("\n--- EXPLORATORY ---")
print(exploratory)


familiar_items = familiar[
    "itemid"
].tolist()

exploratory_items = exploratory[
    "itemid"
].tolist()


print(
    "\nSame exact ordering:",
    familiar_items
    == exploratory_items
)

print(
    "Overlap:",
    len(
        set(familiar_items)
        & set(exploratory_items)
    )
)