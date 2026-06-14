import { useCallback, useState } from "react";

export type ReactorState = "idle" | "listen" | "speak";

/** The reactor's idle/listen/speak machine (the visual state of the core ring). */
export function useReactorState(): {
  state: ReactorState;
  idle: () => void;
  listen: () => void;
  speak: () => void;
} {
  const [state, setState] = useState<ReactorState>("idle");
  return {
    state,
    idle: useCallback(() => setState("idle"), []),
    listen: useCallback(() => setState("listen"), []),
    speak: useCallback(() => setState("speak"), []),
  };
}
