// router.test.ts — Vitest unit tests for the PURE question→answer router (the Stage-3 gate).
// Mirrors the project's test-first culture: the router is verified on a small deterministic
// fixture AND against the real exported graph.json (the roadmap's "what depends on MOD-006"
// example), so a regression in matching, composition, or citations fails the build.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import type { GraphData } from "./types";
import {
  buildIndex,
  compose,
  matchNode,
  neighborhood,
  normalize,
  route,
  routeGraph,
  scoreNode,
  tokenize,
} from "./router";

// --- a tiny, fully-known fixture -------------------------------------------------------------
const FIXTURE: GraphData = {
  nodes: [
    { id: "MOD-006", label: "Module", name: "Gold Decision Builder", summary: "The deterministic builder that turns features into a packet.", confidence: "confirmed", evidence: ["design", "code"], status: "active" },
    { id: "SCHEMA-011", label: "ArtifactSchema", name: "Gold DecisionPacket v0 Schema", summary: "The frozen paper-only decision packet schema.", confidence: "confirmed", evidence: ["design"], status: "active" },
    { id: "FILE-015", label: "File", name: "models.py (gold)", summary: "Dataclasses for the gold packet.", confidence: "confirmed", evidence: ["code"], status: "implemented" },
    { id: "MOD-007", label: "Module", name: "Paper Runtime", summary: "Stateful runtime that admits a gold packet.", confidence: "single-source", evidence: ["design"], status: "planned" },
    { id: "ADR-010", label: "DecisionRecord", name: "ADR - JARVIS GraphRAG Integration", summary: "Governance boundary for wiring JARVIS to the dev_graph.", confidence: "confirmed", evidence: ["ADR"], status: "active" },
    { id: "TEST-099", label: "Test", name: "test gold builder", summary: "Determinism + replay tests for the gold builder.", confidence: "single-source", evidence: ["code"], status: "implemented" },
  ],
  edges: [
    { source: "MOD-006", type: "CONTAINS", target: "FILE-015" },
    { source: "MOD-006", type: "PRODUCES", target: "SCHEMA-011" },
    { source: "MOD-007", type: "DEPENDS_ON", target: "MOD-006" }, // MOD-007 depends on MOD-006
    { source: "FILE-015", type: "DEPENDS_ON", target: "MOD-006" },
    { source: "FILE-015", type: "RELATES_TO_TEST", target: "TEST-099" }, // file relates to its test
  ],
};
const IDX = buildIndex(FIXTURE);

describe("normalize / tokenize", () => {
  it("lowercases and strips punctuation", () => {
    expect(normalize("ADR-010, decide?")).toBe("adr 010 decide");
  });
  it("drops stop-words and 1-char tokens", () => {
    expect(tokenize("what depends on the Gold Decision Builder?")).toEqual(["gold", "decision", "builder"]);
  });
});

describe("scoreNode", () => {
  const gold = FIXTURE.nodes[0];
  it("rewards a full name-phrase and name-word hits", () => {
    const q = "what depends on the gold decision builder";
    expect(scoreNode(normalize(q), tokenize(q), gold)).toBeGreaterThanOrEqual(14 + 12);
  });
  it("matches a hyphenated canonical_id even though the hyphen normalizes to a space", () => {
    const adr = FIXTURE.nodes[4];
    const q = "what does ADR-010 decide";
    expect(scoreNode(normalize(q), tokenize(q), adr)).toBeGreaterThanOrEqual(18);
  });
});

describe("matchNode", () => {
  it("matches the Gold Decision Builder by name", () => {
    expect(matchNode(IDX, "what depends on the Gold Decision Builder?")?.id).toBe("MOD-006");
  });
  it("matches a node by canonical_id", () => {
    expect(matchNode(IDX, "tell me about MOD-006")?.id).toBe("MOD-006");
    expect(matchNode(IDX, "ADR-010")?.id).toBe("ADR-010");
  });
  it("returns null for an empty / stop-word-only question", () => {
    expect(matchNode(IDX, "what is it?")).toBeNull();
  });
  it("returns null for an off-graph question (fail-closed)", () => {
    expect(matchNode(IDX, "what was the 10-year yield?")).toBeNull();
  });
});

