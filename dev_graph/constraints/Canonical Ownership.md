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
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Canonical Ownership

## Definition

Every implementation concept (module, file, test, gate, predicate, schema, workflow, agent, skill, constraint, API doc source, benchmark, decision) has exactly ONE canonical node in dev_graph. No duplicates.

## Purpose

Prevents semantic drift, conflicting metadata, and ambiguous retrieval results. When a context pack includes a node, there must be zero ambiguity about which node is authoritative.

## Architecture Role

Foundation of the ontology model. All graph traversal, Dataview queries, MCP lookups, and semantic retrieval assume one canonical node per concept.

## Constraint Expression

```
for all concepts C in dev_graph:
  count(nodes where node.represents(C) AND node.canonical == true) == 1
```

## Severity

**Error** (blocking). Duplicate nodes corrupt context packs and produce contradictory implementation guidance.

## Verification

- **Pre-creation check**: Before creating any new node, search dev_graph for existing nodes covering the same concept
- **Smart Connections**: If semantic similarity > 85% with an existing node in the same directory, flag as potential duplicate
- **Monthly audit**: Cross-check all nodes within each directory for semantic overlap

## Enforcement Rules

1. Before creating a new node, run `search_notes` to confirm no existing node covers the concept
2. If a concept is already covered, UPDATE the existing node rather than creating a new one
3. Other nodes reference the canonical node via `[[wikilink]]`
4. Never duplicate a definition — link instead

## Exceptions

None. If two nodes appear to cover the same concept, one must be deprecated or merged.

## Relationships

### Depends On

### Provides
- Unambiguous node identity for all retrieval operations
- Clean graph traversal without duplicate paths

### Validated By
- Smart Connections duplicate detection (>85% similarity threshold)
- Monthly semantic audit

### Constrained By

### Supersedes

### Used By
- [[Dev Graph Governance]]
- [[Context Pack Assembly Rules]]
- [[Admissibility Checks]]
- [[ADR - Dev Graph Bootstrap]]

### Produces

### Consumes
