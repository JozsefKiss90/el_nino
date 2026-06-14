import type { ReactorState } from "../hooks/useReactorState";

// Caption — the state line + spoken-words caption beneath the reactor.
export function Caption({ state, text }: { state: ReactorState; text: string }) {
  const line =
    state === "listen"
      ? "STATE: LISTENING — SPEAK NOW · TAP CORE TO CANCEL"
      : state === "speak"
        ? "STATE: SPEAKING — TAP CORE OR ESC TO SILENCE"
        : "STATE: IDLE — TAP THE CORE AND SPEAK, OR TYPE";
  return (
    <>
      <div className="stateline">
        STATE: <b>{state.toUpperCase()}</b>
        <span style={{ opacity: 0 }}>{line}</span>
      </div>
      <div className="caption">{text || <span style={{ opacity: 0.5 }}>Spoken words will run here…</span>}</div>
    </>
  );
}
