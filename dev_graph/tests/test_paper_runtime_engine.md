---
type: test
canonical_id: TEST-014
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_paper_runtime_engine.py"
related_files:
  - "[[engine.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/gold/test_paper_runtime_engine.py"
test_type: unit
covers:
  - "[[Paper-Trading Runtime]]"
  - "[[Paper Runtime API]]"
required_for: []
---

# test_paper_runtime_engine

## Definition

Behavioral tests for `evaluate()`: ADMIT / REJECT(duplicate) / REJECT(operational) / HOLD(WATCH) /
HOLD(INDETERMINATE), the first-failure-names-the-guard order, the config require-flags, the
`supervisor_ok` None stub, the canonical guard-block order, and the `RuntimeDecisionRecord`
fail-closed `__post_init__` (ADMIT ⇔ no triggered guard).

## Purpose

Guarantee the verdict logic + the Runtime Admission Gate (GATE-003) invariant hold end-to-end.

## Relationships

### Used By
- [[Paper-Trading Runtime]]
- [[Paper Runtime API]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
