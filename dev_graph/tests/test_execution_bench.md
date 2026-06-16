---
type: test
canonical_id: TEST-021
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_execution_bench.py"
related_files:
  - "[[run_execution_bench.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/execution/test_execution_bench.py"
test_type: benchmark
covers:
  - "[[Execution]]"
  - "[[Execution Layer Benchmark]]"
required_for: []
---

# test_execution_bench

## Definition

The [[Execution Layer Benchmark]] (BENCH-004) in-sync + determinism test (the BENCH-003
`test_paper_runtime_bench` idiom): the harness is deterministic, every block replays byte-identically, the
real sequence is grounded in the real corpus (`952cc83a…`, not invented), the synthetic sequence reaches the
full execution outcome space (fill / non-LONG no-fill / idempotent no-double-fill / guard-block attribution),
the captured guard configs fingerprint into the replay key, and the committed golden artifact stays in sync
(drift ⇒ red). 15 tests.

## Purpose

Guard the execution-determinism replay invariant (ADR-011 gate d) and the committed golden artifact against
drift, so a silent change to `src/execution`, the fill model, or the captured guard config fails CI.

## Constraints

Asserts only over the deterministic harness; no clock/network/randomness. Closes ADR-011 §7 gate (d) as
traceable replay evidence.

## Relationships

### Used By
- [[Execution]]
- [[Execution Layer Benchmark]]

### Justified By
- [[ADR - Execution Layer Planning]]
