import { useCallback, useEffect, useRef, useState } from "react";
import { detectSource, liveNeighborhood } from "../data/graph";
import { buildIndex, route, type GraphIndex } from "../data/router";
import type { Answer, GraphData, GraphSource, Health } from "../data/types";

export interface GraphHook {
  ready: boolean;
  source: GraphSource;
  health: Health | null;
  nodeCount: number;
  edgeCount: number;
  graph: GraphData | null;
  /** Answer a question from the graph. Pure router for the text; live bridge for the subgraph. */
  ask: (q: string) => Promise<Answer | null>;
}

/**
 * useGraph — owns source detection (live bridge vs offline graph.json), the pre-built index, and
 * the ask() entry point. The answer text/citations come from the PURE router over the offline
 * projection (which carries node summaries); when the bridge is live, the rendered subgraph is
 * swapped for the bridge's multi-hop neighborhood. Read-only throughout (ADR-010 §1).
 */
export function useGraph(): GraphHook {
  const [ready, setReady] = useState(false);
  const [source, setSource] = useState<GraphSource>("none");
  const [health, setHealth] = useState<Health | null>(null);
  const [counts, setCounts] = useState({ n: 0, e: 0 });
  const [graph, setGraph] = useState<GraphData | null>(null);
  const idxRef = useRef<GraphIndex | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const { source: src, health: h, graph } = await detectSource();
      if (!alive) return;
      setSource(src);
      setHealth(h);
      if (graph) {
        idxRef.current = buildIndex(graph);
        setGraph(graph);
        setCounts({ n: graph.nodes.length, e: graph.edges.length });
      } else if (h) {
        setCounts({ n: h.node_count, e: h.edge_count });
      }
      setReady(true);
    })();
    return () => {
      alive = false;
    };
  }, []);

  const ask = useCallback(
    async (q: string): Promise<Answer | null> => {
      const idx = idxRef.current;
      if (!idx) return null;
      const a = route(idx, q);
      if (a.matched && source === "live" && a.focus) {
        const live = await liveNeighborhood(a.focus);
        // prefer the live neighborhood whenever the bridge returned one — even an isolated node
        // (zero edges) is a valid live result, so don't gate on edges.length.
        if (live && live.nodes.length) {
          a.subgraph = live;
          a.source = `Neo4j bridge · ${a.focus}`;
        }
      }
      return a;
    },
    [source],
  );

  return { ready, source, health, nodeCount: counts.n, edgeCount: counts.e, graph, ask };
}
