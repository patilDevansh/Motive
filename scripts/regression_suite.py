from dataclasses import dataclass
from typing import Callable, Optional

import pandas as pd

from src.recommender import Recommender
from src.intent import UserIntent
from src.explanations import GroundedExplanationGenerator


# ==========================================================
# CONFIGURATION
# ==========================================================

NEW_USER_ID = 999999999
LOW_HISTORY_USER_ID = 1
ESTABLISHED_USER_ID = 1150086

DEFAULT_K = 5


# ==========================================================
# RESULT OBJECT
# ==========================================================

@dataclass
class CheckResult:
    scenario: str
    check: str
    passed: bool
    detail: str = ""


# ==========================================================
# HELPERS
# ==========================================================

def make_intent(
    exploration=None,
    popularity=None,
    brand=None,
    min_price=None,
    max_price=None,
    use_case=None,
    priority_features=None,
    avoid_features=None,
):
    supported = []
    unverifiable = []

    if exploration in {
        "familiar",
        "exploratory",
    }:
        supported.append(
            "exploration_preference"
        )

    if popularity in {
        "popular",
        "niche",
    }:
        supported.append(
            "popularity_preference"
        )

    if brand is not None:
        unverifiable.append(
            "requested_brand"
        )

    if min_price is not None:
        unverifiable.append(
            "min_price"
        )

    if max_price is not None:
        unverifiable.append(
            "max_price"
        )

    if use_case is not None:
        unverifiable.append(
            "use_case"
        )

    if priority_features:
        unverifiable.append(
            "priority_features"
        )

    if avoid_features:
        unverifiable.append(
            "avoid_features"
        )

    return UserIntent(
        exploration_preference=exploration,
        popularity_preference=popularity,
        requested_brand=brand,
        min_price=min_price,
        max_price=max_price,
        use_case=use_case,
        priority_features=(
            priority_features or []
        ),
        avoid_features=(
            avoid_features or []
        ),
        supported_preferences=supported,
        unverifiable_constraints=unverifiable,
    )


def add_check(
    results,
    scenario,
    check,
    condition,
    detail=""
):
    results.append(
        CheckResult(
            scenario=scenario,
            check=check,
            passed=bool(condition),
            detail=detail,
        )
    )


def get_ids(result):
    recommendations = result[
        "recommendations"
    ]

    return recommendations[
        "itemid"
    ].astype(int).tolist()


def evidence_by_item(result):
    return {
        int(item["itemid"]): item
        for item in result[
            "evidence"
        ]
    }


def has_reason(
    evidence,
    reason_type
):
    return any(
        reason.get("type")
        == reason_type
        for reason in evidence.get(
            "reasons",
            []
        )
    )


def run_safely(
    scenario_name,
    fn: Callable,
    results
):
    try:
        return fn()

    except Exception as exc:
        add_check(
            results,
            scenario_name,
            "Scenario executes",
            False,
            f"{type(exc).__name__}: {exc}",
        )

        return None


# ==========================================================
# GENERAL RESULT VALIDATION
# ==========================================================

