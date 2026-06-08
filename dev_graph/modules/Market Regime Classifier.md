---
type: module
canonical_id: MOD-005
status: active
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - code
source_paths:
  - "src/regime/regime_classifier/regime_classifier.py"
related_files:
  - "[[regime_classifier.py]]"
  - "[[taxonomy.py]]"
  - "[[config.py (regime)]]"
  - "[[models.py (regime)]]"
related_tests:
  - "[[test_regime_classifier]]"
  - "[[test_regime_bench]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
module_name: "regime_classifier"
module_path: "src/regime/regime_classifier"
responsibility: "Classify a validated Feature Vector into exactly one deterministic market regime"
depends_on:
  - "[[Feature Builder]]"
provides:
  - "[[Regime Classification API]]"
---

# Market Regime Classifier

## Definition

The deterministic, snapshot-local rule-selection engine that turns a Feature Vector (SCHEMA-009) into a frozen `RegimeClassification` (SCHEMA-010). The third stage of the analysis path: `SCHEMA-001 → MOD-003 → MOD-004 → [Regime Classifier] → future Gold DecisionPacket v0`.

## Purpose

Produce the enumerated, grounded `regime_class` that [[ADR - Gold DecisionPacket v0 Planning]] gate (d) requires — replay-safe, provenance-tagged, fail-closed, and free of history or learning. Realizes [[Market Regime Classification]] (CAP-019).

## Architecture Role

Realizes the Regime Taxonomy layer governed by [[ADR - Deterministic Regime Taxonomy]] (ADR-007); realizes the [[Regime Classification Pattern]]; grounded in [[Regime Taxonomy]]. Consumes SCHEMA-009; produces SCHEMA-010 via [[Regime Classification API]] (INT-007). Pure functions, zero runtime dependencies (ADR-003).

## Inputs (or Dependencies)

- A `FeatureVector` (SCHEMA-009) from [[Feature Builder]] (MOD-004) — never a raw snapshot, path, or external API.
- A versioned `RegimeConfig` (defaults to the canonical anchor set).

## Outputs (or Provides)

- A `RegimeClassification` (SCHEMA-010): `matched_rule_id` (primary) + projected `regime`, `rule_margin` (+ `rule_threshold`/`rule_scale`), provenance, explainability/trace metadata, and three independent versions.

## Constraints

- **Pure / stateless / deterministic**: same `snapshot_id` + `taxonomy_version` + `classifier_version` ⇒ identical decision.
- **Snapshot-local only**: no history, momentum, learning, hidden state, clock, randomness, or IO.
- **Exactly one regime**: priority-ordered first-match selection; NEUTRAL is the sole catch-all; INDETERMINATE is the fail-closed terminal.
- **Config-driven thresholds**: all numbers live in the versioned `RegimeConfig`; `taxonomy_version`↔fingerprint coherence prevents un-versioned drift.

## Implementation Notes

- `models.py` — SCHEMA-010 dataclasses (`Regime` enum, `RegimeClassification`, `FeatureProvenance`) + the version constants + `to_dict()`.
- `config.py` — `RegimeConfig` (every threshold + margin scale + `near_band` + `required_features` + three versions), `DEFAULT_REGIME_CONFIG`, fail-closed `from_mapping`/`load_config` (`RegimeConfigError`), and `decision_fingerprint()`.
- `taxonomy.py` — declarative priority-ordered `RULE_TABLE` of `RegimeRule`s (predicate + `MarginSpec`) + pure `margin_value`/`near_proximity` helpers, mirroring MOD-004's `FEATURE_REGISTRY` and the guardrail predicate-tuple convention.
- `regime_classifier.py` — `classify(fv, config, as_of)`: global fail-closed gate → INDETERMINATE; a single full pass recording eligibility / matches / near-activation; highest-priority match wins; secondary matches ordered by margin desc; near matches by proximity desc.
- 12 regimes: LIQUIDITY_STRESS, RISK_OFF, VOLATILE, RESTRICTIVE_RATES, REFLATION, DISINFLATION, CURVE_INVERSION, STRONG_USD, RISK_ON, LOW_VOL, NEUTRAL, + INDETERMINATE. Real PASS fixture → RESTRICTIVE_RATES (rule_margin 0.46).

## Open Questions

- The downstream consumer (Gold DecisionPacket v0 builder) is deferred (ADR-006 §8); SCHEMA-010 is exposed via INT-007 as its canonical input.
- Domain-anchored thresholds await a real historical corpus for governed recalibration (a future `taxonomy_version` bump).

## Relationships

### Implements
- [[Regime Classification API]]

### Consumes
- [[Feature Vector Schema]]

### Produces
- [[Regime Classification Schema]]

### Contains
- [[regime_classifier.py]]
- [[taxonomy.py]]
- [[config.py (regime)]]
- [[models.py (regime)]]

### Validated By
- [[test_regime_classifier]]
- [[test_regime_bench]]

### Depends On
- [[Feature Builder]]

### Realizes
- [[Regime Classification Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Regime Taxonomy]]
