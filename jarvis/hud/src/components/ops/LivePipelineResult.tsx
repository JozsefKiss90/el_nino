// LivePipelineResult — the single full L3 run on real data, as a 4-chip flowline (TARGET lines 623-632).
export function LivePipelineResult() {
  return (
    <section className="panel" style={{ marginBottom: "14px" }}>
      <div className="ph"><span className="pt">LIVE PIPELINE RESULT — THE ONLY FULL L3 RUN ON REAL DATA</span><span className="tag g">VERDICT: ADMIT</span></div>
      <div className="flowline">
        <div className="chip"><div className="k">SNAPSHOT → REGIME</div><div className="v cy">RESTRICTIVE_RATES</div></div><span className="arr">▶</span>
        <div className="chip"><div className="k">CONFIDENCE</div><div className="v am">0.397</div></div><span className="arr">▶</span>
        <div className="chip"><div className="k">DIRECTION</div><div className="v rd">AVOID</div></div><span className="arr">▶</span>
        <div className="chip"><div className="k">PAPER RUNTIME ADMISSION</div><div className="v gn">ADMIT</div></div>
      </div>
      <div style={{ marginTop: "10px", fontSize: "10.5px", color: "var(--dim)" }}>Fail-closed logic at work: restrictive rate environment → low confidence → AVOID — and AVOID is a valid, logged decision, so the runtime passes it with ADMIT.</div>
    </section>
  );
}
