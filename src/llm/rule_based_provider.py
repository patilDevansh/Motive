import re

from src.intent import UserIntent
from src.llm.base import LLMProvider
from src.explanations import GroundedExplanationGenerator


class RuleBasedProvider(LLMProvider):

    def __init__(self):
        self.explanation_generator = (
            GroundedExplanationGenerator()
        )

    def parse_intent(
        self,
        user_text: str
    ) -> UserIntent:

        text = user_text.lower()

        exploration_preference = None
        popularity_preference = None

        requested_brand = None
        min_price = None
        max_price = None

        use_case = None
        priority_features = None
        avoid_features = None

        unverifiable_constraints = []

        # --------------------------------------------------
        # Exploration / familiarity
        # --------------------------------------------------

        familiar_phrases = [
            "similar to what",
            "close to what",
            "what i usually",
            "what i already like",
            "familiar"
        ]

        exploratory_phrases = [
            "something different",
            "different from",
            "exploratory",
            "something new"
        ]

        if any(
            phrase in text
            for phrase in familiar_phrases
        ):
            exploration_preference = "familiar"

        elif any(
            phrase in text
            for phrase in exploratory_phrases
        ):
            exploration_preference = "exploratory"

        # --------------------------------------------------
        # Popularity
        # --------------------------------------------------

        niche_phrases = [
            "less popular",
            "not very popular",
            "less mainstream",
            "niche"
        ]

        popular_phrases = [
            "most popular",
            "very popular",
            "popular products",
            "popular"
        ]

        if any(
            phrase in text
            for phrase in niche_phrases
        ):
            popularity_preference = "niche"

        elif any(
            phrase in text
            for phrase in popular_phrases
        ):
            popularity_preference = "popular"

        # --------------------------------------------------
        # Brand
        # --------------------------------------------------

        known_brands = [
            "bose",
            "apple",
            "sony",
            "samsung",
            "nike",
            "adidas"
        ]

        for brand in known_brands:
            if brand in text:
                requested_brand = (
                    brand.capitalize()
                )

                unverifiable_constraints.append(
                    "requested_brand"
                )

                break

        # --------------------------------------------------
        # Price
        # --------------------------------------------------

        under_match = re.search(
            r"under\s*\$?(\d+(?:\.\d+)?)",
            text
        )

        if under_match:
            max_price = float(
                under_match.group(1)
            )

            unverifiable_constraints.append(
                "max_price"
            )

        between_match = re.search(
            r"between\s*\$?(\d+(?:\.\d+)?)"
            r"\s*(?:and|-)\s*"
            r"\$?(\d+(?:\.\d+)?)",
            text
        )

        if between_match:
            min_price = float(
                between_match.group(1)
            )

            max_price = float(
                between_match.group(2)
            )

            if (
                "min_price"
                not in unverifiable_constraints
            ):
                unverifiable_constraints.append(
                    "min_price"
                )

            if (
                "max_price"
                not in unverifiable_constraints
            ):
                unverifiable_constraints.append(
                    "max_price"
                )

        # --------------------------------------------------
        # Use case
        # --------------------------------------------------

        if "travel" in text:
            use_case = "travel"

            unverifiable_constraints.append(
                "use_case"
            )

        # --------------------------------------------------
        # Desired features
        # --------------------------------------------------

        if "durable" in text:
            priority_features = [
                "durability"
            ]

            unverifiable_constraints.append(
                "priority_features"
            )

        # --------------------------------------------------
        # Avoided features
        # --------------------------------------------------

        if "bulky" in text:
            avoid_features = [
                "bulky"
            ]

            unverifiable_constraints.append(
                "avoid_features"
            )

        supported_preferences = []

        if exploration_preference is not None:
            supported_preferences.append(
                "exploration_preference"
            )

        if popularity_preference is not None:
            supported_preferences.append(
                "popularity_preference"
            )

        return UserIntent(
            exploration_preference=
                exploration_preference,

            popularity_preference=
                popularity_preference,

            requested_brand=
                requested_brand,

            min_price=
                min_price,

            max_price=
                max_price,

            use_case=
                use_case,

            priority_features=
                priority_features,

            avoid_features=
                avoid_features,

            supported_preferences=
                supported_preferences,

            unverifiable_constraints=
                unverifiable_constraints
        )

    def generate_explanation(
        self,
        recommendation_evidence,
        intent=None
    ):
        return (
            self.explanation_generator
            .generate(
                recommendation_evidence,
                intent=intent
            )
        )