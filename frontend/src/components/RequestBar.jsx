import QuickDirections from "./QuickDirections.jsx";

// After results arrive, the request becomes compact, editable context above
// them. Edit the words and rerun, or pick a new direction to rerun at once.
export default function RequestBar({
  form,
  setField,
  errors,
  busy,
  lastRequest,
  onRun,
  onRunDirection,
  onOpenComposer,
}) {
  const edited = lastRequest && form.query.trim() !== lastRequest.query.trim();

  function submit(e) {
    e.preventDefault();
    onRun();
  }

  return (
    <form className={`request-bar${busy ? " is-busy" : ""}`} onSubmit={submit} noValidate aria-label="Current request">
      <div className="rb-main">
        <label htmlFor="rb-query" className="rb-label">Request</label>
        <input
          id="rb-query"
          className="rb-input"
          value={form.query}
          readOnly={busy}
          onChange={(e) => setField("query", e.target.value)}
          aria-invalid={!!errors.query}
          aria-describedby="rb-meta"
        />
        <button type="submit" className="btn-primary btn-md" disabled={busy}>
          {busy ? "Ranking…" : edited ? "Rerun with edits" : "Rerun"}
        </button>
      </div>

      <div className="rb-sub">
        <p id="rb-meta" className="rb-meta">
          Shopper <strong>{form.shopperId || "—"}</strong>
          <span aria-hidden="true" className="rb-sep" />
          <strong>{form.k}</strong> results
          {edited && !busy && <span className="rb-edited">Edited, rerun to apply</span>}
          {errors.query && <span className="field-error">{errors.query}</span>}
          {errors.shopperId && <span className="field-error">{errors.shopperId}</span>}
        </p>
        <button type="button" className="link-btn" onClick={onOpenComposer} disabled={busy}>
          Edit shopper, count or recent
        </button>
      </div>

      <div className="rb-refine">
        <span className="field-label" id="refine-label">Rerun with a new direction</span>
        <QuickDirections
          compact
          labelId="refine-label"
          query={form.query}
          disabled={busy}
          onPick={onRunDirection}
        />
      </div>
    </form>
  );
}
