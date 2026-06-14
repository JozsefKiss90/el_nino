// LaNinaBranch — RIGHT panel (TARGET lines 840-851). The conditional, spec-only intraday protection
// rail. Dashed panel border. Static content, ported 1:1.
export function LaNinaBranch() {
  return (
    <div className="panel" style={{ borderStyle: "dashed" }}>
      <div className="ph"><span className="pt">LA NIÑA BRANCH</span><span className="tag a">CONDITIONAL · SPEC ONLY</span></div>
      <div className="fd" style={{ fontSize: "10.5px", color: "var(--dim)", lineHeight: "1.65" }}>Intraday protection rail, parallel to the EOD chain. Builds only if E3 proves the intraday gap is material.</div>
      <div style={{ marginTop: "8px" }}>
        <div className="kv"><span className="k">Step 1</span><span className="v">IMS hourly snapshots · frozen schema · parent_snapshot_id</span></div>
        <div className="kv"><span className="k">Step 2</span><span className="v">24h contingency table · deterministic evaluator — never LLM</span></div>
        <div className="kv"><span className="k">Step 3</span><span className="v c">one-way valve: reduce · exit · tighten · freeze only</span></div>
        <div className="kv"><span className="k">New direction / size-up</span><span className="v r">EOD ONLY</span></div>
        <div className="kv"><span className="k">Deploy order</span><span className="v">alert-only → evidence → reflex</span></div>
      </div>
      <div style={{ fontSize: "9.5px", color: "var(--accd)", letterSpacing: ".08em", marginTop: "9px", fontStyle: "italic" }}>Direction daily · protection continuously · discretion intraday never.</div>
    </div>
  );
}
