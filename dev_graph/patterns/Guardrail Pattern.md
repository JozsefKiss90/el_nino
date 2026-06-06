---
type: pattern
canonical_id: PAT-002
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "guardrail"
pattern_type: governance
instances:
  - "[[Guardrail Enforcement]]"
  - "[[Promotion Validation]]"
  - "[[Stop-Loss Management]]"
  - "[[Order Management]]"
realized_by_capabilities:
  - "[[Guardrail Enforcement]]"
  - "[[Promotion Validation]]"
  - "[[Stop-Loss Management]]"
  - "[[Order Management]]"
realized_by_modules: []
related_knowledge:
  - "[[Guardrail Philosophy]]"
---

# Guardrail Pattern

## Definition

A validation checkpoint composed of boolean predicates that must ALL pass before an action is permitted. Predicates are evaluated by a gate at a system boundary. Failure blocks the action entirely — there is no partial pass.

## Structural Constraints

1. Predicates are boolean — pass or fail, no partial scores
2. Gate evaluates ALL predicates — conjunction, not disjunction
3. Gate is positioned at a system BOUNDARY — not within internal logic
4. Failure is blocking — the action does not proceed
5. Configuration is external to the agent — stored in env vars or policy files, not in agent-accessible memory

## When to Apply

Apply at every boundary where an autonomous agent's action could cause irreversible harm. Trading execution, promotion decisions, treasury spend, position sizing.

## Relationships

### Provides
- Structural guidance for defensive validation checkpoints

### Realized By
- [[Guardrail Enforcement]]
- [[Promotion Validation]]
- [[Stop-Loss Management]]
- [[Order Management]]

### Originates From
- [[Guardrail Philosophy]]
