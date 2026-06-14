// GovernanceSpine — RIGHT panel (TARGET lines 828-839). The constitution / ADR / hooks spine that
// runs alongside every stage. Static content, ported 1:1.
export function GovernanceSpine() {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">GOVERNANCE SPINE</span><span className="tag c">ALWAYS ON</span></div>
      <div className="fd" style={{ fontSize: "10.5px", color: "var(--dim)", lineHeight: "1.65" }}>Runs alongside every stage, not after it.</div>
      <div style={{ marginTop: "8px" }}>
        <div className="kv"><span className="k">Constitution</span><span className="v">CLAUDE.md — truth hierarchy, claim discipline</span></div>
        <div className="kv"><span className="k">ADR chain</span><span className="v c">ADR-001 → 009 (010 pending)</span></div>
        <div className="kv"><span className="k">Python hooks</span><span className="v">snapshot boundary · readiness claims · pre-PR gate</span></div>
        <div className="kv"><span className="k">LLM role</span><span className="v a">analyst & auditor only</span></div>
        <div className="kv"><span className="k">Policy changes</span><span className="v">human-approved · 3-state gate</span></div>
        <div className="kv"><span className="k">Known gap</span><span className="v r">DAG "ready" = shell-mode only</span></div>
      </div>
    </div>
  );
}
