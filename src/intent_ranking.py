class IntentRankingAdjuster:
    def adjust(
        self,
        ranked_candidates,
        intent
    ):
        if ranked_candidates.empty:
            return ranked_candidates.copy()

        adjusted = ranked_candidates.copy()

        # Default: no intent effect
        adjusted["intent_adjustment"] = 0.0

        if intent is None:
            return adjusted

        # ==================================================
        # 1. EXPLORATION / FAMILIARITY
        # ==================================================

        exploration = (
            intent.exploration_preference
        )

        if exploration == "familiar":

            familiar_signal = (
                adjusted[
                    "max_content_similarity"
                ]
                +
                0.1
                * adjusted[
                    "history_support_count"
                ]
            )

            adjusted[
                "intent_adjustment"
            ] += familiar_signal

        elif exploration == "exploratory":

            exploratory_signal = (
                1.0
                - adjusted[
                    "max_content_similarity"
                ].clip(
                    lower=0.0,
                    upper=1.0
                )
            )

            adjusted[
                "intent_adjustment"
            ] += exploratory_signal

        # ==================================================
        # 2. POPULARITY PREFERENCE
        # ==================================================

        popularity = (
            intent.popularity_preference
        )

        max_popularity = (
            adjusted[
                "popularity_score"
            ].max()
        )

        if max_popularity > 0:

            popularity_norm = (
                adjusted[
                    "popularity_score"
                ]
                / max_popularity
            )

        else:

            popularity_norm = 0.0

        if popularity == "popular":

            adjusted[
                "intent_adjustment"
            ] += popularity_norm

        elif popularity == "niche":

            adjusted[
                "intent_adjustment"
            ] += (
                1.0
                - popularity_norm
            )

        # "neutral" or None:
        # do not change ranking

        return adjusted