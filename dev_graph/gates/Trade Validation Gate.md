---
type: gate
canonical_id: GATE-001
status: active
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-16
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files:
  - "[[guardrail_engine.py]]"
related_tests:
  - "[[test_guardrail_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Execution Layer Planning]]"
gate_id: "trade-validation-gate"
gate_scope: "Risk Control trade-validation boundary — every proposed trade before broker submission"
required_artifacts:
  - "[[Trade Validation Request Schema]]"
blocking: true
---

# Trade Validation Gate

## Definition

The blocking quality checkpoint at the Risk Control boundary: a proposed trade may proceed only if every hard-limit predicate passes. Enforced by `GuardrailEngine.validate()` (MOD-001) as a short-circuit conjunction.

## Purpose

Operationalizes the [[Guardrail Philosophy]]: no trade reaches the broker without passing validation. The gate is the named checkpoint; the predicates are its pass/fail conditions.

## Architecture Role

Guards the Guardrail Enforcement capability (CAP-008). Consumes a [[Trade Validation Request Schema]]; aggregates the five predicate results into a single approve/block decision ([[Trade Validation Decision Schema]]).

## Constraints

- `blocking: true` — a failing predicate blocks the trade (fail closed).
- Decision is deterministic and attributes every block to the first failing predicate.

## Implementation Notes

Realized by `guardrail_engine.py` (FILE-001): `GuardrailEngine.validate()` evaluates `ALL_PREDICATES` in order. The gate's pass/fail logic is fully implemented and covered by `test_guardrail_engine` (TEST-002).

## Open Questions

- **Wired (2026-06-16):** the gate is now invoked at the trade boundary by the [[Execution]] module (MOD-008) — the orchestrator runs `GuardrailEngine.validate()` before `execute()` (ADR-011 §4 / gate c), so a failing predicate blocks the (paper) fill. Advanced `in-progress → implemented`. (Live-money order routing remains a Non-Goal; this is the paper-execution boundary.)

## Relationships

### Guards
- [[Guardrail Enforcement]]

### Used By
- [[Execution]]

### Depends On
- [[Position Size OK]]
- [[Daily Loss Cap OK]]
- [[Max Trades OK]]
- [[Max Positions OK]]
- [[Withdrawal Disabled]]

### Consumes
- [[Trade Validation Request Schema]]

### Validated By
- [[test_guardrail_engine]]

### Justified By
- [[ADR - Ontology Redesign]]
