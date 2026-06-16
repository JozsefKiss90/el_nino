---
type: file
canonical_id: FILE-024
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/models.py"
related_files: []
related_tests:
  - "[[test_execution_engine]]"
  - "[[test_execution_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/models.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# models.py (execution)

## Definition

The SCHEMA-014 + SCHEMA-015 frozen dataclasses: `ExecutionRecord` (the (paper) fill + guard provenance +
determinism flags), `Fill`, `GuardResult`; `PortfolioState` / `Position` / `ExecutionEntry` (append-only,
self-describing); `compute_execution_id`.

## Purpose

Realize the execution contracts ([[Execution Record Schema]], [[Portfolio State Schema]]) as deterministic,
byte-stable dataclasses (sorted-key `to_dict`, SHA-256 `state_hash`, fail-closed `from_dict`). Mark-to-
snapshot P&L at the re-derived price (ADR-011 D1). `paper_only` invariant on the record.

## Implementation Notes

`compute_execution_id` binds the prior portfolio `state_hash` (per-execution identity). `GuardResult` is a
plain DTO (no `src/risk` import — the orchestrator maps `TradeValidationDecision` into it). Reuses
`Direction` from the gold packet module. Produces [[Execution Record Schema]] + [[Portfolio State Schema]].

## Relationships

### Depends On
- [[Execution]]

### Produces
- [[Execution Record Schema]]
- [[Portfolio State Schema]]

### Validated By
- [[test_execution_engine]]
- [[test_execution_determinism]]
