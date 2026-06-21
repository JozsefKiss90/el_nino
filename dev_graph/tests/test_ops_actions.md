---
type: test
canonical_id: TEST-031
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_actions.py"
related_files:
  - "[[actions.py (ops)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operations Control Plane]]"
test_path: "tests/ops/test_actions.py"
test_type: unit
covers:
  - "[[actions.py (ops)]]"
required_for: []
---

# test_ops_actions

## Definition

Headless unit tests for the Tier-2 safe actions [[actions.py (ops)]] (FILE-041) — 14 tests, mocked
subprocess (no real process), real in-process `run_once` for the chain action.

## Purpose

Lock the safe-tier invariants: `run_chain_now` persists + audits (idempotent on re-run); re-run
calibration / re-sync Neo4j audit on success AND failure; actions **never raise** (incl. on an
audit-write failure -> `AUDIT-WRITE-FAILED`); subprocess output secret-redaction; no credential value in
the audit log; the `SAFE_ACTIONS` registry.

## Constraints

No network, no real PowerShell; injected runner; deterministic clock.

## Implementation Notes

Uses the committed pass-snapshot fixture for the real chain run; a `blocker` file forces the audit-write
`OSError` path; a leaky runner verifies the redaction of a `NEO4J_PASSWORD` value.

## Relationships

### Used By
- [[actions.py (ops)]]

### Justified By
- [[ADR - Operations Control Plane]]
