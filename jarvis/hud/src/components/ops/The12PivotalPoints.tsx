// The12PivotalPoints — the parked-questions parking orbit, 4 categorized panels (TARGET lines 671-695).
export function The12PivotalPoints() {
  return (
    <section style={{ marginBottom: "14px" }}>
      <div className="ph" style={{ marginBottom: "10px" }}><span className="pt" style={{ color: "var(--red)" }}>THE 12 PIVOTAL POINTS — QUESTIONS PARKED FOR RETURN</span><span className="tag">PARKING ORBIT</span></div>
      <div className="grid pts" style={{ marginBottom: "0" }}>
        <div className="panel pcat k1"><h3>LA NIÑA / MONITOR</h3><ol>
          <li><span className="n">01</span><span><b>4 mechanical triggers</b> — threshold AND reflex pre-defined: price, vol-spike, velocity, data outage. Nothing decided in the moment.</span></li>
          <li><span className="n">02</span><span><b>Alert-only first</b> — automatic reflex only after evidence (governance-before-autonomy).</span></li>
          <li><span className="n">03</span><span><b>Determinism</b> — every monitor event logged in the Trade Logger like a fill; lives only on the Alpaca paper backend.</span></li>
          <li><span className="n">04</span><span><b>Not tunable yet</b> — thresholds are guesses without data; spec stays in the drawer.</span></li>
        </ol></div>
        <div className="panel pcat k2"><h3>BACKTEST & PAPER</h3><ol>
          <li><span className="n">05</span><span><b>Resolution problem</b> — EOD data can't replay the monitor: (a) high/low approximation, (b) hourly bars.</span></li>
          <li><span className="n">06</span><span><b>Different roles</b> — backtest: "is the monitor needed at all?" · paper: "does it work?"</span></li>
          <li><span className="n">07</span><span><b>Correct order</b> — gap measurement → intraday replay → alert-only paper → automatic reflex.</span></li>
        </ol></div>
        <div className="panel pcat k3"><h3>DATA & LEARNING</h3><ol>
          <li><span className="n">08</span><span><b>Collecting ≠ learning</b> — collect now (cheap); learning automation waits for closed trades.</span></li>
          <li><span className="n">09</span><span><b>Unified scorecard</b> — backtest and paper emit identical schema; precondition for every comparison.</span></li>
          <li><span className="n">10</span><span><b>Zapier</b> — forbidden in core; OK on the periphery (push notifications, Google Sheet rows).</span></li>
          <li><span className="n">11</span><span><b>Human-Approved Policy Evolution</b> — three-state gate: Accept → ADR · Reject → Failure Library · Return. Counter-arguments mandatory.</span></li>
        </ol></div>
        <div className="panel pcat k4"><h3>LOOK-AHEAD BIAS</h3><ol>
          <li><span className="n">12</span><span><b>§5.3 extension</b> — (a) release date vs reference date (FRED vintage_date) · (b) revised data: historical runs use revision_seq=0.</span></li>
        </ol></div>
      </div>
    </section>
  );
}
