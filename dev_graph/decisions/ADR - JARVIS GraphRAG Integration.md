---
type: decision_record
canonical_id: ADR-010
status: active
implementation_status: not-started
canonical: true
created: 2026-06-14
updated: 2026-06-14
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "jarvis/JARVIS_INTEGRATION_ROADMAP.md"
  - "jarvis/backend/app.py"
  - "sync_to_neo4j.py"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Dev Graph Bootstrap]]"
decision_id: "ADR-010"
decision_date: 2026-06-14
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - JARVIS GraphRAG Integration

## Status

**Accepted** — authored 2026-06-14. This is a **governance and architectural-boundary** record,
mirroring [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) and [[ADR - Paper-Trading Runtime
Planning]] (ADR-009). It **authors no application code**. It establishes the boundary under which the
**JARVIS console** may be wired to the operational dev_graph (Neo4j + the read-only `neo4j` MCP, or the
offline `graph.json` projection) and refactored, capability-first, so that JARVIS answers from the graph
instead of from its hardcoded keyword corpus. The concrete code (the `graph.json` exporter, the
graph-grounded console, the React refactor, the `/ask` GraphRAG endpoint, and the voice bridge) is built
in subsequent slices governed by the invariants recorded here.

## Context

The dev_graph is the project's ontology-governed Engineering Digital Twin — 23 typed node directories,
~158 canonical nodes, ~1106 typed edges. `sync_to_neo4j.py` projects the canonical markdown into a
read-only Neo4j store; `jarvis/backend/app.py` is **already** a read-only FastAPI bridge over that store
(`/health /meta /node /neighbors /search /path /subgraph`); `jarvis/frontend/index.html` is a cytoscape
explorer over the bridge; the `neo4j` MCP serves the same store read-only (`NEO4J_READ_ONLY=true`).

Separately, `jarvis/sources/el_nino_jarvis_interface (6).html` is a 207 KB monolithic JARVIS console (a
voice-style HUD) that currently answers questions from a **hardcoded keyword corpus** baked into the HTML
— a second, hand-maintained source of "truth" about the system, decoupled from the dev_graph. That is the
gap: JARVIS should answer *from the graph*, with the same single-source-of-truth and fail-closed
discipline the trading engine holds for trades.

This ADR answers a deliberately narrow question:

> **Under what governance constraints may the JARVIS console be connected to the dev_graph and refactored,
> so that it becomes a faithful, read-only, citation-grounded window onto the canonical graph rather than
> a second source of truth?**

## Decision

The following constraints bind the JARVIS integration and the slices that implement it. They are
invariants of record; the code authored in later slices must satisfy them.

### 1. JARVIS is a READ-ONLY consumer of the dev_graph

JARVIS **reads** the graph — live via Neo4j (the existing read-only bridge / MCP) or offline via
`graph.json` — and **never authors it**. The dev_graph markdown stays the single source of truth; Neo4j
and `graph.json` are **rebuildable projections** of it (`sync_to_neo4j.py` and the new
`export_graph_json.py`). JARVIS issues no write Cypher, mutates no node, and proposes no graph edit. The
existing bridge already enforces this at the driver (READ access mode) and with a mutating-clause keyword
guard; the integration must not weaken either. This extends [[Canonical Ownership]] (CON-003): there is
ONE canonical node per concept, owned by the markdown — JARVIS may surface it, never own it.

### 2. The bridge is the EXISTING FastAPI app, extended — not a new server

`jarvis/backend/app.py` is the one bridge. The future LLM uplink (`/ask`), the future voice endpoints
(`/voice/health`, `/voice/stt`, `/voice/tts`), and static serving of the built front end all **fold into
that single FastAPI app** — one service, one URL. The separate `voice_bridge.py` the console HTML imagines
is **not** built; its endpoints become a router on the existing app. The cytoscape setup in
`jarvis/frontend/index.html` is the **graph-render building block** reused by the console's mini-view and,
later, the React `<GraphView>` — no second renderer is written. (Reuse-not-rebuild; one front end lineage,
not three.)

### 3. Every graph-grounded answer cites canonical_ids and carries the evidence-class

The dev_graph's `confidence` (confirmed / single-source / inferred / speculative / experimental) and
`evidence` arrays are already node properties in the markdown and Neo4j. Every answer JARVIS composes from
the graph MUST (a) cite the `canonical_id`(s) it drew from, and (b) annotate each claim with the source
node's evidence-class (e.g. `[MOD-006 · single-source]`). This is **fail-closed applied to the
assistant**: no claim without a backing node. The future `/ask` GraphRAG endpoint must be grounded **only**
in the supplied subgraph, must cite the nodes/edges it traversed, and must say "not in the graph" rather
than invent — the same discipline ADR-009 §8 holds for the runtime verdict.

### 4. Offline `graph.json` and live Neo4j are interchangeable sources behind one typed layer