def validate_common_result(
    scenario,
    result,
    expected_segment,
    expected_k,
    results
):
    if result is None:
        return

    add_check(
        results,
        scenario,
        "Correct segment",
        result.get("segment")
        == expected_segment,
        (
            f"expected={expected_segment}, "
            f"actual={result.get('segment')}"
        ),
    )

    recommendations = result.get(
        "recommendations"
    )

    evidence = result.get(
        "evidence"
    )

    add_check(
        results,
        scenario,
        "Recommendations are DataFrame",
        isinstance(
            recommendations,
            pd.DataFrame
        ),
        type(recommendations).__name__,
    )

    if not isinstance(
        recommendations,
        pd.DataFrame
    ):
        return

    add_check(
        results,
        scenario,
        "Correct recommendation count",
        len(recommendations)
        == expected_k,
        (
            f"expected={expected_k}, "
            f"actual={len(recommendations)}"
        ),
    )

    ids = recommendations[
        "itemid"
    ].astype(int).tolist()

    add_check(
        results,
        scenario,
        "No duplicate items",
        len(ids)
        == len(set(ids)),
        str(ids),
    )

    add_check(
        results,
        scenario,
        "Evidence count matches recommendations",
        len(evidence)
        == len(recommendations),
        (
            f"recommendations={len(recommendations)}, "
            f"evidence={len(evidence)}"
        ),
    )

    recommendation_ids = set(ids)

    evidence_ids = {
        int(item["itemid"])
        for item in evidence
    }

    add_check(
        results,
        scenario,
        "Evidence IDs match recommendations",
        recommendation_ids
        == evidence_ids,
        (
            f"recommendations={sorted(recommendation_ids)}, "
            f"evidence={sorted(evidence_ids)}"
        ),
    )

    scores = recommendations[
        "score"
    ].astype(float).tolist()

    add_check(
        results,
        scenario,
        "Scores sorted descending",
        scores
        == sorted(
            scores,
            reverse=True
        ),
        str(scores),
    )


# ==========================================================
# SCENARIO TESTS
# ==========================================================

def test_new_user(
    recommender,
    generator,
    results
):
    scenario = "Cold start / popular"

    intent = make_intent(
        popularity="popular"
    )

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=NEW_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "new_user",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    for item in result["evidence"]:

        add_check(
            results,
            scenario,
            f"{item['itemid']} cold-start reason",
            has_reason(
                item,
                "cold_start_popularity"
            ),
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} has no fake content provenance",
            item.get(
                "content_sources",
                []
            ) == [],
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} has no fake session provenance",
            item.get(
                "covisitation_sources",
                []
            ) == [],
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} intent did not claim ranking use",
            item.get(
                "intent_used",
                []
            ) == [],
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} no artificial rank movement",
            (
                item.get("base_rank")
                is None
                and
                item.get("final_rank")
                is None
            ),
        )

    explanations = generator.generate(
        result["evidence"],
        intent=intent,
    )

    for item in explanations:

        text = item[
            "explanation"
        ].lower()

        add_check(
            results,
            scenario,
            f"{item['itemid']} explanation identifies cold start",
            (
                "no interaction history"
                in text
                or
                "weighted catalog popularity"
                in text
            ),
            text,
        )


def test_low_history_no_intent(
    recommender,
    generator,
    results
):
    scenario = "Low history / no intent"

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=LOW_HISTORY_USER_ID,
                k=DEFAULT_K,
                intent=None,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "low_history",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    for item in result["evidence"]:

        add_check(
            results,
            scenario,
            f"{item['itemid']} no intent recorded",
            item.get(
                "intent_used",
                []
            ) == [],
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} base and final rank unchanged",
            item.get(
                "base_rank"
            )
            == item.get(
                "final_rank"
            ),
            (
                f"{item.get('base_rank')} "
                f"→ {item.get('final_rank')}"
            ),
        )

        if (
            item.get(
                "content_sources"
            )
        ):
            strongest = item[
                "content_sources"
            ][0]

            add_check(
                results,
                scenario,
                f"{item['itemid']} valid content provenance",
                (
                    strongest.get(
                        "history_itemid"
                    )
                    is not None
                    and
                    strongest.get(
                        "similarity",
                        0
                    ) > 0
                ),
                str(strongest),
            )


