---
type: artifact_schema
canonical_id: SCHEMA-015
status: active
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
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
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
schema_id: "portfolio-state"
schema_version: "0.1.0"
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
`source_record_id`, `fill_price`, `quantity`, `fill_model_version`, `prior_portfolio_state_hash`, `seq`.

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
