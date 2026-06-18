---
type: test
canonical_id: TEST-025
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_chain_bench.py"
related_files:
  - "[[run_chain_bench.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/orchestration/test_chain_bench.py"
test_type: benchmark
covers:
  - "[[Chain Orchestrator]]"
  - "[[Chain Orchestrator Benchmark]]"
required_for: []
---

# test_chain_bench

## Definition

The [[Chain Orchestrator Benchmark]] (BENCH-006) in-sync + determinism test (the BENCH-004
`test_execution_bench` idiom): the harness is deterministic, the real sequence replays byte-identically
across all five record types, the real ADMIT is grounded in the consumable corpus (`952cc83a…`,
`packet_id gold-v0:5653d07a0b3949d5`, never invented), the monochromatic-AVOID corpus is an
ADMIT-then-idempotent-REJECT no-fill, the full replay key is complete, and the committed golden artifact
stays in sync (drift ⇒ red). 8 tests.

## Purpose

Guard the end-to-end replay-determinism + admission-idempotency evidence and the committed golden artifact
against drift, so a silent change to any composed layer, config, or the captured guard/operational input
fails CI.

## Constraints

Asserts only over the deterministic harness; no clock / network / randomness. Carries the full replay key
(every composed layer's version axis + the captured fingerprints).

## Relationships

### Used By
- [[Chain Orchestrator]]
- [[Chain Orchestrator Benchmark]]

### Justified By
- [[ADR - Execution Layer Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
