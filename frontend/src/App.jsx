import { useCallback, useEffect, useRef, useState } from "react";
import AppHeader, { NAV } from "./components/AppHeader.jsx";
import DiscoverWorkspace from "./components/DiscoverWorkspace.jsx";
import SystemPage from "./components/SystemPage.jsx";
import IntentPage from "./components/IntentPage.jsx";
import TrustPage from "./components/TrustPage.jsx";
import useRecentRequests from "./hooks/useRecentRequests.js";
import useTheme from "./hooks/useTheme.js";
import useActiveSection from "./hooks/useActiveSection.js";
import useEngineStatus from "./hooks/useEngineStatus.js";
import { getIntelligentRecommendations } from "./services/api.js";
import { unverifiedFrom } from "./lib/labels.js";
import { DIRECTIONS } from "./components/QuickDirections.jsx";

const NAV_IDS = NAV.map(([id]) => id);

const reduceMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

function validate(form) {
  const errors = {};
  if (!form.query.trim()) errors.query = "Describe which way the ranking should move, or pick a direction.";
  const id = form.shopperId.trim();
  if (!id) errors.shopperId = "Enter a shopper ID, or use the demo shopper.";
  else if (!/^\d+$/.test(id)) errors.shopperId = "Shopper IDs are whole numbers.";
  const k = Number(form.k);
  if (!Number.isInteger(k) || k < 1 || k > 100) errors.k = "Choose between 1 and 100 results.";
  return errors;
}

export default function App() {
  // Everything the user is working on lives here, so moving between
  // sections never erases a request or its results.
  const [form, setForm] = useState({ query: DIRECTIONS[0].query, shopperId: "", k: 5 });
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [lastRequest, setLastRequest] = useState(null);
  const [runId, setRunId] = useState(0);
  const [composerOpen, setComposerOpen] = useState(false);
  const [announcement, setAnnouncement] = useState("");

  const controller = useRef(null);
  const pending = useRef(null);
  const resultsRef = useRef(null);

  const { recent, add: addRecent, clear: clearRecent } = useRecentRequests();
  const { theme, toggle: toggleTheme } = useTheme();
  const active = useActiveSection(NAV_IDS);
  const engine = useEngineStatus();

  useEffect(() => () => controller.current?.abort(), []);

  const setField = useCallback((key, value) => {
    setForm((f) => ({ ...f, [key]: value }));
    setErrors((e) => (e[key] ? { ...e, [key]: undefined } : e));
  }, []);

  const run = useCallback(
    async (override) => {
      const req = { ...form, ...(override || {}) };
      const errs = validate(req);
      setErrors(errs);
      if (Object.keys(errs).length) {
        setAnnouncement("Please fix the highlighted fields.");
        return;
      }
      if (status === "loading") return; // no duplicate submissions

      controller.current?.abort();
      const c = new AbortController();
      controller.current = c;
      pending.current = req;

      const hadResult = !!result;
      setStatus("loading");
      setError(null);
      setRunId((n) => n + 1);
      setAnnouncement("Ranking in progress.");

      try {
        const data = await getIntelligentRecommendations(req, c.signal);
        if (c.signal.aborted) return;
        setResult(data);
        setLastRequest(req);
        setStatus("done");
        setComposerOpen(false);
        addRecent(req);
        const n = (data.recommendations || []).length;
        setAnnouncement(`Ranking complete. ${n} ${n === 1 ? "item" : "items"} ranked.`);
        if (!hadResult) {
          requestAnimationFrame(() =>
            document.getElementById("discover")?.scrollIntoView({ behavior: reduceMotion() ? "auto" : "smooth", block: "start" })
          );
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        setError(err);
        setStatus("error");
        setAnnouncement(`Ranking didn't complete. ${err.message}`);
      }
    },
    [form, status, result, addRecent]
  );

  const runDirection = useCallback(
    (d) => {
      setField("query", d.query);
      run({ query: d.query });
    },
    [run, setField]
  );

  const retry = useCallback(() => run(pending.current || undefined), [run]);

  return (
    <>
      <a className="skip-link" href="#discover">Skip to Discover</a>
      <AppHeader active={active} engine={engine} theme={theme} onToggleTheme={toggleTheme} />

      <main>
        <DiscoverWorkspace
          form={form}
          setField={setField}
          errors={errors}
          status={status}
          result={result}
          error={error}
          lastRequest={lastRequest}
          runId={runId}
          onSubmit={() => run()}
          onRunDirection={runDirection}
          onRetry={retry}
          recent={recent}
          clearRecent={clearRecent}
          composerOpen={composerOpen}
          setComposerOpen={setComposerOpen}
          resultsRef={resultsRef}
        />
        <SystemPage />
        <IntentPage />
        <TrustPage latestConstraints={unverifiedFrom(result)} />
      </main>

      <footer className="footer">
        <div className="wrap footer-inner">
          <p>
            <strong>Motive</strong> ranks the anonymized Retailrocket e-commerce dataset with a
            learned tree model. Claude interprets requests into structured intent.
          </p>
          <a href="/docs" target="_blank" rel="noopener noreferrer">
            API reference<span className="visually-hidden"> (opens in a new tab)</span>
            <svg viewBox="0 0 12 12" aria-hidden="true" className="ext"><path d="M4.5 2.5h5v5M9.5 2.5 3 9" /></svg>
          </a>
        </div>
      </footer>

      <div className="visually-hidden" aria-live="polite" aria-atomic="true">{announcement}</div>
    </>
  );
}
