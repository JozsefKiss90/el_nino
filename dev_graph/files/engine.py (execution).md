---
type: file
canonical_id: FILE-027
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/engine.py"
related_files: []
related_tests:
  - "[[test_execution_engine]]"
  - "[[test_execution_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/engine.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# engine.py (execution)

## Definition

`execute(admit, direction, instrument_price, prior_portfolio, guard_result, port, fill_model, config) ->
(ExecutionRecord, new PortfolioState)` — the **pure** execution core (the [[Execution API]], INT-011).

## Purpose

Execute an ADMITted paper decision: a fail-closed fill decision (guard block → idempotency → non-LONG
stance → fill), the portfolio transition (mark-to-snapshot, ADR-011 D1), and the record. No IO, clock,
randomness, or `src/risk` import (ADR-011 §2 / ADR-009 §3): the GATE-001 outcome arrives as a forwarded
`GuardResult`; `direction`/`instrument_price` are forwarded from the lineage the orchestrator holds.

## Implementation Notes

A non-ADMIT input raises (`ExecutionContractError`). Only an approved LONG on a fresh `source_snapshot_id`
fills; everything else is a no-fill record (portfolio unchanged) — total, fail-closed, idempotent (mirrors
the runtime `evaluate`). `execution_id` binds the prior portfolio `state_hash`. Dispatches the fill to the
injected `ExecutionPort` (simulated by default).

## Relationships

### Depends On
- [[Execution]]

### Implements
- [[Execution API]]

### Validated By
- [[test_execution_engine]]
- [[test_execution_determinism]]
