from pathlib import Path
import pickle

from src.artifacts import load_artifacts
from src.content import ContentRecommender
from src.popularity import PopularityRecommender
from src.routing import UserRouter
from src.candidates import CandidateGenerator
from src.features import FeatureBuilder
from src.reranker import TreeReranker
from src.covisitation import CovisitationRecommender
from src.intent_ranking import IntentRankingAdjuster
from src.evidence import RecommendationEvidenceBuilder


class Recommender:
    def __init__(self):

        # ==================================================
        # 1. LOAD CORE ARTIFACTS
        # ==================================================

        artifacts = load_artifacts()

        self.user_item_strength = artifacts[
            "user_item_strength"
        ]

        # ==================================================
        # 2. USER ROUTING
        # ==================================================

        self.router = UserRouter(
            user_history_count=artifacts[
                "user_history_count"
            ]
        )

        # ==================================================
        # 3. CONTENT MODEL
        # ==================================================

        self.content_model = ContentRecommender(
            normalized_item_matrix=artifacts[
                "normalized_item_matrix"
            ],
            item_ids=artifacts[
                "item_ids"
            ],
            item_to_index=artifacts[
                "item_to_index"
            ],
            content_neighbors=artifacts[
                "content_neighbors"
            ]
        )

        # ==================================================
        # 4. POPULARITY MODEL
        # ==================================================

        self.popularity_model = PopularityRecommender(
            weighted_popularity=artifacts[
                "weighted_popularity"
            ]
        )

        # ==================================================
        # 5. LOAD CO-VISITATION ARTIFACT
        # ==================================================

        project_root = (
            Path(__file__)
            .resolve()
            .parents[1]
        )

        covisitation_path = (
            project_root
            / "artifacts"
            / "reranker_covisitation.pkl"
        )

        with open(
            covisitation_path,
            "rb"
        ) as f:
            covisitation_neighbor_map = pickle.load(f)

        self.covisitation_model = (
            CovisitationRecommender(
                neighbor_map=covisitation_neighbor_map
            )
        )

        # ==================================================
        # 6. CANDIDATE GENERATOR
        # ==================================================

        self.candidate_generator = (
            CandidateGenerator(
                content_model=self.content_model,
                popularity_model=self.popularity_model,
                router=self.router,
                user_item_strength=self.user_item_strength,
                covisitation_model=self.covisitation_model
            )
        )

        # ==================================================
        # 7. FEATURE BUILDER
        # ==================================================

        self.feature_builder = FeatureBuilder()

        # ==================================================
        # 8. TRAINED TREE RERANKER
        # ==================================================

        self.reranker = TreeReranker()

        # ==================================================
        # 9. INTENT RANKING ADJUSTER
        # ==================================================

        self.intent_adjuster = IntentRankingAdjuster()

        self.evidence_builder = RecommendationEvidenceBuilder()

    # ======================================================
    # USER HISTORY
    # ======================================================

    def _get_user_history(
        self,
        user_id
    ):
        return self.user_item_strength[
            self.user_item_strength[
                "visitorid"
            ]
            == int(user_id)
        ].copy()

    # ======================================================
    # NEW USER
    # ======================================================

    def _recommend_new_user(
        self,
        k=10
    ):
        """
        New users have no behavioral history.

        The tree reranker was trained on users with history,
        so cold-start users continue to use weighted
        popularity.
        """

        recommendations = (
            self.popularity_model
            .recommend(k=k)
            .copy()
        )

        recommendations[
            "source"
        ] = "weighted_popularity_cold_start"

        return recommendations[
            [
                "itemid",
                "score",
                "source"
            ]
        ].reset_index(
            drop=True
        )

    # ======================================================
    # KNOWN USER
    # ======================================================

    def _recommend_known_user(
        self,
        user_id,
        k=10,
        intent=None
    ):
        """
        Canonical recommendation path for users with history.

        This method owns all known-user ranking logic so that
        recommend() and recommend_with_evidence() cannot drift
        into different scoring behavior.
        """

        # ==================================================
        # 1. GENERATE CANDIDATES
        # ==================================================

        candidates = (
            self.candidate_generator
            .generate(
                user_id=user_id,
                n_candidates=200,
                neighbors_per_item=50,
                max_history_items=20,
                popularity_candidates=0,
                covisitation_neighbors_per_item=50
            )
        )

        # ==================================================
        # 2. BUILD FEATURES
        # ==================================================

        features = (
            self.feature_builder
            .build(
                candidates
            )
        )

        # ==================================================
        # 3. LEARNED TREE RERANKER
        # ==================================================

        ranked = (
            self.reranker
            .rerank(
                features,
                k=min(
                    50,
                    len(features)
                )
            )
        )

        ranked = (
            ranked
            .reset_index(drop=True)
            .copy()
        )

        # Preserve the learned ranking before intent.
        ranked["base_rank"] = ranked.index + 1
        ranked["base_score"] = ranked["reranker_score"]

        # ==================================================
        # 4. INTENT ADJUSTMENT
        # ==================================================

        adjusted = (
            self.intent_adjuster
            .adjust(
                ranked_candidates=ranked,
                intent=intent
            )
            .copy()
        )

        # ==================================================
        # 5. FINAL SCORE
        # ==================================================

        if (
            intent is not None
            and "intent_adjustment" in adjusted.columns
        ):
            # Normalize reranker scores to 0-1 so the 85/15
            # blend is meaningful even when tree probabilities
            # are numerically very small.
            min_reranker = adjusted["reranker_score"].min()
            max_reranker = adjusted["reranker_score"].max()

            if max_reranker > min_reranker:
                adjusted["_reranker_norm"] = (
                    adjusted["reranker_score"] - min_reranker
                ) / (
                    max_reranker - min_reranker
                )
            else:
                adjusted["_reranker_norm"] = 1.0

            # Normalize intent adjustment to 0-1.
            min_adjustment = adjusted["intent_adjustment"].min()
            max_adjustment = adjusted["intent_adjustment"].max()

            if max_adjustment > min_adjustment:
                adjusted["_intent_norm"] = (
                    adjusted["intent_adjustment"] - min_adjustment
                ) / (
                    max_adjustment - min_adjustment
                )
            else:
                adjusted["_intent_norm"] = 0.0

            # Hand-set product heuristic:
            # 85% learned ranking, 15% supported user intent.
            adjusted["final_score"] = (
                0.85 * adjusted["_reranker_norm"]
                + 0.15 * adjusted["_intent_norm"]
            )

        else:
            adjusted["final_score"] = adjusted["reranker_score"]
            adjusted["intent_adjustment"] = 0.0

        # ==================================================
        # 6. FINAL SORT
        # ==================================================

        adjusted = (
            adjusted
            .sort_values(
                "final_score",
                ascending=False
            )
            .head(k)
            .reset_index(drop=True)
        )

        # Must be assigned after final sorting.
        adjusted["final_rank"] = adjusted.index + 1
        adjusted["score"] = adjusted["final_score"]

        # ==================================================
        # 7. SOURCE LABEL
        # ==================================================

        if intent is None:
            adjusted["source"] = "tree_reranker"
        else:
            adjusted["source"] = "tree_reranker_with_intent"

        return adjusted

    def recommend_with_evidence(
        self,
        user_id,
        k=10,
        intent=None
    ):
        """
        Return recommendations plus grounded evidence while
        reusing the exact same ranking path as recommend().
        """

        user_id = int(user_id)

        segment = (
            self.router
            .get_segment(
                user_id
            )
        )

        # ==================================================
        # NEW USER
        # ==================================================

        if segment == "new_user":

            recommendations = (
                self._recommend_new_user(
                    k=k
                )
            )

            evidence = []

            for _, row in recommendations.iterrows():

                evidence.append({
                    "itemid": int(
                        row["itemid"]
                    ),

                    "score": float(
                        row["score"]
                    ),

                    "reasons": [
                        {
                            "type": "cold_start_popularity",
                            "value": float(
                                row["score"]
                            )
                        }
                    ],

                    "content_sources": [],
                    "covisitation_sources": [],
                    "intent_used": [],

                    "base_rank": None,
                    "final_rank": None,
                    "base_score": None,
                    "final_score": float(
                        row["score"]
                    ),

                    "intent_adjustment": 0.0,

                    "unverifiable_constraints": (
                        intent.unverifiable_constraints
                        if intent is not None
                        else []
                    )
                })

            return {
                "segment": segment,
                "recommendations": recommendations,
                "evidence": evidence
            }

        # ==================================================
        # KNOWN USER
        # ==================================================

        ranked = (
            self._recommend_known_user(
                user_id=user_id,
                k=k,
                intent=intent
            )
        )

        evidence = (
            self.evidence_builder
            .build(
                ranked,
                intent=intent
            )
        )

        recommendations = ranked[
            [
                "itemid",
                "score",
                "source"
            ]
        ].reset_index(drop=True)

        return {
            "segment": segment,
            "recommendations": recommendations,
            "evidence": evidence
        }


    def recommend(
        self,
        user_id,
        k=10,
        intent=None
    ):
        """
        Simple recommendation interface returning only the
        recommendation DataFrame.
        """

        user_id = int(user_id)

        segment = (
            self.router
            .get_segment(
                user_id
            )
        )

        # ==================================================
        # NEW USER
        # ==================================================

        if segment == "new_user":
            return (
                self._recommend_new_user(
                    k=k
                )
            )

        # ==================================================
        # KNOWN USER
        # ==================================================

        ranked = (
            self._recommend_known_user(
                user_id=user_id,
                k=k,
                intent=intent
            )
        )

        return ranked[
            [
                "itemid",
                "score",
                "source"
            ]
        ].reset_index(drop=True)

