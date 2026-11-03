import QuickDirections from "./QuickDirections.jsx";
import RecentRequests from "./RecentRequests.jsx";

export const DEMO_SHOPPER = "1150086";
const COUNTS = [3, 5, 10, 20];

export default function RequestComposer({
  form,
  setField,
  errors,
  busy,
  onSubmit,
  recent,
  onClearRecent,
  firstRun,
  onClose,
}) {
  function submit(e) {
    e.preventDefault();
    onSubmit();
  }
  function onKeyDown(e) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      onSubmit();
    }
  }
  const usingDemo = form.shopperId.trim() === DEMO_SHOPPER;

  return (
    <form className={`composer${busy ? " is-busy" : ""}`} onSubmit={submit} noValidate aria-labelledby="composer-title">
      <div className="composer-head">
        <div>
          <h2 id="composer-title" className="composer-title">
            {firstRun ? "Try Motive" : "Edit request"}
          </h2>
          <p className="composer-sub">
            Describe which way the ranking should move. Motive interprets it, ranks with a
            learned model and shows the evidence.
          </p>
        </div>
        {onClose && (
          <button type="button" className="btn-ghost" onClick={onClose} disabled={busy}>
            Close
          </button>
        )}
      </div>

      <div className="composer-block">
        <span className="field-label" id="dir-label">Start with a direction</span>
        <QuickDirections
          query={form.query}
          disabled={busy}
          labelId="dir-label"
          onPick={(d) => setField("query", d.query)}
        />
      </div>

      <div className="composer-block">
        <label htmlFor="query" className="field-label">Your request</label>
        <textarea
          id="query"
          className="composer-query"
          value={form.query}
          onChange={(e) => setField("query", e.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          readOnly={busy}
          placeholder="e.g. Something a little different from what I usually pick"
          aria-invalid={!!errors.query}
          aria-describedby={errors.query ? "query-error" : "query-hint"}
        />
        {errors.query ? (
          <p id="query-error" className="field-error">{errors.query}</p>
        ) : (
          <p id="query-hint" className="field-hint">
            Directions fill this in. You can edit the words freely before ranking.
          </p>
        )}
      </div>

      <div className="composer-row">
        <div className="shopper-field">
          <label htmlFor="shopperId" className="field-label">Shopper ID</label>
          <input
            id="shopperId"
            className="text-input"
            inputMode="numeric"
            autoComplete="off"
            placeholder="Retailrocket visitor ID"
            value={form.shopperId}
            readOnly={busy}
            onChange={(e) => setField("shopperId", e.target.value)}
            aria-invalid={!!errors.shopperId}
            aria-describedby={errors.shopperId ? "shopper-error" : undefined}
          />
          {errors.shopperId && <p id="shopper-error" className="field-error">{errors.shopperId}</p>}
        </div>

        <div className={`demo${usingDemo ? " is-active" : ""}`}>
          <div className="demo-text">
            <span className="demo-label">Demo shopper</span>
            <span className="demo-id">{DEMO_SHOPPER}</span>
            <span className="demo-note">An established shopper with history</span>
          </div>
          <button
            type="button"
            className="btn-secondary btn-sm"
            disabled={busy || usingDemo}
            onClick={() => setField("shopperId", DEMO_SHOPPER)}
          >
            {usingDemo ? "In use" : "Use demo"}
          </button>
        </div>
      </div>

      <RecentRequests
        recent={recent}
        disabled={busy}
        onClear={onClearRecent}
        onPick={(r) => {
          setField("query", r.query);
          if (r.shopperId) setField("shopperId", r.shopperId);
          if (r.k) setField("k", r.k);
        }}
      />

      <div className="composer-foot">
        <div className="count">
          <span className="field-label" id="count-label">Results</span>
          <div className="segmented" role="radiogroup" aria-labelledby="count-label">
            {COUNTS.map((n) => (
              <button
                key={n}
                type="button"
                role="radio"
                aria-checked={form.k === n}
                className={form.k === n ? "is-active" : ""}
                disabled={busy}
                onClick={() => setField("k", n)}
              >
                {n}
              </button>
            ))}
          </div>
          {errors.k && <p className="field-error">{errors.k}</p>}
        </div>

        <div className="composer-submit">
          <span className="kbd-hint" aria-hidden="true">
            <kbd>⌘</kbd>/<kbd>Ctrl</kbd> + <kbd>Enter</kbd>
          </span>
          <button type="submit" className="btn-primary" disabled={busy} aria-describedby="submit-note">
            {busy ? "Ranking…" : "Rank recommendations"}
          </button>
          <span id="submit-note" className="visually-hidden">
            Shortcut: Command or Control plus Enter from the request field.
          </span>
        </div>
      </div>
    </form>
  );
}
