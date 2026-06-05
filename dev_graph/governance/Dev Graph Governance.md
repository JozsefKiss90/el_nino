---
type: governance
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
source_paths:
  - "wiki/CLAUDE.md"
  - "wiki/governance/Metadata Migration Plan.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Dev Graph Governance

## Definition

Root governance document for the dev_graph implementation graph. Establishes the governance framework that all dev_graph operations must follow.

## Purpose

Provides the single authoritative source for dev_graph governance rules, adapted from `wiki/CLAUDE.md` principles for implementation artifacts rather than knowledge synthesis.

## Architecture Role

Top-level governance node. All other governance documents, constraints, and operational procedures derive authority from this document and from `dev_graph/CLAUDE.md`.

## Governance Principles

1. **Canonical ownership**: Every implementation concept has ONE canonical node. Search before creating.
2. **Frontmatter-first metadata**: All nodes have valid YAML frontmatter with closed enums.
3. **Append-only schema evolution**: Enum values are never renamed or removed. New values may be appended.
4. **Never delete — deprecate instead**: Set `status: deprecated` rather than removing nodes.
5. **Cross-graph references are read-only**: dev_graph may reference wiki nodes via wikilinks but MUST NOT modify them.
6. **All mutations logged**: Every write operation is recorded in `dev_graph/log.md`.
7. **Constraints are first-class nodes**: Hard rules live in `dev_graph/constraints/`, not buried in prose.

## Inherited from Wiki Governance

The following principles are inherited from [[REF - Wiki CLAUDE]] and adapted:

| Wiki Principle | Dev Graph Adaptation |
|---|---|
| Canonical ownership (1 concept = 1 page) | 1 implementation concept = 1 node |
| Frontmatter with closed enums | Extended schema with `implementation_status` and relationship arrays |
| Status lifecycle (active/stub/deprecated/draft) | Extended to 7 statuses (active/planned/implemented/validated/deprecated/blocked/draft) |
| Confidence lifecycle | Same 4 levels, same promotion/demotion rules |
| Contradiction handling | Same: flag, document, do not silently merge |
| MCP write safety | Adapted classification for dev_graph operations |
| Dataview governance | Scoped to `FROM "dev_graph"` |
| Automation boundaries | Same batch limits, escalation triggers |
| Domain-directory binding | `type` maps to directory |

## Not Inherited

- Wiki ingestion workflow (dev_graph does not ingest raw sources)
- Source page schema (no `SRC -` prefixed pages in dev_graph)
- Wiki-specific domain structure (20 wiki domains vs 16 dev_graph directories)
- Hub connectivity targets (dev_graph uses different connectivity metrics)

## Node Lifecycle

```
planned -> active -> implemented -> tested -> validated
                                                  |
                                           (deprecated)
```

Transitions:
- `planned -> active`: Work has begun on the concept
- `active -> implemented`: Code exists that realizes the concept
- `implemented -> tested`: Tests cover the implementation
- `tested -> validated`: All gates pass, all predicates hold
- Any -> `deprecated`: Concept superseded or removed
- Any -> `blocked`: External dependency prevents progress

## Relationship Rules

- Every **module** MUST reference its constraints and the files it contains
- Every **file** MUST reference its parent module and its tests
- Every **test** MUST reference what it covers (files or modules)
- Every **gate** MUST reference its predicates
- Every **decision** MUST reference what it constrains or enables
- Every **context pack** MUST list all required nodes with admissibility status

## Relationships

### Depends On
- [[REF - Wiki CLAUDE]]
- [[REF - Wiki Metadata Migration Plan]]

### Provides
- Governance framework for all dev_graph operations

### Validated By
- [[Dev Graph Dashboard]]

### Constrained By
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]

### Supersedes

### Used By
- All dev_graph nodes

### Produces

### Consumes
