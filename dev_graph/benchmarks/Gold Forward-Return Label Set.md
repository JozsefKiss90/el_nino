---
type: benchmark_result
canonical_id: BENCH-005
status: active
implementation_status: implemented
canonical: true
created: 2026-06-17
updated: 2026-06-17
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/calibration/run_forward_return_labels.py"
  - "benchmarks/calibration/artifacts/forward_return_labels.json"
related_files:
  - "[[run_forward_return_labels.py]]"
related_tests:
  - "[[test_forward_return_labels]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Empirical Calibration Methodology]]"
measures:
  - forward_return
  - directional_pnl
  - hit_rate
  - regime_direction_correctness
  - horizon_coverage
  - realized_pending_status
---

# Gold Forward-Return Label Set

## Definition

The committed golden artifact `benchmarks/calibration/artifacts/forward_return_labels.json` produced
by the [[Gold Forward-Return Labeler]] (MOD-009): per (gold-decision × holding-horizon) labels of the
realized forward gold return, plus the per regime × horizon aggregate that
[[ADR - Empirical Calibration Methodology]] (ADR-012) gate G3 will consume.

## Purpose

Pin the deterministic measurement output (artifact-in-sync) and record today's honest, sparse
real-corpus labels alongside the synthetic validation set. Measurement only — it does **not**
calibrate the regime→direction table; G3 stays deferred.

## Architecture Role

The G3 calibration **input** artifact. Strictly downstream of the decision chain; carries forward
returns that must never reach a decision (see MOD-009).

## Constraints

Deterministic, sorted-key JSON; committed scope reproducible from el_nino-committed inputs only
(the Mr-Ripley full-corpus run is a stdout-only diagnostic, never committed); honestly-banked,
`snapshot_id`-deduped snapshots only.

## Implementation Notes

Pins, per (decision × horizon): entry/exit price, exit snapshot, `forward_return`, `move_sign`,
`direction_correct`, `directional_pnl`, and a `realized | pending | no_exit_in_tolerance | no_price`
status; plus a per regime × horizon aggregate (counts by status, mean/median return, hit-rate over
scored labels, mean directional P&L, per-direction breakdown). Records the `decision_versions`
provenance (feature_schema/taxonomy/classifier/decision_policy) the labels are tied to — a future
calibration `*_version` bump re-pins this artifact.

**Current state (2026-06-17):** committed real corpus = 1 deduped snapshot (RESTRICTIVE_RATES/AVOID),
all horizons pending → 0 realized. Synthetic set = 6 regimes, all 4 directions, all 3 statuses,
9 realized (proves the math the monochromatic corpus cannot). Full corpus (5 snapshots, via
`--include-external`) = all RESTRICTIVE_RATES/AVOID, all pending or no_exit_in_tolerance, 0 realized.

## Relationships

### Depends On
- [[Gold Forward-Return Labeler]]
- [[Gold Decision Builder]]
- [[Market Regime Classifier]]

### Validated By
- [[test_forward_return_labels]]

### Justified By
- [[ADR - Empirical Calibration Methodology]]

### Constrained By
- [[Canonical Ownership]]
