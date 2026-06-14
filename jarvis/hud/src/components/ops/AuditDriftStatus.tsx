// AuditDriftStatus — the Mr-Ripley repo consistency audit drift table (TARGET lines 697-711). New
// component for the OpsDeck page (does not reuse the legacy DriftTable). Read-only audit board.
export function AuditDriftStatus() {
  return (
    <section className="panel" style={{ marginBottom: "14px" }}>
      <div className="ph"><span className="pt" style={{ color: "var(--red)" }}>AUDIT DRIFT STATUS — MR-RIPLEY REPO CONSISTENCY AUDIT (2026-04-11)</span><span className="tag r">3 HIGH · 2 MED · 1 LOW</span></div>
      <table className="drift">
        <thead><tr><th>ID</th><th>SEV</th><th>DRIFT</th><th>RECOMMENDED DIRECTION</th><th>CLOSURE</th></tr></thead>
        <tbody>
          <tr><td><b>DRIFT-CLI-001</b></td><td><span className="sev h">HIGH</span></td><td>README_LAYER2 claims a CLI rename (--date / --db-path); code still uses --clock-date / --db</td><td>Revert docs to match code</td><td><span className="unk">UNKNOWN</span></td></tr>
          <tr><td><b>DRIFT-FIELD-001</b></td><td><span className="sev h">HIGH</span></td><td>CLAUDE.md §6.2 mandates a non-existent "as_of" snapshot field — real anchor is clock_ts</td><td>Constitution fix: as_of → clock_ts</td><td><span className="unk">UNKNOWN</span></td></tr>
          <tr><td><b>DRIFT-VERDICT-001</b></td><td><span className="sev h">HIGH</span></td><td>Governance "ready" born in shell mode — structurally valid, semantically vacuous</td><td>execution_mode: shell_v1 flag / caveat</td><td><span className="unk">UNKNOWN</span></td></tr>
          <tr><td><b>DRIFT-LIST-001</b></td><td><span className="sev m">MED</span></td><td>--list doesn't show engine_version / config_version fields</td><td>Code fix: extend SELECT</td><td><span className="unk">UNKNOWN</span></td></tr>
          <tr><td><b>DRIFT-PATH-001</b></td><td><span className="sev m">MED</span></td><td>Workflow YAMLs reference canonical docs without Documentation/ prefix</td><td>Add prefix in 3 YAMLs</td><td><span className="unk">UNKNOWN</span></td></tr>
          <tr><td><b>DRIFT-TIMESTAMP-001</b></td><td><span className="sev l">LOW</span></td><td>Verdict artifacts 6 days newer than run state — temporal coherence gap</td><td>run_id field in artifacts</td><td><span className="unk">UNKNOWN</span></td></tr>
        </tbody>
      </table>
      <div style={{ marginTop: "9px", fontSize: "10.5px", color: "var(--dim)" }}>Core VERIFIED: immutable schema · registry SSOT · fail-closed gate · version-locked snapshots · point-in-time alignment · zero execution logic. <span style={{ color: "var(--amb)" }}>Drift touches the doc–code–governance sync, not Layer-2 runtime correctness.</span> Execution status of the G-1…G-12 fix plan is not evidenced in the June materials.</div>
    </section>
  );
}
