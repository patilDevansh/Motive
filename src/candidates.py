from collections import defaultdict

import pandas as pd


class CandidateGenerator:
    def __init__(
        self,
        content_model,
        popularity_model,
        router,
        user_item_strength,
        covisitation_model=None
    ):
        self.content_model = content_model
        self.popularity_model = popularity_model
        self.router = router
        self.user_item_strength = user_item_strength
        self.covisitation_model = covisitation_model

    def _get_user_history(self, user_id):
        return self.user_item_strength[
            self.user_item_strength["visitorid"]
            == int(user_id)
        ].copy()
    

    def generate(
        self,
        user_id,
        n_candidates=100,
        neighbors_per_item=50,
        max_history_items=20,
        popularity_candidates=0,
        covisitation_neighbors_per_item=50
    ):
        user_id = int(user_id)

        segment = self.router.get_segment(
            user_id
        )

        user_history = self._get_user_history(
            user_id
        )

        history_count = len(
            user_history
        )

        # ==================================================
        # CASE 1: Completely new user
        # ==================================================

        if segment == "new_user":

            popular = (
                self.popularity_model
                .recommend(k=n_candidates)
                .copy()
            )

            popular = popular.rename(
                columns={
                    "score": "popularity_score"
                }
            )

            # No personalized evidence exists
            popular["content_score"] = 0.0
            popular["max_content_similarity"] = 0.0
            popular["history_support_count"] = 0

            popular["covisitation_score"] = 0.0
            popular["max_covisitation_score"] = 0.0
            popular["covisitation_support_count"] = 0

            popular["content_sources"] = [
                [] for _ in range(len(popular))
            ]

            popular["covisitation_sources"] = [
                [] for _ in range(len(popular))
            ]


            popular["user_history_count"] = 0
            popular["segment"] = segment

            return popular[
                [
                    "itemid",
                    "content_score",
                    "max_content_similarity",
                    "history_support_count",
                    "covisitation_score",
                    "max_covisitation_score",
                    "covisitation_support_count",
                    "popularity_score",
                    "user_history_count",
                    "content_sources",
                    "covisitation_sources",
                    "segment"
                ]
            ].reset_index(drop=True)

        # ==================================================
        # CASE 2: Known user
        # ==================================================

        user_history = (
            user_history
            .sort_values(
                "weight",
                ascending=False
            )
        )

        # Only strongest history items are used
        # as retrieval sources.
        source_history = (
            user_history
            .head(max_history_items)
        )

        # Never recommend items already interacted with.
        seen_items = set(
            user_history[
                "itemid"
            ].astype(int)
        )

        # One dictionary shared by all retrieval sources.
        candidate_data = defaultdict(
            lambda: {
                "content_score": 0.0,
                "max_content_similarity": 0.0,
                "history_support_count": 0,

                "covisitation_score": 0.0,
                "max_covisitation_score": 0.0,
                "covisitation_support_count": 0,

                "popularity_score": 0.0,

                # Explanation provenance only.
                # These do NOT affect ranking.
                "content_sources": [],
                "covisitation_sources": []
            }
        )
        # ==================================================
        # 1. CONTENT CANDIDATE GENERATION
        # ==================================================

        for _, row in source_history.iterrows():

            source_item = int(
                row["itemid"]
            )

            source_weight = float(
                row["weight"]
            )

            neighbors = (
                self.content_model
                .get_similar_items(
                    source_item,
                    k=neighbors_per_item
                )
            )

            for _, neighbor in neighbors.iterrows():

                candidate_item = int(
                    neighbor["itemid"]
                )

                if candidate_item in seen_items:
                    continue

                similarity = float(
                    neighbor["similarity"]
                )

                weighted_content_score = (
                    source_weight
                    * similarity
                )

                candidate_data[
                    candidate_item
                ]["content_score"] += (
                    weighted_content_score
                )

                candidate_data[
                    candidate_item
                ]["max_content_similarity"] = max(
                    candidate_data[
                        candidate_item
                    ]["max_content_similarity"],
                    similarity
                )

                candidate_data[
                    candidate_item
                ]["history_support_count"] += 1

                candidate_data[
                candidate_item
            ]["content_sources"].append(
                {
                    "history_itemid": source_item,
                    "history_weight": source_weight,
                    "similarity": similarity,
                    "weighted_contribution": weighted_content_score
                }
            )

        # ==================================================
        # 2. CO-VISITATION CANDIDATE GENERATION
        # ==================================================

        if self.covisitation_model is not None:

            for _, row in source_history.iterrows():

                source_item = int(
                    row["itemid"]
                )

                source_weight = float(
                    row["weight"]
                )

                related_items = (
                    self.covisitation_model
                    .get_related_items(
                        item_id=source_item,
                        k=covisitation_neighbors_per_item
                    )
                )

                for _, neighbor in related_items.iterrows():

                    candidate_item = int(
                        neighbor["itemid"]
                    )

                    if candidate_item in seen_items:
                        continue

                    covis_score = float(
                        neighbor[
                            "covisitation_score"
                        ]
                    )

                    weighted_covis_score = (
                        source_weight
                        * covis_score
                    )

                    candidate_data[
                        candidate_item
                    ]["covisitation_score"] += (
                        weighted_covis_score
                    )

                    candidate_data[
                        candidate_item
                    ]["max_covisitation_score"] = max(
                        candidate_data[
                            candidate_item
                        ]["max_covisitation_score"],
                        covis_score
                    )

                    candidate_data[
                        candidate_item
                    ][
                        "covisitation_support_count"
                    ] += 1

                    candidate_data[
                    candidate_item
                        ]["covisitation_sources"].append(
                            {
                                "history_itemid": source_item,
                                "history_weight": source_weight,
                                "covisitation_score": covis_score,
                                "weighted_contribution": weighted_covis_score
                            }
                        )
        # ==================================================
        # 3. OPTIONAL POPULARITY CANDIDATES
        # ==================================================
        #
        # For our current experiment this will be 0.
        # We keep support here so the class remains reusable.
        # ==================================================

        if popularity_candidates > 0:

            popular_items = (
                self.popularity_model
                .weighted_popularity
                .head(popularity_candidates)
            )

            for item_id, popularity_score in (
                popular_items.items()
            ):

                item_id = int(
                    item_id
                )

                if item_id in seen_items:
                    continue

                # Creates the candidate if content /
                # co-visitation did not already create it.
                candidate_data[
                    item_id
                ]

                candidate_data[
                    item_id
                ]["popularity_score"] = float(
                    popularity_score
                )

        # ==================================================
        # 4. CONVERT CANDIDATES TO DATAFRAME
        # ==================================================

        rows = []

        weighted_popularity = (
            self.popularity_model
            .weighted_popularity
        )

        for item_id, features in (
            candidate_data.items()
        ):

            popularity_score = float(
                weighted_popularity.get(
                    item_id,
                    features[
                        "popularity_score"
                    ]
                )
            )

            rows.append({
                "itemid":
                    int(item_id),

                "content_score":
                    features[
                        "content_score"
                    ],

                "max_content_similarity":
                    features[
                        "max_content_similarity"
                    ],

                "history_support_count":
                    features[
                        "history_support_count"
                    ],

                "covisitation_score":
                    features[
                        "covisitation_score"
                    ],

                "max_covisitation_score":
                    features[
                        "max_covisitation_score"
                    ],

                "covisitation_support_count":
                    features[
                        "covisitation_support_count"
                    ],

                "content_sources":
                features[
                    "content_sources"
                ],

                "covisitation_sources":
                    features[
                        "covisitation_sources"
                    ],
                "popularity_score":
                    popularity_score,

                "user_history_count":
                    history_count,

                "segment":
                    segment
            })

        candidates = pd.DataFrame(
            rows
        )

        # ==================================================
        # 5. FALLBACK IF NO PERSONALIZED CANDIDATES EXIST
        # ==================================================

        if candidates.empty:

            popular = (
                self.popularity_model
                .recommend(k=n_candidates)
                .copy()
            )

            popular = popular.rename(
                columns={
                    "score": "popularity_score"
                }
            )

            popular["content_score"] = 0.0
            popular["max_content_similarity"] = 0.0
            popular["history_support_count"] = 0

            popular["covisitation_score"] = 0.0
            popular["max_covisitation_score"] = 0.0
            popular["covisitation_support_count"] = 0

            popular["content_sources"] = [
            [] for _ in range(len(popular))
        ]

            popular["covisitation_sources"] = [
                [] for _ in range(len(popular))
            ]

            popular["user_history_count"] = (
                            history_count
                        )

            # Preserve the real user's segment.
            popular["segment"] = segment

            return popular[
                [
                    "itemid",
                    "content_score",
                    "max_content_similarity",
                    "history_support_count",
                    "covisitation_score",
                    "max_covisitation_score",
                    "covisitation_support_count",
                    "popularity_score",
                    "user_history_count",
                    "segment"
                ]
            ].reset_index(drop=True)

        # ==================================================
        # 6. NORMALIZE RETRIEVAL SIGNALS
        # ==================================================
        #
        # These normalized values are ONLY used to fill
        # the candidate pool.
        #
        # They are NOT the final recommendation score.
        # ==================================================

        max_content_score = (
            candidates[
                "content_score"
            ].max()
        )

        max_covis_score = (
            candidates[
                "covisitation_score"
            ].max()
        )

        if max_content_score > 0:

            candidates[
                "_content_retrieval"
            ] = (
                candidates[
                    "content_score"
                ]
                / max_content_score
            )

        else:

            candidates[
                "_content_retrieval"
            ] = 0.0

        if max_covis_score > 0:

            candidates[
                "_covis_retrieval"
            ] = (
                candidates[
                    "covisitation_score"
                ]
                / max_covis_score
            )

        else:

            candidates[
                "_covis_retrieval"
            ] = 0.0

        # ==================================================
        # 7. SELECT A DIVERSE CANDIDATE POOL
        # ==================================================
        #
        # Current experiment:
        #
        # ~50% content retrieval
        # ~50% behavioral co-visitation retrieval
        #
        # The reranker will later learn the final ordering.
        # ==================================================

        content_slots = (
            n_candidates // 2
        )

        covisitation_slots = (
            n_candidates
            - content_slots
        )

        top_content = (
            candidates[
                candidates[
                    "content_score"
                ] > 0
            ]
            .sort_values(
                "content_score",
                ascending=False
            )
            .head(content_slots)
        )

        top_covisitation = (
            candidates[
                candidates[
                    "covisitation_score"
                ] > 0
            ]
            .sort_values(
                "covisitation_score",
                ascending=False
            )
            .head(covisitation_slots)
        )

        selected = pd.concat(
            [
                top_content,
                top_covisitation
            ],
            ignore_index=True
        )

        # Same item may have been retrieved by both systems.
        selected = (
            selected
            .drop_duplicates(
                subset=["itemid"]
            )
        )

        # ==================================================
        # 8. REFILL EMPTY SLOTS
        # ==================================================
        #
        # Overlap between retrieval systems or lack of
        # co-visitation neighbors may leave < n_candidates.
        # ==================================================

        if len(selected) < n_candidates:

            already_selected = set(
                selected[
                    "itemid"
                ].astype(int)
            )

            remaining = candidates[
                ~candidates[
                    "itemid"
                ].isin(
                    already_selected
                )
            ].copy()

            remaining[
                "_fallback_retrieval_score"
            ] = (
                remaining[
                    "_content_retrieval"
                ]
                +
                remaining[
                    "_covis_retrieval"
                ]
            )

            remaining = (
                remaining
                .sort_values(
                    "_fallback_retrieval_score",
                    ascending=False
                )
                .head(
                    n_candidates
                    - len(selected)
                )
            )

            selected = pd.concat(
                [
                    selected,
                    remaining
                ],
                ignore_index=True
            )

        # ==================================================
        # 9. FINAL CLEAN CANDIDATE DATAFRAME
        # ==================================================

        candidates = (
            selected
            .drop_duplicates(
                subset=["itemid"]
            )
            .head(n_candidates)
            .drop(
                columns=[
                    "_content_retrieval",
                    "_covis_retrieval",
                    "_fallback_retrieval_score"
                ],
                errors="ignore"
            )
            .reset_index(drop=True)
        )

        return candidates