---
type: file
canonical_id: FILE-012
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
  - "[[config.py (regime)]]"
  - "[[models.py (regime)]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
file_path: "src/regime/regime_classifier/taxonomy.py"
language: "python"
module: "[[Market Regime Classifier]]"
owns: []
used_by: []
---

# taxonomy.py

## Definition

The declarative, priority-ordered `RULE_TABLE` of `RegimeRule`s (each a pure predicate + a `MarginSpec`) plus the pure `margin_value` / `near_proximity` helpers. The canonical encoding of the regime taxonomy.

## Purpose

Express the regime selection logic as data, not control flow — mirroring MOD-004's `FEATURE_REGISTRY` and the Guardrail Engine's predicate tuple — so the rule set is auditable, testable, and reachable-by-construction.

## Architecture Role

Consumed by `regime_classifier.py`. Reads all thresholds/scales from the passed `RegimeConfig` (no hard-coded numeric constants). Projects `matched_rule_id → regime` per ADR-007.

## Constraints

- Pure: predicates and helpers are functions of `(FeatureVector, RegimeConfig)` only.
- Priority-ordered, first-match-wins; the last rule (NEUTRAL) is the unconditional, sole catch-all.
- Predicates only read features guaranteed present by each rule's `required_features`.

## Implementation Notes

- `RegimeRule(rule_id, regime, priority, required_features, trigger_features, predicate, margin)`; `MarginSpec(feature, threshold, scale, direction)` with threshold/scale read from config via callables.
- 11 signal rules R01..R11 (NEUTRAL last); the INDETERMINATE terminal is handled in the driver, not the table.
- `near_proximity` returns proximity in [0,1] when a non-matching deciding feature is within `near_band` of its threshold.

## Relationships

### Depends On
- [[Market Regime Classifier]]
- [[config.py (regime)]]
- [[models.py (regime)]]

### Consumes
- [[Feature Vector Schema]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
