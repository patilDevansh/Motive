import { truncate } from "../lib/formatting.js";

export default function RecentRequests({ recent, onPick, onClear, disabled }) {
  if (!recent.length) return null;
  return (
    <div className="recent">
      <div className="recent-head">
        <span className="field-label" id="recent-label">Recent directions</span>
        <span className="recent-note">Saved in this browser only</span>
        <button type="button" className="link-btn recent-clear" onClick={onClear} disabled={disabled}>
          Clear
        </button>
      </div>
      <ul className="recent-list" aria-labelledby="recent-label">
        {recent.map((r) => (
          <li key={r.query}>
            <button
              type="button"
              className="recent-item"
              disabled={disabled}
              onClick={() => onPick(r)}
              title={r.query}
            >
              <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3.5A4.5 4.5 0 1 1 3.6 7M3.5 3.8V7h3.2" /></svg>
              <span>{truncate(r.query, 64)}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
