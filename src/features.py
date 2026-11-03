import numpy as np
import pandas as pd



class FeatureBuilder:
    def build(self, candidates):
        if candidates.empty:
            return candidates.copy()

        features = candidates.copy()

        # --------------------------------------------------
        # Popularity-derived features
        # --------------------------------------------------

        features["log_popularity"] = np.log1p(
            features["popularity_score"]
        )

        features["multi_history_support"] = (
            features["history_support_count"] > 1
        ).astype(int)

        features["avg_content_support"] = (
            features["content_score"]
            / features[
                "history_support_count"
            ].clip(lower=1)
        )

        # --------------------------------------------------
        # Co-visitation-derived features
        # --------------------------------------------------

        features["log_covisitation_score"] = np.log1p(
            features["covisitation_score"]
        )

        features["multi_covisitation_support"] = (
            features[
                "covisitation_support_count"
            ] > 1
        ).astype(int)

        features["avg_covisitation_support"] = (
            features["covisitation_score"]
            / features[
                "covisitation_support_count"
            ].clip(lower=1)
        )

        return features