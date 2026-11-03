// Constraints Motive understood but could not verify in the anonymized catalog.
// Presented as transparency, not as an error.
export default function UnsupportedConstraints({ constraints }) {
  if (!constraints.length) return null;
  return (
    <div className="unverified" role="note" aria-labelledby="unverified-title">
      <div className="unverified-head">
        <p id="unverified-title" className="unverified-title">Understood, but not used for ranking</p>
        <p className="unverified-text">
          This catalog doesn't contain reliable information to verify{" "}
          {constraints.length === 1 ? "this detail" : "these details"}, so Motive left{" "}
          {constraints.length === 1 ? "it" : "them"} out of the ranking rather than guessing.
        </p>
      </div>
      <ul className="facets">
        {constraints.map((c, i) => (
          <li className="facet facet--unverified chip-enter" style={{ "--i": i + 3 }} key={c.field}>
            <span className="facet-label">{c.label}</span>
            <span className="facet-value">{c.value ?? "Mentioned"}</span>
            <span className="status-tag">Not verified</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
