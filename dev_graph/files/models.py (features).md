---
type: file
canonical_id: FILE-009
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[feature_builder.py]]"
related_tests:
  - "[[test_feature_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
file_path: "src/features/feature_builder/models.py"
language: "python"
module: "[[Feature Builder]]"
owns:
  - "[[Feature Vector Schema]]"
used_by:
  - "[[feature_builder.py]]"
---

# models.py (features)

## Definition

The Feature Vector contract (SCHEMA-009) as stdlib frozen dataclasses: `Feature` (value + provenance) and `FeatureVector` (snapshot_id, schema_version, name-sorted features, unavailable_features), plus the `FEATURE_SCHEMA_VERSION` constant.

## Purpose

Give the feature layer a typed, immutable, dependency-free output shape with provenance baked into every feature.

## Architecture Role

Realizes SCHEMA-009. Consumed by `feature_builder.py` (FILE-010). Disambiguated from the other three `models.py` nodes (FILE-003 risk, FILE-006 supervisor, FILE-007 snapshot) by basename.

## Constraints

- Stdlib only (ADR-003); `from __future__ import annotations`; full type hints.
- `FEATURE_SCHEMA_VERSION` is part of the determinism key (ADR-005) — bumping it is the only sanctioned way to change feature semantics.

## Implementation Notes

- `Feature`: name, value, inputs (tuple of series_ids), max_staleness_days, revision_risk.
- `FeatureVector`: logically immutable; `features` name-sorted at construction; `.names` and `.value(name)` accessors.

## Relationships

### Depends On
- [[Feature Builder]]

### Validated By
- [[test_feature_builder]]

### Used By
- [[feature_builder.py]]

### Justified By
- [[ADR - Feature Layer Contract]]
