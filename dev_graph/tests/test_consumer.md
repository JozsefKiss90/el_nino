---
type: test
canonical_id: TEST-006
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
  - "[[consumer.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
test_path: "tests/snapshot/test_consumer.py"
test_type: unit
covers:
  - "[[consumer.py]]"
  - "[[Snapshot API]]"
required_for: []
---

# test_consumer

## Definition

Tests for the fail-closed Snapshot Consumer gate (INT-001 consumer side). 8 tests, using PASS / FAIL / FORCED fixtures derived from the real artifact plus inline dry-run/malformed cases.

## Purpose

Prove the Layer-3 consumption contract: a clean PASS snapshot is returned; failed-gate / forced / dry-run / absent all output nothing; a malformed payload raises rather than silently returning `None`.

## Constraints

- FAIL/FORCED fixtures are derived from the real artifact so they stay structurally faithful.
- Asserts both `is_consumable()` and the `consume()` entry point.

## Implementation Notes

Covers: PASS returned (+ `id_matches`), failed gate → None, forced → None (fail-closed), dry-run → None, absent file → None, malformed (missing `guards`) → `SnapshotContractError`, `str` path acceptance.

## Relationships

### Validated By

### Used By
- [[consumer.py]]
- [[Snapshot API]]

### Justified By
- [[ADR - Implementation Substrate]]
