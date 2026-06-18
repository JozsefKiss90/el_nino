---
type: file
canonical_id: FILE-019
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/paper_runtime/models.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_engine]]"
  - "[[test_paper_runtime_determinism]]"
  - "[[test_paper_runtime_ledger]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/gold/paper_runtime/models.py"
language: "python"
module: "[[Paper-Trading Runtime]]"
owns: []
used_by: []
---

# models.py (paper_runtime)

## Definition

The runtime's contract models (SCHEMA-012 + SCHEMA-013): `RuntimeDecisionRecord`, `Verdict`,
`GuardOutcome`, `OperationalInput`, `LedgerEntry`, `RuntimeLedger`, plus `compute_record_id` and
`digest_snapshot_guards`. Frozen, stdlib-only, byte-stable `to_dict()`.

## Purpose

Define the wrapping record + the self-describing append-only ledger, keyed for replay by `record_id`
(binds the prior ledger state) and `source_snapshot_id` (idempotency).

## Implementation Notes

Reuses `_GUARD_NAMES` imported from `gold.decision_builder.models` (single guard ordering — no parallel
list). `RuntimeDecisionRecord.__post_init__` enforces ADMIT ⇔ no triggered guard + the paper-only
invariant. `RuntimeLedger.has_admit` counts only prior ADMITs (PRED-006 once-ever); **v0.2.0**
`RuntimeLedger.last_admit_as_of(exclude_self)` returns the most recent ADMIT's recorded `as_of` (the
computed-cooldown time source, PRED-008 — no schema change, reads existing entry fields). `OperationalInput`
is default-closed and fingerprinted. Fail-closed `from_dict`/`from_mapping` (`RuntimeContractError`).

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_engine]]
- [[test_paper_runtime_determinism]]
- [[test_paper_runtime_ledger]]
