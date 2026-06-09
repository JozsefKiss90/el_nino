---
type: test
canonical_id: TEST-015
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_paper_runtime_determinism.py"
related_files:
  - "[[config.py (paper_runtime)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/gold/test_paper_runtime_determinism.py"
test_type: unit
covers:
  - "[[Paper-Trading Runtime]]"
  - "[[Runtime Decision Record Schema]]"
required_for: []
---

# test_paper_runtime_determinism

## Definition

Determinism + fingerprint-coherence tests: a `RuntimeDecisionRecord` is byte-identical across two
`evaluate()` runs from the same prior ledger; `record_id` binds the prior ledger state; the pinned
`runtime_policy_fingerprint` (`ab798cae…6f32`) changes on a require-flag edit and is unchanged by a
version-only bump; the fingerprint threads into `record_id`.

## Purpose

Pin the v0 runtime policy set so an un-versioned policy edit fails CI, and prove byte-identical replay.

## Relationships

### Used By
- [[Paper-Trading Runtime]]
- [[Runtime Decision Record Schema]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
