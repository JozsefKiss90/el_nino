import { VITALS_GAUGES } from "../../data/snapshot";

// SystemVitals — the SYSTEM VITALS panel (TARGET lines 448-461): three audit-score gauges
// (MOD-005/006/007) drawn as SVG rings, plus the CI/type-safety/module/engine readout rows.
export function SystemVitals() {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">SYSTEM VITALS</span><span className="tag g">NOMINAL</span></div>
      <div className="gauges">
        {VITALS_GAUGES.map((g) => (
          <div className="g" key={g.mod}>
            <svg viewBox="0 0 74 74">
              <circle className="bgc" cx="37" cy="37" r="31" />
              <circle className="fgc" cx="37" cy="37" r="31" strokeDasharray="194.8" strokeDashoffset={g.dashoffset} />
            </svg>
            <div className="num">{g.score}</div>
            <div className="lbl">{g.mod}<br />{g.label}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 10 }}>
        <div className="kv"><span className="k">Test suite</span><span className="v g">853 / 853 GREEN</span></div>
        <div className="kv"><span className="k">Type safety</span><span className="v c">mypy --strict · ruff</span></div>
        <div className="kv"><span className="k">L3 modules</span><span className="v">MOD-003→007 (+001, 002)</span></div>
        <div className="kv"><span className="k">Engine</span><span className="v">gold-v3.3.0</span></div>
      </div>
    </div>
  );
}
