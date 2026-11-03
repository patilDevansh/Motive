from typing import Any, Dict

from src.intent import UserIntent


VALID_EXPLORATION = {
    "familiar",
    "balanced",
    "exploratory",
    None,
}

VALID_POPULARITY = {
    "popular",
    "neutral",
    "niche",
    None,
}


def validate_intent_payload(
    payload: Dict[str, Any]
) -> UserIntent:
    """
    Validate raw structured LLM output and convert it
    into a safe UserIntent object.

    The validator protects the recommender from:
    - invalid enum values
    - malformed list fields
    - invalid price ranges
    - unsupported fields being marked as supported
    - unknown unverifiable constraints
    """

    if not isinstance(payload, dict):
        raise TypeError(
            "Intent payload must be a dictionary."
        )

    # --------------------------------------------------
    # Supported ranking preferences
    # --------------------------------------------------

    exploration = payload.get(
        "exploration_preference"
    )

    popularity = payload.get(
        "popularity_preference"
    )

    if exploration not in VALID_EXPLORATION:
        raise ValueError(
            "Invalid exploration_preference: "
            f"{exploration}"
        )

    if popularity not in VALID_POPULARITY:
        raise ValueError(
            "Invalid popularity_preference: "
            f"{popularity}"
        )

    # --------------------------------------------------
    # Price fields
    # --------------------------------------------------

    min_price = payload.get(
        "min_price"
    )

    max_price = payload.get(
        "max_price"
    )

    if min_price is not None:
        try:
            min_price = float(
                min_price
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "min_price must be numeric or null."
            ) from exc

        if min_price < 0:
            raise ValueError(
                "min_price cannot be negative."
            )

    if max_price is not None:
        try:
            max_price = float(
                max_price
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "max_price must be numeric or null."
            ) from exc

        if max_price < 0:
            raise ValueError(
                "max_price cannot be negative."
            )

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise ValueError(
            "min_price cannot exceed max_price."
        )

    # --------------------------------------------------
    # List-like semantic fields
    # --------------------------------------------------

    priority_features = payload.get(
        "priority_features"
    )

    avoid_features = payload.get(
        "avoid_features"
    )

    if (
        priority_features is not None
        and not isinstance(
            priority_features,
            list
        )
    ):
        raise ValueError(
            "priority_features must be a list or null."
        )

    if (
        avoid_features is not None
        and not isinstance(
            avoid_features,
            list
        )
    ):
        raise ValueError(
            "avoid_features must be a list or null."
        )

    # --------------------------------------------------
    # Grounding metadata
    # --------------------------------------------------

    supported_preferences = payload.get(
        "supported_preferences"
    )

    if supported_preferences is None:
        supported_preferences = []

    unverifiable_constraints = payload.get(
        "unverifiable_constraints"
    )

    if unverifiable_constraints is None:
        unverifiable_constraints = []

    if not isinstance(
        supported_preferences,
        list
    ):
        raise ValueError(
            "supported_preferences must be a list."
        )

    if not isinstance(
        unverifiable_constraints,
        list
    ):
        raise ValueError(
            "unverifiable_constraints must be a list."
        )

    # --------------------------------------------------
    # Validate supported preference names
    # --------------------------------------------------

    allowed_supported = {
        "exploration_preference",
        "popularity_preference",
    }

    for field in supported_preferences:
        if field not in allowed_supported:
            raise ValueError(
                "Unsupported field incorrectly "
                "marked as supported: "
                f"{field}"
            )

    # --------------------------------------------------
    # Validate unverifiable constraint names
    # --------------------------------------------------

    allowed_unverifiable = {
        "requested_brand",
        "min_price",
        "max_price",
        "use_case",
        "priority_features",
        "avoid_features",
    }

    for field in unverifiable_constraints:
        if field not in allowed_unverifiable:
            raise ValueError(
                "Unknown unverifiable constraint: "
                f"{field}"
            )

    # --------------------------------------------------
    # Internal consistency checks
    # --------------------------------------------------

    if (
        exploration is not None
        and "exploration_preference"
        not in supported_preferences
    ):
        supported_preferences.append(
            "exploration_preference"
        )

    if (
        popularity is not None
        and "popularity_preference"
        not in supported_preferences
    ):
        supported_preferences.append(
            "popularity_preference"
        )

    requested_brand = payload.get(
        "requested_brand"
    )

    use_case = payload.get(
        "use_case"
    )

    inferred_unverifiable = {
        "requested_brand": requested_brand,
        "min_price": min_price,
        "max_price": max_price,
        "use_case": use_case,
        "priority_features": priority_features,
        "avoid_features": avoid_features,
    }

    for field, value in inferred_unverifiable.items():
        if (
            value is not None
            and field
            not in unverifiable_constraints
        ):
            unverifiable_constraints.append(
                field
            )

    # --------------------------------------------------
    # Return safe UserIntent
    # --------------------------------------------------

    return UserIntent(
        exploration_preference=exploration,
        popularity_preference=popularity,

        requested_brand=requested_brand,

        min_price=min_price,
        max_price=max_price,

        use_case=use_case,

        priority_features=priority_features,

        avoid_features=avoid_features,

        supported_preferences=
            supported_preferences,

        unverifiable_constraints=
            unverifiable_constraints,
    )