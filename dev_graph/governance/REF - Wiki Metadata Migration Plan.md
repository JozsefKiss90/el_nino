---
type: reference
canonical_id: REF-002
status: active
implementation_status: validated
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
source_paths:
  - "wiki/governance/Metadata Migration Plan.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# REF - Wiki Metadata Migration Plan

## Definition

Reference node pointing to the wiki's metadata schema specification at `wiki/governance/Metadata Migration Plan.md`.

## Purpose

Documents the schema design patterns that dev_graph's frontmatter inherits from the wiki's proven metadata architecture.

## Target

`wiki/governance/Metadata Migration Plan.md` — Full metadata schema specification covering universal fields, domain-specific extensions, enum definitions, and anti-entropy rules.

## Key Patterns Referenced

| Pattern | Wiki Implementation | Dev Graph Adaptation |
|---|---|---|
| Universal frontmatter | 5 required fields (type, domain, created, updated, status) | 11 required fields (added implementation_status, canonical, confidence, relationship arrays) |
| Closed enums | type(17), domain(20), status(4), confidence(4) | type(17 new), status(7), impl_status(7), confidence(4 same) |
| Flat YAML only | No nested objects | Same: no nested objects |
| Domain-directory binding | `domain` maps to `/wiki/<domain>/` | `type` maps to `/dev_graph/<type_dir>/` |
| Anti-entropy rules | No freeform fields, no duplicate semantics | Same: all fields defined in CLAUDE.md |
| Schema evolution | Append-only enums, additive fields | Same: governance-first |

## Relationships

### Depends On

### Provides
- Schema design pattern reference for dev_graph

### Validated By

### Constrained By
- [[No Wiki Mutation]] (this reference is read-only)

### Supersedes

### Used By
- [[Dev Graph Governance]]

### Produces

### Consumes
