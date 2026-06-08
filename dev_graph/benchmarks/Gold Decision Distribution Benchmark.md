---
type: benchmark_result
canonical_id: BENCH-002
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
  - "benchmarks/gold/run_gold_bench.py"
related_files: []
related_tests:
  - "[[test_gold_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
measures:
  - "replay_determinism"
  - "direction_distribution"
  - "regime_direction_map"
  - "confidence_stats"
  - "uncertainty_stats"
---

# Gold Decision Distribution Benchmark

## Definition

The deterministic benchmark + replay harness for the Gold Decision Builder (MOD-006). Two parts: (1) **determinism evidence** — every consumable real snapshot replayed twice through `consume → build_features → classify → build_decision` is byte-identical (`all_replays_byte_identical = true`, 3 consumable, all RESTRICTIVE_RATES → AVOID); (2) a clearly-labelled **synthetic sweep** over the same regime feature grid emitting the direction distribution, the observed regime→direction map, and confidence/uncertainty stats.

## Purpose

Provide gold-layer determinism evidence and a paper-decision distribution, and pin them via a committed golden artifact (`benchmarks/gold/artifacts/gold_bench.json`) that a test asserts stays in sync.

## Results (v0)

- Determinism: `all_replays_byte_identical = true`; real PASS → RESTRICTIVE_RATES / AVOID / confidence 0.39744 / `packet_id gold-v0:5653d07a0b3949d5`.
- Synthetic sweep (292 cells): all four directions reachable (LONG/FLAT/AVOID/WATCH); confidence mean ≈ 0.264 (min 0.0 INDETERMINATE, max 0.95).
- `decision_policy_version 0.1.0`; `decision_policy_fingerprint be7e3192…a8a5` recorded.

## Relationships

### Depends On
- [[Gold Decision Builder]]

### Validated By
- [[test_gold_bench]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Gold Decision Confidence Semantics]]
