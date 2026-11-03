INTENT_CHALLENGE_CASES = [

    {
        "text": (
            "Keep it pretty safe, but don't just "
            "show me whatever everyone else buys."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I'm traveling soon and I tend to be "
            "rough with my stuff. Keep it below $200."
        ),
        "expected": {
            "use_case": "travel",
            "priority_features": ["durability"],
            "max_price": 200.0,
            "unverifiable_constraints": [
                "max_price",
                "use_case",
                "priority_features"
            ]
        }
    },

    {
        "text": (
            "Sony would be nice, and stick fairly "
            "close to things I've liked before."
        ),
        "expected": {
            "requested_brand": "Sony",
            "exploration_preference": "familiar",
            "unverifiable_constraints": [
                "requested_brand"
            ]
        }
    },

    {
        "text": (
            "Surprise me. I don't want the obvious "
            "best-sellers."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Something mainstream is fine, but "
            "I'd like it to feel different from "
            "my normal choices."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "popular",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I'd rather not spend more than 300 "
            "and I hate bulky products."
        ),
        "expected": {
            "max_price": 300.0,
            "avoid_features": ["bulky"],
            "unverifiable_constraints": [
                "max_price",
                "avoid_features"
            ]
        }
    },

    {
        "text": (
            "Don't wander too far from my usual "
            "taste."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Go off the beaten path."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    }
]