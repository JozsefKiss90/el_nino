---
type: test
canonical_id: TEST-013
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_paper_runtime_guards.py"
related_files:
  - "[[predicates.py (paper_runtime)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/gold/test_paper_runtime_guards.py"
test_type: unit
covers:
  - "[[Paper-Trading Runtime]]"
required_for: []
---

# test_paper_runtime_guards

## Definition

Unit tests for the runtime guard predicates (PRED-006/007 + echoes), each in isolation: once-ever dedup
(prior ADMIT only), operational preconditions (halt / degraded / not-tradeable / venue-closed / wrong
instrument / default-closed), and the snapshot echoes (true / false / default-closed-on-absent).

## Purpose

Pin each guard's pure `(passed, reason)` behavior independently of the engine.

## Relationships

### Used By
- [[Paper-Trading Runtime]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
