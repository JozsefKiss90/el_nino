---
type: file
canonical_id: FILE-010
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
related_files:
  - "[[models.py (features)]]"
related_tests:
  - "[[test_feature_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
file_path: "src/features/feature_builder/feature_builder.py"
language: "python"
module: "[[Feature Builder]]"
owns: []
used_by: []
---

# feature_builder.py

## Definition

The deterministic transform: a fixed `FEATURE_REGISTRY` of `FeatureSpec`s plus `build_features(snapshot) -> FeatureVector`.

## Purpose

Turn a validated `Snapshot` (from MOD-003) into a provenance-tagged feature vector, purely and deterministically — the core of the Feature Layer governed by ADR-005.

## Architecture Role

Implements MOD-004; produces SCHEMA-009. Depends on `models.py (features)` (FILE-009) and reads `Snapshot`/`SeriesValue` from the snapshot consumer (no IO of its own).

## Constraints

- Pure / total / deterministic: same `snapshot_id` + `FEATURE_SCHEMA_VERSION` ⇒ identical vector.
- No IO, clock, randomness, or history. Only levels/spreads (ADR-005 allowed classes) in the v0.1.0 set.
- A missing input series marks the feature `unavailable` (never a partial/invented value).

## Implementation Notes

- `_level(name, sid)` / `_spread(name, a, b)` factories bind series ids via default args (no loop-capture bug).
- 14-feature registry; `build_features` iterates the name-sorted registry, computes value + `max_staleness_days` + `revision_risk` from the snapshot's per-series fields.

## Relationships

### Depends On
- [[Feature Builder]]
- [[models.py (features)]]

### Implements
- [[Feature Vector Schema]]

### Consumes
- [[Layer 2 Snapshot Schema]]

### Validated By
- [[test_feature_builder]]

### Justified By
- [[ADR - Feature Layer Contract]]
