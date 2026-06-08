---
type: capability
canonical_id: CAP-019
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
related_files: []
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
capability_id: "market-regime-classification"
parent_system: "[[Trading Engine]]"
implemented_by:
  - "[[Market Regime Classifier]]"
interfaces:
  - "[[Regime Classification API]]"
---

# Market Regime Classification

## Definition

The capability to classify a single Layer-2-derived feature vector (SCHEMA-009) into exactly one deterministic macro-financial-conditions regime (SCHEMA-010), using only snapshot-local information. The semantic abstraction layer between Feature Engineering (MOD-004) and the future Gold Decision Builder.

## Purpose

Give the decision layer a single, replay-safe, enumerated regime label + provenance instead of raw feature spaghetti. Satisfies [[ADR - Gold DecisionPacket v0 Planning]] gate (d).

## Architecture Role

An L2 (analysis) capability. It interprets — it never trades, never reads positions/orders, never touches raw snapshots. Realizes the [[Regime Classification Pattern]]; grounded in [[Regime Taxonomy]]; governed by [[ADR - Deterministic Regime Taxonomy]]. (Placed under the Trading Engine bounded context per the slice's STEP 4 directive; it feeds the future Gold Trading Decision branch, which remains permanently separate from the Supervisor treasury branch per ADR-004.)

## Inputs

- A `FeatureVector` (SCHEMA-009) from [[Feature Builder]] (MOD-004).
- A versioned `RegimeConfig` (thresholds, scales, versions) — defaulting to the canonical anchor set.

## Outputs

- A `RegimeClassification` (SCHEMA-010): one `regime` (projection of `matched_rule_id`), `rule_margin` (+ `rule_threshold`/`rule_scale`), provenance, explainability/trace metadata, and three independent versions.

## Constraints

- Deterministic, pure, fail-closed (missing required feature ⇒ INDETERMINATE).
- Snapshot-local only — no history, momentum, learning, hidden state, clock, or randomness.
- Exactly one regime per snapshot; NEUTRAL is the sole catch-all.

## Related Schemas / Tests / Decisions

- Input: [[Feature Vector Schema]] (SCHEMA-009). Output: [[Regime Classification Schema]] (SCHEMA-010).
- Validated by [[test_regime_classifier]] (TEST-008); benchmarked by [[Regime Distribution Benchmark]] (BENCH-001).
- Governed by [[ADR - Deterministic Regime Taxonomy]] (ADR-007); knowledge [[Regime Taxonomy]] (KA-011).

## Relationships

### Contains
- [[Market Regime Classifier]]

### Depends On
- [[Feature Engineering]]

### Provides
- [[Regime Classification API]]

### Consumes
- [[Feature Vector Schema]]

### Produces
- [[Regime Classification Schema]]

### Implemented By
- [[Market Regime Classifier]]

### Validated By
- [[test_regime_classifier]]

### Realizes
- [[Regime Classification Pattern]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Regime Taxonomy]]
