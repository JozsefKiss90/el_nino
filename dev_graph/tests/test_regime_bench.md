---
type: test
canonical_id: TEST-009
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/regime/run_regime_bench.py"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
test_path: "tests/regime/test_regime_bench.py"
test_type: benchmark
covers:
  - "[[Regime Distribution Benchmark]]"
  - "[[Market Regime Classifier]]"
required_for: []
---

# test_regime_bench

## Definition

Tests for the regime benchmark + replay harness (BENCH-001). Asserts the harness is itself deterministic, that real-snapshot replay is byte-identical, that the synthetic sweep reaches every regime, and that the committed golden artifact stays in sync.

## Purpose

Guarantee the STEP 9 (benchmark) and STEP 10 (replay determinism) evidence is reproducible and that the committed artifact does not drift from the code.

## Constraints

- The harness is deterministic (fixed grid, no randomness/clock); two builds must be byte-identical.

## Implementation Notes

Covers: report determinism (build twice ⇒ identical JSON); `all_replays_byte_identical == true` with 3 consumable real snapshots; real PASS + both source snapshots → RESTRICTIVE_RATES while FAIL/forced are non-consumable; synthetic sweep full coverage (11/11 regimes reachable); committed `artifacts/regime_bench.json` equals a freshly built report.

## Relationships

### Used By
- [[Regime Distribution Benchmark]]
- [[Market Regime Classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
