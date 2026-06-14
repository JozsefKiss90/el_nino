import { useState } from "react";
import { GraphView } from "../components/GraphView";
import { FlowInvariants } from "../components/flow/FlowInvariants";
import { GovernanceSpine } from "../components/flow/GovernanceSpine";
import { LaNinaBranch } from "../components/flow/LaNinaBranch";
import { ProgressiveReveal } from "../components/flow/ProgressiveReveal";
import type { GraphHook } from "../hooks/useGraph";

// SystemFlow — the #pg-flow page ported 1:1 from the TARGET (jarvis/sources/
// el_nino_jarvis_interface (6).html, lines 715-862). The full-width sticky .frail rail sits above
// the .fgrid (as in the source); the grid carries the LEFT progressive-reveal flow and the RIGHT
// stack of three governance panels. AFTER the grid we fold in the HUD-only full dev_graph projection
// via the shared GraphView — a feature the static TARGET lacks, preserved read-only per ADR-010.
const STEP_COUNT = 8;
const NEXT_NAMES = [
  "LAYER 2 — ADAPTERS & TRUTH DB",
  "QUALITY GATE",
  "SNAPSHOT PUBLISHER",
  "LAYER 3 — EL NIÑO DECISION CHAIN",
  "RECORD & REVIEW",
  "EXECUTION — PAPER FIRST",
  "PHASE D — LIVE EXECUTION GATE",
];

export function SystemFlow({ graph, onQuery }: { graph: GraphHook; onQuery: (q: string) => void }) {
  const [revealed, setRevealed] = useState(1);
  const complete = revealed >= STEP_COUNT;
  const hint = complete ? "" : `NEXT: ${revealed + 1} / ${STEP_COUNT} — ${NEXT_NAMES[revealed - 1]}`;

  return (
    <div className="page show" id="pg-flow">
      <div className="frail">
        <span className="lbl">SYSTEM FLOW — PROGRESSIVE REVEAL</span>
        <div className="rsteps">
          {Array.from({ length: STEP_COUNT }, (_, i) => (
            <div key={i} className={`rstep${i < revealed ? " on" : ""}`}></div>
          ))}
        </div>
        <span className="rcount">{revealed}/{STEP_COUNT}</span>
      </div>

      <div className="fgrid">
        <ProgressiveReveal
          revealed={revealed}
          complete={complete}
          hint={hint}
          onNext={() => setRevealed((c) => Math.min(c + 1, STEP_COUNT))}
          onAll={() => setRevealed(STEP_COUNT)}
        />
        <div className="fcol" style={{ gap: "14px" }}>
          <GovernanceSpine />
          <LaNinaBranch />
          <FlowInvariants />
        </div>
      </div>

      <div className="panel gv-wrap">
        <div className="ph">
          <span className="pt">DEV_GRAPH — FULL PROJECTION</span>
          <span className="tag c">{graph.nodeCount} nodes · {graph.edgeCount} edges</span>
        </div>
        {graph.graph ? (
          <GraphView graph={graph.graph} height={560} onNodeClick={(id) => onQuery(id)} />
        ) : (
          <div className="gv-empty">Graph not loaded — start the bridge or serve graph.json.</div>
        )}
      </div>
    </div>
  );
}
