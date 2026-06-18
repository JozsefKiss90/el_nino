---
type: file
canonical_id: FILE-034
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/runtime.py"
related_files: []
related_tests:
  - "[[test_chain_determinism]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/orchestration/runtime.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# runtime.py (orchestration)

## Definition

The IO shell + replay driver + CLI for the chain orchestrator (MOD-010): the only IO in the layer. Provides
`run_once` (single-step operational entrypoint), the pure `run_sequence` (in-memory replay / BENCH-006
vehicle), `find_latest_snapshot`, and the `python -m orchestration.runtime` CLI.

## Purpose

Confine all IO to the edge (mirrors the MOD-007 / MOD-008 `runtime.py` shells): `run_once` runs
`consume → load ledger + portfolio → run_chain → persist` and `run_sequence` threads ledger + portfolio in
memory over an ordered snapshot list with no IO.

## Architecture Role

The IO boundary of [[Chain Orchestrator]] (MOD-010). Reuses MOD-007 `load_ledger`/`persist_ledger` +
MOD-008 `load_portfolio`/`persist_portfolio` + MOD-003 `consume`. The CLI is the operator entry; scheduling
is documented (`CHAIN_ORCHESTRATOR_RUNBOOK.md`), not wired.

## Constraints

- **Crash-consistent persistence** — persists the portfolio **first, then the ledger** (each atomic,
  temp-file + `os.replace`): a crash between leaves a redo state (no admitted-but-never-filled snapshot),
  and the portfolio `has_execution` guard prevents a double-fill on re-run.
- Fail-closed — a non-consumable snapshot ⇒ `run_once` returns `None` (Layer-3 outputs nothing); a
  structurally malformed snapshot / corrupt ledger / portfolio raises loudly.
- `run_sequence` is pure (no IO) — the deterministic replay vehicle.

## Implementation Notes

`run_once` / `run_sequence` accept the captured `operational_input` + `guard_config` + the per-layer configs
and forward them to `run_chain`. `run_once` also accepts an optional `operational_feed` + `operational_capture_path`
(the live operational-feed seam, [[operational_feed.py]] FILE-036): when given, it reads the feed at the
snapshot's `clock_ts` and captures the produced `OperationalInput` for replay — the IO-path-only read;
`run_sequence` has **no** feed parameter (the replay quarantine). The CLI defaults the snapshot to the
el_nino latest pointer, supports `--snapshot-dir` (latest `snapshot_*.json` archive), `--ledger`/`--portfolio`
paths (under `runtime/chain/`, gitignored), `--guard-from-env` (load real GATE-001 limits fail-closed), and
`--operational-feed` (use the deterministic market-calendar feed, captured to `--operational-capture`).

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Validated By
- [[test_chain_determinism]]
