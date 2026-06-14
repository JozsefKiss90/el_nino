// NextActions — the 3-item action queue + governance key/value rows (TARGET lines 657-668).
export function NextActions() {
  return (
    <section className="panel">
      <div className="ph"><span className="pt">NEXT ACTIONS</span><span className="tag a">QUEUE: 3</span></div>
      <div className="act"><div className="h"><span className="p1">① E2b — ALPACA EXECUTION ADAPTER</span><span className="tag a">BLOCKER: ADR-010</span></div><div className="d">Start design; ADR-010 required first. Unified scorecard schema: offline_sim and alpaca_paper emit identical formats.</div></div>
      <div className="act"><div className="h"><span className="p2">② CORPUS ACCUMULATION</span><span className="tag c">PASSIVE</span></div><div className="d">+1 snapshot daily at 23:00. Sample size for E3 calibration is calendar-bound — wait, don't build.</div></div>
      <div className="act"><div className="h"><span className="p3">③ LA NIÑA — SPEC IN DRAWER</span><span className="tag">ON HOLD</span></div><div className="d">Intraday protection layer, one-way valve (risk-reducing only). Builds only if E3 high/low gap measurement shows a material gap.</div></div>
      <div style={{ marginTop: "12px" }}>
        <div className="kv"><span className="k">dev_graph governance</span><span className="v c">ADR chain 001–009</span></div>
        <div className="kv"><span className="k">DecisionPacket schema</span><span className="v">frozen · generator not built</span></div>
        <div className="kv"><span className="k">Supervisor verdicts</span><span className="v">PASS / SOFT_SHRINK / HARD_VETO / STUB</span></div>
        <div className="kv"><span className="k">Zapier in core</span><span className="v r">FORBIDDEN — periphery only</span></div>
      </div>
    </section>
  );
}
