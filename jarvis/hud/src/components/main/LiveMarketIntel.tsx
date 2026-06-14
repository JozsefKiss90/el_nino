// LiveMarketIntel — the LIVE MARKET INTEL panel (TARGET lines 541-548). Approximate web pulls; the
// snapshot remains the only canonical truth. Static prose ported verbatim.
export function LiveMarketIntel() {
  return (
    <div className="panel mi">
      <div className="ph"><span className="pt">LIVE MARKET INTEL</span><span className="tag c">WEB · 2026-06-12</span></div>
      <div className="row"><span className="nm">GOLD XAU/USD</span><span><span className="px dn">≈4,195</span> <span className="dlt">vs 5,019 snap −16.4%</span></span></div>
      <div className="row"><span className="nm">US 10Y YIELD</span><span><span className="px wn">≈4.54%</span> <span className="dlt">vs 4.27% snap</span></span></div>
      <div className="row"><span className="nm">52W RANGE (XAU)</span><span className="px" style={{ fontSize: "11px" }}>3,249 — 5,597</span></div>
      <div className="row"><span className="nm">FED PATH</span><span className="px wn" style={{ fontSize: "11px" }}>HIKE PRICED · DEC</span></div>
      <div className="note">
        Tape: US–Iran conflict driving energy costs; CPI hottest in 3+ years; markets price a Fed <b>hike</b>. The
        RESTRICTIVE_RATES read still rhymes with the live tape. Approximate web pulls — the snapshot remains the only
        canonical truth.
      </div>
    </div>
  );
}
