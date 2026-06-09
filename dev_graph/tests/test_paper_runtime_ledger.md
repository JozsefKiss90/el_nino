---
type: test
canonical_id: TEST-016
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_paper_runtime_ledger.py"
related_files:
  - "[[runtime.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/gold/test_paper_runtime_ledger.py"
test_type: unit
covers:
  - "[[Paper-Trading Runtime]]"
  - "[[Runtime Ledger Schema]]"
required_for: []
---

# test_paper_runtime_ledger

## Definition

Ledger idempotency + sequence-replay tests: `run_sequence` twice ⇒ identical records + identical ending
`state_hash`; a re-presented snapshot ⇒ duplicate / non-ADMIT; `has_admit` counts only ADMITs;
append-only immutability + length-derived `seq`; a halted op mid-sequence ⇒ REJECT with the ledger
still advancing; `state_hash` stable through serialization; `seq` continuity across persist/reload;
default-closed loaders (absent ledger ⇒ empty, absent operational ⇒ closed).

## Purpose

Prove the self-describing ledger is sufficient replay state and the runtime is idempotent.

## Relationships

### Used By
- [[Paper-Trading Runtime]]
- [[Runtime Ledger Schema]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
