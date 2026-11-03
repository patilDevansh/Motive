// Specific, calm error messages. The request is always kept.
function describe(error) {
  const s = error?.status;
  const kind = error?.kind;
  if (kind === "network" || s === 0) {
    return {
      title: "We couldn't reach the ranking service.",
      body: "Your request has been kept so you can try again.",
      hint: "If you're running Motive locally, check that the FastAPI server is still running.",
    };
  }
  if (kind === "unexpected") {
    return {
      title: "The ranking service returned something Motive couldn't read.",
      body: "Your request has been kept. Trying again usually resolves this.",
      hint: null,
    };
  }
  if (s === 503) {
    return {
      title: "Request interpretation is unavailable.",
      body: "The server has no Claude API key configured, so natural-language requests can't be interpreted yet.",
      hint: "Set ANTHROPIC_API_KEY in the server's environment and restart it.",
    };
  }
  if (s === 502) {
    return {
      title: "Motive couldn't interpret this request.",
      body: "Your request has been kept. Rephrasing it or trying again usually works.",
      hint: error?.message,
    };
  }
  if (s === 422) {
    return {
      title: "The ranking service rejected this request.",
      body: "Check the shopper ID, the request text and the number of results.",
      hint: error?.message,
    };
  }
  return {
    title: "Ranking didn't complete.",
    body: "Your request has been kept so you can try again.",
    hint: error?.message,
  };
}

export default function ErrorState({ error, onRetry, hasPrevious }) {
  const d = describe(error);
  return (
    <div className="error-state" role="alert">
      <div className="error-icon" aria-hidden="true">
        <svg viewBox="0 0 20 20"><path d="M10 6v5M10 14h.01" /><circle cx="10" cy="10" r="7.5" /></svg>
      </div>
      <div className="error-body">
        <p className="error-title">{d.title}</p>
        <p className="error-text">{d.body}</p>
        {d.hint && <p className="error-hint">{d.hint}</p>}
        {hasPrevious && <p className="error-hint">Your previous results are still shown below.</p>}
        {onRetry && (
          <button type="button" className="btn-secondary btn-sm" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
