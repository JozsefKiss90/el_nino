---
type: reference
canonical_id: REF-003
status: active
implementation_status: validated
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
source_paths:
  - "wiki/observability/Graph Health Dashboard.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# REF - Wiki Graph Health Dashboard

## Definition

Reference node pointing to the wiki's observability dashboard at `wiki/observability/Graph Health Dashboard.md`.

## Purpose

Documents the Dataview query patterns that dev_graph's dashboard adapts for implementation artifact monitoring.

## Target

`wiki/observability/Graph Health Dashboard.md` — 15 Dataview queries covering metadata coverage, confidence distribution, orphan pages, stale content, type distribution, and more.

## Key Patterns Referenced

| Wiki Query Pattern | Dev Graph Adaptation |
|---|---|
| `FROM "wiki"` scoping | Changed to `FROM "dev_graph"` |
| `WHERE type != null` structural file exclusion | Same: excludes CLAUDE, index, log, README |
| `GROUP BY type` distribution | Same pattern, different type enum values |
| `GROUP BY confidence` distribution | Same pattern, same enum values |
| Stale detection (`date(updated) < date(today) - dur(30 days)`) | Same pattern |
| Orphan detection (`length(file.inlinks) = 0`) | Same pattern |
| Known Distinct Pairs section | Available for dev_graph if needed |

## Relationships

### Depends On

### Provides
- Dataview query pattern reference for [[Dev Graph Dashboard]]

### Validated By

### Constrained By
- [[No Wiki Mutation]] (this reference is read-only)

### Supersedes

### Used By
- [[Dev Graph Dashboard]]

### Produces

### Consumes
