import { OPERATOR_PORTRAIT } from "../../assets/portrait";

// OperatorPanel — THE OPERATOR board: portrait + the three house rules (doctrine).
// Re-skinned 1:1 to the TARGET (lines 438-446).
export function OperatorPanel() {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">THE OPERATOR</span><span className="tag a">EL NIÑO MARKET MAKER</span></div>
      <img className="opimg" src={OPERATOR_PORTRAIT} alt="El Niño operator — market maker" />
      <div className="oprules">
        <div className="rl">RULE #1 — DON'T GET <b>ATTACHED</b></div>
        <div className="rl">RULE #2 — FOLLOW THE <b>MATH</b></div>
        <div className="rl">RULE #3 — ELIMINATE <b>EMOTION</b></div>
      </div>
    </div>
  );
}
