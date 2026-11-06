const RESULTS = [
  { name: "Rule-based parser", value: 46.15 },
  { name: "Claude semantic parser", value: 96.15, accent: true },
];

export default function IntentPage() {
  return (
    <section id="intent" className="intent-section" aria-labelledby="intent-title">
      <div className="wrap intent-story">
        <div className="intent-copy">
          <h2 id="intent-title" className="section-title">Why intent matters</h2>
          <p>
            The recommender can rank items. It can't read a sentence. People rarely use the
            exact words a rule was written to catch.
          </p>
          <p>
            Claude has one narrow job: convert what you wrote into structured intent. It never
            sees the catalog and never picks a product. The trained model does the ranking.
          </p>
          <ol className="intent-chain" aria-label="Where Claude sits in the flow">
            <li>Your words</li>
            <li className="is-accent">Claude: structured intent</li>
            <li>Learned ranking</li>
          </ol>
        </div>

        <div className="intent-panels">
          <figure className="example">
            <figcaption className="example-cap">Illustrative example</figcaption>
            <blockquote className="example-quote">“Something unusual and not widely chosen.”</blockquote>
            <div className="example-rows">
              <div className="example-row">
                <span className="example-who">Keyword matching</span>
                <span className="example-out example-out--none">No match for “exploratory” or “niche”</span>
              </div>
              <div className="example-row is-accent">
                <span className="example-who">Semantic interpretation</span>
                <span className="example-out">
                  <span className="mini-chip"><span className="mc-k">Exploration</span> Exploratory</span>
                  <span className="mini-chip"><span className="mc-k">Popularity</span> Niche</span>
                </span>
              </div>
            </div>
          </figure>

          <figure className="bench">
            <div className="bench-head">
              <figcaption className="bench-title">Intent parsing benchmark</figcaption>
              <span className="badge">Frozen holdout</span>
            </div>
            <p className="bench-desc">Exact-field accuracy on the project's frozen intent test set.</p>
            <dl className="bench-bars">
              {RESULTS.map((r) => (
                <div className={`bench-bar${r.accent ? " is-accent" : ""}`} key={r.name}>
                  <dt>{r.name}</dt>
                  <dd>
                    <span className="bench-track"><span className="bench-fill" style={{ width: `${r.value}%` }} /></span>
                    <span className="bench-val">{r.value.toFixed(2)}%</span>
                  </dd>
                </div>
              ))}
            </dl>
            <p className="bench-note">
              Schema-valid structured output: <strong>10 / 10</strong>. These numbers describe this
              project's test set, not general model accuracy.
            </p>
          </figure>
        </div>
      </div>
    </section>
  );
}
