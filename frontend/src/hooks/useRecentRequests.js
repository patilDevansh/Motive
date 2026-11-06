import { useCallback, useState } from "react";

// Last few requests, stored only in this browser's localStorage.
// Nothing here is sent anywhere.
const KEY = "motive.recent-requests";
const MAX = 5;

function read() {
  try {
    const raw = window.localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list.filter((r) => r && typeof r.query === "string").slice(0, MAX) : [];
  } catch {
    return [];
  }
}

function write(list) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* storage unavailable: recent list simply won't persist */
  }
}

export default function useRecentRequests() {
  const [recent, setRecent] = useState(read);

  const add = useCallback((req) => {
    setRecent((prev) => {
      const q = req.query.trim();
      const next = [
        { query: q, shopperId: String(req.shopperId), k: req.k },
        ...prev.filter((r) => r.query.toLowerCase() !== q.toLowerCase()),
      ].slice(0, MAX);
      write(next);
      return next;
    });
  }, []);

  const clear = useCallback(() => {
    write([]);
    setRecent([]);
  }, []);

  return { recent, add, clear };
}
