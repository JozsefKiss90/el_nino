---
type: predicate
canonical_id: PRED-001
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
predicate_id: "position-size-ok"
predicate_scope: "Position size must not exceed the lesser of the %-of-equity and absolute caps"
implemented_in: "src/risk/guardrail_engine/predicates.py"
validated_by:
  - "[[test_predicates]]"
---

# Position Size OK

## Definition

Boolean condition: `size <= min(current_equity * max_position_pct, max_trade_size)`. Passes when a proposed position is within both the percentage-of-equity and absolute-dollar caps.

## Purpose

Enforces the "max position size" hard limit (default 5% of portfolio; absolute cap from `MAX_TRADE_SIZE`).

## Implementation Notes

Implemented as `position_size_ok(request, config)` in `predicates.py` (FILE-002). Pure function returning `(passed, reason)`. Covered by `test_predicates` (boundary cases: at-limit pass, above-limit block, absolute-cap-binds).

## Relationships

### Guards
- [[Trade Validation Gate]]

### Validated By
- [[test_predicates]]

### Justified By
- [[ADR - Ontology Redesign]]
