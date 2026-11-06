INTENT_CASES = [

    {
        "text": (
            "Show me products similar to what "
            "I usually interact with."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "popularity_preference": None,
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I want something different from "
            "what I normally look at."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": None,
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Show me the most popular products."
        ),
        "expected": {
            "exploration_preference": None,
            "popularity_preference": "popular",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I want something less mainstream."
        ),
        "expected": {
            "exploration_preference": None,
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Show me something different "
            "and not very popular."
        ),
        "expected": {
            "exploration_preference": "exploratory",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I want Bose products under $250."
        ),
        "expected": {
            "requested_brand": "Bose",
            "max_price": 250.0,
            "unverifiable_constraints": [
                "requested_brand",
                "max_price"
            ]
        }
    },

    {
        "text": (
            "Find me something for travel "
            "that is durable."
        ),
        "expected": {
            "use_case": "travel",
            "priority_features": [
                "durability"
            ],
            "unverifiable_constraints": [
                "use_case",
                "priority_features"
            ]
        }
    },

    {
        "text": (
            "I do not want anything bulky."
        ),
        "expected": {
            "avoid_features": [
                "bulky"
            ],
            "unverifiable_constraints": [
                "avoid_features"
            ]
        }
    },

    {
        "text": (
            "Give me something familiar "
            "but less popular."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "popularity_preference": "niche",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "I want something popular "
            "and close to what I already like."
        ),
        "expected": {
            "exploration_preference": "familiar",
            "popularity_preference": "popular",
            "unverifiable_constraints": []
        }
    },

    {
        "text": (
            "Show me Apple products "
            "between $100 and $500."
        ),
        "expected": {
            "requested_brand": "Apple",
            "min_price": 100.0,
            "max_price": 500.0,
            "unverifiable_constraints": [
                "requested_brand",
                "min_price",
                "max_price"
            ]
        }
    },

    {
        "text": (
            "Recommend something."
        ),
        "expected": {
            "exploration_preference": None,
            "popularity_preference": None,
            "unverifiable_constraints": []
        }
    }
]