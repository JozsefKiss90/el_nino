---
type: file
canonical_id: FILE-001
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[models.py]]"
  - "[[predicates.py]]"
related_tests:
  - "[[test_guardrail_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/risk/guardrail_engine/guardrail_engine.py"
language: "python"
module: "[[Guardrail Engine]]"
owns:
  - "GuardrailEngine"
  - "load_config_from_env"
  - "GuardrailConfigError"
used_by: []
---

# guardrail_engine.py

## Definition

The orchestrator source file of the Guardrail Engine module (MOD-001). Defines `GuardrailEngine.validate()` (short-circuit predicate conjunction), the fail-closed `load_config_from_env()` loader, and `GuardrailConfigError`.

## Purpose

Implements the Risk Check API (INT-003) in code: consumes a `TradeValidationRequest`, returns a `TradeValidationDecision`.

## Architecture Role

Entry point of the Guardrail Engine module within Risk Control. Stateless, synchronous, deterministic.

## Constraints

- Missing hard-limit config raises `GuardrailConfigError` (fail closed).
- Malformed request (size ≤ 0) is blocked, not raised.
- Evaluation order is fixed (short-circuit on first failing predicate).

## Implementation Notes

`GuardrailEngine.__init__` takes a `GuardrailConfig` and an injectable predicate sequence (defaults to `ALL_PREDICATES`). `validate()` returns the first failing predicate's name as `triggered_predicate`, or `None` on approval. Covered by `test_guardrail_engine.py` (8 tests, all passing 2026-06-06).

## Relationships

### Depends On
- [[Guardrail Engine]]
- [[models.py]]
- [[predicates.py]]

### Implements
- [[Risk Check API]]

### Validated By
- [[test_guardrail_engine]]
