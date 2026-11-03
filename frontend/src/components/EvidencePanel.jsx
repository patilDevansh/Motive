import { reasonInfo, INTENT_FIELDS } from "../lib/labels.js";


function formatNumber(value, digits = 2) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toFixed(digits);
}


function rankMovementText(baseRank, finalRank) {
  if (
    baseRank == null ||
    finalRank == null
  ) {
    return null;
  }

  const base = Number(baseRank);
  const final = Number(finalRank);

  if (base === final) {
    return `Stayed at #${final}`;
  }

  if (final < base) {
    const movement = base - final;

    return (
      `Moved #${base} → #${final} ` +
      `(${movement} ${movement === 1 ? "place" : "places"} up)`
    );
  }

  const movement = final - base;

  return (
    `Moved #${base} → #${final} ` +
    `(${movement} ${movement === 1 ? "place" : "places"} down)`
  );
}


export default function EvidencePanel({
  id,
  labelledBy,
  evidence,
  open,
}) {
  const reasons =
    evidence?.reasons || [];

  const intentUsed =
    evidence?.intent_used || [];

  const contentSources =
    evidence?.content_sources || [];

  const covisitationSources =
    evidence?.covisitation_sources || [];

  const unsupported =
    evidence?.unverifiable_constraints || [];

  const baseRank =
    evidence?.base_rank;

  const finalRank =
    evidence?.final_rank;

  const movementText =
    rankMovementText(
      baseRank,
      finalRank
    );

  const filteredReasons =
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

  const hasDetailedEvidence =
    filteredReasons.length > 0 ||
    contentSources.length > 0 ||
    covisitationSources.length > 0 ||
    intentUsed.length > 0 ||
    unsupported.length > 0;

  return (
    <div
      id={id}
      role="region"
      aria-labelledby={labelledBy}
      className={`evidence${open ? " is-open" : ""}`}
    >
      <div className="evidence-inner">
        <div className="evidence-body">

          {!hasDetailedEvidence ? (
            <p className="evidence-empty">
              No individual signals were reported for this item.
              It ranked on the model&apos;s combined score.
            </p>
          ) : (
            <ul className="evidence-rows">

              {/* ==========================================
                  EXACT CONTENT PROVENANCE
                  ========================================== */}

              {contentSources.map(
                (source, index) => (
                  <li
                    className="evidence-row"
                    key={`content-source-${source.history_itemid}-${index}`}
                  >
                    <span className="ev-name">
                      Catalog-property match
                    </span>

                    <span className="ev-desc">
                      This recommendation was retrieved from
                      history item{" "}
                      <strong>
                        {source.history_itemid}
                      </strong>
                      . Their anonymized catalog-property
                      vectors had a similarity of{" "}
                      <strong>
                        {formatNumber(
                          source.similarity
                        )}
                      </strong>
                      .
                    </span>

                    <span className="ev-raw">
                      <span className="ev-raw-label">
                        Source item
                      </span>

                      <span className="ev-raw-value">
                        {source.history_itemid}
                      </span>
                    </span>
                  </li>
                )
              )}

              {/* ==========================================
                  EXACT CO-VISITATION PROVENANCE
                  ========================================== */}

              {covisitationSources.map(
                (source, index) => (
                  <li
                    className="evidence-row"
                    key={`covis-source-${source.history_itemid}-${index}`}
                  >
                    <span className="ev-name">
                      Session relationship
                    </span>

                    <span className="ev-desc">
                      This item also has a behavioral
                      co-visitation relationship with
                      history item{" "}
                      <strong>
                        {source.history_itemid}
                      </strong>
                      .
                    </span>

                    <span className="ev-raw">
                      <span className="ev-raw-label">
                        Co-visitation
                      </span>

                      <span className="ev-raw-value">
                        {formatNumber(
                          source.covisitation_score
                        )}
                      </span>
                    </span>
                  </li>
                )
              )}

              {/* ==========================================
                  AGGREGATE SIGNALS
                  ========================================== */}

              {filteredReasons.map((reason, index) => {
                const info =
                  reasonInfo(
                    reason.type
                  );

                return (
                  <li
                    className="evidence-row"
                    key={`${reason.type}-${index}`}
                  >
                    <span className="ev-name">
                      {info.title}
                    </span>

                    <span className="ev-desc">
                      {info.describe(
                        reason.value
                      )}
                    </span>

                    <span className="ev-raw">
                      <span className="ev-raw-label">
                        {info.rawLabel}
                      </span>

                      <span className="ev-raw-value">
                        {info.rawValue(
                          reason.value
                        )}
                      </span>
                    </span>
                  </li>
                );
              })}

              {/* ==========================================
                  INTENT + EXACT RANK MOVEMENT
                  ========================================== */}

              {intentUsed.length > 0 && (
                <li className="evidence-row evidence-row--intent">
                  <span className="ev-name">
                    Your request
                  </span>

                  <span className="ev-desc">
                    The supported{" "}
                    {intentUsed
                      .map(
                        (field) =>
                          (
                            INTENT_FIELDS[
                              field
                            ]?.label ||
                            field
                          ).toLowerCase()
                      )
                      .join(" and ")}{" "}
                    direction was applied after the learned
                    ranking.

                    {movementText && (
                      <>
                        {" "}
                        <strong>
                          {movementText}.
                        </strong>
                      </>
                    )}
                  </span>

                  {baseRank != null &&
                    finalRank != null && (
                      <span className="ev-raw">
                        <span className="ev-raw-label">
                          Rank
                        </span>

                        <span className="ev-raw-value">
                          #{baseRank} → #{finalRank}
                        </span>
                      </span>
                    )}
                </li>
              )}

              {/* ==========================================
                  UNVERIFIABLE REQUESTS
                  ========================================== */}

              {unsupported.length > 0 && (
                <li className="evidence-row">
                  <span className="ev-name">
                    Not verified
                  </span>

                  <span className="ev-desc">
                    Your request also mentioned{" "}
                    {unsupported
                      .map(
                        (field) =>
                          (
                            INTENT_FIELDS[
                              field
                            ]?.label ||
                            field.replaceAll(
                              "_",
                              " "
                            )
                          ).toLowerCase()
                      )
                      .join(", ")}
                    . The anonymized catalog does not contain
                    reliable information to verify these
                    constraints.
                  </span>
                </li>
              )}
            </ul>
          )}

          <p className="evidence-footnote">
            Similarity, co-visitation, popularity and ranking
            values are internal recommendation signals. They
            are not probabilities and should not be compared
            directly across different signal types.
          </p>
        </div>
      </div>
    </div>
  );
}