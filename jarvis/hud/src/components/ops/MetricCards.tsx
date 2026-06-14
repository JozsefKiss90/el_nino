// MetricCards — 4 metric panels (TARGET lines 616-621). The REAL SNAPSHOTS .val reflects the live
// corpus count from App (was id="corpusN2" in the source).
export function MetricCards({ corpus }: { corpus: { count: number; day: number } }) {
  return (
    <div className="grid cards">
      <div className="panel metric"><div className="ph"><span className="pt">REAL SNAPSHOTS</span><span className="tag c">CORPUS</span></div><div className="val">{corpus.count}</div><div className="note2">2026-05-01 · 2026-06-11<br />Forward accumulation: <b style={{ color: "var(--grn)" }}>+1 / day</b></div></div>
      <div className="panel metric"><div className="ph"><span className="pt">TEST SUITE</span><span className="tag g">CI</span></div><div className="val g">853</div><div className="note2">tests, all green<br />mypy --strict · ruff · pytest</div></div>
      <div className="panel metric"><div className="ph"><span className="pt">AUDIT SCOREBOARD</span><span className="tag a">QA</span></div><div className="val a">97·94·97</div><div className="note2">MOD-005 · MOD-006 · MOD-007<br />/100, independent audits</div></div>
      <div className="panel metric"><div className="ph"><span className="pt">NEXT SNAPSHOT</span><span className="tag c">SCHEDULED</span></div><div className="val">23:00</div><div className="note2">MrRipley-Layer2-DailyEOD<br />Windows Task · DEBT-01 <b style={{ color: "var(--grn)" }}>FIXED</b></div></div>
    </div>
  );
}
