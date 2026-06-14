// OperatorPanel — the house rules from the operator's board (doctrine, unchanged from Stage 2).
const RULES: { n: string; t: string }[] = [
  { n: "1", t: "Don't get attached — positions are hypotheses, not relationships. AVOID is a valid answer." },
  { n: "2", t: "Follow the math — same snapshot, bit-identical decision. The regime classifier outranks your gut." },
  { n: "3", t: "Eliminate emotion — execution is blocked, guards are predicates, every autonomy step needs a signature." },
];

export function OperatorPanel() {
  return (
    <div className="panel">
      <div className="ph">
        <span className="pt">OPERATOR'S BOARD</span>
        <span className="tag c">DOCTRINE</span>
      </div>
      {RULES.map((r) => (
        <div className="op-row" key={r.n}>
          <b>RULE {r.n}</b>
          <span>{r.t}</span>
        </div>
      ))}
    </div>
  );
}
