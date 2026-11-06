import { useEffect, useState } from "react";
import IntentSummary from "./IntentSummary.jsx";
import RecommendationCard from "./RecommendationCard.jsx";
import ResultComparison from "./ResultComparison.jsx";
import { GlyphLegend } from "./SignalGlyph.jsx";
import { isTie } from "../lib/formatting.js";

export default function ResultsWorkspace({ result, stale }) {
  const [openKey, setOpenKey] = useState(null); // accordion: one drawer at a time
  useEffect(() => setOpenKey(null), [result]);

  const recs = result.recommendations || [];
  const evidenceById = new Map((result.evidence || []).map((e) => [e.itemid, e]));
  const explById = new Map((result.explanations || []).map((e) => [e.itemid, e.explanation]));
  const maxScore = recs.reduce((m, r) => Math.max(m, Number(r.score) || 0), 0);
  const items = recs.map((rec) => ({ rec, evidence: evidenceById.get(rec.itemid) }));

  const tieRank = recs.map((r, i) => {
    for (let j = 0; j < i; j++) if (isTie(recs[j].score, r.score)) return j + 1;
    return null;
  });

  return (
    <div className={`results${stale ? " is-stale" : ""}`}>
      <IntentSummary result={result} />

      <section className="ranked" aria-labelledby="ranked-title">
        <div className="ranked-head">
          <div>
            <h2 id="ranked-title" className="ranked-title">
              Ranking complete. {recs.length} {recs.length === 1 ? "item" : "items"} for shopper {result.user_id}.
            </h2>
            <p className="ranked-note">
              Items are anonymized and shown by ID. Each mark is generated from the item ID, not
              a product image.
            </p>
          </div>
          <GlyphLegend />
        </div>

        {recs.length === 0 ? (
          <p className="ranked-empty">
            No items came back for this shopper. Try another shopper ID or a broader request.
          </p>
        ) : (
          <div className="ranked-grid">
            <ol className="rec-list">
              {recs.map((rec, i) => {
                const key = `${rec.itemid}-${i}`;
                return (
                  <RecommendationCard
                    key={key}
                    rank={i + 1}
                    rec={rec}
                    evidence={evidenceById.get(rec.itemid)}
                    explanation={explById.get(rec.itemid)}
                    maxScore={maxScore}
                    tiedWithRank={tieRank[i]}
                    open={openKey === key}
                    onToggle={() => setOpenKey((k) => (k === key ? null : key))}
                  />
                );
              })}
            </ol>
            <aside className="ranked-aside">
              <ResultComparison items={items} />
            </aside>
          </div>
        )}
      </section>
    </div>
  );
}
