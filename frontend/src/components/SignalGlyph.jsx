import { CHANNELS } from "../lib/labels.js";

// The Motive glyph: signals converging into one ranked node.
// Each channel has its own line style so meaning never depends on color:
// history = solid, sessions = double, popularity = thin, your request = dashed.
const YS = [8, 24, 40, 56];
const NODE = { x: 104, y: 32 };

function channelPath(y) {
  return `M4 ${y} C 58 ${y}, 58 ${NODE.y}, ${NODE.x - 7} ${NODE.y}`;
}

export default function SignalGlyph({ channels, size = "sm", pulse = false, title, decorative = false, className = "" }) {
  const active = CHANNELS.filter((c) => (channels[c.key] || 0) > 0);
  const label =
    title ||
    (active.length
      ? `Signals behind this item: ${active.map((c) => c.name.toLowerCase()).join(", ")}`
      : "No specific signals reported");

  return (
    <svg
      className={`glyph glyph--${size}${pulse ? " glyph--pulse" : ""} ${className}`}
      viewBox="0 0 120 64"
      {...(decorative ? { "aria-hidden": true, focusable: "false" } : { role: "img", "aria-label": label })}
    >
      {CHANNELS.map((c, i) => {
        const level = channels[c.key] || 0;
        const d = channelPath(YS[i]);
        const on = level > 0;
        const base = `glyph-line glyph-line--${c.style}${on ? " is-on" : ""}${level > 1 ? " is-strong" : ""}`;
        return (
          <g key={c.key}>
            {c.style === "double" && on ? (
              <>
                <path d={d} className={base} transform="translate(0 -1.3)" />
                <path d={d} className={base} transform="translate(0 1.3)" />
              </>
            ) : (
              <path d={d} className={base} />
            )}
            <circle
              cx="4"
              cy={YS[i]}
              r={on ? 2.4 : 1.6}
              className={`glyph-dot${on ? " is-on" : ""}${c.key === "intent" ? " glyph-dot--intent" : ""}`}
            />
          </g>
        );
      })}
      <circle cx={NODE.x} cy={NODE.y} r="6.5" className={`glyph-node${active.length ? " is-on" : ""}`} />
      <circle cx={NODE.x} cy={NODE.y} r="2.2" className="glyph-core" />
    </svg>
  );
}

// Legend so the glyph can be read without prior explanation.
export function GlyphLegend() {
  return (
    <ul className="glyph-legend" aria-label="How to read the signal glyph">
      {CHANNELS.map((c) => (
        <li key={c.key}>
          <svg viewBox="0 0 28 8" aria-hidden="true">
            {c.style === "double" ? (
              <>
                <path d="M1 2.7H27" className={`legend-line legend-line--${c.style}`} />
                <path d="M1 5.3H27" className={`legend-line legend-line--${c.style}`} />
              </>
            ) : (
              <path d="M1 4H27" className={`legend-line legend-line--${c.style}`} />
            )}
          </svg>
          {c.name}
        </li>
      ))}
    </ul>
  );
}
