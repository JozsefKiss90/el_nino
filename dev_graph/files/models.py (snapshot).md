---
type: file
canonical_id: FILE-007
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
  - "snapshot_sources/latest_snapshot.json"
related_files: []
related_tests:
  - "[[test_models (snapshot)]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/snapshot/snapshot_consumer/models.py"
language: "python"
module: "[[Snapshot Consumer]]"
owns:
  - "[[Layer 2 Snapshot Schema]]"
used_by:
  - "[[consumer.py]]"
---

# models.py (snapshot)

## Definition

The Layer-2 Snapshot contract (SCHEMA-001) realised as stdlib frozen dataclasses: `Snapshot`, `SeriesValue`, `Guards`, `QualitySummary`, plus `SnapshotContractError`.

## Purpose

Give Layer 3 a typed, immutable, dependency-free view of the snapshot, with `from_dict` parsers and the deterministic identity recomputation that anchors the contract.

## Architecture Role

Realizes SCHEMA-001. Consumed by `consumer.py` (FILE-008). Disambiguated from `models.py` (FILE-003, risk) and `models.py (supervisor)` (FILE-006) by basename.

## Constraints

- Stdlib only (ADR-003); `from __future__ import annotations`; full type hints; `mypy --strict` target.
- Parses the full-fidelity `values_by_group` representation, not the lossy `values`/`tierN_series` maps.
- `recompute_id()` MUST mirror the Layer-2 publisher's `compute_snapshot_id` byte-for-byte.

## Implementation Notes

- `SeriesValue.from_grouped_entry` requires `series_id/tier/group/obs_ts/value/staleness_days/source`; tolerates missing `as_of_ts/revision_seq/revision_risk`.
- `Guards.from_dict` requires `snapshot_ok`; reads the rest tolerantly so an evolving guard block does not break ingestion.
- Verified: `recompute_id()` reproduces the real artifact's `snapshot_id` (`952cc83a…afaef`).

## Relationships

### Depends On
- [[Snapshot Consumer]]

### Validated By
- [[test_models (snapshot)]]

### Used By
- [[consumer.py]]

### Justified By
- [[ADR - Implementation Substrate]]
