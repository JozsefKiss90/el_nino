---
type: test
canonical_id: TEST-022
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-17
updated: 2026-06-17
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/calibration/test_forward_return_labels.py"
related_files:
  - "[[run_forward_return_labels.py]]"
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Empirical Calibration Methodology]]"
test_path: "tests/calibration/test_forward_return_labels.py"
test_type: benchmark
covers:
  - "[[Gold Forward-Return Labeler]]"
  - "[[Gold Forward-Return Label Set]]"
required_for: []
---

# test_forward_return_labels

## Definition

The test suite for the [[Gold Forward-Return Labeler]] (MOD-009) and its committed golden
[[Gold Forward-Return Label Set]] (BENCH-005). 19 tests.

## Purpose

Establish correctness **synthetically** (the monochromatic real corpus cannot exercise it) and
enforce the look-ahead containment wall as a regression guard.

## Constraints

Deterministic; no network/clock; synthetic inputs are clearly labelled.

## Implementation Notes

Coverage:
- **Determinism + artifact-in-sync**: `build_report()` byte-identical across runs; committed artifact
  equals `build_report()`.
- **Pure math**: `forward_return`, `move_sign`, `direction_correct` (LONG/AVOID/FLAT/WATCH × up/down/
  flat), `directional_pnl`, `target_offset_days`/`max_gap_days`.
- **Exit selection**: single-point→pending; clean exit at horizon→realized; gap-beyond-tolerance→
  no_exit_in_tolerance; nearest-at-or-after chosen; non-positive entry/exit price fails closed.
- **Synthetic validation set**: all 4 directions + 6 regimes + all 3 statuses; pinned labels and
  per-regime hit-rates; `realized_count == 9`.
- **Real corpus today**: three committed JSONs dedup to one banked snapshot, all horizons pending.
- **Containment (non-negotiable)**: `test_decision_chain_does_not_import_the_labeler` statically
  asserts no `src/{snapshot,features,regime,gold}` file imports the labeler or `benchmarks/`;
  `test_decision_point_carries_no_forward_data` asserts the input row holds only entry-side facts.

## Relationships

### Used By
- [[Gold Forward-Return Labeler]]
- [[Gold Forward-Return Label Set]]

### Justified By
- [[ADR - Empirical Calibration Methodology]]

### Constrained By
- [[Canonical Ownership]]
