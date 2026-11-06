import { INTENT_FIELDS, intentChip, segmentInfo, unverifiedFrom } from "../lib/labels.js";
import UnsupportedConstraints from "./UnsupportedConstraints.jsx";

export default function IntentSummary({ result }) {
  const intent = result.parsed_intent || {};
  const steering = Object.keys(INTENT_FIELDS)
    .filter((f) => intent[f] !== null && intent[f] !== undefined && intent[f] !== "")
    .map((f) => ({ field: f, ...intentChip(f, intent[f]) }));
  const segment = segmentInfo(result.segment);
  const constraints = unverifiedFrom(result);

  // Only claim a preference influenced ranking when the evidence says so.
  const applied = (result.evidence || []).some((e) => (e.intent_used || []).length > 0);

  let n = 0;
  return (
    <section className="understood" aria-labelledby="understood-title">
      <div className="understood-grid">
        <div className="understood-ask">
          <span className="field-label">You asked</span>
          <blockquote className="understood-query">{result.query}</blockquote>
        </div>

        <div className="understood-read">
          <h2 id="understood-title" className="field-label">Here is what Motive understood</h2>
          <ul className="facets">
            {segment && (
              <li className={`facet facet--profile facet--${segment.kind} chip-enter`} style={{ "--i": n++ }}>
                <span className="facet-label">{segment.label}</span>
                <span className="facet-value">{segment.value}</span>
                <span className="facet-note">{segment.note}</span>
              </li>
            )}
            {steering.map((c) => (
              <li className="facet facet--steer chip-enter" style={{ "--i": n++ }} key={c.field}>
                <span className="facet-label">{c.label}</span>
                <span className="facet-value">{c.value}</span>
                <span className="facet-note">{c.note}</span>
                {applied && <span className="status-tag status-tag--accent">Influenced the ranking</span>}
              </li>
            ))}
          </ul>
          {steering.length === 0 && (
            <p className="understood-quiet">
              No exploration or popularity preference in this request. The learned ranking ran as-is.
            </p>
          )}
          {steering.length > 0 && !applied && (
            <p className="understood-quiet">
              These preferences were understood, but this ranking route didn't apply them to the
              order.
            </p>
          )}
        </div>
      </div>

      <UnsupportedConstraints constraints={constraints} />
    </section>
  );
}
