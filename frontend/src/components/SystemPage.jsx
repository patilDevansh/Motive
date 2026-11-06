import { useState } from "react";

function WeightsViz() {
  return (
    <svg viewBox="0 0 96 44" className="stage-viz" aria-hidden="true">
      {[["view", 1], ["cart", 3], ["buy", 5]].map(([n, w], i) => (
        <g key={n} transform={`translate(0 ${4 + i * 14})`}>
          <text x="0" y="8" className="viz-text">{n}</text>
          <rect x="30" y="1" height="8" rx="1.5" width={w * 12} className="viz-fill" />
        </g>
      ))}
    </svg>
  );
}
function CandidatesViz() {
  return (
    <svg viewBox="0 0 96 44" className="stage-viz" aria-hidden="true">
      <circle cx="36" cy="22" r="17" className="viz-ring" />
      <circle cx="60" cy="22" r="17" className="viz-ring viz-ring--alt" />
      {[[26, 16], [30, 30], [48, 18], [48, 28], [68, 14], [70, 28]].map(([x, y]) => (
        <circle key={`${x}-${y}`} cx={x} cy={y} r="2.2" className="viz-dot" />
      ))}
    </svg>
  );
}
function RerankViz() {
  return (
    <svg viewBox="0 0 96 44" className="stage-viz" aria-hidden="true">
      {[62, 50, 40, 30].map((w, i) => (
        <rect key={w} x="16" y={3 + i * 10} height="6" rx="1.5" width={w} className={i === 0 ? "viz-fill viz-fill--accent" : "viz-fill"} />
      ))}
      {[1, 2, 3, 4].map((n, i) => (
        <text key={n} x="4" y={9 + i * 10} className="viz-text">{n}</text>
      ))}
    </svg>
  );
}
function SteerViz() {
  return (
    <svg viewBox="0 0 96 44" className="stage-viz" aria-hidden="true">
      {[56, 48, 44, 34].map((w, i) => (
        <rect key={i} x="16" y={3 + i * 10} height="6" rx="1.5" width={w} className={i === 1 ? "viz-fill viz-fill--accent" : "viz-fill viz-fill--muted"} />
      ))}
      <path d="M78 19 V 9 M74 13 l4 -4 4 4" className="viz-arrow" />
    </svg>
  );
}
function EvidenceViz() {
  return (
    <svg viewBox="0 0 96 44" className="stage-viz" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <g key={i} transform={`translate(0 ${5 + i * 13})`}>
          <circle cx="6" cy="4" r="3" className={i === 2 ? "viz-dot viz-dot--accent" : "viz-dot"} />
          <rect x="14" y="1.5" height="5" rx="1.5" width={[58, 44, 50][i]} className="viz-fill viz-fill--muted" />
        </g>
      ))}
    </svg>
  );
}

const STAGES = [
  {
    title: "Behavior",
    text: "Views, carts and purchases carry different interaction strengths.",
    Viz: WeightsViz,
    handoff: "weighted history",
    detailTitle: "Interaction strength",
    detail: { type: "weights", rows: [["View", 1], ["Add to cart", 3], ["Purchase", 5]] },
  },
  {
    title: "Candidate discovery",
    text: "Content similarity and session co-visitation propose candidates.",
    Viz: CandidatesViz,
    handoff: "candidate pool",
    detailTitle: "Two independent sources",
    detail: {
      type: "pairs",
      rows: [
        ["Content similarity", "Items whose anonymized properties resemble the shopper's history."],
        ["Session co-visitation", "Items that shoppers tend to encounter in the same sessions."],
      ],
    },
  },
  {
    title: "ML reranking",
    text: "A trained tree model combines recommendation features into one ranking.",
    Viz: RerankViz,
    handoff: "ranked list",
    detailTitle: "Features the model combines",
    detail: {
      type: "tags",
      rows: [
        "Content score", "Max content similarity", "History support", "Co-visitation score",
        "Max co-visitation", "Co-visitation support", "Popularity", "History strength", "Shopper segment",
      ],
    },
  },
  {
    title: "Intent steering",
    text: "Supported preferences adjust the ranking without replacing the learned model.",
    Viz: SteerViz,
    handoff: "adjusted ranking",
    intent: true,
    detailTitle: "Supported preferences",
    detail: {
      type: "pairs",
      rows: [
        ["Exploration", "Familiar, balanced or exploratory"],
        ["Popularity", "Popular, neutral or niche"],
        ["Everything else", "Brand, price or use case is reported as not verifiable, not used"],
      ],
    },
  },
  {
    title: "Evidence",
    text: "The signals responsible for each recommendation stay inspectable.",
    Viz: EvidenceViz,
    detailTitle: "Signals kept with each result",
    detail: {
      type: "tags",
      rows: [
        "Similar to your history", "Multiple past interactions", "Behavioral relationship",
        "Multiple behavioral signals", "Catalog popularity", "Your request",
      ],
    },
  },
];

function Detail({ stage }) {
  const { detail } = stage;
  if (detail.type === "weights") {
    return (
      <dl className="sd-weights">
        {detail.rows.map(([n, w]) => (
          <div key={n}>
            <dt>{n}</dt>
            <dd><span className="sd-bar" style={{ width: `${w * 18}%` }} /><span>{w}</span></dd>
          </div>
        ))}
      </dl>
    );
  }
  if (detail.type === "pairs") {
    return (
      <dl className="sd-pairs">
        {detail.rows.map(([k, v]) => (
          <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
        ))}
      </dl>
    );
  }
  return (
    <ul className="sd-tags">
      {detail.rows.map((t) => <li key={t}>{t}</li>)}
    </ul>
  );
}

export default function SystemPage() {
  const [active, setActive] = useState(0);
  const stage = STAGES[active];

  return (
    <section id="system" className="system-section" aria-labelledby="system-title">
      <div className="wrap">
        <div className="system-panel">
          <div className="system-intro">
            <span className="system-kicker">System deep dive</span>
            <h2 id="system-title" className="section-title">How Motive builds a ranking</h2>
            <p>
              The learned model decides what ranks. Everything around it either feeds it
              signals or keeps its decisions inspectable. Hover or focus a stage for detail.
            </p>
          </div>

          <ol className="flow">
            {STAGES.map(({ title, text, Viz, handoff, intent }, i) => (
              <li
                key={title}
                className={`flow-stage${intent ? " is-intent" : ""}${active === i ? " is-active" : ""}${active === i - 1 ? " is-next" : ""}`}
              >
                <button
                  type="button"
                  className="flow-card"
                  aria-pressed={active === i}
                  aria-controls="system-detail"
                  onMouseEnter={() => setActive(i)}
                  onFocus={() => setActive(i)}
                  onClick={() => setActive(i)}
                >
                  <span className="flow-num">{String(i + 1).padStart(2, "0")}</span>
                  <Viz />
                  <span className="flow-title">{title}</span>
                  <span className="flow-text">{text}</span>
                </button>
                <span className={`flow-handoff${handoff ? "" : " is-end"}`} aria-hidden={!handoff}>
                  <span className="flow-arrow" aria-hidden="true" />
                  <span>{handoff || "end"}</span>
                </span>
              </li>
            ))}
          </ol>

          <div id="system-detail" className="system-detail" aria-live="polite">
            <p className="sd-title">
              <span className="sd-stage">{String(active + 1).padStart(2, "0")} {stage.title}</span>
              {stage.detailTitle}
            </p>
            <Detail stage={stage} />
          </div>

          <p className="system-note">
            Shoppers with no history take a different route: weighted popularity, so a first
            visit still gets a sensible list.
          </p>
        </div>
      </div>
    </section>
  );
}
