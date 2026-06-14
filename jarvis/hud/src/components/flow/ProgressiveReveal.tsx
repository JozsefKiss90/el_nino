// ProgressiveReveal — the LEFT column of SYSTEM FLOW (TARGET lines 726-825): the 8-stage pipeline
// (fs1..fs8) plus the .fctrl controls and .fend cap. The reveal state lives in SystemFlow (so the
// full-width .frail rail can share it); this renders steps with " show" when index < revealed.
interface Props {
  revealed: number;
  complete: boolean;
  hint: string;
  onNext: () => void;
  onAll: () => void;
}

export function ProgressiveReveal({ revealed, complete, hint, onNext, onAll }: Props) {
  const stepCls = (i: number) => `fstep${i < revealed ? " show" : ""}`;
  return (
    <div className="fcol">
      <div className={stepCls(0)} id="fs1">
        <div className="fstage">
          <div className="ft"><span>① DATA SOURCES</span><span className="tag c">EXTERNAL FEEDS</span></div>
          <div className="fd">Raw macro observations, pulled daily. Nothing downstream ever touches these directly.</div>
          <div className="fchips">
            <span className="fchip">FRED<small>yields · breakevens · real yields · VIX · SP500 · USD · CPI/PCE</small></span>
            <span className="fchip">goldapi.com<small>XAU/USD spot</small></span>
            <span className="fchip">Yahoo<small>MOVE index · GLD holdings proxy</small></span>
          </div>
        </div>
        <div className="fconn"><span>registry-driven pulls — series_registry.json is the single source of truth</span></div>
      </div>

      <div className={stepCls(1)} id="fs2">
        <div className="fstage">
          <div className="ft"><span>② LAYER 2 — ADAPTERS & TRUTH DB</span><span className="tag c">C:\Code\Mr-Ripley</span></div>
          <div className="fd">Four adapters write to SQLite (<b>layer2_truth.db</b>) with <b>INSERT OR IGNORE</b> — observations are append-only and immutable. Every read enforces point-in-time discipline: <b>obs_ts ≤ clock_date</b> AND <b>as_of_ts ≤ clock_ts</b>, deterministic tie-breaking. No hardcoded series logic anywhere.</div>
          <div className="fchips">
            <span className="fchip">fred_loader</span><span className="fchip">gold_adapter</span>
            <span className="fchip">move_adapter</span><span className="fchip">gld_holdings_adapter</span>
            <span className="fchip">20 series<small>15 Tier-1 · 5 Tier-2</small></span>
          </div>
        </div>
        <div className="fconn"><span>daily EOD run — 23:00 · MrRipley-Layer2-DailyEOD scheduled task</span></div>
      </div>

      <div className={stepCls(2)} id="fs3">
        <div className="fstage">
          <div className="ft"><span>③ QUALITY GATE</span><span className="tag g">FAIL-CLOSED</span></div>
          <div className="fd">All <b>15 Tier-1 series</b> must pass freshness thresholds or the snapshot is <b>blocked</b> — no output beats wrong output. Tier-2 series can only warn, never block. A single stale Tier-1 print kills the publish (unless --force, which is logged).</div>
        </div>
        <div className="fconn"><span>PASS verdict only</span></div>
      </div>

      <div className={stepCls(3)} id="fs4">
        <div className="fstage">
          <div className="ft"><span>④ SNAPSHOT PUBLISHER</span><span className="tag c">IMMUTABLE</span></div>
          <div className="fd">Builds the payload, computes <b>snapshot_id = SHA-256</b> of deterministic content, version-locks on the (clock_ts, engine_version, config_version) triple, stamps the <b>5 guards</b> (data · idempotency · cooldown · risk · supervisor veto), archives JSON. Published once, never rewritten.</div>
        </div>
        <div className="fconn"></div>
        <div className="fbound">═══ SNAPSHOT BOUNDARY — THE ONLY LEGAL CROSSING ═══<br />
          <span style={{ fontSize: "8px", letterSpacing: ".14em", color: "var(--accd)", fontFamily: "var(--mono)", fontWeight: 400 }}>downstream reads published snapshots only · never raw observations · never "latest"</span>
        </div>
        <div className="fconn"></div>
      </div>

      <div className={stepCls(4)} id="fs5">
        <div className="fstage">
          <div className="ft"><span>⑤ LAYER 3 — EL NIÑO DECISION CHAIN</span><span className="tag g">853 TESTS · C:\Code\el_nino</span></div>
          <div className="fd">Deterministic end-to-end: the same snapshot in produces a bit-identical decision out. Every packet anchored to its snapshot_id — fully replayable.</div>
          <div className="fmods">
            <div className="fm"><b>MOD-003</b><i>Snapshot Consumer</i>fail-closed read</div>
            <div className="fm"><b>MOD-004</b><i>Feature Builder</i>14 macro features</div>
            <div className="fm"><b>MOD-005</b><i>Regime Classifier</i>11 regimes +2 · 97/100</div>
            <div className="fm"><b>MOD-006</b><i>Decision Builder</i>direction + confidence · 94/100</div>
            <div className="fm"><b>MOD-007</b><i>Paper Runtime</i>admission gate · 97/100</div>
          </div>
          <div className="fchips" style={{ marginTop: "9px" }}>
            <span className="fchip">MOD-001<small>predicate guardrails</small></span>
            <span className="fchip">Supervisor verdicts<small>PASS · SOFT_SHRINK · HARD_VETO · STUB</small></span>
            <span className="fchip">Directions<small>LONG · FLAT · AVOID · WATCH</small></span>
          </div>
        </div>
        <div className="fconn"><span>ADMIT / HOLD / REJECT</span></div>
      </div>

      <div className={stepCls(5)} id="fs6">
        <div className="fstage">
          <div className="ft"><span>⑥ RECORD & REVIEW</span><span className="tag c">HUMAN IN THE LOOP</span></div>
          <div className="fd">Every admitted decision is logged. The <b>unified scorecard</b> (built in E2b) anchors fills to decision_id + snapshot_id: slippage, PnL, drawdown, hold time, close reason, guard flags. offline_sim and alpaca_paper emit the <b>identical schema</b> — only backend and fill_price differ. Analysis stays manual until closed trades exist.</div>
        </div>
        <div className="fconn"><span>E2b — not yet built</span></div>
      </div>

      <div className={stepCls(6)} id="fs7">
        <div className="fstage fut">
          <div className="ft"><span>⑦ EXECUTION — PAPER FIRST</span><span className="tag a">PLANNED · E2b</span></div>
          <div className="fd"><b>Alpaca Paper API</b> → GLD ETF with virtual money · <b>offline sim</b> → deterministic replay. Blocker: ADR-010 must be written before design starts.</div>
        </div>
        <div className="fconn"></div>
      </div>

      <div className={stepCls(7)} id="fs8">
        <div className="fstage blk">
          <div className="ft"><span>⛔ PHASE D — LIVE EXECUTION GATE</span><span className="tag r">BLOCKED BY DESIGN</span></div>
          <div className="fd">No automated trading, no signal execution, no order generation — forbidden until proven safe through E2b fills, E3 calibration, E4 supervision and E5 governed learning. Every autonomy increase requires human sign-off.</div>
        </div>
      </div>

      {!complete && (
        <div className="fctrl" id="fctrl">
          <button className="fnext" id="fnext" type="button" onClick={onNext}>▶ REVEAL NEXT STAGE</button>
          <div className="fhint" id="fhint">{hint}</div>
          <button className="fall" id="fall" type="button" onClick={onAll}>reveal everything at once</button>
        </div>
      )}
      <div className={`fend${complete ? " show" : ""}`} id="fend">SAME SNAPSHOT IN — BIT-IDENTICAL DECISION OUT.<br />THE GATE STAYS CLOSED UNTIL PROVEN SAFE. · RULE #2: FOLLOW THE MATH.</div>
    </div>
  );
}
