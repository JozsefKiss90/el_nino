---
type: module
canonical_id: MOD-009
status: active
implementation_status: tested
canonical: true
created: 2026-06-17
updated: 2026-06-17
confidence: confirmed
evidence:
  - code
  - design
  - ADR
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
module_name: "forward_return_labeler"
module_path: "benchmarks/calibration"
responsibility: "Downstream, read-only labeling of banked gold decisions with realized forward gold returns — the ADR-012 gate G3 measurement prerequisite"
depends_on:
  - "[[Gold Decision Builder]]"
  - "[[Market Regime Classifier]]"
  - "[[Feature Builder]]"
  - "[[Snapshot Consumer]]"
provides: []
---

# Gold Forward-Return Labeler

## Definition

A deterministic, **strictly-downstream, read-only** measurement module that labels each
already-produced [[Gold DecisionPacket v0 Schema]] decision with the **gold return realized after
its timestamp**, and aggregates the labels per regime × holding horizon. It is the implementation
of [[ADR - Empirical Calibration Methodology]] (ADR-012) **gate G3's stated prerequisite** — the
per-regime outcome data a future regime→direction table calibration will consume.

## Purpose

G3 is the hardest ADR-012 calibration gate because it needs forward gold-return outcomes per
regime, and no such measurement existed. This module produces those labels. It is **measurement
only**: it never calibrates the regime→direction table, changes any config, or bumps any
`*_version`. G3 itself stays **deferred** — the real corpus is still monochromatic
(1/12 regimes, 1/4 directions, no realizable forward return yet).

## Architecture Role

Offline analysis tool living under `benchmarks/` (deliberately **not** in the shipped decision
`src/`). It sits strictly **after** `consume → build_features → classify → build_decision`: it
re-runs that chain read-only to recover each banked decision, then computes forward returns from
**later** banked snapshots. It is **not** a realization of [[Performance Scoring]] (CAP-013): that
capability is trade-log-driven strategy scoring feeding the Supervisor/promotion (treasury) branch
and its SCHEMA-005 scorecards, a bounded context [[ADR - Decision Layer Re-grounding]] /
[[ADR - Gold Decision Confidence Semantics]] keep permanently separate from the gold-decision
branch. Folding the gold-return labeler into CAP-013 would conflate those contexts (CON-003); it is
instead a standalone calibration tool governed directly by ADR-012. CAP-013 remains `not-started`.

## Inputs (Dependencies)

- The immutable banked PIT corpus (consumable SCHEMA-001 snapshot JSONs): the committed el_nino
  fixture, and — for the operator's full-corpus diagnostic only — the Mr-Ripley `runtime/snapshots`
  archives (a separate repo; not part of the committed golden).
- The read-only decision chain ([[Snapshot Consumer]], [[Feature Builder]],
  [[Market Regime Classifier]], [[Gold Decision Builder]]) to recover `(snapshot_id, clock_ts,
  gold_price, regime, direction)` per banked decision.

## Outputs (Provides)

- The committed golden label set `benchmarks/calibration/artifacts/forward_return_labels.json`
  ([[Gold Forward-Return Label Set]], BENCH-005): per (decision × horizon) labels
  (entry/exit price, forward return, direction-correctness, directional P&L, and a
  realized / pending / no_exit_in_tolerance status) plus the per regime × horizon aggregate G3 will
  consume.

## Constraints

- **Look-ahead containment (non-negotiable, ADR-012 §5).** Strictly downstream of the decision
  chain. The chain MUST NOT import this module; no forward price/return/label may ever reach
  `build_decision` (called with only `(fv, rc)` — no future data). Enforced structurally by
  `test_decision_chain_does_not_import_the_labeler`.
- **Deterministic / PIT-honest.** Pure computation over the immutable, content-addressed corpus;
  ISO timestamps parsed deterministically (no wall-clock); sorted-key canonical JSON; only
  honestly-banked snapshots, deduped by `snapshot_id`; never back-fabricated.
- **Rule-based only** (ADR-005/007) — it measures realized returns; it does not predict or learn.
- **No decision-path / config / `*_version` change.**

## Implementation Notes

Single harness file `run_forward_return_labels.py` (benchmark idiom: pure functions + `build_report()`
+ committed golden + artifact-in-sync test).
- **Horizons** `HORIZONS_TD = (5, 20, 60)` trading-day-equivalents (macro/regime horizons), mapped to
  calendar days via a documented `CAL_PER_TD = 1.4` (the corpus banks ~per calendar day).
- **Exit selection** = nearest banked snapshot at-or-after `entry.clock_ts + horizon`, within a gap
  tolerance `max_gap_days = ceil(0.25 · target_offset)`. Status is `realized` (clean exit),
  `pending` (horizon beyond the latest banked snapshot — knowable later), or `no_exit_in_tolerance`
  (a later snapshot exists but the nearest is past tolerance — a permanent corpus hole). Non-positive
  prices fail closed to `no_price`.
- **Per-label** fields: forward_return `(exit−entry)/entry`; `direction_correct` (LONG↔up, AVOID↔down,
  FLAT↔within flat-band, WATCH→None); `directional_pnl` (LONG +r, AVOID −r, FLAT 0, WATCH None);
  `move_sign`.
- **Aggregate** per regime × horizon: counts by status, mean/median forward return, hit-rate over
  scored labels, mean directional P&L, and a per-direction breakdown — the G3 input.
- Committed golden is built from el_nino-committed inputs only (reproducible in CI). `--include-external`
  adds the Mr-Ripley archives to a stdout-only diagnostic, never to the committed artifact.
- **Today:** committed real corpus dedups to 1 snapshot (all horizons pending); the full corpus
  (5 snapshots) is all RESTRICTIVE_RATES/AVOID, all pending or no_exit_in_tolerance, 0 realized.
  Correctness is established by the synthetic validation set (all 4 directions, 6 regimes, all 3
  statuses, 9 realized). Verified: 19 tests, mypy --strict + ruff clean.

## Open Questions

- GLD-ETF returns as an alternative return series to the snapshot `gold_price` (the price series is
  pluggable; deferred until G3 coverage matters).
- The `CAL_PER_TD`, `MAX_GAP_FRACTION`, and `FLAT_BAND` parameters are documented defaults, revisable
  under ADR-012 governance when real coverage accrues.

## Relationships

### Depends On
- [[Gold Decision Builder]]
- [[Market Regime Classifier]]
- [[Feature Builder]]
- [[Snapshot Consumer]]

### Contains
- [[run_forward_return_labels.py]]

### Produces
- [[Gold Forward-Return Label Set]]

### Validated By
- [[test_forward_return_labels]]
- [[Gold Forward-Return Label Set]]

### Justified By
- [[ADR - Empirical Calibration Methodology]]

### Constrained By
- [[Canonical Ownership]]
