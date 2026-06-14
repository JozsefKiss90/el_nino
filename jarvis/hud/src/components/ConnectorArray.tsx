import type { GraphSource, Health } from "../data/types";

// ConnectorArray — the live status of JARVIS's uplinks. The dev_graph, voice, and LLM rows are
// driven by real probes; the rest mirror the project's connector inventory.
interface Props {
  source: GraphSource;
  health: Health | null;
  nodeCount: number;
  voiceBridgeOnline: boolean;
  uplinkAvailable: boolean | null;
}

export function ConnectorArray({ source, health, nodeCount, voiceBridgeOnline, uplinkAvailable }: Props) {
  const neo4j =
    source === "live"
      ? { cls: "st-on", txt: `● LIVE (${health?.node_count ?? nodeCount} nodes)` }
      : source === "offline"
        ? { cls: "st-sb", txt: `◐ OFFLINE (${nodeCount} nodes)` }
        : { cls: "st-dn", txt: "✕ NO GRAPH" };

  const voice = voiceBridgeOnline
    ? { cls: "st-on", txt: "● BRIDGE (Whisper+Piper)" }
    : { cls: "st-sb", txt: "◐ WEB SPEECH (fallback)" };

  const uplink =
    uplinkAvailable === true
      ? { cls: "st-on", txt: "● LIVE (Claude)" }
      : uplinkAvailable === false
        ? { cls: "st-off", txt: "□ NO API KEY" }
        : { cls: "st-off", txt: "□ RESERVED SLOT" };

  const rows: { n: string; s: string; cls: string; txt: string }[] = [
    { n: "Neo4j dev_graph", s: "read-only bridge · graph.json", ...neo4j },
    { n: "Voice I/O", s: "Web Speech ⇄ local bridge", ...voice },
    { n: "LLM Uplink", s: "Anthropic API · GraphRAG /ask", ...uplink },
    { n: "Web Intelligence", s: "market tape · news pull", cls: "st-on", txt: "● LIVE" },
    { n: "Layer-2 Truth DB", s: "SQLite", cls: "st-sb", txt: "◐ LOCAL ONLY" },
    { n: "Alpaca Paper API", s: "fills · GLD ETF", cls: "st-off", txt: "□ AWAITING E2b" },
    { n: "Google Drive", s: "doc search", cls: "st-dn", txt: "✕ NOT GRANTED" },
  ];

  return (
    <div className="panel">
      <div className="ph">
        <span className="pt">CONNECTOR ARRAY</span>
        <span className="tag a">READ-ONLY</span>
      </div>
      <div className="conn">
        {rows.map((r) => (
          <div className="cn" key={r.n}>
            <span className="n">{r.n}<small>{r.s}</small></span>
            <span className={r.cls}>{r.txt}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
