// Single source of truth for turning backend field names into product language.
// Raw evidence values are internal, unitless scores: they appear only as
// secondary detail, never as percentages or "confidence".
import { fmtNum, money, joinList, humanize, capitalize } from "./formatting.js";

export { joinList, humanize };

export const REASONS = {
  content_similarity: {
    short: "Similar to your history",
    title: "Similar to your history",
    describe: () =>
      "Its anonymized catalog properties closely resemble items you have viewed, carted or bought.",
    rawLabel: "Content similarity",
    rawValue: (v) => fmtNum(v),
  },
  multiple_history_support: {
    short: "Several past interactions",
    title: "Supported by multiple past interactions",
    describe: (v) => `${fmtNum(v)} different items in your history independently point toward it.`,
    rawLabel: "Supporting history items",
    rawValue: (v) => fmtNum(v),
  },
  covisitation: {
    short: "Behavioral relationship",
    title: "Behavioral relationship",
    describe: () =>
      "This item appeared in sessions alongside products connected to your history.",
    rawLabel: "Co-visitation score",
    rawValue: (v) => fmtNum(v),
  },
  multiple_covisitation_support: {
    short: "Multiple behavioral signals",
    title: "Multiple behavioral signals",
    describe: (v) => `${fmtNum(v)} of your items share session patterns with it, not just one.`,
    rawLabel: "Supporting session items",
    rawValue: (v) => fmtNum(v),
  },
    popularity: {
    short: "Popularity signal",
    title: "Popularity signal",
    describe: () =>
      "Weighted interaction volume across the whole catalog was one of the inputs the model considered.",
    rawLabel: "Popularity score",
    rawValue: (v) => fmtNum(v),
  },

  cold_start_popularity: {
    short: "Cold-start popularity",
    title: "Cold-start popularity",
    describe: () =>
      "No interaction history was available for this shopper, so this item was surfaced using catalog-wide weighted popularity.",
    rawLabel: "Weighted popularity score",
    rawValue: (v) => fmtNum(v),
  },
  
}

export function reasonInfo(type) {
  return REASONS[type] || {
    short: humanize(type),
    title: humanize(type),
    describe: () =>
      "A ranking signal reported by the recommender.",
    rawLabel: "Value",
    rawValue: (v) => fmtNum(v),
  };
}

// The four lines of the convergence glyph, in drawing order.
export const CHANNELS = [
  { key: "history", name: "History match", style: "solid" },
  { key: "sessions", name: "Session patterns", style: "double" },
  { key: "popularity", name: "Catalog popularity", style: "thin" },
  { key: "intent", name: "Your request", style: "dashed" },
];

// 0 = absent, 1 = present, 2 = present with multiple independent support.
export function channelsFor(evidence) {
  const types = new Set((evidence?.reasons || []).map((r) => r.type));
  return {
    history: types.has("multiple_history_support") ? 2 : types.has("content_similarity") ? 1 : 0,
    sessions: types.has("multiple_covisitation_support") ? 2 : types.has("covisitation") ? 1 : 0,
    popularity: types.has("popularity") ? 1 : 0,
    intent: (evidence?.intent_used || []).length > 0 ? 1 : 0,
  };
}

// Signal families for side-by-side comparison. Values are only ever compared
// within one family, never across families.
export const FAMILIES = [
  {
    key: "history",
    label: "History match",
    valueType: "content_similarity",
    supportType: "multiple_history_support",
    valueLabel: "similarity",
  },
  {
    key: "sessions",
    label: "Session patterns",
    valueType: "covisitation",
    supportType: "multiple_covisitation_support",
    valueLabel: "co-visitation",
  },
  {
    key: "popularity",
    label: "Catalog popularity",
    valueType: "popularity",
    valueLabel: "popularity",
  },
  { key: "intent", label: "Your request" },
];

export function familyReading(family, evidence) {
  if (family.key === "intent") {
    const used = (evidence?.intent_used || []).length > 0;
    return { present: used, value: null, support: null };
  }
  const reasons = evidence?.reasons || [];
  const main = reasons.find((r) => r.type === family.valueType);
  const support = family.supportType ? reasons.find((r) => r.type === family.supportType) : null;
  return {
    present: !!(main || support),
    value: main ? Number(main.value) : null,
    support: support ? Number(support.value) : null,
  };
}

