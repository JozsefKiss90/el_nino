import type { ReactorState } from "../hooks/useReactorState";

// Reactor — the arc-reactor core. Click toggles listen/cancel; its ring reflects the state machine.
export function Reactor({ state, onTap, scale = 1 }: { state: ReactorState; onTap: () => void; scale?: number }) {
  return (
    <div className={`reactor ${state}`} onClick={onTap} title="Tap the core: listen · tap again while speaking: silence">
      <div className="heart" style={{ transform: `scale(${scale})` }} />
    </div>
  );
}
