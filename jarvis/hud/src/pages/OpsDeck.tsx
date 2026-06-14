import { Architecture } from "../components/ops/Architecture";
import { AuditDriftStatus } from "../components/ops/AuditDriftStatus";
import { EpochRoadmap } from "../components/ops/EpochRoadmap";
import { LivePipelineResult } from "../components/ops/LivePipelineResult";
import { MetricCards } from "../components/ops/MetricCards";
import { NextActions } from "../components/ops/NextActions";
import { PipelineStatus } from "../components/ops/PipelineStatus";
import { The12PivotalPoints } from "../components/ops/The12PivotalPoints";

// OpsDeck (#pg-ops) — the operations deck: pipeline status, metric cards, the single live L3 run,
// the epoch roadmap, layer-model architecture + action queue, the 12 parked questions, and the
// Mr-Ripley audit-drift board. Ported 1:1 from the TARGET (jarvis/sources/el_nino_jarvis_interface
// (6).html, lines 597-712). The corpus count is live (App's counter); clicking a pipeline module
// raises a cross-page graph query (onQuery) that switches to the console and queries that node.
export function OpsDeck({ corpus, onQuery }: { corpus: { count: number; day: number }; onQuery: (q: string) => void }) {
  return (
    <div className="page show" id="pg-ops">
      <PipelineStatus onQuery={onQuery} />
      <MetricCards corpus={corpus} />
      <LivePipelineResult />
      <EpochRoadmap />
      <div className="grid two">
        <Architecture />
        <NextActions />
      </div>
      <The12PivotalPoints />
      <AuditDriftStatus />
    </div>
  );
}
