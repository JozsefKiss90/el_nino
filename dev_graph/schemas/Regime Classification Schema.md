---
type: artifact_schema
canonical_id: SCHEMA-010
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - code
source_paths:
  - "src/regime/regime_classifier/models.py"
related_files:
  - "[[models.py (regime)]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
schema_id: "regime-classification"
schema_version: "1.0.0"
schema_path: "src/regime/regime_classifier/models.py"
validated_by:
  - "[[test_regime_classifier]]"
consumed_by:
  - "[[Gold Decision Builder]]"
produced_by:
  - "[[Market Regime Classifier]]"
---

# Regime Classification Schema

## Definition

The deterministic output contract of the Market Regime Classifier (MOD-005): a frozen `RegimeClassification` derived purely from one Feature Vector (SCHEMA-009). Rule-selection-first — `matched_rule_id` is the primary key and `regime` is its projection. This is the canonical upstream contract for the future Gold DecisionPacket builder (it is **not** the Gold packet, and **not** part of the Supervisor treasury branch).

## Purpose

Give the downstream decision layer one versioned, replay-safe regime shape, anchored to the producing `snapshot_id`, with self-describing margins and full explainability — so the same snapshot + same versions always reproduce the same classification.

## Architecture Role

Output schema of MOD-005; input is SCHEMA-009 (a FeatureVector). Governed by [[ADR - Deterministic Regime Taxonomy]] (ADR-007). Note the `schema_version` here (`1.0.0`) is the *contract-shape* version; the artifact also carries three independent runtime versions (below).

## Schema Definition

**RegimeClassification** — field groups:

*Decision* (keyed by `taxonomy_version` + `classifier_version`)

| Field | Type | Notes |
|-------|------|-------|
| matched_rule_id | string | PRIMARY — e.g. `R04_restrictive_rates`, `R00_indeterminate` |
| regime | enum(Regime) | projection = `RULE_TABLE[matched].regime` |
| rule_priority | int | matched rule's priority (1..11; 0 for INDETERMINATE) |
| rule_margin | number [0,1] | rule-local activation margin; NOT a global score |
| rule_threshold | number \| null | deciding-feature threshold the margin is relative to (null for NEUTRAL/INDETERMINATE) |
| rule_scale | number \| null | deciding-feature scale (null for NEUTRAL/INDETERMINATE) |
| trigger_features | array<string> | deciding/gating features (name-sorted) |
| indeterminate_reason | string \| null | required only when regime = INDETERMINATE |

*Provenance / identity*

| Field | Type | Notes |
|-------|------|-------|
| snapshot_id | string | echoed from the FeatureVector (replay anchor) |
| feature_schema_version | string | echoed SCHEMA-009 version |
| provenance | array<FeatureProvenance> | one per trigger feature, verbatim from the vector |
| as_of | string \| null | deterministic caller-supplied; never wall-clock |

*Explainability / trace* (keyed by `classification_trace_version`)

| Field | Type | Notes |
|-------|------|-------|
| evaluated_rule_ids | array<string> | eligible rules whose predicate ran (priority order) |
| skipped_rule_ids | array<string> | rules skipped for a missing per-rule feature |
| failed_required_features | array<string> | absent features referenced by the gate or skipped rules |
| secondary_matching_rules | array<string> | other matched rules, ordered by activation margin desc |
| near_matching_rules | array<string> | non-matching rules within `near_band`, proximity desc |

*Versions*: `taxonomy_version`, `classifier_version`, `classification_trace_version` (independent).

**FeatureProvenance**: `name`, `value`, `inputs` (SCHEMA-001 series_ids), `max_staleness_days`, `revision_risk`.

## Validation Rules

- `rule_margin` ∈ [0,1]; `regime` == the matched rule's regime.
- INDETERMINATE ⇒ `rule_margin == 0.0` and `indeterminate_reason` set; NEUTRAL/INDETERMINATE ⇒ `rule_threshold`/`rule_scale` are null and `trigger_features` empty; otherwise both set.
- `matched_rule_id` ∉ `secondary_matching_rules`.
- Determinism: `(snapshot_id, taxonomy_version, classifier_version)` determines the decision; `+ classification_trace_version` determines the full `to_dict()`.
- `to_dict()` emits alphabetically-sorted keys + 6-dp-rounded margin → byte-stable JSON.

## Open Questions

- `consumed_by` → [[Gold Decision Builder]] (MOD-006), now authored. (ADR-006 §7 reserved SCHEMA-010 as a *candidate* for the Gold packet; it is used here for the regime contract, so the Gold packet took the next free id, SCHEMA-011.)

## Relationships

### Produced By
- [[Market Regime Classifier]]

### Used By
- [[models.py (regime)]]
- [[Regime Classification API]]
- [[Gold Decision Builder]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Regime Taxonomy]]
