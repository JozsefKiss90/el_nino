---
type: artifact_schema
canonical_id: SCHEMA-015
status: active
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-23
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/execution/models.py"
related_files:
  - "[[models.py (execution)]]"
related_tests:
  - "[[test_execution_determinism]]"
  - "[[test_guard_day_scope]]"
  - "[[test_reconcile_entry]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
schema_id: "portfolio-state"
schema_version: "0.2.0"
schema_path: "src/execution/models.py"
validated_by:
  - "[[test_execution_determinism]]"
  - "[[Execution Layer Benchmark]]"
consumed_by:
  - "[[Execution]]"
produced_by:
  - "[[Execution]]"
---

# Portfolio State Schema

## Definition

The append-only, self-describing portfolio/position state of the execution layer: a frozen `PortfolioState`
of per-instrument positions + an append-only `executions` history keyed by `source_snapshot_id`. Like the
[[Runtime Ledger Schema]] (SCHEMA-013), it is **both** an input and an output of `execute()` (the layer
threads `prior_portfolio -> new_portfolio`), making the stateful execution layer a pure function of explicit
values (ADR-011 §2; ADR-009 §4/§5). It is the state contract realizing [[Position Tracking]] (CAP-007).

## Purpose

Hold the portfolio/position state as an explicit value, not ambient process memory (the KA-009
Wake-Execute-Sleep / file-mediated discipline). **Self-describing** so the state alone is sufficient replay
state: each execution entry records everything needed to reproduce its own portfolio transition. P&L is
**mark-to-snapshot** — marked at the re-derived snapshot instrument price (ADR-011 D1), never a live mark on
the replay path.

## Architecture Role

Consumed and produced by the re-grounded [[Order Management]] (CAP-005) via [[Execution API]] (INT-011);
maintained as the state of [[Position Tracking]] (CAP-007). Persisted/loaded only at the IO boundary shell,
never inside the pure core. Per ADR-003: frozen stdlib dataclasses.

## Schema Definition (illustrative v0 — non-normative until the contract is frozen at code)

**PortfolioState**: `portfolio_schema_version` (string), `positions` (map<instrument, Position>),
`executions` (ordered array<ExecutionEntry>). Methods (planned): `empty()`, `apply(execution_record)` → a
NEW frozen state (`seq = len(executions)`), `state_hash()` (SHA-256 over canonical JSON — the identity that
threads into `execution_id`).

**Position** (per instrument)

| Field | Type | Notes |
|-------|------|-------|
| instrument | enum | `GLD` |
| quantity | number | signed units held |
| avg_cost | number | running average entry price |
| realized_pnl | number | closed-leg P&L |
| unrealized_pnl | number | mark-to-snapshot at the re-derived price (ADR-011 D1) |

**ExecutionEntry** (self-describing): `source_snapshot_id` (the idempotency key / replay anchor),
`source_record_id`, `fill_price`, `quantity`, `fill_model_version`, `prior_portfolio_state_hash`, `seq`,
`as_of` (additive, `schema_version 0.2.0`, ADR-014 §5.2 — the admitting snapshot clock; day-scopes the
guard's `trades_today` so `max_trades_per_day` is a genuine daily cap, mirroring the PRED-008 cooldown
discipline; folds into the replay key → BENCH-004/006 re-pinned).

**ReconcileEntry** (additive new kind, ADR-014 §6.2 — **live-path-only**): `source_snapshot_id`,
`instrument`, `observed_qty`, `observed_avg_price`, `marker`, `seq`, `as_of`. A reconcile *observation* of
broker truth (the authority for position truth) — **not** a fill the system placed, so it carries **no**
`source_record_id` and **no** `guard_result` (distinct from `ExecutionEntry`). It heals a broker↔local
divergence into the append-only history without faking an execution; adopting the observed position into
the local position is a separate ops-console **governed adopt**, never automatic. **Determinism trick:**
`PortfolioState` carries `reconciles: tuple[ReconcileEntry, ...] = ()` and `to_dict()` **omits an empty
`reconciles`** — the sim/replay portfolio (which never produces one) stays byte-identical, so **no further
`schema_version` bump and no benchmark re-pin** for this kind.

**PendingOrder** (additive new kind, ADR-014 §6.3 — **live-path-only**): `source_snapshot_id`,
`source_record_id`, `instrument`, `side` (buy/sell), `requested_qty` (0.0 for a notional order),
`client_order_id`, `seq`, `as_of`. The **durable order↔snapshot lineage** for an order that was accepted
(QUEUED) but had not filled within its run: a market+day order can fill *after* the run ends
(queue-to-next-open), and the per-run `ExecutionRecord` is not itself persisted, so this entry is what lets
the **next startup reconcile fold the cross-run fill exactly once** (book the buy/sell-fold + an
`ExecutionEntry`, then drop the pending order). `client_order_id` 422 dedup + open-orders netting keep the
queue window double-order-safe. **Same determinism trick:** `PortfolioState` carries
`pending: tuple[PendingOrder, ...] = ()` and `to_dict()` **omits an empty `pending`** — the sim/replay
portfolio (which never queues an async order) stays byte-identical, so **no `schema_version` bump and no
benchmark re-pin** for this kind (verified: BENCH-004/006 byte-identical after the change).

## Validation Rules

- **Append-only**: `apply` returns a new state; existing entries are never mutated or deleted.
- **Idempotency**: an already-applied `source_snapshot_id` is not double-applied (the MOD-007 once-ever
  discipline) — replay-safe.
- **Determinism (ADR-011 §2 / ADR-009 §5)**: `to_dict()` emits entries in insertion order with sorted keys;
  `state_hash()` over canonical JSON. Replaying the same ADMIT sequence from the same starting state yields a
  byte-identical ending state + `state_hash`.
- `from_dict` is fail-closed (a malformed entry raises a contract error).

## Open Questions

- Contract frozen at STEP 2 (`schema_version 0.1.0`); threaded `prior → new` by [[Execution]] (MOD-008). Its
  byte-identical ending-`state_hash` determinism is now pinned by the [[Execution Layer Benchmark]]
  (BENCH-004) — ADR-011 §7 gate (d) **Closed**. Single instrument (`GLD`); multi-instrument + alternative
  persistence backends are deferred (ADR-011 Non-Goals).

## Relationships

### Produced By
- [[Execution]]

### Consumed By
- [[Execution]]

### Used By
- [[Position Tracking]]

### Validated By
- [[test_execution_determinism]]
- [[Execution Layer Benchmark]]

### Justified By
- [[ADR - Execution Layer Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Stateless Agent Architecture]]
