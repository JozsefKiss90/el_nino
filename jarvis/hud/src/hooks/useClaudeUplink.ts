import { useCallback, useState } from "react";
import { API_BASE } from "../data/api";
import type { GraphData } from "../data/types";

// useClaudeUplink — client for POST /ask (Stage 4: GraphRAG over the Claude API). The endpoint
// retrieves a subgraph, grounds Claude in it, and returns a cited, evidence-annotated answer.
// `available` is null until first call; false when the bridge has no ANTHROPIC_API_KEY (503), in
// which case the UI keeps the offline graph answering (useGraph) as the no-API fallback.

export interface UplinkResult {
  answer: string;
  citations: string[];
  subgraph: GraphData;
}

interface Uplink {
  available: boolean | null;
  pending: boolean;
  ask: (question: string) => Promise<UplinkResult | null>;
}

export function useClaudeUplink(): Uplink {
  const [available, setAvailable] = useState<boolean | null>(null);
  const [pending, setPending] = useState(false);

  const ask = useCallback(async (question: string): Promise<UplinkResult | null> => {
    setPending(true);
    try {
      const r = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (r.status === 503) {
        setAvailable(false); // no API key configured on the bridge — use offline fallback
        return null;
      }
      if (!r.ok) {
        setAvailable(false); // 4xx/5xx (e.g. 502 Claude timeout) — mark offline, fall back to router
        return null;
      }
      const j = (await r.json()) as { answer: string; citations?: string[]; subgraph?: GraphData };
      setAvailable(true);
      return {
        answer: j.answer,
        citations: j.citations ?? [],
        subgraph: j.subgraph ?? { nodes: [], edges: [] },
      };
    } catch {
      setAvailable(false); // network error reaching the bridge — fall back to the offline router
      return null;
    } finally {
      setPending(false);
    }
  }, []);

  return { available, pending, ask };
}
