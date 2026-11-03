import SignalGlyph from "./SignalGlyph.jsx";

const PARTS = [
  ["Intent interpretation", "What Motive understood from your words"],
  ["Ranked list", "Items ordered by the learned model"],
  ["Evidence", "The signals behind every position"],
];

export default function EmptyResults() {
  return (
    <div className="empty">
      <SignalGlyph channels={{ history: 1, sessions: 1, popularity: 1, intent: 1 }} size="sm" decorative />
      <div className="empty-copy">
        <p className="empty-title">Your ranked list will appear here.</p>
        <ul className="empty-parts">
          {PARTS.map(([t, d]) => (
            <li key={t}>
              <strong>{t}</strong>
              <span>{d}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
