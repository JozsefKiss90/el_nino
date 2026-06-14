// StrategyStrip — the three-panel doctrine strip beneath the main grid (TARGET lines 578-593):
// DOCTRINE, DECISION STRATEGY, and PROTECTION — LA NIÑA. Static prose ported verbatim.
export function StrategyStrip() {
  return (
    <div className="strat">
      <div className="panel">
        <div className="ph"><span className="pt">DOCTRINE</span><span className="tag c">CONSTITUTION</span></div>
        <div className="doct">GOLD-FIRST · FAIL-CLOSED · SNAPSHOT-DRIVEN</div>
        <p>
          Same snapshot → <b>bit-identical decision</b>. No output beats wrong output. Layer 3 reads <b>only published
          snapshots</b> — never raw data, never "latest". LLM = <b>analyst &amp; auditor</b>, never the decision engine.{" "}
          <b>Governance before autonomy</b>. Truth is constrained. Claims are earned. Execution is forbidden until proven safe.
        </p>
      </div>
      <div className="panel">
        <div className="ph"><span className="pt">DECISION STRATEGY</span><span className="tag c">L3 CHAIN</span></div>
        <p>
          EOD macro snapshot → <b>14 features</b> → one of <b>11 regimes</b> (+ NEUTRAL, INDETERMINATE) → direction{" "}
          <b>LONG / FLAT / AVOID / WATCH</b> with confidence → admission <b>ADMIT / HOLD / REJECT</b>. Supervisor verdicts:
          PASS / SOFT_SHRINK / HARD_VETO / STUB. Every decision anchored to a snapshot_id — fully replayable. Look-ahead
          controls: FRED vintage dates, revision_seq=0.
        </p>
      </div>
      <div className="panel">
        <div className="ph"><span className="pt">PROTECTION — LA NIÑA</span><span className="tag a">SPEC IN DRAWER</span></div>
        <p>
          Conditional intraday shield: hourly IMS + a 24h <b>contingency table</b> pre-authorized at EOD, executed by
          deterministic code, never an LLM. <b>One-way valve</b>: intraday authority may only reduce risk. Builds only if E3
          proves the gap is material; deploys alert-only first. <i>Direction daily · protection continuously · discretion
          intraday never.</i>
        </p>
      </div>
    </div>
  );
}
