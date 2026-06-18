---
type: benchmark_result
canonical_id: BENCH-004
status: active
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/execution/run_execution_bench.py"
  - "benchmarks/execution/artifacts/execution_bench.json"
related_files:
  - "[[run_execution_bench.py]]"
related_tests:
  - "[[test_execution_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
measures:
  - "replay_determinism"
  - "idempotency"
  - "fill_distribution"
  - "portfolio_state_hash"
  - "guard_block_attribution"
---

# Execution Layer Benchmark

## Definition

The deterministic byte-identical sequence-replay benchmark + harness for the execution layer ([[Execution]]
MOD-008). The **closing artifact for ADR-011 §7 gate (d)** — it proves the ADR-011 §2 execution-determinism
invariant over the STEP-2 simulator core. Two parts:
(1) **real sequence** — build ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012) records by threading the
real consumable snapshots through `consume → build_features → classify → build_decision → evaluate` (one
runtime ledger, genuine dedup), forwarding each ADMIT's gold-packet `direction` and the D1 re-derived
`instrument_price` (the FeatureVector's `gold_price`); thread the ADMITs through the execution `run_sequence`
twice with the same captured `guard_config`; assert byte-identical [[Execution Record Schema]] (SCHEMA-014)
records + an identical ending [[Portfolio State Schema]] (SCHEMA-015) `state_hash`; re-present to evidence
deterministic idempotency;
(2) a clearly-labelled **synthetic sequence** exercising the full execution outcome space (APPROVE+LONG ⇒
fill / non-LONG ⇒ no-fill / duplicate ⇒ idempotent no-double-fill / guard BLOCK ⇒ no-fill + `blocked_by`
attribution) under captured APPROVE and BLOCK guard configs.

## Purpose

Provide execution determinism + idempotency + fill/guard-block evidence pinned via a committed golden
artifact (`benchmarks/execution/artifacts/execution_bench.json`) that [[test_execution_bench]] asserts stays
in sync (drift ⇒ red). Determinism discipline (ADR-011 gate c.4): the guard config is an **explicit captured
value** folded into the replay key, never read from `os.environ` on the replay path — no clock / network /
randomness.

## Results (v0)

- `all_replays_byte_identical = true` across all blocks (real + synthetic-approve + synthetic-block).
- **Real sequence** (`952cc83a…`, the one consumable corpus snapshot): one runtime ADMIT, `direction = AVOID`
  (RESTRICTIVE_RATES), `instrument_price = 4624.5`. AVOID is **non-LONG** ⇒ a deterministic **no-fill**; the
  re-presentation replays byte-identically. The real corpus therefore evidences **replay determinism + stable
  portfolio state**; it never reaches the once-ever fill-dedup branch (no execution entry is appended). Both
  banked snapshots (`952cc83a…` 2026-05-01 and `05c8369d…` 2026-06-11) classify `RESTRICTIVE_RATES → AVOID`;
  `05c8369d…` lives only in the Mr-Ripley truth DB, not as a committed el_nino consumable file.
- **Synthetic sequence** exercises the fill paths the AVOID corpus cannot: `fill_distribution = {filled 1,
  no_fill 4}` (LONG fills at `100.05` = 5 bps adverse slippage; AVOID + FLAT no-fill; the duplicate LONG ⇒
  idempotent no-double-fill, portfolio unchanged); `guard_block_attribution = {SYN4_long_block:
  position_size_ok}` under a restrictive captured guard config.
- `pinned_portfolio_state_hash = 847f714a…` (the synthetic-approve ending portfolio, one GLD position);
  `execution_policy_version 0.1.0` / `fill_model_version 0.1.0`; fingerprints pinned.
- **v0.2.0 runtime re-pin (2026-06-18):** the real sequence threads MOD-007 `evaluate`, so the
  computed-cooldown `runtime_policy_version 0.1.0 → 0.2.0` cascaded the real ADMIT `record_id` →
  `execution_id` (golden `execution_id` re-pinned). The fill behavior, distributions, guard-block
  attribution, and `pinned_portfolio_state_hash` are **unchanged** (identity-only re-pin).

## Relationships

### Depends On
- [[Execution]]
- [[Execution Record Schema]]
- [[Portfolio State Schema]]

### Validated By
- [[test_execution_bench]]

### Justified By
- [[ADR - Execution Layer Planning]]
