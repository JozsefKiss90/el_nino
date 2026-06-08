---
type: interface
canonical_id: INT-007
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
  - design
source_paths:
  - "src/regime/regime_classifier/regime_classifier.py"
related_files:
  - "[[regime_classifier.py]]"
related_tests:
  - "[[test_regime_classifier]]"
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
interface_id: "regime-classification-api"
interface_version: "1.0.0"
parent_capability: "[[Market Regime Classification]]"
input_schema: "[[Feature Vector Schema]]"
output_schema: "[[Regime Classification Schema]]"
implemented_by:
  - "[[Market Regime Classifier]]"
stability: experimental
---

# Regime Classification API

## Definition

The boundary contract by which a consumer obtains a deterministic regime classification for one snapshot:

```
classify(fv: FeatureVector, config: RegimeConfig = DEFAULT, as_of: str | None = None) -> RegimeClassification
```

Input schema: SCHEMA-009 Feature Vector. Output schema: SCHEMA-010 Regime Classification. This is the **canonical upstream contract the future Gold Decision Builder consumes** (STEP 11) — the Gold layer reasons over the regime label + provenance, not over raw features.

## Purpose

Make the Feature → Regime seam an explicit, versioned contract so the (deferred) Gold builder depends on a stable abstraction rather than re-deriving regime logic from raw features.

## Architecture Role

Output interface of CAP-019 Market Regime Classification, implemented by MOD-005. Pure call (no IO); the only side-channel is the injected `RegimeConfig`, itself versioned.

## Contract

- **Determinism:** same `snapshot_id` + `taxonomy_version` + `classifier_version` ⇒ identical decision; + `classification_trace_version` ⇒ byte-identical `to_dict()`.
- **Totality:** every consumable FeatureVector yields exactly one regime (NEUTRAL catch-all) or INDETERMINATE.
- **Provenance:** the result carries the deciding features (read verbatim from the vector), the matched rule, and the three versions.
- **`as_of`** is an optional *deterministic, caller-supplied* string (e.g. the snapshot's clock_date) — never a wall-clock read.

## Error Modes

- Missing globally-required feature → returns a `RegimeClassification` with `regime = INDETERMINATE`, `rule_margin = 0.0`, and `failed_required_features` naming the gap (fail-closed; not an exception).
- Invalid configuration (when loaded via `load_config`/`from_mapping`) → raises `RegimeConfigError` at the boundary, before `classify` runs.

## Stability

`experimental` / `interface_version: 1.0.0` — the contract is implemented and tested against the real fixture, but its sole downstream consumer (the Gold DecisionPacket builder) is deferred (ADR-006 §8), so the contract may extend (not break) when that consumer is authored.

## Open Questions

- The Gold builder ([[Gold Decision Builder]], MOD-006) is now authored; `output_schema` (SCHEMA-010) `consumed_by` → it.

## Relationships

### Consumes
- [[Feature Vector Schema]]

### Produces
- [[Regime Classification Schema]]

### Implemented By
- [[Market Regime Classifier]]

### Validated By
- [[test_regime_classifier]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Regime Taxonomy]]
