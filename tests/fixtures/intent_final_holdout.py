INTENT_FINAL_HOLDOUT = [

    {
        "text": (
            "Stay close to my usual preferences, "
            "but don't just give me the obvious popular choices."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I'd like to try something outside my normal pattern, "
            "but I still want something people commonly choose."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "popular",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I'd prefer Sony and I don't want to go above $350."
        ),
        "expected": {
            "requested_brand": "Sony",
            "max_price": 350.0,
            "unverifiable_constraints": [
                "requested_brand",
                "max_price"
            ]
        }
    },

    {
        "text": (
            "This is for travel and I want something compact."
        ),
        "expected": {
            "use_case": "travel",
            "priority_features": [
                "compact"
            ],
            "unverifiable_constraints": [
                "use_case",
                "priority_features"
            ]
        }
    },

    {
        "text": (
            "Avoid anything heavy or bulky."
        ),
        "expected": {
            "avoid_features": [
                "heavy",
                "bulky"
            ],
            "unverifiable_constraints": [
                "avoid_features"
            ]
        }
    },

    {
        "text": (
            "Keep the choices pretty conventional."
        ),
        "expected": {
            "popularity_preference": "popular",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I want to discover things I normally wouldn't consider."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Don't change things up too much."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I'd like to stay somewhere between $150 and $400."
        ),
        "expected": {
            "min_price": 150.0,
            "max_price": 400.0,
            "unverifiable_constraints": [
                "min_price",
                "max_price"
            ]
        }
    },

    {
        "text": (
            "Show me something unusual and not widely chosen."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    }
]