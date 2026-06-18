---
type: benchmark_result
canonical_id: BENCH-003
status: active
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
  - benchmark
source_paths:
  - "benchmarks/gold/run_paper_runtime_bench.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
measures:
  - "replay_determinism"
  - "idempotency"
  - "verdict_distribution"
  - "no_enrich_back"
  - "ledger_state_hash"
---

# Paper-Trading Runtime Benchmark

## Definition

The deterministic benchmark + replay harness for the paper-trading runtime (MOD-007). Two parts:
(1) **real sequence** — build packets from the real consumable snapshots (with forwarded
`snapshot_guards` + `as_of`, `guards` left `None`), thread them through `run_sequence` twice, assert
byte-identical records + ending ledger, and re-present the first snapshot to evidence idempotency;
(2) a clearly-labelled **synthetic sequence** that exercises the full verdict space (ADMIT / HOLD /
REJECT-operational / REJECT-data / REJECT-duplicate) and records the verdict distribution.

## Purpose

Provide runtime determinism + idempotency evidence and a verdict distribution, pinned via a committed
golden artifact (`benchmarks/gold/artifacts/paper_runtime_bench.json`) that a test asserts stays in
sync. Also evidences **no enrich-back** (every packet's `guard_refs` stays unevaluated).

## Results (v0)

- Real sequence: `all_replays_byte_identical = true`, `no_enrich_back = true`. The three real snapshot
  paths are content-identical (one underlying snapshot), so verdicts are `[ADMIT, REJECT, REJECT,
  REJECT]` — the first admits, the rest are duplicates (`duplicate_ok`). Re-presented snapshot ⇒ REJECT
  / `duplicate_ok`.
- Synthetic sequence: `all_replays_byte_identical = true`; verdict distribution `ADMIT 3 / HOLD 1 /
  REJECT 3` (operational / data / duplicate reject attribution pinned).
- **v0.2.0 re-pin (2026-06-18, computed-cooldown amendment):** `runtime_policy_version 0.1.0 → 0.2.0`;
  `runtime_policy_fingerprint ab798cae…6f32 → 47ca2649…98cc8`; record/ledger schema versions `0.1.0`
  (unchanged). The verdict distributions + triggered-guard attributions above are **unchanged** (every
  existing distinct-admit gap is ≥24h > the 20h default cooldown window, so the computed cooldown blocks
  nothing here); only the version-keyed `record_id`s were re-pinned. The cooldown block/elapsed/fail-closed
  paths are exercised by new synthetic unit tests ([[Cooldown OK]] PRED-008), not this corpus.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_bench]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
