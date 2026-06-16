---
type: file
canonical_id: FILE-028
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/runtime.py"
related_files: []
related_tests:
  - "[[test_execution_guards]]"
  - "[[test_execution_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/runtime.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# runtime.py (execution)

## Definition

The IO boundary shell + **guard-wiring composition root**: `load_portfolio`/`persist_portfolio`,
`build_guard_request`/`run_guard` (the GATE-001 wiring), `run_once` (load → guard → execute → persist), and
`run_sequence` (the pure replay / BENCH-004 driver — no IO).

## Purpose

Confine all execution IO to one place (mirrors the runtime `runtime.py`) and wire [[Trade Validation Gate]]
(GATE-001) into the trade pipeline (ADR-011 gate c): build a `TradeValidationRequest`, run
`GuardrailEngine.validate()` **before** `execute()`, forward the outcome as a `GuardResult`. The **only**
file that imports `src/risk` (bounded-context hygiene, ADR-009 §3) — the pure `execute()` core never does.

## Implementation Notes

`load_portfolio`: absent ⇒ `PortfolioState.empty()`, malformed ⇒ `ExecutionContractError`. `persist_portfolio`
writes canonical JSON atomically (temp + `os.replace`). The guard's `GuardrailConfig` is an explicit
**captured** value (ADR-011 gate c.4 — replay determinism), never read from the environment on the replay
path. Implements [[Execution API]] (INT-011).

## Relationships

### Depends On
- [[Execution]]

### Implements
- [[Execution API]]

### Validated By
- [[test_execution_guards]]
- [[test_execution_determinism]]
