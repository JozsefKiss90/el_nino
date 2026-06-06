---
type: test
canonical_id: TEST-002
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
  - "[[guardrail_engine.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
test_path: "tests/risk/test_guardrail_engine.py"
test_type: unit
covers:
  - "[[guardrail_engine.py]]"
  - "[[Guardrail Engine]]"
required_for: []
---

# test_guardrail_engine

## Definition

Behavioral test suite for the Guardrail Engine (`guardrail_engine.py`, MOD-001). 8 tests covering approve/block behavior, the decision invariant, and config loading.

## Purpose

Verifies: approve when all predicates pass; block + correct `triggered_predicate` on oversized position; block on malformed request; short-circuit on first failing predicate; determinism; fail-closed config loading; and the SCHEMA-008 decision invariant.

## Constraints

- Deterministic; uses an injected/env config (no live brokerage).

## Implementation Notes

All 8 tests passing under pytest 9.0.2 / Python 3.10.6 on 2026-06-06 (15 total across both suites).

## Relationships

### Depends On
- [[guardrail_engine.py]]
- [[models.py]]
