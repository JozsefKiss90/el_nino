import type { GraphStats } from "../../data/graph";

// Architecture — Layer model (L2 Truth → L3 El Niño → L4 Execution) (TARGET lines 649-656).
// The dev_graph size/ADR-range is derived from the loaded projection (graphStats) rather than a
// hardcoded string, so it can't drift (PROJECTION_SYNC_PLAN.md Rec 4); the fallback is the current
// projection's value for when the graph hasn't loaded yet.
export function Architecture({ stats }: { stats?: GraphStats | null }) {
  const graphLine = stats
    ? `${stats.nodes} nodes · ${stats.edges} edges · ${stats.adrRange}`
    : "159 nodes · 1113 edges · ADR-001–010";
  return (
    <section className="panel">
      <div className="ph"><span className="pt">ARCHITECTURE — LAYER MODEL</span><span className="tag c">SNAPSHOT-DRIVEN</span></div>
      <div className="lyr l2"><b>LAYER 2 — Truth Layer</b> &nbsp;<span style={{ color: "var(--accd)" }}>C:\Code\Mr-Ripley</span><br />Daily EOD macro snapshot: gold · USD · rates · volatility · macro. Quality gate, immutable snapshot_id (SHA-256), registry as single source of truth.</div>
      <div className="down">▼ &nbsp;ONLY published snapshots — never raw data, never "latest"</div>
      <div className="lyr l3"><b>LAYER 3 — El Niño</b> &nbsp;<span style={{ color: "var(--accd)" }}>C:\Code\el_nino</span><br />Snapshot Consumer → Feature Builder → Regime Classifier → Gold Decision Builder → Paper Runtime (ADMIT / HOLD / REJECT). dev_graph: {graphLine} · Neo4j + PostgreSQL + Obsidian.</div>
      <div className="down">▼ &nbsp;[E2b: Alpaca Execution Adapter — not yet built]</div>
      <div className="lyr l4"><b>LAYER 4 — Execution</b> &nbsp;<span style={{ color: "var(--red)" }}>PLANNED · NOT BUILDING</span><br />Alpaca Paper API → GLD ETF with virtual money · offline sim → deterministic replay.</div>
    </section>
  );
}
