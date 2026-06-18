---
type: file
canonical_id: FILE-020
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/paper_runtime/config.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/gold/paper_runtime/config.py"
language: "python"
module: "[[Paper-Trading Runtime]]"
owns: []
used_by: []
---

# config.py (paper_runtime)

## Definition

`RuntimePolicyConfig` (the `require_operational` / `require_snapshot_guards` admission flags, plus the
**v0.2.0** `require_cooldown` + `cooldown_window_hours`) + `runtime_policy_version` +
`runtime_policy_fingerprint()` + `DEFAULT_RUNTIME_POLICY_CONFIG` + fail-closed `from_mapping`/`load_config`
(`RuntimePolicyConfigError`).

## Purpose

Govern which guards are *required* to ADMIT, versioned and fingerprinted so a silent policy edit fails
a CI coherence test (ADR-009 §7).

## Implementation Notes

Copies the gold `decision_policy_fingerprint` idiom verbatim: SHA-256 over the sorted policy fields
(`json.dumps(..., sort_keys=True, separators=(",",":"))`), the version excluded. **v0.2.0** default
fingerprint `47ca2649dd70a2d4ffae81561cc76c538e75b3558b06daa4dbc33a11d5a98cc8`
(`runtime_policy_version 0.2.0`; the cooldown fields fold into the digest). IO at the boundary only.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_determinism]]
