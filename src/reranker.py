from pathlib import Path
import pickle

import pandas as pd


class TreeReranker:
    def __init__(self, model_path=None):

        if model_path is None:
            project_root = (
                Path(__file__)
                .resolve()
                .parents[1]
            )

            model_path = (
                project_root
                / "artifacts"
                / "reranker_tree.pkl"
            )

        with open(
            model_path,
            "rb"
        ) as f:
            artifact = pickle.load(f)

        self.model = artifact["model"]

        self.feature_columns = artifact[
            "feature_columns"
        ]


    def rerank(
        self,
        candidates,
        k=10
    ):
        if candidates.empty:
            return candidates.copy()

        scored = candidates.copy()

        # --------------------------------------------------
        # Feature used during training
        # --------------------------------------------------

        scored["is_established"] = (
            scored["segment"]
            == "established"
        ).astype(int)

        # --------------------------------------------------
        # Make sure production features match training
        # --------------------------------------------------

        missing_features = [
            column
            for column in self.feature_columns
            if column not in scored.columns
        ]

        if missing_features:
            raise ValueError(
                "Missing reranker features: "
                f"{missing_features}"
            )

        # --------------------------------------------------
        # Score candidates using trained tree model
        # --------------------------------------------------

        X = scored[
            self.feature_columns
        ].astype(float)

        scored[
            "reranker_score"
        ] = self.model.predict_proba(
            X
        )[:, 1]

        # --------------------------------------------------
        # Learned final ranking
        # --------------------------------------------------

        scored = (
            scored
            .sort_values(
                "reranker_score",
                ascending=False
            )
            .head(k)
            .reset_index(drop=True)
        )

        return scored