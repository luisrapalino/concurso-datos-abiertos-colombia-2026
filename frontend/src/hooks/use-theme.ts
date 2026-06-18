"use client";

import { useCallback, useEffect, useState } from "react";

export const THEME_STORAGE_KEY = "radar-theme";

export type ThemePreference = "light" | "dark" | "system";

function resolveDark(preference: ThemePreference) {
  if (preference === "dark") return true;
  if (preference === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(preference: ThemePreference) {
  const isDark = resolveDark(preference);
  document.documentElement.classList.toggle("dark", isDark);
  document.documentElement.style.colorScheme = isDark ? "dark" : "light";
  return isDark;
}

export function useTheme() {
  const [preference, setPreference] = useState<ThemePreference>("system");
  const [resolved, setResolved] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemePreference | null;
    const initial = stored ?? "system";
    setPreference(initial);
    setResolved(applyTheme(initial) ? "dark" : "light");
  }, []);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if (preference === "system") {
        setResolved(applyTheme("system") ? "dark" : "light");
      }
    };
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, [preference]);

  const setTheme = useCallback((next: ThemePreference) => {
    localStorage.setItem(THEME_STORAGE_KEY, next);
    setPreference(next);
    setResolved(applyTheme(next) ? "dark" : "light");
  }, []);

  const toggle = useCallback(() => {
    setTheme(resolved === "dark" ? "light" : "dark");
  }, [resolved, setTheme]);

  return { preference, resolved, setTheme, toggle };
}
