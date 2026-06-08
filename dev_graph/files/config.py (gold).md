---
type: file
canonical_id: FILE-016
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/decision_builder/config.py"
related_files: []
related_tests:
  - "[[test_decision_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Gold Decision Confidence Semantics]]"
file_path: "src/gold/decision_builder/config.py"
language: "python"
module: "[[Gold Decision Builder]]"
owns: []
used_by: []
---

# config.py (gold)

## Definition

`DecisionPolicyConfig` — the versioned gold decision policy: the v0 confidence weights + floors AND the regime→direction table, governed by a single `decision_policy_version`. Includes `DEFAULT_DECISION_POLICY_CONFIG`, fail-closed `from_mapping`/`load_config` (`DecisionPolicyConfigError`), and `decision_policy_fingerprint()`.

## Purpose

Pin the confidence model's weights and the regime→direction policy under one governed version (ADR-008 §7), with a fingerprint coherence check that fails CI on an un-versioned edit. The regime→direction table is config (not an ADR) — domain-anchored, provisional, recalibrated via a `decision_policy_version` bump.

## Implementation Notes

Basename-disambiguated as `config.py (gold)` (2nd `config.py`: regime/gold). `__post_init__` validates weights/floors and asserts the direction table is total over all 12 regimes with INDETERMINATE → WATCH. Imports `Regime` from the regime package for the totality check.

## Relationships

### Depends On
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]
