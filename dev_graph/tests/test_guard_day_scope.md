---
type: test
canonical_id: TEST-039
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_guard_day_scope.py"
related_files:
  - "[[runtime.py (execution)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/execution/test_guard_day_scope.py"
test_type: unit
covers:
  - "[[runtime.py (execution)]]"
  - "[[Portfolio State Schema]]"
required_for: []
---

# test_guard_day_scope

## Definition

Tests that the GATE-001 guard's daily inputs are day-scoped by the snapshot `as_of` (ADR-014 §5.2):
`build_guard_request.trades_today` counts only executions on the same trading day as the request `as_of`,
so `max_trades_per_day` is a genuine daily cap that resets per day (not the lifetime fill count that
silently became a forever-block). Mirrors the PRED-008 cooldown discipline (snapshot clock, never
wall-clock); unparseable/None `as_of` groups deterministically.

## Purpose

Pin the day-scoping fix so the guard's daily cap behaves daily and stays replay-safe.

## Relationships

### Validated By
- [[runtime.py (execution)]]

### Used By
- [[runtime.py (execution)]]
- [[Portfolio State Schema]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
