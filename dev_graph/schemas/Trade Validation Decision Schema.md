---
type: artifact_schema
canonical_id: SCHEMA-008
status: active
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
schema_id: "trade-validation-decision"
schema_version: "0.1.0"
schema_path: "src/risk/guardrail_engine/models.py"
validated_by: []
consumed_by: []
produced_by:
  - "[[Guardrail Engine]]"
---

# Trade Validation Decision Schema

## Definition

The data contract for the approve/block decision returned by the Risk Check API after a trade-validation request is evaluated.

## Purpose

Gives the Guardrail Engine's output a canonical, versioned shape, including the identity of the first failing predicate so callers and audit logs can attribute every block to a specific guardrail.

## Architecture Role

Output schema of the Risk Check API (INT-003). Produced by the Guardrail Engine (MOD-001); consumed by the trade executor / order-management caller (out of the first implementation slice).

## Schema Definition

| Field | Type | Notes |
|-------|------|-------|
| approved | boolean | True = APPROVE, false = BLOCK |
| triggered_predicate | string \| null | Name of the first failing predicate; null when approved |
| reason | string | Human-readable explanation of the decision |
| evaluated_at | timestamp | When the decision was produced |

## Validation Rules

- When `approved` is false, `triggered_predicate` MUST be non-null (every block attributes to a predicate).
- When `approved` is true, `triggered_predicate` is null.

## Open Questions

- `consumed_by` is empty: the trade-executing caller is out of the first implementation slice; link it when that module node exists.

## Relationships

### Used By
- [[Guardrail Engine]]
- [[Risk Check API]]
- [[models.py]]

### Justified By
- [[ADR - Ontology Redesign]]
