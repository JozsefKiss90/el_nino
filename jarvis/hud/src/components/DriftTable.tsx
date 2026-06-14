// DriftTable — the April 2026 repo-consistency audit drifts (from the project record).
const DRIFTS: { sev: string; cls: string; item: string }[] = [
  { sev: "HIGH", cls: "r", item: "README claims a CLI rename the code never received." },
  { sev: "HIGH", cls: "r", item: "Constitution mandates a non-existent as-of field; the real anchor is clock_ts." },
  { sev: "HIGH", cls: "r", item: "Governance 'ready' verdict is shell-mode only — semantically vacuous." },
  { sev: "MED", cls: "a", item: "Producer/consumer snapshot copies drifted (DEBT-01) — now closed." },
];

export function DriftTable() {
  return (
    <div className="panel">
      <div className="ph">
        <span className="pt">AUDIT DRIFT</span>
        <span className="tag a">APR 2026</span>
      </div>
      <table className="dt">
        <thead>
          <tr><th>SEV</th><th>FINDING</th></tr>
        </thead>
        <tbody>
          {DRIFTS.map((d, i) => (
            <tr key={i}>
              <td><span className={`kv`}><span className={`v ${d.cls}`}>{d.sev}</span></span></td>
              <td>{d.item}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
