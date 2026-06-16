---
type: file
canonical_id: FILE-025
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/config.py"
related_files: []
related_tests:
  - "[[test_execution_guards]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/config.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# config.py (execution)

## Definition

`ExecutionPolicyConfig` (the fixed v0 `default_size`, `instrument`, `paper_equity`) + `FillModelConfig`
(`slippage_bps`, `fill_model_version`) — versioned, fail-closed, each with a `fingerprint()`.

## Purpose

Hold the execution + fill-model policy as versioned, fingerprinted config (ADR-011 §2 / gate b): the
`fill_model_version` + fingerprints fold into the execution replay key, so an unversioned edit fails a CI
coherence test. Sizing is a fixed `default_size` (ADR-011 D2 — deferred). Mirrors `RuntimePolicyConfig` /
`DecisionPolicyConfig`.

## Implementation Notes

`fingerprint()` = SHA-256 over the policy-defining fields (version excluded). `from_mapping` / `load_config`
are fail-closed (unknown keys / missing version raise). `DEFAULT_FILL_MODEL` + `DEFAULT_EXECUTION_POLICY_CONFIG`
are the canonical v0 configs.

## Relationships

### Depends On
- [[Execution]]

### Validated By
- [[test_execution_guards]]
