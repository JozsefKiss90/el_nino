---
type: file
canonical_id: FILE-023
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/paper_runtime/runtime.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_ledger]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/gold/paper_runtime/runtime.py"
language: "python"
module: "[[Paper-Trading Runtime]]"
owns: []
used_by: []
---

# runtime.py

## Definition

The IO boundary shell + replay driver: `load_ledger` / `persist_ledger` / `load_operational`,
`run_once` (single-step: load → evaluate → persist atomically), and `run_sequence` (pure, in-memory
ledger-threading replay driver — the determinism / BENCH-003 vehicle).

## Purpose

Confine all runtime IO to one place (mirrors `consume()` / `load_config`), keeping the `evaluate()`
core pure. `run_sequence` is the no-IO vehicle for byte-identical replay.

## Implementation Notes

`load_ledger`: absent file ⇒ `RuntimeLedger.empty()`, malformed ⇒ `RuntimeContractError`.
`load_operational`: absent/malformed ⇒ `OperationalInput.closed()` (default-closed). `persist_ledger`
writes canonical JSON atomically (temp + `os.replace`). Implements [[Paper Runtime API]] (INT-010).

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Implements
- [[Paper Runtime API]]

### Validated By
- [[test_paper_runtime_ledger]]
