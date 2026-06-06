---
type: test
canonical_id: TEST-001
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[predicates.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
test_path: "tests/risk/test_predicates.py"
test_type: unit
covers:
  - "[[predicates.py]]"
required_for: []
---

# test_predicates

## Definition

Unit test suite for the hard-limit guardrail predicates (`predicates.py`). 7 tests covering pass/fail boundary cases for each predicate.

## Purpose

Verifies each predicate independently: position-size %-vs-absolute cap selection, daily-loss-cap boundary, max-trades, max-positions, and the withdrawals-disabled invariant.

## Constraints

- Pure unit tests — no IO, deterministic.

## Implementation Notes

Uses `make_config()` / `make_request()` builders for baseline-plus-overrides fixtures. All 7 tests passing under pytest 9.0.2 / Python 3.10.6 on 2026-06-06.

## Relationships

### Depends On
- [[predicates.py]]
- [[models.py]]
