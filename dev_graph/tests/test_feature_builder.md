---
type: test
canonical_id: TEST-007
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - code
  - layer2
source_paths: []
related_files:
  - "[[feature_builder.py]]"
  - "[[models.py (features)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
test_path: "tests/features/test_feature_builder.py"
test_type: unit
covers:
  - "[[feature_builder.py]]"
  - "[[models.py (features)]]"
  - "[[Feature Vector Schema]]"
required_for: []
---

# test_feature_builder

## Definition

Tests for the Feature Builder, grounded against the real Layer-2 artifact (`tests/snapshot/fixtures/latest_snapshot_pass.json`), consumed through MOD-003's `consume()`. 10 tests.

## Purpose

Prove the v0.1.0 feature layer is correct, deterministic, provenance-faithful, and fail-soft on missing inputs.

## Constraints

- Reuses the canonical real snapshot fixture (single source of truth).
- Levels asserted exact; spreads via `pytest.approx`.

## Implementation Notes

Covers: full 14-feature build, snapshot_id + schema_version anchoring, exact level values, spread arithmetic (`curve_2s10s≈0.50`, `curve_5s10s≈0.37`, `policy_spread==0.0`), provenance propagation (max staleness over EFFR/DFF = 2; revision_risk OR), determinism (`build==build`), name-sorting, revision_risk propagation from a flipped input, unavailable-feature on a dropped series, and input-boundary (rejects a raw path).

## Relationships

### Used By
- [[feature_builder.py]]
- [[models.py (features)]]
- [[Feature Vector Schema]]

### Justified By
- [[ADR - Feature Layer Contract]]
