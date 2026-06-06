---
type: predicate
canonical_id: PRED-003
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
predicate_id: "max-trades-ok"
predicate_scope: "Trades executed today must be below the configured daily maximum"
implemented_in: "src/risk/guardrail_engine/predicates.py"
validated_by:
  - "[[test_predicates]]"
---

# Max Trades OK

## Definition

Boolean condition: `trades_today < max_trades_per_day`. Passes while the day's trade count is below the configured limit (`MAX_TRADES_PER_DAY`).

## Purpose

Enforces the "max trades per day" hard limit — bounds churn / overtrading.

## Implementation Notes

Implemented as `max_trades_ok(request, config)` in `predicates.py` (FILE-002). Boundary verified by `test_predicates` (at limit blocks; one below passes).

## Relationships

### Guards
- [[Trade Validation Gate]]

### Validated By
- [[test_predicates]]

### Justified By
- [[ADR - Ontology Redesign]]
