class RecommendationEvidenceBuilder:

    # ======================================================
    # HELPERS
    # ======================================================

    def _content_sources(
        self,
        row,
        limit=3
    ):
        """
        Preserve the strongest content relationships that
        actually produced this candidate.

        These fields are explanation/provenance only.
        They do not affect ranking.
        """

        sources = row.get(
            "content_sources",
            []
        )

        if not isinstance(
            sources,
            list
        ):
            return []

        sources = sorted(
            sources,
            key=lambda x: x.get(
                "similarity",
                0
            ),
            reverse=True
        )

        return [
            {
                "history_itemid": int(
                    source[
                        "history_itemid"
                    ]
                ),

                "history_weight": float(
                    source.get(
                        "history_weight",
                        0
                    )
                ),

                "similarity": float(
                    source.get(
                        "similarity",
                        0
                    )
                ),

                "weighted_contribution": float(
                    source.get(
                        "weighted_contribution",
                        0
                    )
                )
            }

            for source in sources[:limit]
        ]

    def _covisitation_sources(
        self,
        row,
        limit=3
    ):
        """
        Preserve the strongest session/co-visitation
        relationships that produced this candidate.

        These fields are explanation/provenance only.
        They do not affect ranking.
        """

        sources = row.get(
            "covisitation_sources",
            []
        )

        if not isinstance(
            sources,
            list
        ):
            return []

        sources = sorted(
            sources,
            key=lambda x: x.get(
                "covisitation_score",
                0
            ),
            reverse=True
        )

        return [
            {
                "history_itemid": int(
                    source[
                        "history_itemid"
                    ]
                ),

                "history_weight": float(
                    source.get(
                        "history_weight",
                        0
                    )
                ),

                "covisitation_score": float(
                    source.get(
                        "covisitation_score",
                        0
                    )
                ),

                "weighted_contribution": float(
                    source.get(
                        "weighted_contribution",
                        0
                    )
                )
            }

            for source in sources[:limit]
        ]

    def _intent_used(
        self,
        intent
    ):
        """
        Report only intent dimensions that actually have
        a ranking direction.

        balanced / neutral do not alter ranking and
        therefore should not be presented as used.
        """

        if intent is None:
            return []

        used = []

        if (
            intent.exploration_preference
            in {
                "familiar",
                "exploratory"
            }
        ):
            used.append(
                "exploration_preference"
            )

        if (
            intent.popularity_preference
            in {
                "popular",
                "niche"
            }
        ):
            used.append(
                "popularity_preference"
            )

        return used

    # ======================================================
    # BUILD EVIDENCE
    # ======================================================

    def build(
        self,
        ranked_candidates,
        intent=None
    ):
        if ranked_candidates.empty:
            return []

        evidence = []

        for _, row in (
            ranked_candidates.iterrows()
        ):

            reasons = []

            content_sources = (
                self._content_sources(
                    row
                )
            )

            covisitation_sources = (
                self._covisitation_sources(
                    row
                )
            )

            # ==================================================
            # CONTENT EVIDENCE
            # ==================================================

            if row.get(
                "max_content_similarity",
                0
            ) > 0:

                reasons.append({
                    "type":
                        "content_similarity",

                    "value":
                        float(
                            row[
                                "max_content_similarity"
                            ]
                        )
                })

            if row.get(
                "history_support_count",
                0
            ) > 1:

                reasons.append({
                    "type":
                        "multiple_history_support",

                    "value":
                        int(
                            row[
                                "history_support_count"
                            ]
                        )
                })

            # ==================================================
            # BEHAVIORAL / CO-VISITATION EVIDENCE
            # ==================================================

            if row.get(
                "covisitation_score",
                0
            ) > 0:

                reasons.append({
                    "type":
                        "covisitation",

                    "value":
                        float(
                            row[
                                "covisitation_score"
                            ]
                        )
                })

            if row.get(
                "covisitation_support_count",
                0
            ) > 1:

                reasons.append({
                    "type":
                        "multiple_covisitation_support",

                    "value":
                        int(
                            row[
                                "covisitation_support_count"
                            ]
                        )
                })

            # ==================================================
            # POPULARITY EVIDENCE
            # ==================================================

            if row.get(
                "popularity_score",
                0
            ) > 0:

                reasons.append({
                    "type":
                        "popularity",

                    "value":
                        float(
                            row[
                                "popularity_score"
                            ]
                        )
                })

            # ==================================================
            # INTENT EVIDENCE
            # ==================================================

            intent_used = (
                self._intent_used(
                    intent
                )
            )

            # ==================================================
            # FINAL EVIDENCE OBJECT
            # ==================================================

            evidence.append({

                "itemid": int(
                    row["itemid"]
                ),

                "score": float(
                    row["score"]
                    if "score" in row
                    else row[
                        "reranker_score"
                    ]
                ),

                "reasons":
                    reasons,

                # ----------------------------------------------
                # Exact retrieval provenance
                # ----------------------------------------------

                "content_sources":
                    content_sources,

                "covisitation_sources":
                    covisitation_sources,

                # ----------------------------------------------
                # Intent
                # ----------------------------------------------

                "intent_used":
                    intent_used,

                # ----------------------------------------------
                # Ranking before / after intent
                # ----------------------------------------------

                "base_rank":
                    (
                        int(
                            row[
                                "base_rank"
                            ]
                        )
                        if "base_rank" in row
                        else None
                    ),

                "final_rank":
                    (
                        int(
                            row[
                                "final_rank"
                            ]
                        )
                        if "final_rank" in row
                        else None
                    ),

                "base_score":
                    (
                        float(
                            row[
                                "base_score"
                            ]
                        )
                        if "base_score" in row
                        else None
                    ),

                "final_score":
                    (
                        float(
                            row[
                                "final_score"
                            ]
                        )
                        if "final_score" in row
                        else None
                    ),

                "intent_adjustment":
                    float(
                        row.get(
                            "intent_adjustment",
                            0.0
                        )
                    ),

                # ----------------------------------------------
                # Constraints understood but not verifiable
                # ----------------------------------------------

                "unverifiable_constraints":
                    (
                        intent.unverifiable_constraints
                        if intent is not None
                        else []
                    )
            })

        return evidence