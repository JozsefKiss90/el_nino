import { FlowStage } from "../components/FlowStage";
import { GraphView } from "../components/GraphView";
import type { GraphHook } from "../hooks/useGraph";

// SystemFlow — the whole dev_graph rendered with the shared GraphView, plus the Layer-3 flow.
// Clicking any node jumps to the console with a query about it.
export function SystemFlow({ graph, onQuery }: { graph: GraphHook; onQuery: (q: string) => void }) {
  return (
    <div className="col">
      <FlowStage onPick={onQuery} />
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
