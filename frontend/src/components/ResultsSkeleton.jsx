// Structural placeholder while a request runs. No fake content.
export default function ResultsSkeleton({ count = 3 }) {
  return (
    <div className="skeleton" aria-hidden="true">
      <div className="sk-panel">
        <span className="sk-line sk-w40" />
        <div className="sk-facets">
          <span className="sk-block" />
          <span className="sk-block" />
          <span className="sk-block" />
        </div>
      </div>
      {Array.from({ length: Math.min(count, 3) }).map((_, i) => (
        <div className="sk-card" key={i}>
          <span className="sk-rank" />
          <div className="sk-lines">
            <span className="sk-line sk-w30" />
            <span className="sk-line sk-w90" />
            <span className="sk-line sk-w60" />
          </div>
        </div>
      ))}
    </div>
  );
}
