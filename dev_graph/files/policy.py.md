---
type: file
canonical_id: FILE-017
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/decision_builder/policy.py"
related_files: []
related_tests:
  - "[[test_decision_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Gold Decision Confidence Semantics]]"
file_path: "src/gold/decision_builder/policy.py"
language: "python"
module: "[[Gold Decision Builder]]"
owns: []
used_by: []
---

# policy.py

## Definition

Pure decision-policy helpers: `trust_score(rc, fv, config)` (the ADR-008 ordinal trust score + structural-penalty-aggregate uncertainty) and `direction_for(rc, config)` (the versioned regime→direction lookup).

## Purpose

Hold the confidence/direction computation as pure, deterministic functions, separate from the dataclasses and the assembly driver — mirroring the regime layer's `taxonomy.py` helper split.

## Implementation Notes

`trust_score`: anchor = within-rule normalized `rule_margin` (or the NEUTRAL floor); four structural discount factors (ambiguity / fragility / data-quality / coverage); `confidence = anchor × structural`; `uncertainty = 1 − structural` (penalty aggregate, not `1 − confidence`); INDETERMINATE fail-closed to the configured floor. No IO/clock/randomness.

## Relationships

### Depends On
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]
