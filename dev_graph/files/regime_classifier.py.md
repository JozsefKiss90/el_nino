---
type: file
canonical_id: FILE-011
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
  - "[[taxonomy.py]]"
  - "[[config.py (regime)]]"
  - "[[models.py (regime)]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
file_path: "src/regime/regime_classifier/regime_classifier.py"
language: "python"
module: "[[Market Regime Classifier]]"
owns: []
used_by: []
---

# regime_classifier.py

## Definition

The driver: `classify(fv, config=DEFAULT_REGIME_CONFIG, as_of=None) -> RegimeClassification`. A pure, total rule-selection loop over the priority-ordered `RULE_TABLE`.

## Purpose

Turn a validated FeatureVector into exactly one deterministic regime, with full provenance and explainability — the core of the Regime Taxonomy layer governed by ADR-007.

## Architecture Role

Implements MOD-005 and INT-007; produces SCHEMA-010. Imports `RULE_TABLE` + helpers from `taxonomy.py`, the config from `config.py`, and the output models from `models.py` (no IO of its own).

## Constraints

- Pure / total / deterministic: same `snapshot_id` + `taxonomy_version` + `classifier_version` ⇒ identical decision.
- No IO, clock, randomness, or history. Fail-closed: missing required feature ⇒ INDETERMINATE.

## Implementation Notes

- Global required-feature gate first (records `failed_required_features`).
- A single full pass records eligibility, predicate matches, and near-activations; the highest-priority match wins; NEUTRAL guarantees a verdict (defensive `AssertionError` otherwise).
- `secondary_matching_rules` ordered by activation margin desc (tiebreak priority asc); `near_matching_rules` by proximity desc.

## Relationships

### Depends On
- [[Market Regime Classifier]]
- [[taxonomy.py]]
- [[config.py (regime)]]
- [[models.py (regime)]]

### Implements
- [[Regime Classification API]]

### Consumes
- [[Feature Vector Schema]]

### Produces
- [[Regime Classification Schema]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
