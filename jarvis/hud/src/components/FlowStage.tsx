// FlowStage — the Layer-3 analysis pipeline. Click a stage to ask the graph about that module.
const STAGES: { id: string; name: string; sub: string }[] = [
  { id: "Snapshot Consumer", name: "CONSUME", sub: "MOD-003 · SCHEMA-001 → Snapshot" },
  { id: "Feature Builder", name: "FEATURES", sub: "MOD-004 · → SCHEMA-009" },
  { id: "Regime Classifier", name: "CLASSIFY", sub: "MOD-005 · → SCHEMA-010" },
  { id: "Gold Decision Builder", name: "DECIDE", sub: "MOD-006 · → SCHEMA-011" },
  { id: "Paper Runtime", name: "ADMIT", sub: "MOD-007 · → SCHEMA-012" },
];

export function FlowStage({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="panel">
      <div className="ph">
        <span className="pt">LAYER-3 ANALYSIS FLOW</span>
        <span className="tag c">consume → build → classify → decide → admit</span>
      </div>
      <div className="flowstage">
        {STAGES.map((s, i) => (
          <span key={s.id} style={{ display: "flex", gap: 8 }}>
            <span className="fnode" style={{ cursor: "pointer" }} onClick={() => onPick(s.id)}>
              {s.name}
              <small>{s.sub}</small>
            </span>
            {i < STAGES.length - 1 && <span className="fsep">▶</span>}
          </span>
        ))}
      </div>
    </div>
  );
}
