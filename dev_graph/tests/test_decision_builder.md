---
type: test
canonical_id: TEST-010
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_decision_builder.py"
related_files:
  - "[[builder.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Gold Decision Confidence Semantics]]"
test_path: "tests/gold/test_decision_builder.py"
test_type: unit
covers:
  - "[[Gold Decision Builder]]"
required_for: []
---

# test_decision_builder

## Definition

Unit + determinism + fail-closed tests for the Gold Decision Builder (MOD-006). 20 tests covering: the real-snapshot golden (RESTRICTIVE_RATES → AVOID / confidence 0.39744 / uncertainty 0.136 / `packet_id gold-v0:0ebde87216151527`), byte-identical replay, the recorded `confidence_inputs`, the INDETERMINATE fail-closed floor (→ WATCH / 0.0 / 1.0), the NEUTRAL confident-quiet floor, direction-table totality, the pinned `decision_policy_fingerprint` + drift/version-exclusion behavior, `packet_id` sensitivity to both `decision_policy_version` and the config fingerprint, snapshot-id-mismatch fail-closed, guard-ref default-null + passthrough, and config fail-closed paths.

## Purpose

Pin the ADR-008 confidence model + the regime→direction policy + the step-0 full-key `packet_id` against regression, and prove determinism / fail-closed behavior.

## Relationships

### Used By
- [[Gold Decision Builder]]

### Justified By
- [[ADR - Gold Decision Confidence Semantics]]
