---
type: file
canonical_id: FILE-030
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-17
updated: 2026-06-17
confidence: confirmed
evidence:
  - code
source_paths:
  - "benchmarks/calibration/run_forward_return_labels.py"
related_files: []
related_tests:
  - "[[test_forward_return_labels]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Empirical Calibration Methodology]]"
file_path: "benchmarks/calibration/run_forward_return_labels.py"
language: "python"
module: "[[Gold Forward-Return Labeler]]"
owns:
  - "forward_return"
  - "select_exit"
  - "label_point"
  - "aggregate_by_regime_horizon"
  - "build_report"
used_by: []
---

# run_forward_return_labels.py

## Definition

The single harness file for the [[Gold Forward-Return Labeler]] (MOD-009): pure label/return-math
functions + a read-only corpus driver + the committed golden writer, mirroring the
`run_*_bench.py` idiom.

## Purpose

Produce `benchmarks/calibration/artifacts/forward_return_labels.json` ([[Gold Forward-Return Label
Set]], BENCH-005) — per (decision × horizon) forward-return labels + the per regime × horizon
aggregate that [[ADR - Empirical Calibration Methodology]] gate G3 will consume. Measurement only.

## Architecture Role

Offline, strictly-downstream tool under `benchmarks/calibration/`. Imports the decision chain
read-only (`consume`, `build_features`, `classify`, `build_decision`); the chain never imports it.
Forward returns are computed only from snapshots banked **after** an entry — never fed back onto the
decision path.

## Constraints

- Look-ahead containment + determinism + PIT honesty (see the parent module). `build_decision` is
  called with `(fv, rc)` only; no future data. Non-positive prices fail closed.
- The committed golden is reproducible from el_nino-committed inputs alone (no Mr-Ripley dependency).

## Implementation Notes

Pure core: `forward_return`, `move_sign`, `direction_correct`, `directional_pnl`,
`target_offset_days`, `max_gap_days`, `select_exit`, `label_point`, `label_all`,
`aggregate_by_regime_horizon`, `coverage`, `_mean`, `_median`. Driver: `decision_points_from_corpus`
(the only chain-touching, read-only function; dedups by `snapshot_id`), `build_report`
(`include_external` adds a stdout-only full-corpus diagnostic). `ARTIFACT_PATH` is the committed
golden. Verified: 19 tests pass (`tests/calibration/test_forward_return_labels.py`); mypy --strict
+ ruff clean.

## Relationships

### Depends On
- [[Gold Forward-Return Labeler]]

### Validated By
- [[test_forward_return_labels]]

### Justified By
- [[ADR - Empirical Calibration Methodology]]

### Constrained By
- [[Canonical Ownership]]
