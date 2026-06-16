import type { GraphSource } from "../../data/types";

// ConnectorArray — the TARGET's 10-row CONNECTOR ARRAY (lines 550-564), kept READ-ONLY (ADR-010).
// The Neo4j dev_graph, Voice I/O, and LLM Uplink rows reflect live probe state from props; the rest
// mirror the project's connector inventory verbatim. No row ever mutates anything.
interface Props {
  source: GraphSource;
  voiceBridgeOnline: boolean;
  uplinkAvailable: boolean | null;
}

export function ConnectorArray({ source, voiceBridgeOnline, uplinkAvailable }: Props) {
  const neo4j =
    source === "live"
      ? { cls: "st-on", txt: "● LIVE BRIDGE" }
      : { cls: "st-sb", txt: "◐ LOCAL ONLY" };
  const voice = voiceBridgeOnline
    ? { cls: "st-on", txt: "● BRIDGE" }
    : { cls: "st-on", txt: "● WEB SPEECH" };
  const llm =
    uplinkAvailable === true
      ? { cls: "st-on", txt: "● LIVE (Claude)" }
      : uplinkAvailable === false
        ? { cls: "st-off", txt: "□ NO API KEY" }
        : { cls: "st-off", txt: "□ RESERVED SLOT" };

  const rows: { n: string; s: string; cls: string; txt: string }[] = [
    { n: "Web Intelligence", s: "market tape · news pull", cls: "st-on", txt: "● LIVE" },
    { n: "Embedded KB + Snapshot", s: "20 series · corpus → console", cls: "st-on", txt: "● LIVE" },
    { n: "Voice I/O", s: "Web Speech ⇄ local bridge (Whisper + Piper)", ...voice },
    { n: "Layer-2 Truth DB", s: "SQLite MCP", cls: "st-sb", txt: "◐ LOCAL ONLY" },
    { n: "Neo4j dev_graph", s: "bolt://localhost:7688", ...neo4j },
    { n: "mcpvault / Obsidian", s: "wiki read-write", cls: "st-sb", txt: "◐ LOCAL ONLY" },
    { n: "PostgreSQL", s: "graph sync target", cls: "st-sb", txt: "◐ LOCAL ONLY" },
    { n: "Google Drive", s: "doc search", cls: "st-dn", txt: "✕ NOT GRANTED" },
    { n: "Alpaca Paper API", s: "fills · GLD ETF", cls: "st-off", txt: "□ AWAITING E2b" },
    { n: "LLM Uplink", s: "Anthropic API · free-form Q&A", ...llm },
  ];

  return (
    <div className="panel">
      <div className="ph"><span className="pt">CONNECTOR ARRAY</span><span className="tag a">3 / 10 LIVE</span></div>
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
