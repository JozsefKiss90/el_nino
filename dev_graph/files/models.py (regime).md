---
type: file
canonical_id: FILE-014
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[regime_classifier.py]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
file_path: "src/regime/regime_classifier/models.py"
language: "python"
module: "[[Market Regime Classifier]]"
owns: []
used_by: []
---

# models.py (regime)

## Definition

The SCHEMA-010 output models: the `Regime` enum (12 values), `RegimeClassification` (frozen, with cross-field invariants + deterministic `to_dict()`), `FeatureProvenance`, and the version constants (`TAXONOMY_VERSION`, `CLASSIFIER_VERSION`, `CLASSIFICATION_TRACE_VERSION`).

## Purpose

Define the canonical, replay-safe regime contract (SCHEMA-010) as stdlib frozen dataclasses (ADR-003), with invariants that make INDETERMINATE/NEUTRAL terminals and rule-margin semantics enforceable at construction.

## Architecture Role

Realizes SCHEMA-010. Imported by `config.py` (version constants), `taxonomy.py` (`Regime`), and `regime_classifier.py` (all output types).

## Constraints

- Frozen dataclasses; `__post_init__` enforces margin ∈ [0,1], regime↔matched-rule consistency, terminal threshold/scale = None, INDETERMINATE invariants, and `matched_rule_id ∉ secondary_matching_rules`.
- `to_dict()` emits alphabetically-sorted keys + 6-dp-rounded margin → byte-stable JSON.

## Implementation Notes

- Field groups: decision / provenance-identity / explainability-trace / versions (see SCHEMA-010).
- `as_of` is an optional deterministic caller-supplied string — never a wall-clock read.

## Relationships

### Depends On
- [[Market Regime Classifier]]

### Implements
- [[Regime Classification Schema]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
