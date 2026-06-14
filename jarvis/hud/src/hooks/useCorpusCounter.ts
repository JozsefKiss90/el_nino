import { useEffect, useState } from "react";

// Two anchor snapshots (2026-05-01, 2026-06-11) then one/day forward accumulation via the
// scheduled EOD task — mirrors the Stage-2 console's dynamic corpus counter.
const ANCHOR = Date.UTC(2026, 5, 11); // 2026-06-11
const BASE = 2;

/** {count, day}: estimated truth-corpus size and the forward-accumulation day index. */
export function useCorpusCounter(): { count: number; day: number } {
  const [state, setState] = useState(() => compute());
  useEffect(() => {
    const id = setInterval(() => setState(compute()), 60_000);
    return () => clearInterval(id);
  }, []);
  return state;
}

function compute(): { count: number; day: number } {
  const days = Math.max(0, Math.floor((Date.now() - ANCHOR) / 86_400_000));
  return { count: BASE + days, day: days + 1 };
}
