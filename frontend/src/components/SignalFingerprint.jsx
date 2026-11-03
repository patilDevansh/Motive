import { useMemo } from "react";

// A deterministic abstract mark generated from the item ID, so an anonymous
// item is recognizable across runs. It is explicitly not a product image.
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function seedFrom(id) {
  const s = String(id);
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function build(id) {
  const rand = mulberry32(seedFrom(id));
  const cells = [];
  for (let x = 0; x < 4; x++) for (let y = 0; y < 4; y++) cells.push([9 + x * 10, 9 + y * 10]);
  // Pick five distinct lattice points.
  for (let i = cells.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [cells[i], cells[j]] = [cells[j], cells[i]];
  }
  const nodes = cells.slice(0, 5);
  const accent = Math.floor(rand() * nodes.length);
  const d = nodes.map(([x, y], i) => `${i ? "L" : "M"}${x} ${y}`).join(" ");
  return { nodes, accent, d };
}

export default function SignalFingerprint({ itemId, size = 44 }) {
  const { nodes, accent, d } = useMemo(() => build(itemId), [itemId]);
  return (
    <svg
      className="fingerprint"
      width={size}
      height={size}
      viewBox="0 0 48 48"
      aria-hidden="true"
    >
      <rect x="0.5" y="0.5" width="47" height="47" rx="11" className="fp-tile" />
      <path d={d} className="fp-path" />
      {nodes.map(([x, y], i) => (
        <circle key={`${x}-${y}`} cx={x} cy={y} r={i === accent ? 3.4 : 2.3} className={i === accent ? "fp-node fp-node--accent" : "fp-node"} />
      ))}
    </svg>
  );
}
