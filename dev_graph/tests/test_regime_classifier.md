---
type: test
canonical_id: TEST-008
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[regime_classifier.py]]"
  - "[[taxonomy.py]]"
  - "[[config.py (regime)]]"
  - "[[models.py (regime)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
test_path: "tests/regime/test_regime_classifier.py"
test_type: unit
covers:
  - "[[regime_classifier.py]]"
  - "[[taxonomy.py]]"
  - "[[config.py (regime)]]"
  - "[[models.py (regime)]]"
  - "[[Regime Classification Schema]]"
required_for: []
---

# test_regime_classifier

## Definition

Tests for the Market Regime Classifier (MOD-005 / SCHEMA-010 / ADR-007), grounded against the real Layer-2 fixture (consumed via MOD-003) and a deterministic synthetic feature grid. ~60 test cases plus an exhaustive parametrized grid sweep (no `hypothesis` dependency).

## Purpose

Prove the regime layer is correct, deterministic, fail-closed, config-driven, fully explainable, and complete (every rule reachable, exactly one label).

## Constraints

- Reuses the canonical real snapshot fixture (single source of truth) for the golden.
- Property tests are exhaustive `parametrize` sweeps over a fixed grid — deterministic, no randomness.
- Regime/matched_rule_id asserted exact; `rule_margin` via `pytest.approx`.

## Implementation Notes

Covers: unit per-regime; exhaustive grid (exactly-one-label, margin∈[0,1], regime=projection); replay determinism + golden (real PASS → RESTRICTIVE_RATES, rule_margin≈0.46) + golden `to_dict()` string; schema/serialization invariants; config-driven thresholds (fingerprint pinned, fail-closed `from_mapping`/`load_config`, injected-config reclassification); fail-closed per required feature; near/secondary trace metadata (incl. margin-ordering); audit fields (evaluated/skipped partition, failed_required_features); trace-version independence; boundary inclusivity/exclusivity; rule-margin interpretability (threshold/scale reconstruct the deciding value); taxonomy completeness (every rule reachable, priorities contiguous, NEUTRAL last & sole catch-all, AssertionError when NEUTRAL removed); provenance propagation.

## Relationships

### Used By
- [[regime_classifier.py]]
- [[taxonomy.py]]
- [[config.py (regime)]]
- [[models.py (regime)]]
- [[Regime Classification Schema]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