describe("neighborhood", () => {
  it("returns the focus plus its 1-hop neighbors and incident edges", () => {
    const g = neighborhood(IDX, "MOD-006");
    const ids = g.nodes.map((n) => n.id).sort();
    expect(ids).toEqual(["FILE-015", "MOD-006", "MOD-007", "SCHEMA-011"]);
    expect(g.edges).toHaveLength(4);
  });
});

describe("compose", () => {
  it("leads with a cited, evidence-annotated summary and names incoming/outgoing edges", () => {
    const node = IDX.byId.get("MOD-006")!;
    const { text, citations } = compose(IDX, node, neighborhood(IDX, "MOD-006"));
    expect(text).toContain("[MOD-006 · confirmed]");
    expect(text).toContain("models.py (gold) [FILE-015]"); // CONTAINS edge, by node name
    expect(text).toContain("depended on by"); // MOD-007 + FILE-015 depend on it
    expect(text).toContain("(evidence: design, code)");
    // citation order: focus first, then referenced neighbors, each with its own confidence
    expect(citations[0]).toEqual({ id: "MOD-006", confidence: "confirmed" });
    expect(citations.map((c) => c.id)).toContain("MOD-007");
    expect(citations.find((c) => c.id === "MOD-007")?.confidence).toBe("single-source");
  });
});

describe("route", () => {
  it("answers a structural question with a focus, citations and a subgraph", () => {
    const a = route(IDX, "what depends on the Gold Decision Builder?");
    expect(a.matched).toBe(true);
    expect(a.focus).toBe("MOD-006");
    expect(a.title).toBe("MODULE — Gold Decision Builder");
    expect(a.confClass).toBe("g"); // confirmed
    expect(a.citations[0].id).toBe("MOD-006");
    expect(a.related).toContain("Paper Runtime");
    expect(a.subgraph.nodes.length).toBeGreaterThan(1);
  });
  it("phrases an incoming RELATES_TO_TEST edge with a proper inverse (no '← ' fallback)", () => {
    // routing to the TEST node: FILE-015 -[RELATES_TO_TEST]-> TEST-099 is incoming to TEST-099
    const a = route(IDX, "test gold builder");
    expect(a.focus).toBe("TEST-099");
    expect(a.text).toContain("related to by models.py (gold) [FILE-015]");
    expect(a.text).not.toContain("←"); // every REL_OUT type has an REL_IN inverse
    // the focus node's own evidence-class is annotated, and the neighbor's confidence is cited
    expect(a.evidenceClass).toBe("single-source");
    expect(a.citations.find((c) => c.id === "FILE-015")?.confidence).toBe("confirmed");
  });

  it("fails closed on an off-graph question — no fabricated answer", () => {
    const a = route(IDX, "should I buy gold tomorrow?");
    expect(a.matched).toBe(false);
    expect(a.citations).toHaveLength(0);
    expect(a.subgraph.nodes).toHaveLength(0);
    expect(a.text).toContain("won't guess");
  });
});

// --- against the REAL exported graph.json (the roadmap gate) ----------------------------------
describe("real graph.json projection", () => {
  const graph = JSON.parse(
    readFileSync(fileURLToPath(new URL("../../public/graph.json", import.meta.url)), "utf8"),
  ) as GraphData;

  it("loads 159 nodes / 1113 edges", () => {
    expect(graph.nodes.length).toBe(159);
    expect(graph.edges.length).toBe(1113);
  });

  it('"what depends on the Gold Decision Builder?" → MOD-006, cited, with dependents', () => {
    const a = routeGraph(graph, "what depends on the Gold Decision Builder?");
    expect(a.matched).toBe(true);
    expect(a.focus).toBe("MOD-006");
    expect(a.text).toContain("[MOD-006 · confirmed]");
    expect(a.citations[0].id).toBe("MOD-006");
    // MOD-007 (Paper Runtime) and the gold FILE nodes depend on MOD-006
    const citedIds = a.citations.map((c) => c.id);
    expect(citedIds).toContain("MOD-007");
    expect(a.text).toContain("depended on by");
  });

  it('"what does ADR-010 decide?" → ADR-010', () => {
    const a = routeGraph(graph, "what does ADR-010 decide?");
    expect(a.matched).toBe(true);
    expect(a.focus).toBe("ADR-010");
    expect(a.evidenceClass).toBe("confirmed");
  });

  it("routes a snapshot-series question to no-match (fail-closed, not the graph's job)", () => {
    expect(routeGraph(graph, "what was the 10-year yield?").matched).toBe(false);
  });
});
