import RequestComposer from "./RequestComposer.jsx";
import RequestBar from "./RequestBar.jsx";
import PipelineStatus from "./PipelineStatus.jsx";
import EmptyResults from "./EmptyResults.jsx";
import ErrorState from "./ErrorState.jsx";
import ResultsSkeleton from "./ResultsSkeleton.jsx";
import ResultsWorkspace from "./ResultsWorkspace.jsx";

// Two states:
//   compose: the composer is the primary surface
//   results: results dominate; the request becomes compact, editable context
export default function DiscoverWorkspace(props) {
  const {
    form, setField, errors, status, result, error, lastRequest, runId,
    onSubmit, onRunDirection, onRetry, recent, clearRecent,
    composerOpen, setComposerOpen, resultsRef,
  } = props;

  const busy = status === "loading";
  const hasResult = !!result;

  return (
    <section id="discover" className={`discover${hasResult ? " has-results" : ""}`} aria-labelledby="discover-title">
      <div className="discover-bg" aria-hidden="true" />
      <div className="wrap">
        {hasResult ? (
          <h1 id="discover-title" className="visually-hidden">Discover</h1>
        ) : (
          <header className="discover-intro">
            <h1 id="discover-title" className="discover-title">
              Recommendations that show their reasoning.
            </h1>
            <p className="discover-lede">
              Give Motive a direction in plain words. A learned model ranks items from real
              shopping behavior, your words steer the order, and every result shows the
              evidence behind it.
            </p>
          </header>
        )}

        {!hasResult ? (
          <div className="compose-layout">
            <RequestComposer
              form={form}
              setField={setField}
              errors={errors}
              busy={busy}
              onSubmit={onSubmit}
              recent={recent}
              onClearRecent={clearRecent}
              firstRun
            />
            <div className="compose-side">
              <PipelineStatus status={status} runId={runId} />
              {status === "idle" && <EmptyResults />}
              {status === "error" && <ErrorState error={error} onRetry={onRetry} />}
            </div>
            {busy && (
              <div className="compose-skeleton">
                <ResultsSkeleton count={form.k} />
              </div>
            )}
          </div>
        ) : (
          <div className="results-layout" ref={resultsRef}>
            <RequestBar
              form={form}
              setField={setField}
              errors={errors}
              busy={busy}
              lastRequest={lastRequest}
              onRun={onSubmit}
              onRunDirection={onRunDirection}
              onOpenComposer={() => setComposerOpen(true)}
            />
            {composerOpen && (
              <RequestComposer
                form={form}
                setField={setField}
                errors={errors}
                busy={busy}
                onSubmit={onSubmit}
                recent={recent}
                onClearRecent={clearRecent}
                onClose={() => setComposerOpen(false)}
              />
            )}
            <PipelineStatus status={status} runId={runId} />
            {status === "error" && <ErrorState error={error} onRetry={onRetry} hasPrevious />}
            <ResultsWorkspace result={result} stale={busy} />
          </div>
        )}
      </div>
    </section>
  );
}
