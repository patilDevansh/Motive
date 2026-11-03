CONSTRAINT_LABELS = {
    "requested_brand": "brand",
    "min_price": "minimum price",
    "max_price": "price limit",
    "use_case": "intended use",
    "priority_features": "requested features",
    "avoid_features": "features to avoid",
}


class ExplanationGenerator:
    def generate(
        self,
        recommendation_evidence,
        intent=None
    ):
        raise NotImplementedError(
            "Explanation backend not configured yet."
        )


class GroundedExplanationGenerator:

    # ======================================================
    # CONSTRAINT HELPERS
    # ======================================================

    def _humanize_constraints(
        self,
        constraints
    ):
        return [
            CONSTRAINT_LABELS.get(
                constraint,
                constraint
            )
            for constraint in constraints
        ]

    # ======================================================
    # CONTENT PROVENANCE
    # ======================================================

    def _content_explanation(
        self,
        item
    ):
        sources = item.get(
            "content_sources",
            []
        )

        if not sources:
            return None

        strongest = sources[0]

        source_item = strongest[
            "history_itemid"
        ]

        similarity = strongest[
            "similarity"
        ]

        text = (
            f"Item {item['itemid']} is most similar "
            f"to item {source_item} from your history "
            f"with a catalog-property similarity "
            f"of {similarity:.2f}"
        )

        if len(sources) > 1:

            other_items = [
                str(
                    source[
                        "history_itemid"
                    ]
                )
                for source
                in sources[1:]
            ]

            text += (
                ". Additional history items "
                + ", ".join(other_items)
                + " also contributed content evidence"
            )

        return text

    # ======================================================
    # CO-VISITATION PROVENANCE
    # ======================================================

    def _covisitation_explanation(
        self,
        item
    ):
        sources = item.get(
            "covisitation_sources",
            []
        )

        if not sources:
            return None

        strongest = sources[0]

        source_item = strongest[
            "history_itemid"
        ]

        score = strongest[
            "covisitation_score"
        ]

        text = (
            f"Item {item['itemid']} also has a "
            f"session-based relationship with "
            f"item {source_item} from your history "
            f"with a co-visitation score of "
            f"{score:.2f}"
        )

        if len(sources) > 1:

            other_items = [
                str(
                    source[
                        "history_itemid"
                    ]
                )
                for source
                in sources[1:]
            ]

            text += (
                ". Session relationships with "
                + ", ".join(other_items)
                + " provided additional support"
            )

        return text

    # ======================================================
    # POPULARITY
    # ======================================================

    def _popularity_explanation(
        self,
        item
    ):
        reasons = item.get(
            "reasons",
            []
        )

        for reason in reasons:

            if (
                reason.get("type")
                == "popularity"
            ):

                return (
                    "Its catalog popularity signal "
                    f"was {reason['value']:.0f}"
                )

            if (
                reason.get("type")
                == "cold_start_popularity"
            ):

                return (
                    "Because no interaction history "
                    "was available, it was surfaced "
                    "using weighted catalog popularity "
                    f"with a score of "
                    f"{reason['value']:.0f}"
                )

        return None

    # ======================================================
    # MULTIPLE SUPPORT SIGNALS
    # ======================================================

    def _support_explanation(
        self,
        item
    ):
        reasons = item.get(
            "reasons",
            []
        )

        parts = []

        for reason in reasons:

            if (
                reason.get("type")
                == "multiple_history_support"
            ):

                count = int(
                    reason[
                        "value"
                    ]
                )

                parts.append(
                    f"{count} history items "
                    "supported the content match"
                )

            if (
                reason.get("type")
                == "multiple_covisitation_support"
            ):

                count = int(
                    reason[
                        "value"
                    ]
                )

                parts.append(
                    f"{count} history items "
                    "supported session-based evidence"
                )

        if not parts:
            return None

        return "; ".join(
            parts
        )

    # ======================================================
    # LEGACY / MINIMAL EVIDENCE FALLBACK
    # ======================================================

    def _fallback_reason_explanations(
        self,
        item
    ):
        """
        Backward-compatible fallback for evidence objects
        that contain reason types but do not contain exact
        source provenance.
        """

        reason_types = {
            reason.get("type")
            for reason in item.get(
                "reasons",
                []
            )
        }

        parts = []

        if (
            "content_similarity"
            in reason_types
        ):

            parts.append(
                "It is similar to products "
                "from your interaction history"
            )

        if (
            "covisitation"
            in reason_types
        ):

            parts.append(
                "It has a behavioral relationship "
                "with products users interacted "
                "with in similar sessions"
            )

        return parts

    # ======================================================
    # INTENT DESCRIPTION
    # ======================================================

    def _intent_explanation(
        self,
        item,
        intent
    ):
        if intent is None:
            return None

        intent_used = item.get(
            "intent_used",
            []
        )

        parts = []

        if (
            "exploration_preference"
            in intent_used
        ):

            if (
                intent.exploration_preference
                == "exploratory"
            ):

                parts.append(
                    "your exploratory preference "
                    "favored less familiar items"
                )

            elif (
                intent.exploration_preference
                == "familiar"
            ):

                parts.append(
                    "your familiar preference "
                    "favored items closer to "
                    "your previous interactions"
                )

        if (
            "popularity_preference"
            in intent_used
        ):

            if (
                intent.popularity_preference
                == "niche"
            ):

                parts.append(
                    "your niche preference favored "
                    "less mainstream choices"
                )

            elif (
                intent.popularity_preference
                == "popular"
            ):

                parts.append(
                    "your popular preference favored "
                    "more widely interacted-with items"
                )

        if not parts:
            return None

        return (
            "Your request also influenced the "
            "ranking: "
            + "; ".join(parts)
        )

    # ======================================================
    # RANK MOVEMENT
    # ======================================================

    def _rank_movement_explanation(
        self,
        item
    ):
        """
        Explain exactly how intent changed the item's rank.

        This uses recorded base_rank and final_rank only.
        It does not infer movement when those values
        are unavailable.
        """

        base_rank = item.get(
            "base_rank"
        )

        final_rank = item.get(
            "final_rank"
        )

        intent_used = item.get(
            "intent_used",
            []
        )

        # Cold-start / older evidence may not contain ranks.
        if (
            base_rank is None
            or final_rank is None
        ):
            return None

        # Do not attribute movement to intent if no supported
        # intent dimension was actually used.
        if not intent_used:
            return None

        base_rank = int(
            base_rank
        )

        final_rank = int(
            final_rank
        )

        # --------------------------------------------------
        # Rank unchanged
        # --------------------------------------------------

        if base_rank == final_rank:

            return (
                f"It remained ranked #{final_rank} "
                "after the intent adjustment"
            )

        # --------------------------------------------------
        # Item moved upward
        # --------------------------------------------------

        if final_rank < base_rank:

            positions = (
                base_rank
                - final_rank
            )

            position_word = (
                "position"
                if positions == 1
                else "positions"
            )

            return (
                f"It moved from #{base_rank} "
                f"to #{final_rank} after the intent "
                f"adjustment, moving up "
                f"{positions} {position_word}"
            )

        # --------------------------------------------------
        # Item moved downward
        # --------------------------------------------------

        positions = (
            final_rank
            - base_rank
        )

        position_word = (
            "position"
            if positions == 1
            else "positions"
        )

        return (
            f"It moved from #{base_rank} "
            f"to #{final_rank} after the intent "
            f"adjustment, moving down "
            f"{positions} {position_word}"
        )

    # ======================================================
    # MAIN GENERATOR
    # ======================================================

    def generate(
        self,
        recommendation_evidence,
        intent=None
    ):
        explanations = []

        for item in recommendation_evidence:

            parts = []

            # --------------------------------------------------
            # Exact recommendation evidence
            # --------------------------------------------------

            content_text = (
                self._content_explanation(
                    item
                )
            )

            if content_text:
                parts.append(
                    content_text
                )

            covis_text = (
                self._covisitation_explanation(
                    item
                )
            )

            if covis_text:
                parts.append(
                    covis_text
                )

            support_text = (
                self._support_explanation(
                    item
                )
            )

            if support_text:
                parts.append(
                    support_text
                )

            popularity_text = (
                self._popularity_explanation(
                    item
                )
            )

            if popularity_text:
                parts.append(
                    popularity_text
                )

            # --------------------------------------------------
            # Fallback for older / minimal evidence
            # --------------------------------------------------

            if not parts:

                parts.extend(
                    self._fallback_reason_explanations(
                        item
                    )
                )

            if not parts:

                parts.append(
                    "This item ranked highly using "
                    "the available recommendation signals"
                )

            explanation = (
                ". ".join(
                    parts
                )
                + "."
            )

            # --------------------------------------------------
            # Intent meaning
            # --------------------------------------------------

            intent_text = (
                self._intent_explanation(
                    item,
                    intent
                )
            )

            if intent_text:

                explanation += (
                    " "
                    + intent_text
                    + "."
                )

            # --------------------------------------------------
            # Exact rank movement
            # --------------------------------------------------

            rank_text = (
                self._rank_movement_explanation(
                    item
                )
            )

            if rank_text:

                explanation += (
                    " "
                    + rank_text
                    + "."
                )

            # --------------------------------------------------
            # Unsupported constraints
            # --------------------------------------------------

            unsupported = item.get(
                "unverifiable_constraints",
                []
            )

            if unsupported:

                labels = (
                    self._humanize_constraints(
                        unsupported
                    )
                )

                explanation += (
                    " I understood your requested "
                    + ", ".join(labels)
                    + ", but this catalog does not "
                    "contain reliable information "
                    "to verify those constraints."
                )

            explanations.append({
                "itemid":
                    item[
                        "itemid"
                    ],

                "explanation":
                    explanation
            })

        return explanations