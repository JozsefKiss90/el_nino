<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 3 — `assert port.replayable` fence + separate live paths

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (i). Governed by ADR-014.

## What to build

The `replayable` flag already exists on the `ExecutionPort`; what is net-new is the **enforcing precondition**. Add a cheap `assert port.replayable` on the canonical `run_once` and `run_sequence`, so a non-replayable broker port is **structurally barred** from the replay entrypoint and reachable only via the future `operate_live` path.

Plumb a **separate (ledger_path, portfolio_path) pair** for the live path, physically distinct from the canonical replay files, so live broker state can never contaminate the deterministic files. (The `operate_live` entrypoint that consumes these paths arrives in Slice 5; this slice delivers the fence and the path-threading plumbing so they are independently verifiable.)

## Acceptance criteria

- [ ] `run_once` and `run_sequence` raise (via `assert port.replayable`) when handed a non-replayable port; the simulator (replayable) port passes unchanged.
- [ ] A test asserts the fence rejects a non-replayable port from both canonical entrypoints.
- [ ] The plumbing accepts a separate (ledger_path, portfolio_path) pair distinct from the canonical replay files; a test asserts the canonical files are untouched when the separate pair is used.
- [ ] Existing replay / determinism / benchmark suites stay green and byte-identical (the fence is a no-op for the replayable simulator port).

## Blocked by

None - can start immediately.