`graph.json` (deterministic, server-less) and the Neo4j bridge (live, multi-hop) are **interchangeable
sources** of the same projection. The UI degrades gracefully: it uses the live bridge when `GET /health`
passes, else falls back to `graph.json` offline, and shows which source is active. Both are regenerated
from the markdown — **never hand-edited** (the producer-drift lesson: a hand-edited projection becomes a
second source of truth). TypeScript interfaces mirror the FastAPI Pydantic models (`Node`, `Edge`,
`GraphResponse`); the question→answer router is a pure, unit-tested function.

### 5. Governance habit — re-sync on dev_graph change

Each capability slice is introduced by (or cross-referenced to) this ADR and a dev_graph writeback. Only
changes that touch the dev_graph markdown require a Neo4j re-sync (`python sync_to_neo4j.py --clear`); the
JARVIS app slices (exporter, console, React, `/ask`, voice) do **not** change dev_graph nodes and so do
**not** re-sync — except this ADR itself, which does.

## Non-Goals (explicitly deferred)

This ADR and the slices it governs explicitly exclude:

- **Writing to the graph** — no slice authors, mutates, or proposes dev_graph nodes or edges from JARVIS;
  the graph is authored only by the normal markdown + `sync_to_neo4j.py` flow.
- **Autonomous code generation** — JARVIS explains and traverses the graph; it does not write or commit
  application code on its own.
- **Voice-driven *building*** — voice (Whisper STT / Piper TTS) is an *input/output* modality for
  questions and answers, last and most delicate; it never drives app-building or graph mutation. Web
  Speech remains the always-available fallback, so the graph console, React refactor, and `/ask` ship
  without the voice bridge — it is an enhancement, not a blocker.
- **A second source of truth** — `graph.json` and Neo4j stay projections of the markdown; JARVIS holds no
  authoritative corpus of its own (the hardcoded keyword KB is *removed*, not relocated).
- **Exposing the bridge beyond localhost** — the read-only API stays local; CORS/origin tightening is a
  deploy concern outside this ADR.

## Alternatives Considered

- **Keep the hardcoded keyword corpus, bolt the graph on beside it.** **Rejected** — two corpora drift;
  JARVIS would contradict the canonical graph. The keyword KB is removed, not kept in parallel.
- **Build a new, separate voice/answer server (`voice_bridge.py`) the HTML imagined.** **Rejected** —
  fragments one service into many. Everything folds into the existing FastAPI bridge: one service, one URL.
- **Refactor to React first, then add graph answering.** **Rejected** — capability before refactor:
  prove graph-grounded answering on the current HTML (Stage 2), *then* decompose the monolith (Stage 3),
  so the structural payoff lands on a working capability, not a speculative one.
- **Let `/ask` answer from the LLM's own knowledge, citing the graph loosely.** **Rejected** — violates
  §3; the answer must be grounded only in the retrieved subgraph and fail closed to "not in the graph."

## Consequences

### Positive

- JARVIS becomes a faithful, citation-grounded window onto the canonical dev_graph — the assistant inherits
  the project's fail-closed, single-source-of-truth discipline.
- One service (the existing bridge, extended), one front-end lineage (the cytoscape block → console
  mini-view → React `<GraphView>`), one projection flow (markdown → Neo4j/`graph.json`). No duplication.
- Offline/live duality means the console works with no server (graph.json) and gains multi-hop traversal
  when the bridge is up.
- Evidence-class + citations make JARVIS auditable: every claim names its node and its trust level.

### Negative / Trade-offs

- The console's existing hand-tuned keyword answers are retired; answer quality is now bounded by graph
  coverage and node `summary`/edge quality (improved by improving the markdown, not by editing JARVIS).
- The React refactor and voice bridge are real engineering slices that follow; value lands incrementally.

### Risks

- **Projection drift** — a hand-edited `graph.json` or direct Neo4j write would create a second source of
  truth (mitigated by §1/§4: regenerate from markdown, never edit; the bridge/MCP stay read-only).
- **Ungrounded `/ask` answers** — an LLM uplink that invents beyond the subgraph (mitigated by §3: grounded
  only in the supplied subgraph, cite-or-abstain, offline graph answering as the no-API fallback).

## Future Work

When this ADR is accepted, the slices proceed in order: (1) `jarvis/export_graph_json.py` (offline
projection, reusing the `sync_to_neo4j.py` parser); (2) graph-grounded answering on a copy of the console
HTML with a mini cytoscape view, citations, evidence-class, and a LIVE `/health` chip; (3) the
Vite + React + TypeScript refactor with a pure, Vitest-tested router; (4) `POST /ask` GraphRAG over the
Claude API ([[Anthropic API Docs]], API-002), grounded-and-cited; (5) the voice router (Whisper/Piper) on
the same app plus single-URL static serving, with Web Speech as fallback. Each slice runs its own
writeback; only this governance slice changes the dev_graph and re-syncs Neo4j.

## Relationships

### Justified By
- [[ADR - Ontology Redesign]]
- [[ADR - Dev Graph Bootstrap]]

### Constrained By
- [[No Wiki Mutation]]
- [[Canonical Ownership]]

### Depends On
- [[Anthropic API Docs]]
