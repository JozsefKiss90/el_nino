---
type: constraint
status: active
implementation_status: validated
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
source_paths:
  - "wiki/CLAUDE.md"
  - "wiki/governance/Metadata Migration Plan.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Frontmatter Required

## Definition

Every dev_graph node (except structural files: CLAUDE.md, index.md, log.md, README.md) MUST have valid YAML frontmatter containing all universal fields.

## Purpose

Ensures every node is queryable by Dataview, filterable by MCP tools, and exportable to Neo4j/Postgres. Without frontmatter, a node is invisible to the typed retrieval pipeline.

## Architecture Role

Enables the frontmatter-first metadata model that powers Dataview queries, MCP filtering, admissibility checks, and graph export.

## Constraint Expression

```
for all n in dev_graph_nodes:
  if n.name NOT IN ["CLAUDE", "index", "log", "README"]:
    n.frontmatter MUST contain:
      type, status, implementation_status, canonical,
      created, updated, confidence, source_paths,
      related_files, related_tests, related_constraints,
      related_decisions
    n.frontmatter.type MUST be in type_enum
    n.frontmatter.status MUST be in status_enum
    n.frontmatter.implementation_status MUST be in impl_status_enum
    n.frontmatter.confidence MUST be in confidence_enum
```

## Severity

**Error** (blocking). Nodes without valid frontmatter are excluded from context packs and retrieval.

## Verification

- **Dataview query**: `LIST FROM "dev_graph" WHERE type = null AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE" AND file.name != "README"` must return empty
- **Per-session lint**: Check all touched nodes for frontmatter compliance
- **Weekly lint**: Full vault scan via `get_frontmatter` MCP calls

## Exceptions

Structural files (CLAUDE.md, index.md, log.md, README.md) are exempt by governance.

## Relationships

### Depends On

### Provides
- Dataview queryability for all content nodes
- MCP filterability for all content nodes
- Neo4j/Postgres export readiness

### Validated By
- Dataview missing-frontmatter query on [[Dev Graph Dashboard]]
- Per-session lint workflow

### Constrained By

### Supersedes

### Used By
- [[Dev Graph Governance]]
- [[Admissibility Checks]]
- [[ADR - Dev Graph Bootstrap]]

### Produces

### Consumes
