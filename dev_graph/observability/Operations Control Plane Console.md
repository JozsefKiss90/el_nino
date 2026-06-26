---
type: observability
canonical_id: OBS-002
status: active
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-25
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "ops/app.py"
  - "ops/core.py"
related_files:
  - "[[app.py (ops)]]"
  - "[[core.py (ops)]]"
  - "[[gated.py (ops)]]"
related_tests:
  - "[[test_ops_core]]"
  - "[[test_ops_app]]"
  - "[[test_live_monitoring]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
---

# Operations Control Plane Console

## Definition

The operator-facing observability + control surface provided by the [[Operations Control Plane]] (MOD-011)
module — a **local terminal** Textual TUI over the El Niño Layer-3 runtime. Distinct from the JARVIS
graph console ([[Dev Graph Dashboard]] is the dev_graph's own observability page); this monitors the
**runtime**, not the engineering graph.

## Purpose

A single screen for the operator to monitor every pipeline status and (in higher tiers) trigger operator
actions — all paper-only, secrets-never-shown, and gate-respecting per [[ADR - Operations Control Plane]].

## Architecture Role

A read-only-by-default monitor with two action tiers layered on top. It opens no network listener; it
reads artefacts + calls governed functions in-process. The data it renders comes from the headless
read-model `ops.core.assemble_dashboard()`.

## Inputs (Dependencies)

The governed read-model `ops.core` (which reuses [[Chain Orchestrator]], [[Paper-Trading Runtime]],
[[Execution]], [[Gold Forward-Return Labeler]]), plus the append-only audit log.

## Outputs (Provides)

A live terminal view with: a **header + status bar** (pipeline health, always-on `PAPER-ONLY` badge,
calibration verdict, last verdict), and panes/tabs:

- **Overview** — pipeline headline, the pure latest-decision preview (regime / direction / verdict / the
  six-guard block / fill-or-no-fill), and active policy versions.
- **Gates** — ADR-011 (a–f, all closed) and ADR-012 (G0–G3 advisory) gate boards as DataTables.
- **Calibration** — readiness (N vs G0, regime/direction distributions, realized labels), the discrete
  `eligible` verdict, and the "never bumps" note.
- **Artefacts** — ledger / portfolio / operational-capture / calibration-golden rows.
- **Processes** — daily scheduled task, producer corpus freshness, Neo4j sync.
- **Plugs** — Alpaca paper-execution + clock-feed status (`dormant` / `creds-present`, never a key).
- **Log** — a RichLog tailing the append-only **audit log** + the daily-run logs.

**LIVE monitoring (ISSUE-07, ADR-014).** A top-of-dashboard **live-state strip** (live-plug status,
operator kill-switch ENGAGED/clear, and a loud banner when an unhealed discrepancy → execution is refused)
and a **Live tab** rendering the REAL paper P&L surfaces from the physically-separate `*.live` files: the
live ledger, the live portfolio (per-instrument qty / avg_cost / **realized_pnl** / unrealized_pnl), the
reconcile/discrepancy panel (DISCREPANCY markers surfaced prominently), and the pending-orders panel (the
cross-run async-fold queue). The SIM and LIVE panels are **badged distinct and never interleaved** — the
accumulate-only SIM portfolio (a Q6 determinism artifact, a *model number, not performance*) is never
shown as a track record. One governed Tier-3 control is added: **adopt-broker-position** (confirm + audit
+ server-side precondition) adopts an observed broker position into the live portfolio (append-only
reconcile-adopt, never automatic, ADR-014 §6.2), clearing the terminal-refuse so live execution can resume.

Auto-refresh on an interval + manual refresh; key bindings shown in the footer.

## Constraints

Local-only; paper-only; secrets never displayed; confirm + audit + server-side precondition on every
mutation; read-only-before-actions (the build order is itself a governance gate, ADR-013 §10). No
`wiki/**`/`raw/**` mutation ([[No Wiki Mutation]]).

## Implementation Notes

Rendered by `ops/app.py` (the `OpsConsole` Textual app + `ConfirmModal`) over `ops/core.py`'s frozen
view dataclasses. The whole dashboard is a deterministic, secret-free projection (`Dashboard.to_dict()`)
verified by a no-credential-leak test.

## Relationships

### Depends On
- [[Operations Control Plane]]

### Validated By
- [[test_ops_core]]
- [[test_ops_app]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
