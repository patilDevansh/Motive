export const NAV = [
  ["discover", "Discover"],
  ["system", "System"],
  ["intent", "Intent"],
  ["trust", "Trust"],
];

const ENGINE_LABEL = {
  checking: "Checking engine",
  online: "Engine online",
  offline: "Engine offline",
};

export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" className="bm-tile" />
      <g fill="none" strokeWidth="2" strokeLinecap="round" className="bm-lines">
        <path d="M6 8c8 0 8 8 15 8" />
        <path d="M6 13c8 0 8 3 15 3" />
        <path d="M6 19c8 0 8-3 15-3" />
      </g>
      <path d="M6 24c8 0 8-8 15-8" fill="none" strokeWidth="2" strokeLinecap="round" strokeDasharray="2 3" className="bm-intent" />
      <circle cx="23.5" cy="16" r="3.4" className="bm-node" />
    </svg>
  );
}

export default function AppHeader({ active, engine, theme, onToggleTheme }) {
  return (
    <header className="topbar">
      <div className="wrap topbar-inner">
        <a className="brand" href="#discover" aria-label="Motive, go to Discover">
          <BrandMark />
          <span className="brand-name">Motive</span>
        </a>

        <nav className="nav" aria-label="Sections">
          {NAV.map(([id, label]) => (
            <a
              key={id}
              href={`#${id}`}
              className={active === id ? "is-active" : ""}
              aria-current={active === id ? "location" : undefined}
            >
              {label}
            </a>
          ))}
        </nav>

        <div className="topbar-tools">
          <span className={`engine engine--${engine}`} role="status" title={ENGINE_LABEL[engine]}>
            <span className="engine-dot" aria-hidden="true" />
            <span className="engine-text">{ENGINE_LABEL[engine]}</span>
          </span>
          <button
            type="button"
            className="icon-btn"
            onClick={onToggleTheme}
            aria-label="Dark theme"
            aria-pressed={theme === "dark"}
            title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
          >
            {theme === "dark" ? (
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <circle cx="10" cy="10" r="3.6" />
                <path d="M10 2.5v1.8M10 15.7v1.8M2.5 10h1.8M15.7 10h1.8M4.7 4.7l1.3 1.3M14 14l1.3 1.3M4.7 15.3 6 14M14 6l1.3-1.3" />
              </svg>
            ) : (
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <path d="M16.2 12.4A6.8 6.8 0 0 1 7.6 3.8a6.8 6.8 0 1 0 8.6 8.6Z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
