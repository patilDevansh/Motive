import { useEffect, useState } from "react";
import SignalGlyph from "./SignalGlyph.jsx";
import { CheckIcon } from "./Icons.jsx";

// State-aware pipeline:
//   idle    → one compact line
//   loading → expanded staged sequence (illustrative, timer-driven)
//   done    → compact three-check summary
//   error   → compact stopped line
const STAGES = [
  { text: "Understanding your request", on: { intent: 1 } },
  { text: "Reading behavioral history", on: { intent: 1, history: 1 } },
  { text: "Finding candidate relationships", on: { intent: 1, history: 1, sessions: 1 } },
  { text: "Reranking with learned signals", on: { intent: 1, history: 2, sessions: 2, popularity: 1 } },
  { text: "Preparing evidence", on: { intent: 1, history: 2, sessions: 2, popularity: 1 } },
];
const STEP_MS = 1150;
const BLANK = { history: 0, sessions: 0, popularity: 0, intent: 0 };
const FLOW = ["Behavior", "candidates", "ranking", "evidence"];

export default function PipelineStatus({ status, runId }) {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    if (status !== "loading") return undefined;
    setStage(0);
    const id = setInterval(() => setStage((s) => Math.min(s + 1, STAGES.length - 1)), STEP_MS);
    return () => clearInterval(id);
  }, [status, runId]);

  if (status === "loading") {
    return (
      <section className="pipeline pipeline--active" aria-label="Pipeline">
        <div className="pl-visual">
          <SignalGlyph channels={{ ...BLANK, ...STAGES[stage].on }} size="pipeline" pulse={stage === STAGES.length - 1} decorative />
        </div>
        <div className="pl-body">
          <div className="pl-head">
            <span className="pl-title">Ranking in progress</span>
            <span className="pl-note">Illustrative pipeline, not live telemetry</span>
          </div>
          <ol className="pl-steps">
            {STAGES.map((s, i) => {
              const st = i < stage ? "done" : i === stage ? "current" : "todo";
              return (
                <li key={s.text} className={`pl-step is-${st}`} aria-current={st === "current" ? "step" : undefined}>
                  <span className="pl-marker" aria-hidden="true">{st === "done" && <CheckIcon />}</span>
                  <span>{s.text}</span>
                </li>
              );
            })}
          </ol>
        </div>
      </section>
    );
  }

  if (status === "done") {
    return (
      <section className="pipeline pipeline--compact pipeline--done" aria-label="Pipeline">
        <ul className="pl-summary">
          {["Request interpreted", "Ranking complete", "Evidence ready"].map((t) => (
            <li key={t}>
              <span className="pl-check" aria-hidden="true"><CheckIcon /></span>
              {t}
            </li>
          ))}
        </ul>
      </section>
    );
  }

  if (status === "error") {
    return (
      <section className="pipeline pipeline--compact pipeline--error" aria-label="Pipeline">
        <p className="pl-line">
          <span className="pl-stop" aria-hidden="true" />
          Pipeline stopped before ranking finished
        </p>
      </section>
    );
  }

  return (
    <section className="pipeline pipeline--compact" aria-label="Pipeline">
      <p className="pl-line">
        <SignalGlyph channels={BLANK} size="xs" decorative />
        <strong>Pipeline ready</strong>
        <span className="pl-flow">
          {FLOW.map((f, i) => (
            <span key={f}>
              {i > 0 && <span className="pl-arrow" aria-hidden="true">→</span>}
              {f}
            </span>
          ))}
        </span>
      </p>
    </section>
  );
}
