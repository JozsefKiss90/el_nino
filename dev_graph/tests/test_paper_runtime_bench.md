---
type: test
canonical_id: TEST-017
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "tests/gold/test_paper_runtime_bench.py"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/gold/test_paper_runtime_bench.py"
test_type: benchmark
covers:
  - "[[Paper-Trading Runtime Benchmark]]"
  - "[[Paper-Trading Runtime]]"
required_for: []
---

# test_paper_runtime_bench

## Definition

Tests for the paper-runtime benchmark (BENCH-003): report determinism, both sequences byte-identical,
no enrich-back (packet `guard_refs` stay unevaluated), the real re-presented snapshot flagged a
duplicate, the synthetic sequence reaching every verdict (ADMIT 3 / HOLD 1 / REJECT 3) with pinned
reject attribution, and the committed golden artifact staying in sync.

## Purpose

Guarantee the runtime benchmark stays deterministic and `paper_runtime_bench.json` never drifts.

## Relationships

### Used By
- [[Paper-Trading Runtime Benchmark]]
- [[Paper-Trading Runtime]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
