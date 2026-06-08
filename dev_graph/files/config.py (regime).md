---
type: file
canonical_id: FILE-013
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
  - "[[models.py (regime)]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
file_path: "src/regime/regime_classifier/config.py"
language: "python"
module: "[[Market Regime Classifier]]"
owns: []
used_by: []
---

# config.py (regime)

## Definition

`RegimeConfig` — the frozen, versioned dataclass holding every decision threshold, every rule-margin scale, the `near_band` trace parameter, the required-feature gate, and the three versions. Plus `DEFAULT_REGIME_CONFIG`, fail-closed `from_mapping`/`load_config`, `RegimeConfigError`, and `decision_fingerprint()`.

## Purpose

Make thresholds config-driven and versioned (ADR-007 / refinement R2) rather than free-floating code constants, with a fail-closed loader (ADR-003 config policy) and a fingerprint that binds `taxonomy_version` to its threshold set.

## Architecture Role

Read by `taxonomy.py` (predicates/margins) and `regime_classifier.py` (the required gate, versions). The config IO (`load_config`) lives at the boundary so `classify()` stays pure.

## Constraints

- Frozen dataclass; `__post_init__` validates scales > 0, near_band > 0, ordered VIX bands, non-empty required_features, non-empty versions (fail-closed).
- `from_mapping` rejects unknown keys and a missing `taxonomy_version`; `decision_fingerprint()` excludes `near_band` and version strings.

## Implementation Notes

- Domain-anchored defaults: VIX 15/25/35, MOVE 125, real-yield +1.5/+1.0, 5y5y breakeven 2.5/2.0, curve inversion 0.0, broad-USD 120; per-rule margin scales; `near_band = 0.25`.
- `_DECISION_FIELDS` enumerates the fingerprinted fields (thresholds + scales + required_features).

## Relationships

### Depends On
- [[Market Regime Classifier]]
- [[models.py (regime)]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
