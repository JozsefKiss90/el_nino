// router.ts — the PURE question→answer function (ADR-010 §4: "the question→answer router is a
// pure, unit-tested function"). No I/O, no globals, no Date/Math.random: given the graph data
// and a question it deterministically returns a graph-grounded, cited, evidence-annotated Answer.
//
// This ports the verified Stage-2 (jarvis.html) matcher + composer. The live bridge's multi-hop
// neighborhood is layered on top in graph.ts; the pure router operates on the offline projection
// (or any injected GraphData), which is what makes it unit-testable.

import type { Answer, Citation, GEdge, GNode, GraphData } from "./types";

/** Pre-indexed graph for O(1) lookups — build once, route many. */
export interface GraphIndex {
  byId: Map<string, GNode>;
  nodes: GNode[];
  edges: GEdge[];
}

export function buildIndex(graph: GraphData): GraphIndex {
  const byId = new Map<string, GNode>();
  for (const n of graph.nodes) byId.set(n.id, n);
  return { byId, nodes: graph.nodes, edges: graph.edges };
}

// Stop-words stripped from questions before scoring (interrogatives, articles, the verb "depend").
const STOP = new Set([
  "the", "a", "an", "what", "whats", "is", "are", "of", "on", "to", "do", "does", "depend",
  "depends", "with", "how", "why", "which", "and", "for", "in", "me", "tell", "about", "show",
  "that", "this", "it", "its", "by", "from", "node",
]);

