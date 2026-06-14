// Typed end-to-end (ADR-010 §4): these interfaces mirror the FastAPI Pydantic models in
// jarvis/backend/app.py (_node / _graph) and the jarvis/export_graph_json.py projection —
// the frontend analog of `mypy --strict`.

/** A dev_graph node, as emitted by export_graph_json.py (graph.json). */
export interface GNode {
  id: string; // canonical_id (stable primary key)
  label: string; // PascalCase type label, e.g. "Module", "DecisionRecord"
  name: string; // node title (filename stem)
  summary: string; // first sentence of the node's ## Definition
  confidence: string; // confirmed | single-source | inferred | speculative | experimental
  evidence: string[]; // design | code | ADR | wiki | layer2 | benchmark | external
  status: string; // active | planned | implemented | validated | deprecated | ...
}

/** A typed, directed edge between two canonical_ids. */
export interface GEdge {
  source: string;
  type: string; // relationship type, e.g. DEPENDS_ON, CONTAINS, VALIDATED_BY
  target: string;
}

/** A {nodes, edges} graph payload — the shape of graph.json and every bridge graph response. */
export interface GraphData {
  nodes: GNode[];
  edges: GEdge[];
}

/** The live bridge's node shape (/node, /search) — props is the full frontmatter bag. */
export interface BridgeNode {
  id: string;
  label: string;
  labels: string[];
  name: string;
  props: Record<string, unknown>;
}

/** /health response — drives the LIVE connector chip. */
export interface Health {
  ok: boolean;
  neo4j: boolean;
  node_count: number;
  edge_count: number;
  detail?: string;
}

export type GraphSource = "live" | "offline" | "none";

/** A citation: the canonical_id of a node an answer drew from, with its evidence-class. */
export interface Citation {
  id: string;
  confidence: string;
}

/** The router's pure output — a graph-grounded, cited, evidence-annotated answer. */
export interface Answer {
  matched: boolean;
  focus?: string; // canonical_id of the matched node
  title: string;
  text: string;
  citations: Citation[];
  evidenceClass: string; // the focus node's confidence (e.g. "confirmed")
  confClass: "g" | "a" | ""; // UI color bucket for the evidence tag
  source: string; // provenance line, e.g. "graph.json · MOD-006"
  related: string[]; // neighbor names, clickable to expand
  subgraph: GraphData; // focus + 1-hop neighborhood, for GraphView
}
