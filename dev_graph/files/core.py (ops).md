---
type: file
canonical_id: FILE-039
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/core.py"
related_files: []
related_tests:
  - "[[test_ops_core]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
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

## Relationships

### Depends On
- [[Operations Control Plane]]

### Validated By
- [[test_ops_core]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
