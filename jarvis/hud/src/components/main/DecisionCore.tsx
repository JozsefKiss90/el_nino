import type { ReactorState } from "../../hooks/useReactorState";
import { CORE_READ, ORBITS, SNAPSHOT } from "../../data/snapshot";

// DecisionCore — the arc-reactor core: the spinning rings + heart (the L3 verdict), the 8 macro
// orbit chips, the state line, the live caption, and the regime/confidence/direction/admission
// readout strip. Ported 1:1 from the TARGET (lines 486-512); the reactor doubles as the voice tap.
const STATE_LINE: Record<ReactorState, { word: string; tail: string }> = {
  idle: { word: "IDLE", tail: "TAP THE CORE AND SPEAK" },
  listen: { word: "LISTENING", tail: "SPEAK NOW · TAP CORE TO CANCEL" },
  speak: { word: "SPEAKING", tail: "TAP CORE OR ESC TO SILENCE" },
};

export function DecisionCore({ reactorState, onReactorTap }: { reactorState: ReactorState; onReactorTap: () => void }) {
  const sl = STATE_LINE[reactorState];
  return (
    <>
      <div className="rwrap">
        <div
          className={`reactor ${reactorState}`}
          onClick={onReactorTap}
          title="Tap the core: start listening · tap again while speaking: silence"
        >
          <div className="ring r1"></div>
          <div className="ring r2"></div>
          <div className="ring r3"></div>
          <div className="ring r4"></div>
          <div className="heart">
            <div className="vd">{SNAPSHOT.direction}</div>
            <div className="vs">{SNAPSHOT.asset}</div>
            <div className="hint-mic">TAP TO TALK</div>
          </div>
        </div>
        <div className="orbits">
          {ORBITS.map((o, i) => {
            const theta = -90 + i * 45;
            return (
              <div
                key={o.label}
                className={o.warn ? "orb warn" : "orb"}
                style={{ transform: `rotate(${theta}deg) translate(285px) rotate(${-theta}deg)` }}
              >
                <div className="ok2">{o.label}</div>
                <div className="ov">{o.value}</div>
                <div className="os">{o.source}</div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="stateline">
        STATE: <b>{sl.word}</b> — {sl.tail}
      </div>
      <div className="caption">
        <span style={{ opacity: 0.5 }}>Spoken words will run here, live-highlighted…</span>
      </div>
      <div className="core-read">
        {CORE_READ.map((r) => (
          <div className="cr" key={r.k}>
            <div className="k">{r.k}</div>
            <div className={`v ${r.cls}`}>{r.v}</div>
          </div>
        ))}
      </div>
    </>
  );
}
