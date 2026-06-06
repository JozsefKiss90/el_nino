---
type: predicate
canonical_id: PRED-005
status: active
implementation_status: tested
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
related_files:
  - "[[predicates.py]]"
related_tests:
  - "[[test_predicates]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
predicate_id: "withdrawal-disabled"
predicate_scope: "Withdrawals must be disabled — a system invariant, fail closed if enabled"
implemented_in: "src/risk/guardrail_engine/predicates.py"
validated_by:
  - "[[test_predicates]]"
---

# Withdrawal Disabled

## Definition

Boolean condition: `not config.allow_withdrawals`. Passes only when withdrawals are disabled (the sole safe state); blocks every trade if withdrawals are somehow enabled.

## Purpose

Enforces the "withdrawal disabled (ALWAYS false)" hard limit as a per-evaluation invariant — the agent can never enable fund movement.

## Implementation Notes

Implemented as `withdrawal_disabled(request, config)` in `predicates.py` (FILE-002). `allow_withdrawals` defaults to `false` (fail-closed). Verified by `test_predicates` (enabled → block; disabled → pass).

## Relationships

### Guards
- [[Trade Validation Gate]]

### Validated By
- [[test_predicates]]

### Justified By
- [[ADR - Ontology Redesign]]
