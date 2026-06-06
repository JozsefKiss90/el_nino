---
type: pattern
canonical_id: PAT-006
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/memory/Context Budget Engineering.md"
  - "wiki/memory/Agent Memory Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "context-assembly"
pattern_type: structural
instances:
  - "[[State Persistence]]"
  - "[[Context Assembly]]"
realized_by_capabilities:
  - "[[State Persistence]]"
  - "[[Context Assembly]]"
realized_by_modules: []
related_knowledge:
  - "[[Context Engineering]]"
  - "[[Stateless Agent Architecture]]"
---

# Context Assembly Pattern

## Definition

A structured retrieval and assembly process that selects, prioritizes, and composes information into a bounded context window for a stateless agent invocation. The assembly is budget-aware, intent-aware, and admissibility-checked.

## Structural Constraints

1. Context window has a finite token budget — assembly must fit within it
2. Selection is prioritized (constraints > decisions > code > tests > docs)
3. Admissibility checks filter out deprecated, stale, or contradicted information
4. Intent classification determines the retrieval entry point
5. Read-before-act is mandatory — the agent must read assembled context before acting

## When to Apply

Apply for any agent session that requires structured context: coding sessions, evaluation sessions, governance reviews.

## Relationships

### Provides
- Structural guidance for agent context management

### Realized By
- [[State Persistence]]
- [[Context Assembly]]

### Originates From
- [[Context Engineering]]
- [[Stateless Agent Architecture]]
