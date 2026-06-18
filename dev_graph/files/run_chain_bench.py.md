---
type: file
canonical_id: FILE-035
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "benchmarks/orchestration/run_chain_bench.py"
related_files: []
related_tests:
  - "[[test_chain_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "benchmarks/orchestration/run_chain_bench.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# run_chain_bench.py

## Definition

The BENCH-006 harness: the deterministic, IO-light benchmark that threads the real consumable snapshots
through the orchestrator `run_sequence` **twice** and emits the committed golden artifact
`benchmarks/orchestration/artifacts/chain_bench.json`. Mirrors the BENCH-003 / BENCH-004 harness shape.

## Purpose

Prove the **end-to-end** Layer-3 replay-determinism + admission-idempotency the chain threads: byte-identical
*all five* record types (feature / regime / packet / runtime / execution) + identical ending ledger +
portfolio `state_hash`, with a re-presentation REJECTing on `duplicate_ok` (no second admit, no double-fill).
Carries the **full replay key** (the union of every composed layer's version axis + the captured guard /
operational fingerprints).

## Architecture Role

A benchmark harness over [[Chain Orchestrator]] (MOD-010); it produces the committed golden artifact for
[[Chain Orchestrator Benchmark]] (BENCH-006); [[test_chain_bench]] (TEST-025) regenerates it in-memory and
asserts byte-for-byte sync.

## Constraints

- Deterministic + IO-light: fixed committed inputs, captured guard + operational config, sorted-key canonical
  JSON, no clock / network / randomness.
- Honest caveat (carried from BENCH-004): the monochromatic AVOID corpus ⇒ a deterministic no-fill; the fill
  path is covered by BENCH-004's synthetic execution sweep, not here.
- Reads only; never mutates any layer's logic or contract.

## Implementation Notes

`build_report()` assembles `real_sequence` (the chain replayed twice, all-record byte-identical comparison +
verdict/fill distributions + idempotency) + `replay_key` + top-level `measures` / `pinned_*_state_hash`.
`_replay_key()` sources every layer's version + fingerprint from the `DEFAULT_*` configs.

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Validated By
- [[test_chain_bench]]
