// EpochRoadmap — 7 epoch cards + live-execution gate banner (TARGET lines 634-646).
export function EpochRoadmap() {
  return (
    <section className="panel" style={{ marginBottom: "14px" }}>
      <div className="ph"><span className="pt">EPOCH ROADMAP</span><span className="tag a">BOTTLENECK: CALENDAR TIME, NOT ENGINEERING</span></div>
      <div className="epochs">
        <div className="ep done"><div className="tg">E1</div><div className="nm">DEBT-01 fix — snapshot publisher</div><div className="ss">✔ DONE</div></div>
        <div className="ep done"><div className="tg">E2a</div><div className="nm">Paper Runtime / Admission Gate (MOD-007)</div><div className="ss">✔ DONE · 97/100</div></div>
        <div className="ep next"><div className="tg">E2b</div><div className="nm">Alpaca Execution Adapter + fills + scorecard</div><div className="ss">▶ NEXT</div></div>
        <div className="ep prog"><div className="tg">E3</div><div className="nm">Empirical calibration — corpus accumulation</div><div className="ss">⏳ RUNNING</div></div>
        <div className="ep fut"><div className="tg">E4</div><div className="nm">Supervisor Engine — El Niño LLM layer</div><div className="ss">□ FUTURE</div></div>
        <div className="ep fut"><div className="tg">E5</div><div className="nm">Policy Evolution — Human-Approved Learning</div><div className="ss">□ FUTURE</div></div>
        <div className="ep fut cond"><div className="tg">E6</div><div className="nm">La Niña — intraday protection</div><div className="ss">◇ CONDITIONAL — E3 gap decides</div></div>
      </div>
      <div className="gate">⛔ PHASE D — LIVE EXECUTION GATE: BLOCKED. Automated trading forbidden by design; every decision is paper trading + human oversight.</div>
    </section>
  );
}
