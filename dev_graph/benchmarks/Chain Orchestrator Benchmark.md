---
type: benchmark_result
canonical_id: BENCH-006
status: active
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/orchestration/run_chain_bench.py"
  - "benchmarks/orchestration/artifacts/chain_bench.json"
related_files:
  - "[[run_chain_bench.py]]"
related_tests:
  - "[[test_chain_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
measures:
  - "end_to_end_replay_determinism"
  - "admission_idempotency"
  - "verdict_distribution"
  - "fill_distribution"
  - "ledger_state_hash"
  - "portfolio_state_hash"
  - "full_replay_key"
---

# Chain Orchestrator Benchmark

## Definition

The deterministic byte-identical **end-to-end** sequence-replay benchmark + harness for the chain
orchestrator ([[Chain Orchestrator]] MOD-010). It threads the real consumable snapshots through the
orchestrator `run_sequence` (one runtime ledger + one portfolio — genuine once-ever dedup) **twice** and
asserts byte-identical *all five* record types ([[Feature Vector Schema]] / [[Regime Classification Schema]]
/ [[Gold DecisionPacket v0 Schema]] / [[Runtime Decision Record Schema]] / [[Execution Record Schema]]) +
an identical ending [[Runtime Ledger Schema]] + [[Portfolio State Schema]] `state_hash`; it re-presents the
first snapshot to evidence end-to-end admission idempotency. The report carries the **full replay key** — the
union of every composed layer's version axis + the captured guard / operational fingerprints.

## Purpose

Provide end-to-end replay-determinism + admission-idempotency evidence pinned via a committed golden artifact
(`benchmarks/orchestration/artifacts/chain_bench.json`) that [[test_chain_bench]] asserts stays in sync
(drift ⇒ red). Determinism discipline: the guard config + the operational input are **explicit captured
values** folded into the replay key, never read live on the replay path — no clock / network / randomness.

## Results (v0)

- `all_replays_byte_identical = true` across the real sequence (replayed twice).
- **Real sequence** (the consumable corpus `952cc83a…`, presented across the three consumable paths +
  one re-presentation): `verdict_distribution = {ADMIT 1, HOLD 0, REJECT 3}`. The first presentation ADMITs
  (`RESTRICTIVE_RATES → AVOID`, `packet_id gold-v0:5653d07a0b3949d5`, in-hand `gold_price = 4624.5`); AVOID is
  **non-LONG** ⇒ a deterministic **no-fill**. Every re-presentation of the same `source_snapshot_id` REJECTs
  on `duplicate_ok` (no second admit), and the portfolio never double-fills — the end-to-end idempotency
  evidence. `fill_distribution = {filled 0, no_fill 4}`.
- `pinned_ledger_state_hash = fff4dcc3…`; `pinned_portfolio_state_hash = 2d19b9b5…` (the empty portfolio —
  the AVOID corpus appends no execution entry).
- **Full replay key** pinned: `feature_schema_version 0.1.0`, `taxonomy_version 1.0.0` /
  `classifier_version 0.1.0` / `classification_trace_version 0.1.0`, `decision_policy_version 0.1.0`,
  `runtime_policy_version 0.2.0` (computed-cooldown amendment), `execution_policy_version 0.1.0`, `fill_model_version 0.1.0`,
  `packet/record/ledger/execution/portfolio` schema versions, + the decision / runtime / execution / fill /
  guard / operational fingerprints.

## Honest Caveat

The real corpus is monochromatic `RESTRICTIVE_RATES → AVOID`, so this benchmark proves **end-to-end replay
determinism + admission idempotency**, **not** a real fill. The fill path (APPROVE+LONG ⇒ fill, duplicate ⇒
no-double-fill, guard BLOCK ⇒ attribution) is covered by [[Execution Layer Benchmark]] (BENCH-004)'s
synthetic execution sweep — carried forward unchanged.

## Relationships

### Depends On
- [[Chain Orchestrator]]
- [[Runtime Ledger Schema]]
- [[Portfolio State Schema]]

### Validated By
- [[test_chain_bench]]

### Justified By
- [[ADR - Execution Layer Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
