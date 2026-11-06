// One-click example directions. Each fills the request text; nothing bypasses
// the API, the sentence is still interpreted like anything typed.
export const DIRECTIONS = [
  { id: "surprise", label: "Surprise me", query: "Show me something different from my usual choices." },
  { id: "familiar", label: "Stay familiar", query: "Keep the ranking close to things I usually choose." },
  { id: "niche", label: "Go niche", query: "Prefer less mainstream choices." },
  { id: "popular", label: "Popular picks", query: "Show me widely chosen items." },
];

export const GUARDRAIL = {
  id: "guard",
  label: "Sony under $300 for travel",
  query: "I want Sony products under $300 that are good for travel.",
};

export default function QuickDirections({ query, onPick, disabled, compact = false, labelId }) {
  const current = query.trim();
  const btn = (d, extra = "") => {
    const on = current === d.query;
    return (
      <li key={d.id}>
        <button
          type="button"
          className={`dir-chip${extra}${on ? " is-current" : ""}`}
          aria-pressed={on}
          disabled={disabled}
          onClick={() => onPick(d)}
        >
          {on && (
            <svg viewBox="0 0 12 12" aria-hidden="true" className="dir-check">
              <path d="M2.5 6.3 5 8.6 9.5 3.6" />
            </svg>
          )}
          {d.label}
        </button>
      </li>
    );
  };

  return (
    <div className={`directions${compact ? " directions--compact" : ""}`}>
      <ul aria-labelledby={labelId}>
        {DIRECTIONS.map((d) => btn(d))}
        {!compact && btn(GUARDRAIL, " dir-chip--guard")}
      </ul>
    </div>
  );
}
