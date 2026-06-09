---
type: file
canonical_id: FILE-022
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/paper_runtime/engine.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/gold/paper_runtime/engine.py"
language: "python"
module: "[[Paper-Trading Runtime]]"
owns: []
used_by: []
---

# engine.py

## Definition

`evaluate(packet, prior_ledger, operational_input, config) -> (record, new_ledger)` — the pure runtime
admission core (the Paper Runtime API, INT-010) and the Runtime Admission Gate (GATE-003) verdict logic.

## Purpose

Compute the full six-guard block (canonical `_GUARD_NAMES` order), determine a fail-closed verdict via
a short-circuit conjunction over the required guards, append exactly one self-describing ledger entry,
and build the record. No IO, clock, randomness, or hidden state (ADR-009 §3/§4).

## Implementation Notes

WATCH/INDETERMINATE packet ⇒ HOLD (`actionable_stance`); the first failing required guard (in
`_GUARD_NAMES` order) ⇒ REJECT naming it; else ADMIT. `record_id` binds the prior ledger `state_hash`
(per-evaluation identity). Implements [[Paper Runtime API]] (INT-010); enforces [[Runtime Admission
Gate]] (GATE-003).

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Implements
- [[Paper Runtime API]]

### Validated By
- [[test_paper_runtime_engine]]
