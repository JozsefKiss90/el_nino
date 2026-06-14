// PipelineStatus — Layer-3 chain of five module cards (TARGET lines 599-614). Each .mod is
// clickable: onQuery(moduleName) raises a cross-page graph query (App switches to the console).
export function PipelineStatus({ onQuery }: { onQuery: (q: string) => void }) {
  return (
    <section className="panel" style={{ marginBottom: "14px" }}>
      <div className="ph"><span className="pt">PIPELINE STATUS — LAYER 3 CHAIN</span><span className="tag g">853 TESTS · ALL GREEN</span></div>
      <div className="lane">
        <div className="mod" onClick={() => onQuery("Snapshot Consumer")} style={{ cursor: "pointer" }}><div className="id">MOD-003</div><div className="nm">Snapshot Consumer</div><div className="stt"><span className="ok">✔ DONE</span><span className="sc">fail-closed</span></div>
          <div className="caps"><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span></div></div>
        <div className="mod" onClick={() => onQuery("Feature Builder")} style={{ cursor: "pointer" }}><div className="id">MOD-004</div><div className="nm">Feature Builder</div><div className="stt"><span className="ok">✔ DONE</span><span className="sc">14 features</span></div>
          <div className="caps"><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span><span className="cap f"></span></div></div>
        <div className="mod" onClick={() => onQuery("Regime Classifier")} style={{ cursor: "pointer" }}><div className="id">MOD-005</div><div className="nm">Regime Classifier</div><div className="stt"><span className="ok">✔ DONE</span><span className="sc">AUDIT 97/100</span></div>
          <div className="caps"><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span></div></div>
        <div className="mod" onClick={() => onQuery("Gold Decision Builder")} style={{ cursor: "pointer" }}><div className="id">MOD-006</div><div className="nm">Gold Decision Builder</div><div className="stt"><span className="ok">✔ DONE</span><span className="sc">AUDIT 94/100</span></div>
          <div className="caps"><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap"></span></div></div>
        <div className="mod" onClick={() => onQuery("Paper Trading Runtime")} style={{ cursor: "pointer" }}><div className="id">MOD-007</div><div className="nm">Paper Trading Runtime</div><div className="stt"><span className="ok">✔ DONE</span><span className="sc">AUDIT 97/100</span></div>
          <div className="caps"><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span><span className="cap fa"></span></div></div>
      </div>
      <div style={{ marginTop: "11px", fontSize: "10.5px", color: "var(--dim)" }}>+ <b style={{ color: "var(--txt)" }}>MOD-001</b> Risk Guardrail Engine (predicate-based) · <b style={{ color: "var(--txt)" }}>MOD-002</b> Supervisor Decision Engine (treasury branch) · 11 regimes + NEUTRAL + INDETERMINATE · directions: LONG / FLAT / AVOID / WATCH</div>
    </section>
  );
}
