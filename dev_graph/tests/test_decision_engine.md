---
type: test
canonical_id: TEST-004
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
  - "[[decision_engine.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
test_path: "tests/supervisor/test_decision_engine.py"
test_type: unit
covers:
  - "[[decision_engine.py]]"
  - "[[Decision Engine]]"
required_for: []
---

# test_decision_engine

## Definition

Behavioral test suite for the Decision Engine (`decision_engine.py`, MOD-002). 7 tests covering decision behavior and the packet invariants.

## Purpose

Verifies: promotable early-exit (NOOP); selection of the highest-scoring allowed option + treasury burn; budget filter; exclusion filter (institutional memory); determinism; and the SCHEMA-004 invariants (selected must be allowed; blocked options carry a reason).

## Constraints

- Deterministic; uses constructed scorecard/catalog/treasury inputs (no live evaluation loop).

## Implementation Notes

All 7 tests passing under pytest 9.0.2 / Python 3.10.6 on 2026-06-06 (27 total across the suite).

## Relationships

### Depends On
- [[decision_engine.py]]
- [[models.py (supervisor)]]
