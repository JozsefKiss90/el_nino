---
type: artifact_schema
canonical_id: SCHEMA-009
status: active
implementation_status: implemented
canonical: true
created: 2026-06-07
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - layer2
  - code
source_paths:
  - "snapshot_sources/latest_snapshot.json"
related_files:
  - "[[models.py (features)]]"
related_tests:
  - "[[test_feature_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
  - "[[ADR - Decision Layer Re-grounding]]"
schema_id: "feature-vector"
schema_version: "0.1.0"
schema_path: "src/features/feature_builder/models.py"
validated_by:
  - "[[test_feature_builder]]"
consumed_by:
  - "[[Market Regime Classifier]]"
produced_by:
  - "[[Feature Builder]]"
---

# Feature Vector Schema

## Definition

The deterministic output contract of the Feature Builder (MOD-004): a frozen, snapshot-local vector of features derived purely from a single Layer-2 Snapshot (SCHEMA-001), each carrying its provenance. This is a **new** artifact_schema (SCHEMA-009) — it is the "deterministic SCHEMA-001-derived features" that [[ADR - Decision Layer Re-grounding]] requires before a Gold DecisionPacket v0 may be authored. It is **not** part of the Supervisor treasury branch.

## Purpose

Give every downstream stage (regime/decision, later) one versioned, replay-safe feature shape, anchored to the producing `snapshot_id` so the same snapshot + same `schema_version` always reproduce the same vector.

## Architecture Role

Output schema of MOD-004 Feature Builder; input is SCHEMA-001 (via a consumed `Snapshot` object from MOD-003). Governed by [[ADR - Feature Layer Contract]] (ADR-005).

## Schema Definition

**FeatureVector** (top level):

| Field | Type | Notes |
|-------|------|-------|
| snapshot_id | string | identity of the source Layer-2 snapshot (replay anchor) |
| schema_version | string | feature-schema version (e.g. `0.1.0`); part of the determinism key |
| features | map<string, Feature> | feature_name → Feature; deterministic (name-sorted) |
| unavailable_features | array<string> | feature names skipped because an input series was absent |

**Feature** (per entry):

| Field | Type | Notes |
|-------|------|-------|
| name | string | feature id (e.g. `curve_2s10s`) |
| value | number | the computed value |
| inputs | array<string> | SCHEMA-001 series_ids the value was derived from |
| max_staleness_days | int | max `staleness_days` over `inputs` (provenance) |
| revision_risk | bool | OR of `revision_risk` over `inputs` (provenance) |

## Validation Rules

- Every `Feature.inputs` entry MUST be a real SCHEMA-001 series_id.
- `max_staleness_days` = `max(staleness_days[i] for i in inputs)`; `revision_risk` = `any(revision_risk[i] for i in inputs)` — read from the snapshot, never inferred.
- Determinism: `(snapshot_id, schema_version)` uniquely determines the entire vector.
- A feature whose inputs are not all present is omitted from `features` and listed in `unavailable_features` (no partial/invented values).
- No field may depend on history, cross-snapshot state, or external context (enforced by ADR-005's forbidden-classes list).

## Open Questions

- `consumed_by` now names [[Market Regime Classifier]] (MOD-005), which consumes this vector to produce SCHEMA-010. The further-downstream Gold DecisionPacket v0 consumer remains deferred (ADR-006 §8); link it when authored.
- Ratio features are admissible by ADR-005 but none are in the v0.1.0 set (no divisor with an obvious, unit-safe denominator in the initial set); add when a consumer needs one.

## Relationships

### Produced By
- [[Feature Builder]]

### Used By
- [[models.py (features)]]
- [[Market Regime Classifier]]

### Validated By
- [[test_feature_builder]]

### Justified By
- [[ADR - Feature Layer Contract]]

### Originates From
- [[Layer 2 Design Principles]]
