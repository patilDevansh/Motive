import { useEffect, useState } from "react";

// Tracks which main section is in view and mirrors it in the URL hash
// (replaceState, so the back button isn't flooded).
export default function useActiveSection(ids) {
  const [active, setActive] = useState(() => {
    const h = window.location.hash.slice(1);
    return ids.includes(h) ? h : ids[0];
  });

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return undefined;
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: "-30% 0px -60% 0px" }
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, [ids]);

  useEffect(() => {
    if (window.location.hash.slice(1) !== active) {
      window.history.replaceState(null, "", `#${active}`);
    }
  }, [active]);

  return active;
}
