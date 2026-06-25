---
type: artifact_schema
canonical_id: SCHEMA-014
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
  - "[[test_execution_engine]]"
  - "[[test_price_reference]]"
  - "[[test_live_adapter]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
schema_id: "execution-record"
schema_version: "0.1.0"
schema_path: "src/execution/models.py"
validated_by:
  - "[[test_execution_engine]]"
  - "[[Execution Layer Benchmark]]"
consumed_by:
  - "[[Position Tracking]]"
produced_by:
  - "[[Execution]]"
---

# Execution Record Schema

## Definition

The output contract of the execution layer's pure `execute()`: a frozen `ExecutionRecord` that **wraps** an
ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012) by reference (`source_record_id`) and records the
(paper) fill it produced + the guard provenance it passed. A **net-new, permanently separate**
artifact_schema with a new canonical_id (ADR-011 §1) — a paper execution result, **never** a live order or
broker instruction. `paper_only` (ADR-011 §3).

## Purpose

Capture the deterministic fill outcome of an ADMITted decision on a separate, self-describing record (the
**wrap, never enrich** discipline, ADR-009 §2) — the SCHEMA-012 admission record stays pure. Self-describing
for its own replay (ADR-009 §5): it records the price it used (re-derived per ADR-011 D1) + the fill-model
version + the prior-state hash, so it reproduces **without** touching the frozen pure chain.

## Architecture Role

Output schema of the re-grounded [[Order Management]] (CAP-005), produced via [[Execution API]] (INT-011).
Consumed by [[Position Tracking]] (CAP-007) to update the [[Portfolio State Schema]] (SCHEMA-015). Per
ADR-003: a frozen stdlib dataclass with a byte-stable `to_dict()`.

## Schema Definition (illustrative v0 — non-normative until the contract is frozen at code)

**ExecutionRecord**

| Field | Type | Notes |
|-------|------|-------|
| execution_id | string | deterministic hash over `source_record_id` + `fill_model_version` + `execution_policy_fingerprint` + `instrument_price` + `prior_portfolio_state_hash` (per-execution identity) |
| execution_schema_version | string | this contract-shape version (`0.1.0`) |
| source_record_id | string | the wrapped ADMIT `RuntimeDecisionRecord` (SCHEMA-012); never embedded/mutated |
| source_snapshot_id | string | the replay anchor (echoed from the admit record) |
| instrument | enum | `GLD` (single instrument; multi-instrument is an ADR-011 Non-Goal) |
| direction | enum | echoed gold stance (`LONG`/`FLAT`/`AVOID`/`WATCH`); non-`LONG` ⇒ no fill |
| size | number | the fixed `config.default_size` (ADR-011 D2 — sizing deferred, not computed) |
| instrument_price | number | re-derived from `source_snapshot_id` (ADR-011 D1) |
| fill | object \| null | `{fill_price, quantity, slippage_bps}` — simulated, or the adapter's paper fill (echoed for logging only) |
| guard_result | object | the GATE-001 outcome `{approved (bool), blocked_by (predicate \| null)}` — forwarded, not recomputed |
| execution_mode | enum | `simulated` \| `alpaca_paper` |
| replayable | bool | `true` for `simulated`, `false` for `alpaca_paper` (ADR-011 §2) |
| fill_model_version | string | the fill-model axis (folds into the replay key) |
| prior_portfolio_state_hash | string | the portfolio `state_hash` before this execution |
| new_portfolio_state_hash | string | the portfolio `state_hash` after |
| paper_only | bool | fixed `true` (ADR-011 §3) |
| non_execution_notice | string | carried-forward paper assertion |

**Additive ADR-014 fields** (`execution_schema_version` stays `0.1.0` — additive, output-only, no `from_dict`; sim/replay records leave the live fields `None`/defaults so their `to_dict` + goldens are byte-identical):

| Field | Type | Notes |
|-------|------|-------|
| exec_ref_gld_price | number | the GLD **share** execution reference (§5.1); `== instrument_price`. Sim/replay: derived proxy `gold_price_proxy × OZ_PER_SHARE`; live: the submit-time GLD mark (basis `live_submit_mark`) with the broker fill recorded GLD-vs-GLD |
| exec_ref_gld_price_ts | string \| null | the reference timestamp (snapshot clock on the sim path; pinned submit/open mark on the live path) |
| exec_ref_gld_price_basis | string | provenance label: `sim_derived_proxy` \| `live_submit_mark` \| `live_open_mark` |
| status | enum \| null | live state machine `{QUEUED, PARTIAL, FILLED, EXECUTION_UNCERTAIN, NO_ACTION}` (§6); `None` on the sim/replay path |
| client_order_id | string \| null | deterministic broker idempotency id (`eln-<side>-…`, 422 dedup); live-only |
| alpaca_order_id | string \| null | broker order id (audit lineage); live-only |
| raw_payload | string \| null | the raw broker response / reject body (never silently dropped); live-only |

## Validation Rules

- **Fail-closed:** a non-ADMIT source is rejected (only ADMIT records execute); a BLOCK `guard_result` ⇒ no
  fill (`fill: null`) and `blocked_by` names the first failing predicate.
- **Determinism (ADR-011 §2):** same inputs + versions + fill seed ⇒ identical record; `to_dict()` byte-stable
  (sorted keys). No wall-clock/network/randomness/hidden state on the replay path.
- **paper_only** is fixed `true`; the record never represents a live-money order (ADR-011 §3 / Non-Goals).

## Open Questions

- Contract frozen at STEP 2 (`schema_version 0.1.0`); produced by [[Execution]] (MOD-008), consumed by
  [[Position Tracking]] (CAP-007). Its byte-identical replay determinism is now pinned by the
  [[Execution Layer Benchmark]] (BENCH-004) — ADR-011 §7 gate (d) **Closed**.

## Relationships

### Consumes
- [[Runtime Decision Record Schema]]

### Produced By
- [[Execution]]

### Used By
- [[Position Tracking]]

### Validated By
- [[test_execution_engine]]
- [[Execution Layer Benchmark]]

### Justified By
- [[ADR - Execution Layer Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Paper Trading Validation]]