def test_low_history_familiar_popular(
    recommender,
    generator,
    results
):
    scenario = "Low history / familiar + popular"

    intent = make_intent(
        exploration="familiar",
        popularity="popular",
    )

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=LOW_HISTORY_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "low_history",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    moved = 0

    for item in result["evidence"]:

        used = set(
            item.get(
                "intent_used",
                []
            )
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} records both supported intents",
            used
            == {
                "exploration_preference",
                "popularity_preference",
            },
            str(used),
        )

        base_rank = item.get(
            "base_rank"
        )

        final_rank = item.get(
            "final_rank"
        )

        if (
            base_rank is not None
            and
            final_rank is not None
            and
            base_rank != final_rank
        ):
            moved += 1

        # Intent is a nudge. Catch the original bug where
        # deep items jumped from ~#40-50 directly to the top.
        if (
            base_rank is not None
            and
            final_rank is not None
        ):
            jump = abs(
                int(base_rank)
                - int(final_rank)
            )

            add_check(
                results,
                scenario,
                f"{item['itemid']} intent movement is bounded",
                jump <= 10,
                (
                    f"{base_rank} "
                    f"→ {final_rank}"
                ),
            )

        add_check(
            results,
            scenario,
            f"{item['itemid']} has base score",
            item.get(
                "base_score"
            )
            is not None,
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} has final score",
            item.get(
                "final_score"
            )
            is not None,
        )

    add_check(
        results,
        scenario,
        "Intent produces observable but limited movement",
        moved >= 1,
        f"{moved}/{len(result['evidence'])} returned items moved",
    )

    explanations = generator.generate(
        result["evidence"],
        intent=intent,
    )

    joined = " ".join(
        item["explanation"]
        for item in explanations
    )

    add_check(
        results,
        scenario,
        "Explanation mentions exact history item",
        "item 72028"
        in joined,
        joined,
    )

    add_check(
        results,
        scenario,
        "Explanation reports rank effect",
        (
            "remained ranked"
            in joined
            or
            "moved from #"
            in joined
        ),
        joined,
    )


def test_low_history_exploratory_niche(
    recommender,
    results
):
    scenario = "Low history / exploratory + niche"

    intent = make_intent(
        exploration="exploratory",
        popularity="niche",
    )

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=LOW_HISTORY_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "low_history",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    for item in result["evidence"]:

        add_check(
            results,
            scenario,
            f"{item['itemid']} exploratory+niche applied",
            set(
                item.get(
                    "intent_used",
                    []
                )
            )
            == {
                "exploration_preference",
                "popularity_preference",
            },
        )


def test_established_user(
    recommender,
    results
):
    scenario = "Established / exploratory + niche"

    intent = make_intent(
        exploration="exploratory",
        popularity="niche",
    )

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=ESTABLISHED_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "established",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    add_check(
        results,
        scenario,
        "At least one recommendation has provenance",
        any(
            item.get(
                "content_sources"
            )
            or item.get(
                "covisitation_sources"
            )
            for item in result[
                "evidence"
            ]
        ),
    )


def test_unsupported_constraints(
    recommender,
    generator,
    results
):
    scenario = "Unsupported brand + price + use case"

    intent = make_intent(
        brand="Sony",
        max_price=300,
        use_case="travel",
    )

    result = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=ESTABLISHED_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    validate_common_result(
        scenario,
        result,
        "established",
        DEFAULT_K,
        results,
    )

    if result is None:
        return

    expected = {
        "requested_brand",
        "max_price",
        "use_case",
    }

    for item in result[
        "evidence"
    ]:

        actual = set(
            item.get(
                "unverifiable_constraints",
                []
            )
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} unsupported constraints preserved",
            expected.issubset(
                actual
            ),
            str(actual),
        )

        add_check(
            results,
            scenario,
            f"{item['itemid']} unsupported constraints did not steer ranking",
            item.get(
                "intent_used",
                []
            )
            == [],
            str(
                item.get(
                    "intent_used",
                    []
                )
            ),
        )

    explanations = generator.generate(
        result["evidence"],
        intent=intent,
    )

    for item in explanations:

        text = item[
            "explanation"
        ].lower()

        add_check(
            results,
            scenario,
            f"{item['itemid']} explanation says constraints cannot be verified",
            (
                "does not contain reliable information"
                in text
                or
                "cannot verify"
                in text
            ),
            text,
        )

        # Do not assert "Sony" because the explanation
        # intentionally describes the constraint family,
        # not an unverified product fact.
        add_check(
            results,
            scenario,
            f"{item['itemid']} does not claim verified Sony product",
            "is sony"
            not in text,
            text,
        )


