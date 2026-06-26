---
type: file
canonical_id: FILE-042
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/gated.py"
related_files:
  - "[[core.py (ops)]]"
  - "[[audit.py (ops)]]"
  - "[[alpaca_adapter.py]]"
related_tests:
  - "[[test_ops_gated]]"
  - "[[test_live_monitoring]]"
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Withdrawal Disabled]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
file_path: "ops/gated.py"
language: "python"
module: "[[Operations Control Plane]]"
owns: []
used_by:
  - "[[app.py (ops)]]"
---

# gated.py (ops)

## Definition

The **Tier-3 gated-live actions** (ADR-013 §3) — the most privileged surface:
`run_chain_now_alpaca_paper`, `register_daily_schedule`, `unregister_daily_schedule`,
`commit_calibration_bump`, the operator kill switch (`set_operator_halt` / `resume_operator_halt`), and
the ISSUE-07 `adopt_broker_position`, plus the `GATED_ACTIONS` registry and `precondition_line`. Each
enforces a **server-side precondition**, writes one audit entry, and **never raises**.

## Purpose

Let the operator perform privileged transitions — only behind a confirm modal (in the TUI) + audit + an
in-code precondition that fail-closes.

## Architecture Role

Reuses the governed live plugs ([[alpaca_adapter.py]] `paper_adapter_from_env`) + the existing schedule
script + the read-model gate. No live-money path; paper-only always.

## Constraints

Paper-only / no live-money ([[Withdrawal Disabled]] PRED-005 enforced upstream); the Alpaca run REFUSES
(no order) when `paper_adapter_from_env().client is None` (no creds / non-paper host); the calibration
bump branches on the discrete `eligible` flag and is `executed=False` on **every** branch (never mutates
a `*_version`); structural never-raise (an outer guard funnels any unexpected error to an audited result);
the full audit surface is secret-redacted.

## Implementation Notes

`run_chain_now_alpaca_paper` uses nested try/except so a live-order failure audits as `executed=True`
while a pre/post error audits as `executed=False`. `register`/`unregister` shell the governed
script/`Unregister-ScheduledTask` via an injectable runner. `_finish` redacts + guards the audit write.
The TUI wraps each call in a crash-proof worker behind `ConfirmModal`.

**`adopt_broker_position` (ISSUE-07, ADR-014 §6.2).** The one governed way out of a terminal-refuse: it
adopts the observed broker position (qty + avg entry price) into the live portfolio so the next FLAT cycle
can sell to close instead of refusing — **never automatic**. Server-side precondition (in-code, not the
UI): an unhealed `discrepancy:unexplained_position` with a positive observed qty and no current local open
position must exist (via `core.adoptable_discrepancy`), else REFUSE (`executed=False`, nothing written).
It is **append-only / reuse-only** — records an `adopt:reconcile-adopt` `ReconcileEntry` in the existing
reconcile history and sets the position from the OBSERVED truth using the **existing** immutable
`PortfolioState` value type (`append_reconcile` + `dataclasses.replace`), persisting via the existing
`persist_portfolio` onto the SEPARATE `*.live` file. Only the per-lot cost basis resets to the observed
broker avg; the portfolio-level **realized-P&L accumulator carries forward** from any prior flat position
(mirrors `_apply_live_buy`'s `r0` carry) so adopt never wipes the LIVE real-paper-P&L track record. No
`src/` method, schema, or `*_version` is added/changed; the canonical sim/replay portfolio is never touched.

## Relationships

### Depends On
- [[Operations Control Plane]]
- [[core.py (ops)]]
- [[audit.py (ops)]]
- [[alpaca_adapter.py]]

### Validated By
- [[test_ops_gated]]

### Constrained By
- [[No Wiki Mutation]]
- [[Withdrawal Disabled]]

### Justified By
- [[ADR - Operations Control Plane]]
