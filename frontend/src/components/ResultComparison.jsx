import { FAMILIES, familyReading } from "../lib/labels.js";
import { fmtNum, formatScore, isTie, joinList, rankLabel } from "../lib/formatting.js";

// Signal-level comparison of the top results. Values are compared only
// within one signal family (one row). No causal weights are claimed.
export default function ResultComparison({ items }) {
  const top = items.slice(0, 3);
  if (top.length < 2) return null;

  const rows = FAMILIES.map((f) => {
    const cells = top.map((it) => familyReading(f, it.evidence));
    const max = Math.max(0, ...cells.map((c) => (c.value ?? 0)));
    return { family: f, cells, max };
  });

  const [a, b] = [0, 1].map((i) => new Set(rows.filter((r) => r.cells[i].present).map((r) => r.family.label.toLowerCase())));
  const onlyA = [...a].filter((x) => !b.has(x));
  const onlyB = [...b].filter((x) => !a.has(x));
  const tie = isTie(top[0].rec.score, top[1].rec.score);

  const sentences = [];
  if (tie) sentences.push("#01 and #02 have equal ranking scores.");
  if (onlyA.length) sentences.push(`#01 has ${joinList(onlyA)} evidence that #02 doesn't.`);
  if (onlyB.length) sentences.push(`#02 has ${joinList(onlyB)} evidence that #01 doesn't, yet ranked ${tie ? "alongside it" : "lower"}.`);
  if (!onlyA.length && !onlyB.length) sentences.push("#01 and #02 show the same signal types.");
  sentences.push("These signals contributed to their rankings; the learned model combines them with other features, so this doesn't show exact weights.");

  return (
    <section className="compare" aria-labelledby="compare-title">
      <h3 id="compare-title" className="compare-title">Compare top results</h3>
      <p className="compare-summary">{sentences.join(" ")}</p>

      <div className="compare-scroll">
        <table className="compare-table">
          <thead>
            <tr>
              <th scope="col"><span className="visually-hidden">Signal</span></th>
              {top.map((it, i) => (
                <th scope="col" key={it.rec.itemid + "-" + i}>
                  <span className="ct-rank">#{rankLabel(i + 1)}</span>
                  <span className="ct-item">{it.rec.itemid}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="ct-score-row">
              <th scope="row">Ranking score</th>
              {top.map((it, i) => (
                <td key={i}><span className="ct-score">{formatScore(it.rec.score)}</span></td>
              ))}
            </tr>
            {rows.map(({ family, cells, max }) => (
              <tr key={family.key}>
                <th scope="row">{family.label}</th>
                {cells.map((c, i) => (
                  <td key={i}>
                    <span className={`ct-dot${c.present ? " is-on" : ""}${family.key === "intent" ? " ct-dot--intent" : ""}`} aria-hidden="true" />
                    <span className="visually-hidden">{c.present ? "Present" : "Not reported"}</span>
                    {c.value !== null && (
                      <span className="ct-value">
                        <span className="ct-bar" aria-hidden="true">
                          <span style={{ width: `${max > 0 ? Math.max(6, (c.value / max) * 100) : 0}%` }} />
                        </span>
                        <span className="ct-raw">{fmtNum(c.value)}</span>
                      </span>
                    )}
                    {c.support !== null && <span className="ct-support">{fmtNum(c.support)} sources</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="compare-note">
        Filled marks show a reported signal. Bars compare values within a row only; each row
        uses its own internal scale.
      </p>
    </section>
  );
}
