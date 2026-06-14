import { useCallback, useState } from "react";
import { useClock } from "./hooks/useClock";
import { useCorpusCounter } from "./hooks/useCorpusCounter";
import { useGraph } from "./hooks/useGraph";
import { MainHud } from "./pages/MainHud";
import { OpsDeck } from "./pages/OpsDeck";
import { SystemFlow } from "./pages/SystemFlow";
import { useTheme } from "./theme/ThemeContext";

type Tab = "main" | "ops" | "flow";
const TABS: { id: Tab; label: string }[] = [
  { id: "main", label: "MAIN HUD" },
  { id: "ops", label: "OPS DECK" },
  { id: "flow", label: "SYSTEM FLOW" },
];

export default function App() {
  const graph = useGraph();
  const clock = useClock();
  const corpus = useCorpusCounter();
  const { theme, toggle } = useTheme();
  const [tab, setTab] = useState<Tab>("main");
  const [pendingQuery, setPendingQuery] = useState<string | null>(null);

  // a query raised on another tab → switch to the console and run it
  const raiseQuery = useCallback((q: string) => {
    setPendingQuery(q);
    setTab("main");
  }, []);
  const consumeQuery = useCallback(() => setPendingQuery(null), []);

  const sourcePill =
    graph.source === "live"
      ? `● LIVE · ${graph.nodeCount} nodes`
      : graph.source === "offline"
        ? `◐ OFFLINE · ${graph.nodeCount} nodes`
        : graph.ready ? "✕ NO GRAPH" : "◐ connecting…";

  return (
    <div className="wrap">
      <div className="hud">
        <div className="brand">
          EL NIÑO · JARVIS
          <small>GRAPH-GROUNDED OPS CONSOLE</small>
        </div>
        <div className="stat">
          <span className="pill">dev_graph {sourcePill}</span>
          <span className="pill">corpus {corpus.count} · day {corpus.day}</span>
        </div>
        <button className="theme-btn" onClick={toggle}>THEME · {theme.toUpperCase()}</button>
        <div className="clock">
          UTC<b>{clock}</b>
        </div>
      </div>

      <div className="tabs">
        {TABS.map((t) => (
          <button key={t.id} className={`tab ${tab === t.id ? "act" : ""}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === "main" && <MainHud graph={graph} pendingQuery={pendingQuery} onConsumed={consumeQuery} />}
      {tab === "ops" && <OpsDeck onQuery={raiseQuery} />}
      {tab === "flow" && <SystemFlow graph={graph} onQuery={raiseQuery} />}
    </div>
  );
}
