---
type: file
canonical_id: FILE-033
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/engine.py"
related_files: []
related_tests:
  - "[[test_chain_engine]]"
  - "[[test_chain_determinism]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/orchestration/engine.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# engine.py (orchestration)

## Definition

The pure full-chain core (MOD-010): `run_chain(snapshot, prior_ledger, prior_portfolio, …) -> ChainResult`.
Threads `build_features → classify → build_decision → evaluate → [GATE-001 guard] → execute` over one
loaded, consumable snapshot. Pure: no IO / clock / randomness / hidden state.

## Purpose

Compose the already-governed per-layer pure cores into one deterministic call, forwarding the in-hand
`packet.direction` + `fv.value("gold_price")` into `execute` (ADR-011 D1) and running the GATE-001 guard
here before `execute` (ADR-011 gate c). Execution is gated on ADMIT; on HOLD/REJECT the portfolio is
returned unchanged and `execution_record` is `None`.

## Architecture Role

The engine of [[Chain Orchestrator]] (MOD-010), mirroring the pure `evaluate()` / `execute()` cores it
composes. It is the cross-context importer (incl. `src/risk` via `run_guard`); the per-layer cores stay
clean. Realizes the [[Pipeline Pattern]].

## Constraints

- Pure composition — no layer's logic / contract / `*_version` changes; threads existing cores only.
- In-hand path (ADR-011 D1); `guards=None` into `build_decision` (wrap-not-enrich, ADR-009 §2).
- Fail-closed `ChainContractError` if an ADMIT lacks an in-hand `gold_price` (defensive invariant).

## Implementation Notes

`run_chain` takes the captured `operational_input` + `guard_config` + the per-layer configs as keyword
parameters (defaulting to the captured/`DEFAULT_*` values). It builds `SnapshotGuards` from
`snapshot.guards` and passes `as_of = snapshot.clock_ts` to `build_decision`. Returns a `ChainResult`
bundling the five records + the new ledger + portfolio.

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Validated By
- [[test_chain_engine]]
- [[test_chain_determinism]]
