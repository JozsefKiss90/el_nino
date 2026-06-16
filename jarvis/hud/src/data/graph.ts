// graph.ts — the impure data client (ADR-010 §4: offline graph.json and the live Neo4j bridge are
// interchangeable sources behind one typed layer). All network I/O lives here; the pure router
// (router.ts) does the reasoning. In dev, /api is proxied to the bridge by vite; graph.json is
// served from public/. In prod the bridge mounts the built dist and serves both same-origin.

import { API_BASE as API, GRAPH_JSON_URL as GRAPH_JSON } from "./api";
import type { GraphData, GraphSource, Health } from "./types";

/** Probe the read-only bridge. Returns the Health payload, or null when the bridge is down. */
export async function probeHealth(): Promise<Health | null> {
  try {
    const r = await fetch(`${API}/health`, { cache: "no-store" });
    if (!r.ok) return null;
    return (await r.json()) as Health;
  } catch {
    return null;
  }
}

/** Load the offline projection (public/graph.json). Returns null if unreachable. */
export async function loadGraphJson(): Promise<GraphData | null> {
  try {
    const r = await fetch(GRAPH_JSON, { cache: "no-store" });
    if (!r.ok) return null;
    const j = (await r.json()) as Partial<GraphData>;
    return { nodes: j.nodes ?? [], edges: j.edges ?? [] };
  } catch {
    return null;
  }
}

/** Live, multi-hop neighborhood from the bridge — maps bridge nodes to the GNode shape. */
export async function liveNeighborhood(id: string, depth = 1): Promise<GraphData | null> {
  try {
    const r = await fetch(
      `${API}/node/${encodeURIComponent(id)}/neighbors?depth=${depth}&limit=120`,
      { cache: "no-store" },
    );
    if (!r.ok) return null;
    const j = (await r.json()) as { nodes?: BridgeNodeRaw[]; edges?: GraphData["edges"] };
    const nodes = (j.nodes ?? []).map(mapBridgeNode);
    return { nodes, edges: j.edges ?? [] };
  } catch {
    return null;
  }
}

interface BridgeNodeRaw {
  id: string;
  label: string;
  name: string;
  props?: Record<string, unknown>;
}

function mapBridgeNode(n: BridgeNodeRaw): GraphData["nodes"][number] {
  const ev = n.props?.evidence;
  return {
    id: n.id,
    label: n.label,
    name: n.name,
    summary: n.name, // the bridge does not store the markdown summary; graph.json carries it
    confidence: String(n.props?.confidence ?? ""),
    // evidence is now synced to Neo4j (sync_to_neo4j.py array_fields) — preserve it so the live
    // path carries the same evidence-class as the offline projection (ADR-010 §3).
    evidence: Array.isArray(ev) ? ev.map(String) : [],
    status: String(n.props?.status ?? ""),
  };
}

/** Graph-derived facts for the dashboard chrome — so hardcoded node/edge/ADR strings stop drifting
 * (PROJECTION_SYNC_PLAN.md Rec 4). Derived from the loaded projection; null until the graph loads,
 * letting callers fall back to a static current value. */
export interface GraphStats {
  nodes: number;
  edges: number;
  adrRange: string; // e.g. "ADR-001–010"
}

export function graphStats(graph: GraphData | null): GraphStats | null {
  if (!graph || graph.nodes.length === 0) return null;
  const adrNums = graph.nodes
    .map((n) => /^ADR-0*(\d+)$/.exec(n.id))
    .filter((m): m is RegExpExecArray => m !== null)
    .map((m) => Number(m[1]));
  const pad = (x: number) => String(x).padStart(3, "0");
  const adrRange = adrNums.length
    ? `ADR-${pad(Math.min(...adrNums))}–${pad(Math.max(...adrNums))}`
    : "";
  return { nodes: graph.nodes.length, edges: graph.edges.length, adrRange };
}

/** Decide the active source: live bridge if healthy, else offline graph.json, else none. */
export async function detectSource(): Promise<{ source: GraphSource; health: Health | null; graph: GraphData | null }> {
  const [health, graph] = await Promise.all([probeHealth(), loadGraphJson()]);
  const live = !!(health && health.ok && health.neo4j);
  const source: GraphSource = live ? "live" : graph ? "offline" : "none";
  return { source, health, graph };
}
