---
type: file
canonical_id: FILE-040
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/app.py"
related_files:
  - "[[core.py (ops)]]"
  - "[[actions.py (ops)]]"
  - "[[gated.py (ops)]]"
related_tests:
  - "[[test_ops_app]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "ops/app.py"
language: "python"
module: "[[Operations Control Plane]]"
owns: []
used_by: []
---

# app.py (ops)

## Definition

The **Textual TUI** over `ops/core.py` — the `OpsConsole` app + the `ConfirmModal`. Renders the
read-model and dispatches the action tiers; performs no mutation itself (it calls the governed action
functions).

## Purpose

Give the operator the interactive terminal surface (panes, status bar, key bindings, live log) plus a
`--once` headless dump.

## Architecture Role

The only file that imports Textual/Rich (the optional `ops` dependency group). Bootstraps `src/` onto
`sys.path` so `python -m ops.app` works without an editable install. No network listener.

## Constraints

Read-only-before-actions; Tier-2 safe actions (no confirm) and Tier-3 gated actions (confirm modal +
audit + server-side precondition); subprocess actions run in **crash-proof thread workers** (a raising
action can neither stick the UI nor exit the app); the `--once` dump is stdout-safe (UTF-8/replace).

## Implementation Notes

Tabs: Overview / **Live** / Gates / Calibration / Artefacts / Processes / Plugs / Log. Bindings: `r`
refresh, `c`/`k`/`s` safe tier, `a`/`g`/`u`/`b`/`h`/`j`/`p` gated tier (each opens `ConfirmModal` showing
its precondition; `p` = the ISSUE-07 adopt-broker-position). `@work(thread=True)` workers marshal results
back via `call_from_thread`; the Log pane shows the audit tail + daily-run logs. The status bar's
`PAPER-ONLY` badge is always on.

**LIVE surfaces (ISSUE-07, ADR-014).** A top-of-dashboard **live-state strip** (`#live-strip`: plug
status + kill-switch ENGAGED/clear + a loud refuse/halt banner) and a **Live tab** rendering the live
ledger, the live portfolio (REAL paper P&L), the reconcile/discrepancy DataTable (discrepancy markers in
red), and the pending-orders DataTable — all under the `LIVE_BADGE`. The existing canonical panels are
badged `SIM_BADGE` (the Artefacts pane gains a "model number, never a P&L track record" header) so the
accumulate-only SIM portfolio is never read as performance.

## Relationships

### Depends On
- [[Operations Control Plane]]
- [[core.py (ops)]]
- [[actions.py (ops)]]
- [[gated.py (ops)]]

### Validated By
- [[test_ops_app]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
