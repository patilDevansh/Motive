import { useEffect, useState } from "react";
import { getHealth } from "../services/api.js";

// Polls the real /health route for the header status indicator.
export default function useEngineStatus(intervalMs = 30000) {
  const [status, setStatus] = useState("checking");
  useEffect(() => {
    const c = new AbortController();
    const check = async () => {
      const ok = await getHealth(c.signal);
      if (!c.signal.aborted) setStatus(ok ? "online" : "offline");
    };
    check();
    const id = setInterval(check, intervalMs);
    return () => {
      c.abort();
      clearInterval(id);
    };
  }, [intervalMs]);
  return status;
}