def test_result_counts(
    recommender,
    results
):
    for k in [
        1,
        3,
        10,
    ]:
        scenario = f"Result count k={k}"

        result = run_safely(
            scenario,
            lambda k=k:
                recommender
                .recommend_with_evidence(
                    user_id=LOW_HISTORY_USER_ID,
                    k=k,
                    intent=None,
                ),
            results,
        )

        validate_common_result(
            scenario,
            result,
            "low_history",
            k,
            results,
        )


def test_determinism(
    recommender,
    results
):
    scenario = "Deterministic ranking"

    intent = make_intent(
        exploration="familiar",
        popularity="popular",
    )

    first = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=LOW_HISTORY_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    second = run_safely(
        scenario,
        lambda:
            recommender
            .recommend_with_evidence(
                user_id=LOW_HISTORY_USER_ID,
                k=DEFAULT_K,
                intent=intent,
            ),
        results,
    )

    if (
        first is None
        or second is None
    ):
        return

    first_ids = get_ids(
        first
    )

    second_ids = get_ids(
        second
    )

    add_check(
        results,
        scenario,
        "Repeated calls return same item order",
        first_ids
        == second_ids,
        (
            f"first={first_ids}, "
            f"second={second_ids}"
        ),
    )


# ==========================================================
# REPORTING
# ==========================================================

def print_report(
    results
):
    print()
    print(
        "=" * 78
    )
    print(
        "MOTIVE REGRESSION REPORT"
    )
    print(
        "=" * 78
    )

    scenarios = []

    for result in results:
        if (
            result.scenario
            not in scenarios
        ):
            scenarios.append(
                result.scenario
            )

    for scenario in scenarios:

        scenario_results = [
            result
            for result in results
            if result.scenario
            == scenario
        ]

        passed = sum(
            result.passed
            for result
            in scenario_results
        )

        total = len(
            scenario_results
        )

        status = (
            "PASS"
            if passed == total
            else "FAIL"
        )

        print()
        print(
            f"[{status}] {scenario} "
            f"({passed}/{total})"
        )

        for result in scenario_results:

            icon = (
                "✓"
                if result.passed
                else "✗"
            )

            print(
                f"  {icon} "
                f"{result.check}"
            )

            if (
                not result.passed
                and result.detail
            ):
                print(
                    "      "
                    + result.detail
                )

    total_checks = len(
        results
    )

    passed_checks = sum(
        result.passed
        for result
        in results
    )

    failed_checks = (
        total_checks
        - passed_checks
    )

    print()
    print(
        "=" * 78
    )

    print(
        f"Checks: {passed_checks}/"
        f"{total_checks} passed"
    )

    if failed_checks == 0:
        print(
            "RESULT: FULL REGRESSION PASS"
        )
    else:
        print(
            f"RESULT: {failed_checks} "
            "REGRESSION CHECK(S) FAILED"
        )

    print(
        "=" * 78
    )

    return (
        failed_checks == 0
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print(
        "Loading Motive..."
    )

    recommender = (
        Recommender()
    )

    generator = (
        GroundedExplanationGenerator()
    )

    results = []

    test_new_user(
        recommender,
        generator,
        results,
    )

    test_low_history_no_intent(
        recommender,
        generator,
        results,
    )

    test_low_history_familiar_popular(
        recommender,
        generator,
        results,
    )

    test_low_history_exploratory_niche(
        recommender,
        results,
    )

    test_established_user(
        recommender,
        results,
    )

    test_unsupported_constraints(
        recommender,
        generator,
        results,
    )

    test_result_counts(
        recommender,
        results,
    )

    test_determinism(
        recommender,
        results,
    )

    success = print_report(
        results
    )

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()