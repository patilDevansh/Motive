const LIMITS = [
  ["Not verified", "Brand", "Items carry anonymized properties, not manufacturer names."],
  ["Not verified", "Live price", "There are no current, verified prices to filter on."],
  ["Not available", "Product identity", "Real product names aren't in the catalog, so none are shown."],
  ["Not available", "Retailer links", "There's no store behind the data, so no links are created."],
  ["Not verified", "Specifications", "Real-world specifications can't be confirmed, so none are claimed."],
];

const STEPS = [
  ["Understood", "Your request is parsed in full, including details the catalog can't check."],
  ["Labeled", "Anything unverifiable is shown back to you, not dropped silently."],
  ["Left out", "Unverified details never quietly influence the ranking."],
];

export default function TrustPage({ latestConstraints }) {
  return (
    <section id="trust" className="trust-section" aria-labelledby="trust-title">
      <div className="wrap trust">
        <div className="trust-top">
          <div className="trust-intro">
            <h2 id="trust-title" className="section-title">Grounded by design</h2>
            <p className="trust-principle">
              Motive would rather admit what it doesn't know than invent catalog facts.
            </p>
            <p>
              Motive ranks the Retailrocket dataset, which is anonymized. When a request asks for
              something the catalog can't support, Motive says so and ranks on what it can
              verify.
            </p>
          </div>
          <ol className="trust-steps">
            {STEPS.map(([t, d], i) => (
              <li key={t}>
                <span className="trust-step-num" aria-hidden="true">{i + 1}</span>
                <span className="trust-step-title">{t}</span>
                <span className="trust-step-text">{d}</span>
              </li>
            ))}
          </ol>
        </div>

        {latestConstraints.length > 0 && (
          <div className="trust-live" aria-labelledby="trust-live-title">
            <p id="trust-live-title" className="trust-live-title">From your latest request</p>
            <ul>
              {latestConstraints.map((c) => (
                <li key={c.field}>
                  <span className="tl-label">{c.label}</span>
                  <span className="tl-value">{c.value ?? "Mentioned"}</span>
                  <span className="status-tag">Not verified</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <ul className="limits">
          {LIMITS.map(([status, name, desc]) => (
            <li key={name} className="limit">
              <span className={`status-tag${status === "Not available" ? " status-tag--muted" : ""}`}>{status}</span>
              <span className="limit-name">{name}</span>
              <span className="limit-desc">{desc}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
