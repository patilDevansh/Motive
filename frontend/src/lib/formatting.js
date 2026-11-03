// Pure formatting helpers shared across the UI.

export function fmtNum(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return String(v);
  if (Number.isInteger(n)) return n.toLocaleString("en-US");
  return n.toFixed(Math.abs(n) < 10 ? 2 : 0);
}

export function money(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return String(v);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: Number.isInteger(n) ? 0 : 2,
  }).format(n);
}

export function joinList(items) {
  if (items.length <= 1) return items.join("");
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`;
}

export function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

export function humanize(s) {
  return capitalize(String(s ?? "").replace(/_/g, " "));
}

// Ranking scores use four decimals so rounding never manufactures a tie.
export const formatScore = (v) => Number(v).toFixed(4);

export const TIE_EPSILON = 1e-9;
export const isTie = (a, b) => Math.abs(Number(a) - Number(b)) < TIE_EPSILON;

export function rankLabel(n) {
  return String(n).padStart(2, "0");
}

export function truncate(s, max = 90) {
  const t = String(s || "").trim();
  return t.length > max ? `${t.slice(0, max - 1).trimEnd()}…` : t;
}
