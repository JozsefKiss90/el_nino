---
type: interface
canonical_id: INT-003
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
  - "wiki/systems/Three-Layer Trading System.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
interface_id: "risk-check-api"
interface_version: "0.1.0"
parent_capability: "[[Guardrail Enforcement]]"
input_schema: "[[Trade Validation Request Schema]]"
output_schema: "[[Trade Validation Decision Schema]]"
implemented_by:
  - "[[Guardrail Engine]]"
stability: evolving
---

# Risk Check API

## Definition

The synchronous contract by which the Trading Engine submits a proposed trade to Risk Control for validation and receives an approve/block decision. This is the INT-003 interface reserved by Population Strategy §4.6 (Risk Control → Trading Engine).

## Purpose

Makes the guardrail boundary an explicit, versioned contract rather than an implicit call: every trade crosses this interface before reaching the broker, and no trade may bypass it.

## Architecture Role

Boundary interface of the Guardrail Enforcement capability (CAP-008). Implemented by the Guardrail Engine (MOD-001). Consumes the Trade Validation Request Schema (SCHEMA-007); produces the Trade Validation Decision Schema (SCHEMA-008).

## Contract

- **Operation**: `validate(request) -> decision` — synchronous request/response.
- **Input**: Trade Validation Request Schema (trade params + portfolio context).
- **Output**: Trade Validation Decision Schema (approve/block + triggered predicate + reason).
- **Semantics**: The caller blocks until a decision is returned; evaluation is deterministic (identical inputs → identical decisions).

## Error Modes

- Missing/incomplete guardrail configuration → fail-closed BLOCK (never silently relax a limit).
- Malformed request (failing input-schema validation) → reject with an explanatory reason.

## Stability

`experimental` / `interface_version: 0.1.0` — the contract is concretely implied by Guardrail Enforcement but may refine once the Guardrail Engine is implemented against real code.

## Open Questions

- Whether validation also returns advisory soft-limit warnings (e.g., conviction threshold) alongside the hard approve/block.

## Relationships

### Consumes
- [[Trade Validation Request Schema]]

### Produces
- [[Trade Validation Decision Schema]]

### Validated By
- [[test_guardrail_engine]]

### Justified By
- [[ADR - Ontology Redesign]]
