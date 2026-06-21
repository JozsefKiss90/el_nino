---
type: test
canonical_id: TEST-029
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_core.py"
related_files:
  - "[[core.py (ops)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operations Control Plane]]"
test_path: "tests/ops/test_core.py"
test_type: unit
covers:
  - "[[core.py (ops)]]"
  - "[[Operations Control Plane]]"
required_for: []
---

# test_ops_core

## Definition

Headless unit tests for the read-model [[core.py (ops)]] (FILE-039) — 31 tests, no Textual, no network.

## Purpose

Lock the read-model invariants: view shapes from fixture artefacts; the pure preview persists nothing
(read-only); fail-closed on malformed/permission-denied artefacts; calibration `DEFER` + the `eligible`
flag; live plugs dormant without creds; **no credential value in any output** (`to_dict` + render).

## Constraints

Mocked only (no real Alpaca, no OS-task spawn, no Textual render); deterministic against the committed
snapshot fixture.

## Implementation Notes

Crafts fixture ledger/portfolio/operational/calibration artefacts in `tmp_path`; uses the committed
`latest_snapshot_pass.json` for the preview; asserts purity (no ledger/portfolio file created) and the
no-secret-leak property with fake creds in the environment.

## Relationships

### Used By
- [[core.py (ops)]]
- [[Operations Control Plane]]

### Justified By
- [[ADR - Operations Control Plane]]
