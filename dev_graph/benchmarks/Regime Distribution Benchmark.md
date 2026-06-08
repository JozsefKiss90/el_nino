---
type: benchmark_result
canonical_id: BENCH-001
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/regime/run_regime_bench.py"
  - "benchmarks/regime/artifacts/regime_bench.json"
related_files: []
related_tests:
  - "[[test_regime_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
measures:
  - distribution
  - coverage
  - entropy
  - classification_balance
  - unclassified_pct
  - rule_utilization
  - regime_frequency
---

# Regime Distribution Benchmark

## Definition

The first benchmark_result node (STEP 9 + STEP 10). A deterministic harness (`benchmarks/regime/run_regime_bench.py`) that emits a committed golden artifact (`benchmarks/regime/artifacts/regime_bench.json`) with two parts: real-snapshot replay determinism, and a clearly-labelled synthetic feature-grid sweep measuring the regime distribution.

## Purpose

Provide reproducible evidence that (a) the same snapshot always maps to the same regime (replay determinism) and (b) the taxonomy is balanced and fully reachable, without fabricating market history.

## Measured Metrics

- **determinism**: every available real snapshot (3 fixtures + 2 source snapshots) replayed twice → `all_replays_byte_identical = true`; PASS + both sources → RESTRICTIVE_RATES; FAIL/forced non-consumable.
- **synthetic sweep** (`synthetic: true`): distribution_pct, coverage (regimes_hit/total = 11/11, all_reachable = true), Shannon entropy_bits, classification_balance (normalized entropy), unclassified_pct, rule_utilization, regime_frequency.

## Constraints

- Fully deterministic: fixed inputs, fixed synthetic grid, no randomness, no clock — so the artifact is a committable golden ([[test_regime_bench]] asserts sync).
- The synthetic sweep is explicitly labelled synthetic; there is no real historical corpus in-repo.

## Interpretation

The current artifact (taxonomy_version 1.0.0, classifier_version 0.1.0) records all 11 signal regimes reachable, entropy ≈ 3.01 bits, balance ≈ 0.87, unclassified ≈ 0.34% (the single INDETERMINATE edge cell). A `taxonomy_version` bump regenerates the golden.

## Relationships

### Depends On
- [[Market Regime Classifier]]

### Validated By
- [[test_regime_bench]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Regime Taxonomy]]
