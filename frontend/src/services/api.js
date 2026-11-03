// All API calls use same-origin relative URLs: FastAPI serves both the React
// build and the API, so no host or port is ever hardcoded.

export class ApiError extends Error {
  constructor(message, status, kind = "api") {
    super(message);
    this.name = "ApiError";
    this.status = status; // 0 = network failure
    this.kind = kind; // network | api | unexpected
  }
}

function readDetail(data, status) {
  const detail = data && data.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
  return `The ranking service responded with status ${status}.`;
}

function looksValid(data) {
  return (
    data &&
    typeof data === "object" &&
    Array.isArray(data.recommendations) &&
    (data.evidence === undefined || Array.isArray(data.evidence)) &&
    (data.explanations === undefined || Array.isArray(data.explanations))
  );
}

export async function getIntelligentRecommendations({ shopperId, query, k }, signal) {
  let response;
  try {
    response = await fetch("/recommend/intelligent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: Number(shopperId), query: query.trim(), k: Number(k) }),
      signal,
    });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new ApiError("We couldn't reach the ranking service.", 0, "network");
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) throw new ApiError(readDetail(data, response.status), response.status, "api");
  if (!looksValid(data)) {
    throw new ApiError(
      "The ranking service returned a response Motive couldn't read.",
      response.status,
      "unexpected"
    );
  }
  return data;
}

export async function getHealth(signal) {
  try {
    const res = await fetch("/health", { signal });
    if (!res.ok) return false;
    const data = await res.json();
    return data?.status === "healthy";
  } catch {
    return false;
  }
}
