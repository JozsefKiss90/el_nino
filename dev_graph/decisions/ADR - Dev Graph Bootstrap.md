---
type: decision_record
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
source_paths:
  - "wiki/CLAUDE.md"
  - "llm-wiki.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions: []
decision_id: "ADR-001"
decision_date: 2026-05-25
supersedes: []
superseded_by: []
decision_status: accepted
---

# ADR - Dev Graph Bootstrap

## Status

Accepted

## Context

The Layer 3 Wiki has a mature knowledge graph: 57 frontmattered pages across 20 domains, ~852 wikilinks, governed by an 878-line CLAUDE.md. No application code exists yet. Future Claude Code sessions building the autonomous trading engine need a structured way to track implementation artifacts — modules, files, tests, constraints, gates, decisions, and schemas — separate from the knowledge synthesis layer.

The wiki answers "what do we know?" The dev_graph answers "what must we build, how is it constrained, and what has been decided?"

## Decision

Create `./dev_graph/` as a separate ontology-governed implementation graph with:

1. **Separate CLAUDE.md** adapted from wiki/CLAUDE.md for implementation artifacts
2. **Separate type ontology** — 17 implementation-focused types (module, file, test, gate, predicate, artifact_schema, workflow, agent, skill, decision_record, constraint, api_doc_source, benchmark_result, context_pack, governance, observability, reference)
3. **Extended frontmatter schema** with `implementation_status` and relationship arrays (`related_files`, `related_tests`, `related_constraints`, `related_decisions`)
4. **Own Dataview dashboard** scoped to `FROM "dev_graph"`
5. **Cross-references to wiki governance** via `type: reference` nodes, not by duplicating wiki content
6. **Context pack model** for assembling typed, admissibility-checked implementation context

## Alternatives Considered

### Alternative 1: Extend wiki/ with implementation types

**Rejected.** The wiki ontology is designed for knowledge synthesis (concepts, systems, strategies, risk models). Adding module/file/test types would pollute the domain model, create confusion between "what we know" and "what we build," and violate the wiki's append-only schema evolution principles without introducing `schema_version`.

### Alternative 2: Use only external tools (Neo4j/Postgres)

**Rejected.** External databases lose the Obsidian graph view, Dataview queries, mcpvault access, and Smart Connections semantic search. The markdown-first approach matches the wiki's proven pattern and preserves the full MCP integration stack.

### Alternative 3: Flat file tracking (no graph)

**Rejected.** Flat lists cannot answer graph questions like "which files depend on this module?" or "which constraints apply to this change?" Graph structure with typed edges is essential for the retrieval pipeline.

### Alternative 4: Single merged vault

**Rejected.** The wiki and dev_graph serve different audiences (knowledge vs. implementation), have different type ontologies, different lifecycles, and different governance cadences. Merging would create governance conflicts and reduce clarity.

## Consequences

### Positive

- Clean separation between knowledge and implementation graphs
- Each graph has its own governance, schema, and lifecycle
- Implementation nodes are immediately useful for Claude Code sessions
- Full MCP stack (mcpvault, Smart Connections, Dataview) available from day one
- Neo4j/Postgres export-ready via relationship sections and frontmatter

### Negative

- Two parallel ontologies require clear boundary governance
- wiki/** is immutable from dev_graph sessions (enforced by [[No Wiki Mutation]])
- Schema evolution for dev_graph is independent of wiki schema
- Initial dev_graph is compact (22 files); value grows as code is written

### Risks

- If the codebase grows very large, the dev_graph may need batch tooling for node creation
- Cross-graph references (dev_graph -> wiki) are read-only; if wiki pages move, reference nodes need updating

## Relationships

### Depends On

### Provides
- Architectural foundation for the entire dev_graph

### Validated By
- Successful bootstrap of 22 files with valid frontmatter

### Constrained By
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]

### Supersedes

### Used By
- All dev_graph governance documents
- All dev_graph content nodes

### Produces

### Consumes
