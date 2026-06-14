// TruthCorpus — the TRUTH CORPUS panel (TARGET lines 463-472). Real-snapshot count and
// accumulation day are live from App's corpus counter (+1/day since 2026-06-11); the rest verbatim.
export function TruthCorpus({ corpus }: { corpus: { count: number; day: number } }) {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">TRUTH CORPUS</span><span className="tag c">ACCUMULATING</span></div>
      <div className="kv"><span className="k">Real snapshots</span><span className="v c">{corpus.count}</span></div>
      <div className="kv"><span className="k">Accumulation day</span><span className="v g">{corpus.day}</span></div>
      <div className="kv"><span className="k">Anchors</span><span className="v">2026-05-01 · 2026-06-11</span></div>
      <div className="kv"><span className="k">Next publish</span><span className="v">Tonight 23:00 · Win Task</span></div>
      <div className="kv"><span className="k">DEBT-01</span><span className="v g">FIXED 2026-06-11</span></div>
      <div className="kv"><span className="k">E3 bottleneck</span><span className="v a">CALENDAR, not engineering</span></div>
      <div style={{ fontSize: "8.5px", color: "var(--accd)", letterSpacing: ".08em", marginTop: 6 }}>
        * count estimated from +1/day schedule since 2026-06-11
      </div>
    </div>
  );
}
