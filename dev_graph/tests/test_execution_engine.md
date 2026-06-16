---
type: test
canonical_id: TEST-018
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_execution_engine.py"
related_files:
  - "[[engine.py (execution)]]"
  - "[[models.py (execution)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/execution/test_execution_engine.py"
test_type: unit
covers:
  - "[[Execution]]"
  - "[[Execution API]]"
required_for: []
---

# test_execution_engine

## Definition

Behavioral tests for `execute()`: a LONG+approved fill (adverse slippage, mark-to-snapshot P&L),
cost-averaging accumulation, the fail-closed no-fill paths (guard block / non-LONG stance / already-executed
idempotency), a non-ADMIT input raising, the `GuardResult` + `ExecutionRecord` fail-closed invariants, and
`execution_id` binding the prior portfolio state.

## Purpose

Guarantee the fill decision, the portfolio transition, and the fail-closed/idempotency invariants
(ADR-011 §2/§3, D2) hold end-to-end.

## Relationships

### Used By
- [[Execution]]
- [[Execution API]]

### Justified By
- [[ADR - Execution Layer Planning]]
