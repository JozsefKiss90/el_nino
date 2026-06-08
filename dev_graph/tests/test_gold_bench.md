---
type: test
canonical_id: TEST-011
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
  - "tests/gold/test_gold_bench.py"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
test_path: "tests/gold/test_gold_bench.py"
test_type: benchmark
covers:
  - "[[Gold Decision Distribution Benchmark]]"
  - "[[Gold Decision Builder]]"
required_for: []
---

# test_gold_bench

## Definition

Tests for the gold benchmark + replay harness (BENCH-002): report determinism, real-snapshot packet replay byte-identical, the pinned real PASS packet (RESTRICTIVE_RATES → AVOID / 0.39744 / `gold-v0:5653d07a0b3949d5`), all four directions reachable in the synthetic sweep, the observed regime→direction map matching the policy table, and the committed golden artifact staying in sync.

## Purpose

Guarantee the gold benchmark stays deterministic and the committed `gold_bench.json` artifact never drifts from a freshly built report.

## Relationships

### Used By
- [[Gold Decision Distribution Benchmark]]
- [[Gold Decision Builder]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
