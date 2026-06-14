import { useCallback, useState } from "react";
import { useClock } from "./hooks/useClock";
import { useCorpusCounter } from "./hooks/useCorpusCounter";
import { useGraph } from "./hooks/useGraph";
import { MainHud } from "./pages/MainHud";
import { OpsDeck } from "./pages/OpsDeck";
import { SystemFlow } from "./pages/SystemFlow";
import { useTheme } from "./theme/ThemeContext";

type Tab = "main" | "ops" | "flow";

// App — the persistent chrome (top HUD · nav · ticker · footer) ported 1:1 from the TARGET
// (jarvis/sources/el_nino_jarvis_interface (6).html, lines 396–430, 864–867). The three live tabs
// swap pages; the two `.off` tabs are inert placeholders, matching the source. The dynamic
// graph/corpus state the HUD added surfaces inside the panels (TRUTH CORPUS, CONNECTOR ARRAY,
// KNOWLEDGE GRAPH), so the top-row pills stay verbatim.
export default function App() {
  const graph = useGraph();
  const clock = useClock(); // "YYYY-MM-DD HH:MM:SS UTC"
  const corpus = useCorpusCounter();
  const { theme, toggle } = useTheme();
  const [tab, setTab] = useState<Tab>("main");
  const [pendingQuery, setPendingQuery] = useState<string | null>(null);

  // a query raised on another tab → switch to the console (MAIN) and run it
  const raiseQuery = useCallback((q: string) => {
    setPendingQuery(q);
    setTab("main");
  }, []);
  const consumeQuery = useCallback(() => setPendingQuery(null), []);

  const time = clock.slice(11, 19) || "--:--:--";
  const date = clock.slice(0, 10) || "SYNCING…";

  return (
    <div className="wrap">
      {/* ================= TOP HUD ================= */}
      <div className="hud">
        <div className="brand">
          EL NIÑO<small>GOLD-FIRST · FAIL-CLOSED · SNAPSHOT-DRIVEN DECISION SYSTEM</small>
        </div>
        <div className="stat">
          <span className="pill on"><i>●</i>L2 TRUTH ONLINE</span>
          <span className="pill on"><i>●</i>L3 OPERATIONAL</span>
          <span className="pill warn"><i>◐</i>E2b PENDING</span>
          <span className="pill block"><i>⛔</i>LIVE EXEC BLOCKED</span>
        </div>
        <button className="theme-btn" onClick={toggle}>
          THEME: {theme === "jarvis" ? "JARVIS" : "PIXEL"} ◄►
        </button>
        <div className="clock"><b>{time}</b><span>{date} UTC</span></div>
      </div>

      {/* ================= NAV ================= */}
      <div className="nav">
        <button className={`tab ${tab === "main" ? "act" : ""}`} onClick={() => setTab("main")}>MAIN · JARVIS HUD</button>
        <button className={`tab ${tab === "ops" ? "act" : ""}`} onClick={() => setTab("ops")}>OPS DECK</button>
        <button className={`tab ${tab === "flow" ? "act" : ""}`} onClick={() => setTab("flow")}>SYSTEM FLOW</button>
        <button className="tab off" title="Placeholder — wires to Neo4j dev_graph (140 nodes / 920 edges)">GRAPH 3D — OFFLINE</button>
        <button className="tab off" title="Placeholder — unlocks after E2b scorecard ships">BACKTEST LAB — AWAITING E2b</button>
      </div>

      {/* ================= TICKER ================= */}
      <div className="ticker" aria-label="Market and system feed">
        <div className="tk">
          <span>XAU/USD <b>≈4,195</b> <i className="tdn">▼</i> <i className="twn">−16.4% since AVOID call @5,019</i></span>
          <span>US10Y <b>≈4.54%</b> <i className="twn">restrictive regime persists</i></span>
          <span className="twn">/// MACRO: US–IRAN CONFLICT · ENERGY-DRIVEN CPI AT 3-YEAR HIGH · FED HIKE PRICED FOR DEC ///</span>
          <span>SNAPSHOT DB: 20 SERIES · 15/15 TIER-1 PASS</span>
          <span className="tup">/// NEXT SNAPSHOT: TONIGHT 23:00 — MrRipley-Layer2-DailyEOD ///</span>
          <span className="tup">/// DEBT-01: FIXED 2026-06-11 ///</span>
          <span>TESTS <b className="tup">853 GREEN</b></span>
          <span>AUDITS <b className="twn">97 · 94 · 97</b></span>
          <span className="tdn">/// PHASE D: LIVE EXECUTION GATE — BLOCKED BY DESIGN ///</span>
        </div>
      </div>

      {/* ================= PAGES ================= */}
      {tab === "main" && (
        <MainHud graph={graph} corpus={corpus} pendingQuery={pendingQuery} onConsumed={consumeQuery} />
      )}
      {tab === "ops" && <OpsDeck corpus={corpus} onQuery={raiseQuery} />}
      {tab === "flow" && <SystemFlow graph={graph} onQuery={raiseQuery} />}

      {/* ================= FOOTER ================= */}
      <footer className="foot">
        <span>MR. RIPLEY / EL NIÑO · JARVIS INTERFACE v3 · VOICE + SNAPSHOT KB + THEME</span>
        <span>TRUTH IS CONSTRAINED · CLAIMS ARE EARNED · EXECUTION IS FORBIDDEN UNTIL PROVEN SAFE</span>
        <span>GENERATED 2026-06-12 · MARKET INTEL: WEB PULL (APPROX.)</span>
      </footer>
    </div>
  );
}
