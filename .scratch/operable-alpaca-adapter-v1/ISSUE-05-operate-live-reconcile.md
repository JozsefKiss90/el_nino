<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 5 — `operate_live` reconcile-then-act

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (ii). Governed by ADR-014.

## What to build

The integration slice: a **separate non-replayable `live_runtime.operate_live` entrypoint** — the only path to the live plug. It mirrors the chain `run_once` signature shape (snapshot, **separate** ledger/portfolio paths, configs, port), **reuses** the deterministic decision + the GATE-001 guard + the idempotency layer, and adds only broker mechanics. It must never be reachable from `run_once`/`run_sequence` (the Slice 3 `assert port.replayable` fence enforces this).

- **Reconcile-then-act**: mandatory startup reconcile before any new action — read positions (∪ open orders), compute the **delta** to a cash-capped target, act only on the delta (never a blind buy, never double-act across runs).
- **Authority split**: broker = position truth; local portfolio state = decision lineage + idempotency.
- **Cash-cap**: effective reconcile target = `min(configured_notional, settled_cash)`; bound to the literal settled-cash field (fixed-notional is live-plug-only — the sim keeps fixed-qty `default_size`).
- **In-flight / queue ownership**: open-orders-aware reconcile owns the cross-snapshot queue — `delta = target − position − Σ(expected-lineage open-order qty)`; a queued order that nets to zero → **NO_ACTION**. `client_order_id` 422 owns same-order duplicate-submit only. An **unexpected** open order (wrong qty/side or unknown `client_order_id`) is **not netted** → discrepancy.
- **Discrepancy → terminal-refuse execution only** (no auto-flatten): refusal scopes to execution only — the decision/observation/labeling chain keeps running so the calibration corpus never stalls. Adopting an unexplained non-zero broker position is a **governed adopt** (ops-console-gated), never automatic.
- **Reconcile-heal**: heal via a **new append-only reconcile-entry kind** (SCHEMA-015) — observed broker qty + avg entry price + a reconcile marker — distinct from an execution entry (no `source_record_id`, no `guard_result`). Live-path-only.
- **Idempotency bifurcation, not demotion**: `has_execution(source_snapshot_id)` stays the sole idempotency on the sim/replay path; the live path additionally owns reconcile-delta + open-orders awareness + `client_order_id` dedup.
- **Side-based driving**: LONG→buy, FLAT→sell, AVOID/WATCH→NO_ACTION (resolved before the adapter).
- **Live SELL-fold** (live `live_runtime` only, never the pure core): `realized_pnl += qty × (exit_fill − avg_cost); position → 0`. The simulator portfolio stays accumulate-only (`realized_pnl == 0.0`; its `unrealized_pnl` labeled non-strategic and excluded from all performance/ops readings).
- **Separate paths**: persist to the physically separate (ledger, portfolio) pair from Slice 3.
- **Default-OFF**: enabled only via the ADR-013 gated-live action (confirm + audit + paper-host precondition).
- **No second source of truth**: no new SQLite stores (`fill_record`/`scorecard` rejected); execution outcomes stay on the additive SCHEMA-014/015 fields; per-regime accuracy stays in the calibration labeler.

## Acceptance criteria

- [ ] `operate_live` runs end-to-end against a stub broker + temp separate ledger/portfolio paths; it is unreachable from `run_once`/`run_sequence` (fence holds).
- [ ] A mandatory startup reconcile precedes any new action; the reconcile delta drives side-based buy/sell/NO_ACTION.
- [ ] A queued order that already covers the target nets to NO_ACTION; an unexpected open order → discrepancy.
- [ ] Discrepancy → terminal-refuse-execution while the decision/observation/labeling chain still advances; adopting a non-zero broker position requires the ops-console governed adopt.
- [ ] Reconcile-heal appends a SCHEMA-015 reconcile entry (observed qty + avg entry price + marker), distinct from an execution entry; the canonical replay files stay untouched.
- [ ] Cash-cap target = min(configured_notional, settled_cash) against the settled-cash field; the loop converges and never exceeds available cash.
- [ ] The live SELL-fold realizes P&L (`realized_pnl += qty × (exit_fill − avg_cost)`, position → 0); the simulator portfolio stays accumulate-only with `realized_pnl == 0.0`.
- [ ] Idempotency is bifurcated: `has_execution` remains sole on the sim path; the live path adds reconcile-delta + open-orders + `client_order_id` dedup.
- [ ] The live plug is default-OFF and only enabled via the ADR-013 gated-live action; no new SQLite store is introduced.
- [ ] The deterministic decision + GATE-001 guard + idempotency layer are reused (not reimplemented) by `operate_live`.

## Blocked by

- Slice 2 — Day-scoped guard inputs (`.scratch/operable-alpaca-adapter-v1/ISSUE-02-guard-as-of-day-scope.md`)
- Slice 3 — `assert port.replayable` fence + separate live paths (`.scratch/operable-alpaca-adapter-v1/ISSUE-03-replayable-fence-separate-paths.md`)
- Slice 4 — Widened broker Protocol + side-based adapter + state machine (`.scratch/operable-alpaca-adapter-v1/ISSUE-04-broker-protocol-adapter-state-machine.md`)
