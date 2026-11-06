from src.artifacts import load_artifacts
from src.routing import UserRouter


artifacts = load_artifacts()

router = UserRouter(
    user_history_count=artifacts[
        "user_history_count"
    ]
)

print(
    "Unknown user:",
    router.get_history_count(999999999),
    router.get_segment(999999999)
)

print(
    "User 1:",
    router.get_history_count(1),
    router.get_segment(1)
)

print(
    "User 1150086:",
    router.get_history_count(1150086),
    router.get_segment(1150086)
)