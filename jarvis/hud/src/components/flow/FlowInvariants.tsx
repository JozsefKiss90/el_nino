// FlowInvariants — RIGHT panel (TARGET lines 852-859). The non-negotiable flow invariants. Static
// content, ported 1:1.
export function FlowInvariants() {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">FLOW INVARIANTS</span><span className="tag g">NON-NEGOTIABLE</span></div>
      <div className="kv"><span className="k">Determinism</span><span className="v g">same snapshot → bit-identical decision</span></div>
      <div className="kv"><span className="k">Fail-closed</span><span className="v g">no output &gt; wrong output</span></div>
      <div className="kv"><span className="k">Boundary</span><span className="v g">snapshots only, downstream</span></div>
      <div className="kv"><span className="k">Look-ahead</span><span className="v g">vintage dates · revision_seq=0</span></div>
      <div className="kv"><span className="k">Zapier in core</span><span className="v r">FORBIDDEN</span></div>
    </div>
  );
}
