---
type: file
canonical_id: FILE-020
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-09
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

`RuntimePolicyConfig` (the `require_operational` / `require_snapshot_guards` admission flags) +
`runtime_policy_version` + `runtime_policy_fingerprint()` + `DEFAULT_RUNTIME_POLICY_CONFIG` +
fail-closed `from_mapping`/`load_config` (`RuntimePolicyConfigError`).

## Purpose

Govern which guards are *required* to ADMIT, versioned and fingerprinted so a silent policy edit fails
a CI coherence test (ADR-009 §7).

## Implementation Notes

Copies the gold `decision_policy_fingerprint` idiom verbatim: SHA-256 over the sorted policy fields
(`json.dumps(..., sort_keys=True, separators=(",",":"))`), the version excluded. Default fingerprint
`ab798cae915c1617f26c2a2793d425280d495099e593579a2ba99e74e9e56f32`. IO at the boundary only.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_determinism]]
