---
type: observability
canonical_id: OBS-002
status: active
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
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
related_tests:
  - "[[test_ops_core]]"
  - "[[test_ops_app]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
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
