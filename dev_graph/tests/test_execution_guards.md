---
type: test
canonical_id: TEST-020
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-16
updated: 2026-06-16
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_execution_guards.py"
related_files:
  - "[[runtime.py (execution)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/execution/test_execution_guards.py"
test_type: unit
covers:
  - "[[Execution]]"
  - "[[Execution API]]"
required_for: []
---

# test_execution_guards

## Definition

The GATE-001 guard-wiring (ADR-011 gate c): `run_guard` maps a `GuardrailEngine` APPROVE/BLOCK to a
forwarded `GuardResult`; a block (position-size / withdrawal) yields a no-fill record naming the first
failing predicate; the **captured** guard config drives the outcome regardless of the environment (gate c.4
replay determinism).

## Purpose

Guarantee the dormant guardrail machinery (GATE-001 + PRED-001..005) is correctly wired into the trade
pipeline, fail-closed, and env-independent on the replay path.

## Relationships

### Used By
- [[Execution]]
- [[Execution API]]

### Justified By
- [[ADR - Execution Layer Planning]]
