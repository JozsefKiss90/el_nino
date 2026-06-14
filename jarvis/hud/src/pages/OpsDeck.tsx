import { DriftTable } from "../components/DriftTable";
import { FlowStage } from "../components/FlowStage";
import { OperatorPanel } from "../components/OperatorPanel";

// OpsDeck — doctrine, the Layer-3 flow, and the audit-drift board. Clicking a flow stage jumps to
// the console with that node's query (onQuery switches tabs).
export function OpsDeck({ onQuery }: { onQuery: (q: string) => void }) {
  return (
    <div className="col">
      <FlowStage onPick={onQuery} />
      <div className="grid3" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <OperatorPanel />
        <DriftTable />
      </div>
    </div>
  );
}