export function normalize(s: string): string {
  return (s || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
}

export function tokenize(s: string): string[] {
  return normalize(s).split(" ").filter((t) => t.length > 1 && !STOP.has(t));
}

/**
 * Score a node against a normalized question + its content tokens.
 *  - canonical_id mention (tolerant of "ADR-010" / "ADR 010" / "ADR010") → +20/+18
 *  - full node-name phrase present → +14
 *  - per token: exact name-word +4, name substring +2, summary substring +1
 */
export function scoreNode(nq: string, toks: string[], n: GNode): number {
  const nm = normalize(n.name);
  const idn = normalize(n.id);
  const idc = idn.replace(/ /g, "");
  const sm = normalize(n.summary);
  const nmTok = nm.split(" ");
  let s = 0;
  if (idn && nq.includes(idn)) s += 20;
  else if (idc && nq.replace(/ /g, "").includes(idc)) s += 18;
  if (nm && nm.length > 2 && nq.includes(nm)) s += 14;
  for (const t of toks) {
    if (nmTok.includes(t)) s += 4;
    else if (nm.includes(t)) s += 2;
    if (sm.includes(t)) s += 1;
  }
  return s;
}

/** Best-matching node for a question, or null when nothing clears the threshold (fail-closed). */
export function matchNode(idx: GraphIndex, q: string): GNode | null {
  const nq = normalize(q);
  const toks = tokenize(q);
  if (!toks.length) return null;
  let best: GNode | null = null;
  let bestScore = 0;
  for (const n of idx.nodes) {
    const s = scoreNode(nq, toks, n);
    if (s > bestScore) {
      bestScore = s;
      best = n;
    }
  }
  return bestScore >= 6 ? best : null;
}

/** Focus node + its 1-hop neighborhood, from the offline edge set. */
export function neighborhood(idx: GraphIndex, id: string): GraphData {
  const nodes = new Map<string, GNode>();
  const focus = idx.byId.get(id);
  if (focus) nodes.set(id, focus);
  const edges: GEdge[] = [];
  for (const e of idx.edges) {
    if (e.source === id || e.target === id) {
      edges.push(e);
      const s = idx.byId.get(e.source);
      const t = idx.byId.get(e.target);
      if (s) nodes.set(e.source, s);
      if (t) nodes.set(e.target, t);
    }
  }
  return { nodes: [...nodes.values()], edges };
}

// Relationship phrasing — outgoing (node is source) and incoming (node is target).
const REL_OUT: Record<string, string> = {
  DEPENDS_ON: "depends on", PROVIDES: "provides", VALIDATED_BY: "validated by",
  CONSTRAINED_BY: "constrained by", CONTAINS: "contains", IMPLEMENTS: "implements",
  USED_BY: "used by", PRODUCES: "produces", CONSUMES: "consumes", EMITS: "emits",
  TRIGGERED_BY: "triggered by", GUARDS: "guards", ORIGINATES_FROM: "originates from",
  JUSTIFIED_BY: "justified by", REALIZES: "realizes", COMPOSES: "composes",
  SUPERSEDES: "supersedes", RELATES_TO_FILE: "relates to file", RELATES_TO_TEST: "relates to test",
  DECIDED_BY: "decided by", COVERS: "covers", OWNS: "owns", REQUIRED_FOR: "required for",
  CONSUMED_BY: "consumed by", PRODUCED_BY: "produced by", SUPERSEDED_BY: "superseded by",
};
// Every REL_OUT key has an REL_IN inverse so incoming edges never fall back to "← <out phrase>".
const REL_IN: Record<string, string> = {
  DEPENDS_ON: "depended on by", PROVIDES: "provided by", VALIDATED_BY: "validates",
  CONSTRAINED_BY: "constrains", CONTAINS: "contained by", IMPLEMENTS: "implemented by",
  USED_BY: "uses", PRODUCES: "produced by", CONSUMES: "consumed by", EMITS: "emitted by",
  TRIGGERED_BY: "triggers", GUARDS: "guarded by", ORIGINATES_FROM: "origin of",
  JUSTIFIED_BY: "justifies", REALIZES: "realized by", COMPOSES: "composed by",
  SUPERSEDES: "superseded by", COVERS: "covered by", OWNS: "owned by", DECIDED_BY: "decides",
  RELATES_TO_FILE: "related to by", RELATES_TO_TEST: "related to by", REQUIRED_FOR: "requires",
  CONSUMED_BY: "consumes", PRODUCED_BY: "produces", SUPERSEDED_BY: "supersedes",
};

function relName(idx: GraphIndex, id: string): string {
  return idx.byId.get(id)?.name ?? id;
}

/** Compose an answer body from the node summary + grouped typed edges; collect citations. */
export function compose(
  idx: GraphIndex,
  node: GNode,
  neigh: GraphData,
): { text: string; citations: Citation[] } {
  const id = node.id;
  const ev = node.evidence && node.evidence.length ? node.evidence.join(", ") : "unstated";
  const cite = `[${id} · ${node.confidence || "unstated"}]`;
  const outG: Record<string, string[]> = {};
  const inG: Record<string, string[]> = {};
  const citeIds: string[] = [id];
  const citeSeen = new Set([id]);

  for (const e of neigh.edges) {
    if (e.source === id) {
      (outG[e.type] ??= []).push(`${relName(idx, e.target)} [${e.target}]`);
      if (!citeSeen.has(e.target)) { citeSeen.add(e.target); citeIds.push(e.target); }
    } else if (e.target === id) {
      (inG[e.type] ??= []).push(`${relName(idx, e.source)} [${e.source}]`);
      if (!citeSeen.has(e.source)) { citeSeen.add(e.source); citeIds.push(e.source); }
    }
  }

  const parts: string[] = [];
  for (const t of Object.keys(outG)) {
    parts.push(`${REL_OUT[t] ?? t.toLowerCase().replace(/_/g, " ")} ${outG[t].join(", ")}`);
  }
  for (const t of Object.keys(inG)) {
    parts.push(`${REL_IN[t] ?? `← ${REL_OUT[t] ?? t}`} ${inG[t].join(", ")}`);
  }

  const rel = parts.length ? ` It ${parts.join("; ")}.` : " No typed edges are recorded for it in the graph.";
  const text = `${cite} ${node.summary || node.name}${rel} (evidence: ${ev})`;

  const citations: Citation[] = citeIds.map((cid) => ({
    id: cid,
    confidence: idx.byId.get(cid)?.confidence ?? "unstated",
  }));
  return { text, citations };
}

function confClassOf(confidence: string): "g" | "a" | "" {
  if (confidence === "confirmed") return "g";
  if (confidence === "single-source") return "a";
  return "";
}

/** Suggestion seeds shown on a no-match (fail-closed: "not in the graph", never invent). */
const FALLBACK_SUGGESTIONS = [
  "what depends on the Gold Decision Builder?",
  "what tests cover the Feature Builder?",
  "what does ADR-010 decide?",
];

/**
 * The pure router: question + graph → a graph-grounded Answer. On no match it returns
 * `matched: false` with a fail-closed "not in the graph" message and suggestions — it never
 * fabricates an answer outside the supplied graph (ADR-010 §3).
 */
export function route(idx: GraphIndex, q: string): Answer {
  const node = matchNode(idx, q);
  if (!node) {
    return {
      matched: false,
      title: "NOT IN THE GRAPH",
      text:
        "I could not match that to a dev_graph node, so I won't guess — every claim here must cite a node " +
        "(ADR-010, fail-closed). Try a node by name or id, e.g. " +
        FALLBACK_SUGGESTIONS.map((s) => `"${s}"`).join(", ") +
        ".",
      citations: [],
      evidenceClass: "—",
      confClass: "",
      source: "—",
      related: FALLBACK_SUGGESTIONS,
      subgraph: { nodes: [], edges: [] },
    };
  }

  const neigh = neighborhood(idx, node.id);
  const { text, citations } = compose(idx, node, neigh);

  const seen = new Set<string>();
  const related: string[] = [];
  for (const e of neigh.edges) {
    const other = e.source === node.id ? e.target : e.target === node.id ? e.source : null;
    if (other && !seen.has(other)) {
      seen.add(other);
      related.push(relName(idx, other));
    }
  }

  return {
    matched: true,
    focus: node.id,
    title: `${(node.label || "NODE").toUpperCase()} — ${node.name}`,
    text,
    citations,
    evidenceClass: node.confidence || "—",
    confClass: confClassOf(node.confidence),
    source: `graph.json · ${node.id}`,
    related: related.slice(0, 6),
    subgraph: neigh,
  };
}

/** Convenience: build an index and route in one call (used by tests and the offline path). */
export function routeGraph(graph: GraphData, q: string): Answer {
  return route(buildIndex(graph), q);
}
