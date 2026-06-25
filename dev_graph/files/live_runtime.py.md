---
type: file
canonical_id: FILE-044
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
  - ADR
source_paths:
  - "src/orchestration/live_runtime.py"
related_files:
  - "[[live_adapter.py]]"
  - "[[operational_feed.py]]"
related_tests:
  - "[[test_live_runtime]]"
  - "[[test_replayable_fence]]"
  - "[[test_operator_halt]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "src/orchestration/live_runtime.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns:
  - "operate_live"
  - "reconcile_and_act"
  - "plan_reconcile"
  - "LiveExecutionConfig"
used_by: []
---

# live_runtime.py

## Definition

The non-replayable **LIVE** execution entrypoint (ADR-014 bucket ii). `operate_live` is the only door to
a live broker port: it mirrors the chain `run_once` IO shell but threads a **separate**
`(live_ledger, live_portfolio)` pair and does **reconcile-then-act** with the side/order-based
[[live_adapter.py]] `LiveExecutionAdapter` instead of the LONG-only `execute()` simulator path.

## Purpose

Turn the dormant Alpaca paper adapter into an *operable* one without disturbing the deterministic replay
spine. It **reuses** the same pure cores the chain uses for the decision + idempotency + GATE-001 guard
(`build_features → classify → build_decision → evaluate → run_guard`) — [[Chain Orchestrator]] `run_chain`
and the `SimulatedBrokerAdapter` stay structurally unchanged — and replaces only the *act* with broker
reconcile mechanics.

## Architecture Role

The live counterpart to `orchestration.runtime.run_once`, reachable only past the `assert port.replayable`
fence (ADR-014 §5.3) — never from `run_once`/`run_sequence`. Default-OFF: imported explicitly by the
[[ADR - Operations Control Plane]] gated-live console action (`ops/gated.py`, no file node per the
ops-tooling convention), never from the `orchestration` package `__init__`.

## Inputs

- A consumable Layer-2 snapshot; the separate live `(ledger, portfolio)` paths; a `LiveExecutionAdapter`;
  the captured operational input / feed (incl. the [[operational_feed.py]] `OperatorHaltFeed` kill switch);
  the captured guard/runtime/decision/exec configs + a live `LiveExecutionConfig` (fixed notional).

## Outputs

- A `ChainResult` (the full record bundle) persisted to the **separate** live files; a SCHEMA-014 live
  `ExecutionRecord` (status + broker traceability) and a possibly heal-appended SCHEMA-015 `PortfolioState`.

## Constraints

- **Determinism non-contamination (binding):** no live broker read ever enters the shared deterministic
  guard request / `run_chain` / the simulator; the live path writes only the separate files.
- **No auto-flatten:** a discrepancy terminal-refuses execution + appends a reconcile-heal entry; the
  decision/observation/labeling chain still advances (the ledger persists).
- **Accumulate-only sim preserved:** the live SELL-fold (realized P&L) lives here, never in `execute()`.

## Implementation Notes

`plan_reconcile` (pure) maps the decision direction + broker positions/open-orders to a side-based action
(BUY / SELL / NO_ACTION) or a discrepancy (foreign order / wrong-side / unexplained FLAT position).
`reconcile_and_act` orders the fail-closed gates as `execute()` does (guard → idempotency → stance) then
runs the mandatory startup reconcile (account-status gate + positions ∪ open orders) before any order.
Sizing is cash-capped fixed-notional (fractionable) via the adapter's `resolve_order_qty`; fills resolve
from the broker order read (never the POST echo).

**Real live GLD mark (ADR-014 §5.1, pre-live-readiness Blocker 1 — CLOSED).** The submit mark is read live
from the broker (`adapter.live_submit_mark`, basis `BASIS_LIVE_SUBMIT`, pinned ts) inside the startup
reconcile — **fail-closed, never the sim derived proxy** — so recorded slippage is fill-vs-real-mark (the
"plausible-but-wrong slippage" defect is removed). `reconcile_and_act(exec_ref=None)` triggers the live
read; an injected `exec_ref` (tests / captured mark) skips it.

**Cross-run async-fill fold (ADR-014 §6.3, pre-live-readiness Blocker 2 — CLOSED).** A genuinely-async
order yields a QUEUED record and is recorded as a SCHEMA-015 `PendingOrder` (the durable order↔snapshot
lineage). The next startup reconcile `_fold_pending_fills` books any now-filled ours-lineage order **exactly
once** (buy/sell-fold + an `ExecutionEntry`, drop the pending) before planning — so a later LONG nets to
already-long NO_ACTION and a later FLAT sells the lineaged position instead of mis-flagging an unexplained
discrepancy. `client_order_id` 422 dedup + open-orders netting keep the queue window double-order-safe.

## Open Questions

- Partial-fill P&L attribution across runs (a PARTIAL is kept pending and folded when fully FILLED) and the
  optional real-GLD-close **snapshot** ingest (a sim-fidelity upgrade behind the same `exec_ref` seam) remain
  documented follow-ups. The operator probe (`scripts/alpaca_paper_e2e_probe.py`) confirms the empirical
  B-flags + the live-mark endpoint shape before the first live paper run.

## Relationships

### Depends On
- [[Chain Orchestrator]]
- [[live_adapter.py]]
- [[operational_feed.py]]

### Validated By
- [[test_live_runtime]]
- [[test_replayable_fence]]
- [[test_operator_halt]]

### Used By
- [[ADR - Operations Control Plane]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]

### Constrained By
- [[Canonical Ownership]]