export const INTENT_FIELDS = {
  exploration_preference: {
    label: "Exploration",
    values: {
      familiar: ["Familiar", "Stay close to what you already know"],
      balanced: ["Balanced", "A mix of familiar and new"],
      exploratory: ["Exploratory", "Lean toward less familiar items"],
    },
  },
  popularity_preference: {
    label: "Popularity",
    values: {
      popular: ["Popular", "Favor widely chosen items"],
      neutral: ["Neutral", "No lean toward or away from popular items"],
      niche: ["Niche", "Favor less widely chosen items"],
    },
  },
};

export function intentChip(field, value) {
  const def = INTENT_FIELDS[field];
  if (!def) return { label: humanize(field), value: humanize(value), note: "" };
  const [name, note] = def.values[value] || [humanize(value), ""];
  return { label: def.label, value: name, note };
}

const listValue = (v) => (Array.isArray(v) ? joinList(v.map(String)) : String(v));

export const CONSTRAINTS = {
  requested_brand: { label: "Brand", noun: "brand", format: String },
  max_price: { label: "Price limit", noun: "price limit", format: (v) => `Under ${money(v)}` },
  min_price: { label: "Minimum price", noun: "minimum price", format: (v) => `From ${money(v)}` },
  use_case: { label: "Use case", noun: "use case", format: (v) => capitalize(String(v)) },
  priority_features: { label: "Must have", noun: "requested features", format: listValue },
  avoid_features: { label: "Avoid", noun: "features to avoid", format: listValue },
};

// Unverifiable constraints arrive as field names; human values live in parsed_intent.
export function describeConstraints(fields, parsedIntent) {
  return (fields || []).map((field) => {
    const def = CONSTRAINTS[field] || {
      label: humanize(field),
      noun: humanize(field).toLowerCase(),
      format: String,
    };
    const raw = parsedIntent ? parsedIntent[field] : undefined;
    const has = raw !== null && raw !== undefined && !(Array.isArray(raw) && raw.length === 0);
    return { field, label: def.label, noun: def.noun, value: has ? def.format(raw) : null };
  });
}

export function unverifiedFrom(result) {
  if (!result) return [];
  const intent = result.parsed_intent || {};
  const fields =
    (result.unverifiable_constraints?.length
      ? result.unverifiable_constraints
      : intent.unverifiable_constraints) || [];
  return describeConstraints(fields, intent);
}

const NEW = {
  value: "New shopper",
  note: "No previous interactions were available, so this ranking starts from catalog popularity.",
  kind: "new",
};
const LOW = {
  value: "Limited history",
  note: "Motive has a small amount of interaction history, so the ranking relies more on the behavioral and catalog signals available.",
  kind: "low",
};
const EST = {
  value: "Established history",
  note: "Behavioral history is available for this shopper.",
  kind: "established",
};

export const SEGMENTS = {
  new_user: NEW,
  cold_start: NEW,
  new: NEW,
  low_history: LOW,
  established: EST,
};

export function segmentInfo(segment) {
  if (!segment) return null;
  const s = SEGMENTS[segment] || {
    value: humanize(segment),
    note: "The shopper segment reported by the ranking service.",
    kind: "other",
  };
  return { label: "Profile", ...s };
}

export function sourceTags(source, intentUsed = []) {
  if (!source) return ["Learned ranking"];

  if (source.startsWith("tree_reranker")) {
    const usedIntent =
      Array.isArray(intentUsed) &&
      intentUsed.length > 0;

    return usedIntent
      ? ["Learned ranking", "Intent adjusted"]
      : ["Learned ranking"];
  }

  if (source.includes("popular")) {
    return ["Popularity ranking"];
  }

  return [humanize(source)];
}

// Constraint notes are shown once, above the list, so each explanation keeps
// only the part about why this item surfaced.
export function itemExplanation(text) {
  if (!text) return "";
  const markers = [" I understood your requested", " Some requested constraints"];
  let cut = text.length;
  for (const m of markers) {
    const i = text.indexOf(m);
    if (i !== -1 && i < cut) cut = i;
  }
  return text.slice(0, cut).trim();
}
