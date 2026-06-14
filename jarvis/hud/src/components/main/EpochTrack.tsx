// EpochTrack — the EPOCH TRACK panel (TARGET lines 566-574): the E1→E6 epoch chips and the
// blocked Phase-D execution-gate note. Static, ported verbatim.
export function EpochTrack() {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">EPOCH TRACK</span><span className="tag a">E2b NEXT</span></div>
      <div className="emini">
        <div className="eb d"><b>E1</b>DONE</div>
        <div className="eb d"><b>E2a</b>DONE</div>
        <div className="eb n"><b>E2b</b>NEXT</div>
        <div className="eb p"><b>E3</b>RUNNING</div>
        <div className="eb f"><b>E4</b>—</div>
        <div className="eb f"><b>E5</b>—</div>
        <div className="eb f"><b>E6</b>COND.</div>
      </div>
      <div style={{ fontSize: "10px", color: "var(--red)", letterSpacing: ".12em", marginTop: 9, border: "1px dashed rgba(255,93,82,.4)", padding: "6px 9px" }}>
        ⛔ PHASE D — LIVE EXECUTION GATE: BLOCKED
      </div>
    </div>
  );
}
