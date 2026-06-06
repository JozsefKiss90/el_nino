---
type: predicate
canonical_id: PRED-002
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
predicate_id: "daily-loss-cap-ok"
predicate_scope: "No new trades once realized daily P&L has reached the loss cap"
implemented_in: "src/risk/guardrail_engine/predicates.py"
validated_by:
  - "[[test_predicates]]"
---

# Daily Loss Cap OK

## Definition

Boolean condition: `daily_pnl > -daily_loss_cap`. Passes while the day's realized loss is still within the configured cap; blocks at or beyond it.

## Purpose

Enforces the "daily loss cap" hard limit — halts new trading after a defined drawdown for the day.

## Implementation Notes

Implemented as `daily_loss_cap_ok(request, config)` in `predicates.py` (FILE-002). Boundary verified by `test_predicates` (`-50.0` at cap blocks; `-49.99` passes).

## Relationships

### Guards
- [[Trade Validation Gate]]

### Validated By
- [[test_predicates]]

### Justified By
- [[ADR - Ontology Redesign]]
