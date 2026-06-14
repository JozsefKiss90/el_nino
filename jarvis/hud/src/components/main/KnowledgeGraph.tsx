import type { Answer } from "../../data/types";
import { GraphView } from "../GraphView";

// KnowledgeGraph — the TARGET's KNOWLEDGE GRAPH panel (lines 474-480) with its triple-substrate
// stat rows, now ALSO hosting the live dev_graph view: when the console matches a node, its focus +
// neighborhood render here (click a node to pull it into the console). Read-only (ADR-010).
export function KnowledgeGraph({ answer, onQuery }: { answer: Answer | null; onQuery: (q: string) => void }) {
  const hasGraph = !!answer && answer.subgraph.nodes.length > 0;
  return (
    <div className="panel gv-wrap">
      <div className="ph"><span className="pt">KNOWLEDGE GRAPH</span><span className="tag c">TRIPLE SUBSTRATE</span></div>
      <div className="kv"><span className="k">dev_graph</span><span className="v c">~140 nodes · ~920 edges</span></div>
      <div className="kv"><span className="k">Wiki</span><span className="v">57 pages · ~852 wikilinks</span></div>
      <div className="kv"><span className="k">ADR chain</span><span className="v">ADR-001 → 009</span></div>
      <div className="kv"><span className="k">Substrate</span><span className="v">Neo4j · PostgreSQL · Obsidian</span></div>
      {hasGraph ? (
        <div style={{ marginTop: 10 }}>
          <GraphView graph={answer!.subgraph} focus={answer!.focus} onNodeClick={(_id, name) => onQuery(name)} />
        </div>
      ) : (
        <div className="gv-empty" style={{ marginTop: 8 }}>
          Ask the console a structural question and the matched node + neighborhood render here. Click a node to expand it.
        </div>
      )}
    </div>
  );
}
