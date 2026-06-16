---
type: test
canonical_id: TEST-019
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_execution_determinism.py"
related_files:
  - "[[runtime.py (execution)]]"
  - "[[models.py (execution)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/execution/test_execution_determinism.py"
test_type: regression
covers:
  - "[[Execution]]"
  - "[[Execution API]]"
required_for: []
---

# test_execution_determinism

## Definition

The BENCH-004 core (ADR-011 §2): `run_sequence` twice over the same items + captured guard config yields
byte-identical records and an identical ending portfolio `state_hash`; a persist/load round-trip preserves
the `state_hash`; a missing portfolio file is the empty state; a repeated `source_snapshot_id` does not
double-fill.

## Purpose

Guarantee the execution-determinism replay invariant + idempotency the replay key rests on.

## Relationships

### Used By
- [[Execution]]
- [[Execution API]]

### Justified By
- [[ADR - Execution Layer Planning]]
