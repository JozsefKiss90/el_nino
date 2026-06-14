import { useEffect, useState } from "react";

/** A ticking wall-clock string (UTC) for the HUD header. */
export function useClock(): string {
  const [now, setNow] = useState(() => fmt(new Date()));
  useEffect(() => {
    const id = setInterval(() => setNow(fmt(new Date())), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

function fmt(d: Date): string {
  const p = (n: number) => (n < 10 ? "0" : "") + n;
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())} ${p(d.getUTCHours())}:${p(
    d.getUTCMinutes(),
  )}:${p(d.getUTCSeconds())} UTC`;
}
