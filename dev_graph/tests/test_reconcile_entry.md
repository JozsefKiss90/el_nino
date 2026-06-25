---
type: test
canonical_id: TEST-037
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_reconcile_entry.py"
related_files:
  - "[[models.py (execution)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/execution/test_reconcile_entry.py"
test_type: unit
covers:
  - "[[models.py (execution)]]"
  - "[[Portfolio State Schema]]"
required_for: []
---

# test_reconcile_entry

## Definition

Tests the SCHEMA-015 `ReconcileEntry` kind + `PortfolioState.reconciles` (ADR-014 §6.2): the **determinism
trick** (an empty `reconciles` is omitted from `to_dict` so the sim/replay portfolio + `state_hash` stay
byte-identical → no benchmark re-pin), the round-trip through `from_dict`, and `append_reconcile` leaving
positions + executions untouched (no auto-adopt).

## Purpose

Guard the byte-identity that keeps BENCH-004/006 from re-pinning, and the reconcile-vs-execution
distinction (no `source_record_id`, no `guard_result`).

## Relationships

### Validated By
- [[Portfolio State Schema]]

### Used By
- [[models.py (execution)]]
- [[Portfolio State Schema]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
