---
type: test
canonical_id: TEST-005
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - code
  - layer2
source_paths: []
related_files:
  - "[[models.py (snapshot)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
test_path: "tests/snapshot/test_models.py"
test_type: unit
covers:
  - "[[models.py (snapshot)]]"
  - "[[Layer 2 Snapshot Schema]]"
required_for: []
---

# test_models (snapshot)

## Definition

Unit tests for the SCHEMA-001 models, grounded against a verbatim copy of the real Ripley artifact (`fixtures/latest_snapshot_pass.json`). 8 tests.

## Purpose

Prove the model captures the contract — most importantly that `recompute_id()` reproduces the published `snapshot_id`, which fails if the identity-determining fields are modelled wrongly.

## Constraints

- Fixture is the real artifact, copied immutably into `tests/snapshot/fixtures/`.
- The expected id `952cc83a…afaef` is asserted explicitly as the contract anchor.

## Implementation Notes

Covers: top-level parse (21 series), id recomputation + `id_matches`, full-fidelity `SeriesValue` (gold + revision-risk CPI), guards, quality summary, and three contract-violation raises (missing `snapshot_id`, missing `values_by_group`, non-object payload).

## Relationships

### Validated By

### Used By
- [[models.py (snapshot)]]
- [[Layer 2 Snapshot Schema]]

### Justified By
- [[ADR - Implementation Substrate]]
