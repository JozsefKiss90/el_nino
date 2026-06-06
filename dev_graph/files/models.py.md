---
type: file
canonical_id: FILE-003
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - code
source_paths: []
related_files: []
related_tests:
  - "[[test_predicates]]"
  - "[[test_guardrail_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/risk/guardrail_engine/models.py"
language: "python"
module: "[[Guardrail Engine]]"
owns:
  - "TradeDirection"
  - "TradeValidationRequest"
  - "TradeValidationDecision"
  - "GuardrailConfig"
used_by: []
---

# models.py

## Definition

The data-model source file of the Guardrail Engine module (MOD-001). Defines the frozen dataclasses that realize the Risk Check API contract.

## Purpose

Realizes SCHEMA-007 (`TradeValidationRequest`) and SCHEMA-008 (`TradeValidationDecision`), plus `GuardrailConfig` and the `TradeDirection` enum. Dependency-free stdlib dataclasses per ADR-003.

## Architecture Role

Shared data layer for the Guardrail Engine; consumed by both `predicates.py` and `guardrail_engine.py`.

## Constraints

- `TradeValidationDecision.__post_init__` enforces the SCHEMA-008 invariant (a block must name the triggering predicate; an approve must not).
- Frozen dataclasses — immutable, hashable, value-equal (enables deterministic comparison in tests).

## Implementation Notes

Realizes the two artifact-schema nodes in code. Exercised by both test files.

## Relationships

### Depends On
- [[Guardrail Engine]]

### Produces
- [[Trade Validation Request Schema]]
- [[Trade Validation Decision Schema]]

### Validated By
- [[test_predicates]]
- [[test_guardrail_engine]]
