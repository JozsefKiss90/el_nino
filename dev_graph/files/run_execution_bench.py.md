---
type: file
canonical_id: FILE-029
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "benchmarks/execution/run_execution_bench.py"
related_files: []
related_tests:
  - "[[test_execution_bench]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "benchmarks/execution/run_execution_bench.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# run_execution_bench.py

## Definition

The BENCH-004 harness: the deterministic, IO-light benchmark that threads real + synthetic ADMIT sequences
through the execution `run_sequence` twice and emits the committed golden artifact
`benchmarks/execution/artifacts/execution_bench.json`. The harness for the [[Execution Layer Benchmark]]
(BENCH-004), mirroring the BENCH-003 `run_paper_runtime_bench.py` shape.

## Purpose

Prove the ADR-011 §2 execution-determinism invariant (gate d): byte-identical execution records + identical
ending portfolio `state_hash` across replays, idempotent no-double-fill, the fill/guard-block outcome space,
and `guard_block_attribution` — all under an **explicit captured `guard_config`** (gate c.4), with no clock /
network / randomness.

## Architecture Role

A benchmark harness over [[Execution]] (MOD-008); it imports the execution layer + the upstream chain
(`consume → build_features → classify → build_decision → evaluate`) to ground the real sequence in the real
corpus. It produces the committed golden artifact; [[test_execution_bench]] (TEST-021) regenerates it
in-memory and asserts byte-for-byte sync.

## Constraints

- Deterministic + IO-light: fixed committed inputs, sorted-key canonical JSON, no clock/network/randomness.
- The guard config is a captured constant (ADR-011 gate c.4) — never read from `os.environ`.
- Reads only; never mutates `src/execution` logic or any contract.

## Implementation Notes

`build_report()` assembles `real_sequence` (chain → ADMITs → execution replay) + `synthetic_sequence`
(APPROVE + BLOCK captured-config sub-sequences) + top-level `measures` / `all_replays_byte_identical` /
`pinned_portfolio_state_hash` / fingerprints. `_replay_block` runs `run_sequence` twice and compares
`to_dict()` dumps + `state_hash()`. Synthetic ADMITs are constructed via the TEST-019/020 `_admit` idiom.

## Relationships

### Depends On
- [[Execution]]

### Validated By
- [[test_execution_bench]]
