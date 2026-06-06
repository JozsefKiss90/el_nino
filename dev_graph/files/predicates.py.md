---
type: file
canonical_id: FILE-002
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
related_tests:
  - "[[test_predicates]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/risk/guardrail_engine/predicates.py"
language: "python"
module: "[[Guardrail Engine]]"
owns:
  - "position_size_ok"
  - "daily_loss_cap_ok"
  - "max_trades_ok"
  - "max_positions_ok"
  - "withdrawal_disabled"
  - "ALL_PREDICATES"
used_by: []
---

# predicates.py

## Definition

The hard-limit predicate source file of the Guardrail Engine module (MOD-001). Each predicate is a pure function `(request, config) -> (passed, reason)`.

## Purpose

Encodes the non-negotiable trading guardrails (position size, daily loss cap, max trades/day, max concurrent positions, withdrawals disabled) as independently testable pure functions.

## Architecture Role

Predicate library consumed by `GuardrailEngine.validate()`. Realizes the Guardrail Pattern (PAT-002) in code.

## Constraints

- Pure functions — no side effects, no IO; deterministic.
- Boundary semantics: `position_size_ok` uses the lesser of %-of-equity and absolute caps; `daily_loss_cap_ok` blocks at or beyond the cap.

## Implementation Notes

`ALL_PREDICATES` defines the canonical evaluation order. Grounded in the Guardrail Architecture Hard Limits table. Covered by `test_predicates.py` (7 tests, all passing 2026-06-06).

## Relationships

### Depends On
- [[Guardrail Engine]]
- [[models.py]]

### Realizes
- [[Guardrail Pattern]]

### Validated By
- [[test_predicates]]
