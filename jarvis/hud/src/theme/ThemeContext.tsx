// ThemeContext — JARVIS (cyan) / PIXEL (green) via the data-theme attribute on <html>.
// The CSS-token theme (theme.css) is unchanged; only the attribute flips.

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type Theme = "jarvis" | "pixel";

interface ThemeCtx {
  theme: Theme;
  toggle: () => void;
  setTheme: (t: Theme) => void;
}

const Ctx = createContext<ThemeCtx | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("jarvis");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const value = useMemo<ThemeCtx>(
    () => ({ theme, setTheme, toggle: () => setTheme((t) => (t === "jarvis" ? "pixel" : "jarvis")) }),
    [theme],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useTheme(): ThemeCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("useTheme must be used within ThemeProvider");
  return v;
}
