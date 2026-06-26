---
type: file
canonical_id: FILE-039
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/core.py"
related_files: []
related_tests:
  - "[[test_ops_core]]"
  - "[[test_live_monitoring]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "ops/core.py"
language: "python"
module: "[[Operations Control Plane]]"
owns: []
used_by:
  - "[[app.py (ops)]]"
  - "[[actions.py (ops)]]"
  - "[[gated.py (ops)]]"
---

# core.py (ops)

## Definition

The **headless governed read-model** for the Operations Control Plane (no Textual import). Pure reads
that reuse the `src/` governed functions and never mutate state or open a network connection.

## Purpose

Assemble every console surface as frozen, JSON-friendly view dataclasses the TUI renders and the tests
assert on — so the read-model is fully testable without a terminal.

## Architecture Role

The single data source for `ops/app.py`. Imports `src/` governed loaders + the pure `run_sequence` +
the live-plug factories; stdlib-only otherwise (ADR-003 boundary preserved).

## Constraints

Read-only (never persists, never opens a socket); fail-closed (loader errors caught into an `error`
field, never raised); **secrets never displayed** (plug status derived only from `client is None`);
ASCII-safe emitted strings. Reuses governed functions, never reimplements safety/gate logic.

## Implementation Notes

`OpsPaths` (explicit artefact paths, testable); `assemble_dashboard()` bundles `ledger_view` /
`portfolio_view` / `operational_view`, the pure `decision_preview` (the only place the six-guard block
exists), `gate_board` (ADR-011 a–f static + ADR-012 G0–G3 advisory), `calibration_readiness` (discrete
`eligible` flag + display string + `g0_floor` mirrored from ADR-012), `plug_statuses`, `process_infos`
(injectable scheduled-task fetcher), `policy_versions`, `recent_events`, and the `audit_tail`.
`resolve_run_snapshot` is shared with the Step-2 run action. `Dashboard.to_dict()` is a deterministic,
secret-free projection.

**LIVE read-model (ISSUE-07, ADR-014).** Additive, read-only: the SIM views are refactored into
path-parameterized helpers (`_ledger_view_at` / `_portfolio_view_at` / `_operational_view_at`) reused by
`live_ledger_view` / `live_portfolio_view` / `live_operational_view` reading the physically-separate
`*.live` files (`OpsPaths.live_*_path`). New views: `reconcile_view` (the append-only `ReconcileEntry`
history + a DERIVED `execution_refused` / `adoptable` / `refuse_reason` — advisory; the authoritative
refuse is recomputed live by `reconcile_and_act`), `pending_orders_view` (the cross-run async-fold queue),
and `live_state_view` (plug status + `operator_halt_active` kill switch + a loud refuse/halt banner).
`adoptable_discrepancy` is the shared precondition source for the gated adopt action. `SIM_BADGE` /
`LIVE_BADGE` constants + `render_text_dashboard` keep the accumulate-only SIM portfolio (a model number,
NOT performance) and the LIVE real-paper-P&L panels **badged distinct and never interleaved**. All live
reads are pure / fail-closed / no-secrets — and no `src/` decision logic or determinism path is touched
(BENCH-004/006 byte-identical).

## Relationships

### Depends On
- [[Operations Control Plane]]

### Validated By
- [[test_ops_core]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
