// snapshot.ts — the canonical decision snapshot + display series, ported from the TARGET's `SNAP`
// data (jarvis/sources/el_nino_jarvis_interface (6).html, `var SNAP` ~line 910). The HUD is
// read-only; these are PRESENTATION constants (not live data). Values are the TARGET's as of the
// 2026-03-15 snapshot / 2026-06-12 web pull — a data refresh is a separate pass (see README).

export interface Series {
  id: string;
  name: string;
  value: number;
  unit: string;
  staleDays: number;
  source: string;
  tier: 1 | 2;
  group: string;
}

/** The last full Layer-3 run (snapshot 2026-03-15, verdict PASS → AVOID, admitted). */
export const SNAPSHOT = {
  date: "2026-03-15",
  verdict: "PASS",
  regime: "RESTRICTIVE_RATES",
  confidence: "0.397",
  direction: "AVOID",
  admission: "ADMIT",
  asset: "GOLD · GLD",
  guards:
    "data_ok: true · idempotent_ok: true · cooldown_ok: true · risk_ok: true · supervisor_veto: false",
} as const;

/** All 20 series from the March snapshot (SNAP.s), in source order. */
export const SERIES: Series[] = [
  { id: "T10YIE", name: "10-year breakeven inflation", value: 2.36, unit: "%", staleDays: 2, source: "FRED", tier: 1, group: "breakeven" },
  { id: "T5YIE", name: "5-year breakeven inflation", value: 2.61, unit: "%", staleDays: 2, source: "FRED", tier: 1, group: "breakeven" },
  { id: "T5YIFR", name: "5-year/5-year forward inflation", value: 2.11, unit: "%", staleDays: 2, source: "FRED", tier: 1, group: "breakeven" },
  { id: "gold_price_proxy", name: "gold spot XAU/USD", value: 5019.7, unit: " dollars", staleDays: 2, source: "goldapi.com", tier: 1, group: "gold" },
  { id: "DGS10", name: "10-year Treasury nominal yield", value: 4.27, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "nominal yields" },
  { id: "DGS2", name: "2-year Treasury nominal yield", value: 3.76, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "nominal yields" },
  { id: "DGS5", name: "5-year Treasury nominal yield", value: 3.88, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "nominal yields" },
  { id: "DFF", name: "effective fed funds rate", value: 3.64, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "policy rate" },
  { id: "EFFR", name: "New York Fed EFFR", value: 3.64, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "policy rate" },
  { id: "DFII10", name: "10-year TIPS real yield", value: 1.89, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "real yields" },
  { id: "DFII5", name: "5-year TIPS real yield", value: 1.25, unit: "%", staleDays: 3, source: "FRED", tier: 1, group: "real yields" },
  { id: "SP500", name: "S&P 500 index", value: 6632.19, unit: " points", staleDays: 2, source: "FRED", tier: 1, group: "risk" },
  { id: "VIXCLS", name: "VIX equity implied volatility", value: 27.29, unit: "", staleDays: 3, source: "FRED", tier: 1, group: "stress" },
  { id: "rates_vol_stress_move", name: "MOVE index, bond market stress", value: 91.17, unit: "", staleDays: 2, source: "Yahoo", tier: 1, group: "stress" },
  { id: "DTWEXBGS", name: "broad USD index", value: 119.491, unit: "", staleDays: 9, source: "FRED", tier: 1, group: "USD" },
  { id: "gld_holdings_flow_confirm", name: "GLD Trust ounces held", value: 24949755, unit: " ounces", staleDays: 9, source: "Yahoo GLD proxy", tier: 2, group: "flow" },
  { id: "CPILFESL", name: "core CPI index", value: 333.512, unit: "", staleDays: 42, source: "FRED", tier: 2, group: "monthly inflation" },
  { id: "FEDFUNDS", name: "fed funds rate, monthly average", value: 3.64, unit: "%", staleDays: 42, source: "FRED", tier: 2, group: "monthly inflation" },
  { id: "PCEPI", name: "headline PCE index", value: 128.969, unit: "", staleDays: 73, source: "FRED", tier: 2, group: "monthly inflation" },
  { id: "PCU2122212122210", name: "PPI gold ore mining, discontinued in 2017", value: 314.7, unit: "", staleDays: 3026, source: "FRED", tier: 2, group: "monthly inflation" },
];

/** The 8 macro-series shown as orbit chips around the reactor (DECISION CORE), in display order. */
export interface Orbit {
  label: string;
  value: string;
  source: string;
  warn?: boolean;
}
export const ORBITS: Orbit[] = [
  { label: "GOLD XAU", value: "5,019.70", source: "goldapi · 2d" },
  { label: "DGS10", value: "4.27%", source: "FRED · 3d" },
  { label: "DFII10 REAL", value: "1.89%", source: "FRED · 3d" },
  { label: "VIX", value: "27.29", source: "FRED · 3d", warn: true },
  { label: "MOVE", value: "91.17", source: "Yahoo · 2d", warn: true },
  { label: "T10YIE BE", value: "2.36%", source: "FRED · 2d" },
  { label: "USD BROAD", value: "119.49", source: "FRED · 9d" },
  { label: "EFFR", value: "3.64%", source: "FRED · 3d" },
];

/** DECISION CORE readout strip — regime / confidence / direction / admission, with color buckets. */
export const CORE_READ: { k: string; v: string; cls: "c" | "a" | "r" | "g" }[] = [
  { k: "REGIME", v: SNAPSHOT.regime, cls: "c" },
  { k: "CONFIDENCE", v: SNAPSHOT.confidence, cls: "a" },
  { k: "DIRECTION", v: SNAPSHOT.direction, cls: "r" },
  { k: "ADMISSION", v: SNAPSHOT.admission, cls: "g" },
];

/** SYSTEM VITALS gauges — independent module audit scores. dasharray 194.8 = 2π·r (r=31). */
export interface Gauge {
  score: number;
  dashoffset: string;
  mod: string;
  label: string;
}
export const VITALS_GAUGES: Gauge[] = [
  { score: 97, dashoffset: "5.8", mod: "MOD-005", label: "REGIME" },
  { score: 94, dashoffset: "11.7", mod: "MOD-006", label: "DECISION" },
  { score: 97, dashoffset: "5.8", mod: "MOD-007", label: "RUNTIME" },
];
