---
type: file
canonical_id: FILE-008
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - code
  - layer2
source_paths:
  - "snapshot_sources/snapshot_publisher.py"
related_files:
  - "[[models.py (snapshot)]]"
related_tests:
  - "[[test_consumer]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/snapshot/snapshot_consumer/consumer.py"
language: "python"
module: "[[Snapshot Consumer]]"
owns:
  - "[[Snapshot API]]"
used_by: []
---

# consumer.py

## Definition

The fail-closed Layer-3 gate over the Snapshot API (INT-001): `load_snapshot()`, `is_consumable()`, and the single entry point `consume()`.

## Purpose

Implement the publisher's Layer-3 contract in one place: read the latest snapshot, and return it only when it is safe to act on — otherwise output nothing.

## Architecture Role

Implements the consumer side of INT-001. Depends on `models.py (snapshot)` (FILE-007). The by-`snapshot_id` query mode is deferred.

## Constraints

- `consume()`/`load_snapshot()` return `None` for absent file and for failed-gate/forced/dry-run snapshots.
- A malformed payload raises `SnapshotContractError` — never masked as `None`.
- No observation access; snapshots only.

## Implementation Notes

- `is_consumable = verdict == "PASS" ∧ guards.snapshot_ok ∧ ¬forced ∧ ¬dry_run`. The `forced` exclusion is deliberate fail-closed: a forced snapshot bypassed the quality gate.
- Accepts `str` or `Path`.

## Relationships

### Depends On
- [[Snapshot Consumer]]
- [[models.py (snapshot)]]

### Validated By
- [[test_consumer]]

### Justified By
- [[ADR - Implementation Substrate]]
