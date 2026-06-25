---
type: test
canonical_id: TEST-038
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_operator_halt.py"
related_files:
  - "[[operational_feed.py]]"
  - "[[live_runtime.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/orchestration/test_operator_halt.py"
test_type: integration
covers:
  - "[[operational_feed.py]]"
  - "[[live_runtime.py]]"
required_for: []
---

# test_operator_halt

## Definition

Tests the operator kill switch honor side (ADR-014 §6.6): `operator_halt_active` (absent ⇒ run,
present-halt ⇒ honored, unreadable ⇒ fail-closed-halt), the `OperatorHaltFeed` decorator forcing
`halt=True` so the **existing** `operational_ok` predicate REJECTs, and `operate_live` refusing execution
(no order, chain still advances) when the switch is engaged — and resuming when cleared.

## Purpose

Prove the single governed kill mechanism works through the existing operational honor path (no new read
path, no second mechanism).

## Relationships

### Validated By
- [[operational_feed.py]]
- [[live_runtime.py]]

### Used By
- [[operational_feed.py]]
- [[live_runtime.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
