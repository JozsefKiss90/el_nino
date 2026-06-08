---
type: module
canonical_id: MOD-004
status: active
implementation_status: tested
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
  - "[[feature_builder.py]]"
related_tests:
  - "[[test_feature_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Implementation Substrate]]"
module_name: "feature_builder"
module_path: "src/features/feature_builder"
responsibility: "Transform a validated Layer-2 Snapshot into a deterministic, provenance-tagged feature vector"
depends_on:
  - "[[Snapshot Consumer]]"
provides:
  - "[[Feature Vector Schema]]"
---

# Feature Builder

## Definition

The deterministic, snapshot-local transform that turns a validated `Snapshot` (from MOD-003) into a frozen feature vector (SCHEMA-009). The second stage of the Layer-3 data path: `SCHEMA-001 → MOD-003 → [Feature Builder] → future Gold DecisionPacket v0`.

## Purpose

Produce the "deterministic SCHEMA-001-derived features" that [[ADR - Decision Layer Re-grounding]] requires before a gold decision contract may be authored — replay-safe, provenance-tagged, and free of any historical state.

## Architecture Role

Realizes the Feature Layer governed by [[ADR - Feature Layer Contract]] (ADR-005). Consumes SCHEMA-001 (via a consumed `Snapshot`); produces SCHEMA-009. Pure functions, zero runtime dependencies (ADR-003).

## Inputs (or Dependencies)

- A validated (PASS) `Snapshot` object from [[Snapshot Consumer]] — never raw JSON, a file path, raw observations, or an external API.

## Outputs (or Provides)

- A [[Feature Vector Schema]] instance: `snapshot_id`, `schema_version`, name-sorted `features` (each with value + provenance), and `unavailable_features`.

## Constraints

- **Pure / stateless / deterministic**: same `snapshot_id` + `schema_version` ⇒ identical output.
- **Snapshot-local only**: every feature is a level/spread/ratio/arithmetic transform of one snapshot's series — no history, momentum, z-scores, rolling windows, smoothing, regimes, or embeddings (ADR-005 forbidden classes).
- **Provenance**: each feature carries `inputs`, `max_staleness_days`, `revision_risk` read from the snapshot.
- **No IO**: no file reads, no network, no clock, no randomness.

## Implementation Notes

- `models.py` — SCHEMA-009 dataclasses (`Feature`, `FeatureVector`) + `FEATURE_SCHEMA_VERSION`.
- `feature_builder.py` — a fixed `FEATURE_REGISTRY` of `FeatureSpec`s (name, input series_ids, pure fn) + `build_features(snapshot) -> FeatureVector`. Iterates the name-sorted registry; a feature with any missing input series is added to `unavailable_features` and skipped; otherwise value + provenance are emitted.
- v0.1.0 feature set (14): real_yield_10y, real_yield_5y, breakeven_10y, breakeven_5y, breakeven_5y5y_fwd, curve_2s10s, curve_5s10s, policy_spread, usd_level, vol_level, rates_vol, equity_level, gold_price, gold_flow.

## Open Questions

- Capability attachment: CAP-002 Feature Engineering is currently framed Layer-2-producer-side; this module derives features Layer-3-side from the raw snapshot — same producer/consumer seam as CAP-003/MOD-003. Resolve in a future re-grounding step; not forced here.
- The regime consumer ([[Market Regime Classifier]], MOD-005) now consumes this vector; the Gold DecisionPacket v0 consumer remains deferred (ADR-006 §8).

## Relationships

### Implements
- [[Feature Vector Schema]]

### Consumes
- [[Layer 2 Snapshot Schema]]
- [[Snapshot Consumer]]

### Produces
- [[Feature Vector Schema]]

### Contains
- [[models.py (features)]]
- [[feature_builder.py]]

### Validated By
- [[test_feature_builder]]

### Depends On
- [[Snapshot Consumer]]

### Used By
- [[Market Regime Classifier]]

### Justified By
- [[ADR - Feature Layer Contract]]
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Implementation Substrate]]

### Originates From
- [[Layer 2 Design Principles]]
