---
type: reference
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

# REF - Wiki CLAUDE

## Definition

Reference node pointing to the wiki's governance operations manual at `wiki/CLAUDE.md`.

## Purpose

Enables Graph-RAG traversal from dev_graph governance to the source governance principles. Makes the inheritance relationship explicit and discoverable.

## Target

`wiki/CLAUDE.md` — 878-line ontology operations manual governing the knowledge wiki.

## Key Sections Referenced by Dev Graph

| Wiki Section | Dev Graph Inheritance |
|---|---|
| Canonical Ownership Rules | Inherited directly as [[Canonical Ownership]] constraint |
| Frontmatter Governance | Pattern adapted for dev_graph schema (extended enums, added `implementation_status`) |
| MCP Operational Governance | Pattern adapted as [[MCP Tooling Policy]] with dev_graph classifications |
| Automation Boundaries | Inherited: 15-node batch limit, escalation triggers |
| Schema Evolution Procedures | Inherited: append-only enums, additive fields, governance-first |
| Dataview Governance | Pattern adapted: `FROM "dev_graph"` instead of `FROM "wiki"` |
| Semantic Retrieval Governance | Inherited: canonical precedence, confidence-weighted ranking |
| Continuous Ontology Operations | Pattern adapted: per-session/weekly/monthly cadences |
| Semantic Confidence Lifecycle | Inherited: same 4 levels, same promotion/demotion rules |

## Governance Inheritance

Dev_graph `CLAUDE.md` adapts these principles for implementation artifacts. See [[Dev Graph Governance]] for the adapted rules.

The wiki is the authoritative source for governance design patterns. When in doubt about a governance question not explicitly covered by dev_graph governance, consult this reference.

## Relationships

### Depends On

### Provides
- Governance inheritance link to wiki

### Validated By

### Constrained By
- [[No Wiki Mutation]] (this reference is read-only)

### Supersedes

### Used By
- [[Dev Graph Governance]]
- [[Dev Graph Dashboard]]

### Produces

### Consumes
