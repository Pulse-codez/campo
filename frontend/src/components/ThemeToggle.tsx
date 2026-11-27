"use client";

import { useSyncExternalStore } from "react";

type Theme = "light" | "dark";

export const THEME_KEY = "csc_theme";

function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => observer.disconnect();
}

function readTheme(): Theme {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function useTheme(): Theme {
  return useSyncExternalStore(subscribe, readTheme, () => "dark" as Theme);
}

export default function ThemeToggle() {
  const theme = useTheme();

  function toggle() {
    const next: Theme = readTheme() === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      // Storage can be blocked (private mode). The theme still changes for this visit.
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      className="rounded-full border border-[rgb(var(--fg)/0.2)] bg-[rgb(var(--surface))] px-3.5 py-1.5 text-xs font-semibold text-[rgb(var(--fg))] transition-colors hover:border-[rgb(var(--link))]"
    >
      {theme === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}
