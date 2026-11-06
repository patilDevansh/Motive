import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from "react";

import SignalGlyph from "./SignalGlyph.jsx";
import SignalFingerprint from "./SignalFingerprint.jsx";
import EvidencePanel from "./EvidencePanel.jsx";

import {
  channelsFor,
  reasonInfo,
  sourceTags,
  itemExplanation,
} from "../lib/labels.js";

import {
  formatScore,
  rankLabel,
} from "../lib/formatting.js";


export default function RecommendationCard({
  rank,
  rec,
  evidence,
  explanation,
  maxScore,
  tiedWithRank,
  open,
  onToggle,
}) {
  const panelId = useId();
  const toggleId = useId();
  const whyId = useId();

  const cardRef = useRef(null);
  const whyRef = useRef(null);

  const [whyOpen, setWhyOpen] =
    useState(false);

  const [overflows, setOverflows] =
    useState(false);

  const score = Number(
    rec.score ??
    evidence?.score ??
    0
  );

  const width =
    maxScore > 0
      ? Math.max(
          3,
          (score / maxScore) * 100
        )
      : 0;

  const reasons =
    evidence?.reasons || [];

  const intentUsed =
    evidence?.intent_used || [];

  const contentSources =
    evidence?.content_sources || [];

  const covisitationSources =
    evidence?.covisitation_sources || [];

  const steered =
    intentUsed.length > 0;

  const text =
    itemExplanation(
      explanation
    );

  const baseRank =
    evidence?.base_rank;

  const finalRank =
    evidence?.final_rank;

  const rankChanged =
    steered &&
    baseRank != null &&
    finalRank != null &&
    Number(baseRank) !== Number(finalRank);

  const strongestContentSource =
    contentSources.length > 0
      ? contentSources[0]
      : null;

  /*
   * Remove generic pills when the UI already has
   * more precise provenance for the same signal.
   */
  const visibleReasons =
    reasons.filter((reason) => {
      if (
        reason.type === "content_similarity" &&
        contentSources.length > 0
      ) {
        return false;
      }

      if (
        reason.type === "covisitation" &&
        covisitationSources.length > 0
      ) {
        return false;
      }

      return true;
    });

  /*
   * Count signal families rather than every raw row.
   *
   * Content provenance counts as one.
   * Session provenance counts as one.
   * Remaining aggregate signals count individually.
   * Intent counts as one.
   */
  const signalCount =
    (contentSources.length > 0 ? 1 : 0) +
    (covisitationSources.length > 0 ? 1 : 0) +
    visibleReasons.length +
    (steered ? 1 : 0);

  /*
   * Offer "Read full reasoning" only when the clamp
   * actually hides part of the explanation.
   */
  useLayoutEffect(() => {
    const el =
      whyRef.current;

    if (!el) {
      return undefined;
    }

    const measure = () => {
      if (!whyOpen) {
        setOverflows(
          el.scrollHeight -
            el.clientHeight >
            2
        );
      }
    };

    measure();

    const ro =
      typeof ResizeObserver !== "undefined"
        ? new ResizeObserver(
            measure
          )
        : null;

    ro?.observe(el);

    return () =>
      ro?.disconnect();
  }, [
    text,
    whyOpen,
  ]);

  /*
   * Keep the active card in view when its evidence
   * drawer opens.
   */
  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const id =
      setTimeout(
        () =>
          cardRef.current
            ?.scrollIntoView({
              block: "nearest",
              behavior: "smooth",
            }),
        260
      );

    return () =>
      clearTimeout(id);
  }, [open]);

  return (
    <li
      ref={cardRef}
      className={
        `rec${open ? " is-open" : ""}` +
        `${rank === 1 ? " is-top" : ""}`
      }
      style={{
        "--i": rank - 1,
      }}
    >
      <div
        className="rec-rank"
        aria-hidden="true"
      >
        {rankLabel(rank)}
      </div>

      <div className="rec-main">

        {/* ===============================================
            ITEM HEADER
            =============================================== */}

        <div className="rec-head">

          <SignalFingerprint
            itemId={rec.itemid}
          />

          <div className="rec-id-block">

            <h3 className="rec-item">
              <span className="visually-hidden">
                Rank {rank}:{" "}
              </span>

              <span className="rec-item-label">
                Item
              </span>

              <span className="rec-item-id">
                {rec.itemid}
              </span>
            </h3>

            <p className="rec-mode">
              <span className="visually-hidden">
                Ranking mode:{" "}
              </span>

              {sourceTags(
                rec.source,
                intentUsed
              ).join(" · ")}
            </p>
          </div>
        </div>

        {/* ===============================================
            SHORT USER-FACING EXPLANATION
            =============================================== */}

        {text && (
          <div className="rec-why">

            <span className="mini-label">
              Why it surfaced
            </span>

            <p
              id={whyId}
              ref={whyRef}
              className={
                `rec-why-text${
                  whyOpen
                    ? " is-open"
                    : ""
                }`
              }
            >
              {text}
            </p>

            {(overflows || whyOpen) && (
              <button
                type="button"
                className="link-btn"
                aria-expanded={whyOpen}
                aria-controls={whyId}
                onClick={() =>
                  setWhyOpen(
                    (value) =>
                      !value
                  )
                }
              >
                {whyOpen
                  ? "Show less"
                  : "Read full reasoning"}
              </button>
            )}
          </div>
        )}

        {/* ===============================================
            COMPACT SIGNAL PILLS
            =============================================== */}

        {signalCount > 0 && (
          <ul
            className="pills"
            aria-label="Signals"
          >
            {strongestContentSource && (
              <li className="pill">
                Matched from item{" "}
                {
                  strongestContentSource
                    .history_itemid
                }
              </li>
            )}

            {covisitationSources.length > 0 && (
              <li className="pill">
                Session supported
              </li>
            )}

            {visibleReasons.map(
              (
                reason,
                index
              ) => (
                <li
                  key={`${reason.type}-${index}`}
                  className="pill"
                >
                  {
                    reasonInfo(
                      reason.type
                    ).short
                  }
                </li>
              )
            )}

            {steered && (
              <li className="pill pill--intent">
                Intent adjusted
              </li>
            )}

            {rankChanged && (
              <li className="pill pill--intent">
                #{baseRank} → #{finalRank}
              </li>
            )}
          </ul>
        )}
      </div>

      {/* =================================================
          SCORE
          ================================================= */}

      <div className="rec-side">

        <div className="score">

          <span className="mini-label">
            {steered
              ? "Blended ranking score"
              : "Ranking score"}
          </span>

          <span className="score-value">
            {formatScore(
              score
            )}
          </span>

          <div
            className="score-track"
            aria-hidden="true"
          >
            <div
              className="score-fill"
              style={{
                width:
                  `${width}%`,
              }}
            />
          </div>

          <span className="score-note">
            {tiedWithRank
              ? `Tied with #${rankLabel(
                  tiedWithRank
                )}`
              : "Relative to the top result"}
          </span>
        </div>

        <SignalGlyph
          channels={
            channelsFor(
              evidence
            )
          }
        />
      </div>

      {/* =================================================
          EVIDENCE DRAWER
          ================================================= */}

      <div className="rec-drawer">

        <button
          id={toggleId}
          type="button"
          className="evidence-toggle"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={onToggle}
        >
          <span>
            {open
              ? "Hide evidence"
              : "Inspect evidence"}
          </span>

          <span className="ev-count">
            {signalCount}{" "}
            {signalCount === 1
              ? "signal type"
              : "signal types"}
          </span>

          <svg
            viewBox="0 0 12 12"
            aria-hidden="true"
            className="chev"
          >
            <path d="M3 4.5 6 7.5 9 4.5" />
          </svg>
        </button>

        <EvidencePanel
          id={panelId}
          labelledBy={toggleId}
          evidence={evidence}
          open={open}
        />
      </div>
    </li>
  );
}