---
type: predicate
canonical_id: PRED-004
status: active
implementation_status: tested
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
related_files:
  - "[[predicates.py]]"
related_tests:
  - "[[test_predicates]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
predicate_id: "max-positions-ok"
predicate_scope: "Open position count must be below the configured maximum"
implemented_in: "src/risk/guardrail_engine/predicates.py"
validated_by:
  - "[[test_predicates]]"
---

# Max Positions OK

## Definition

Boolean condition: `open_positions < max_positions`. Passes while the number of concurrently open positions is below the configured limit (default 3–5).

## Purpose

Enforces the "max concurrent positions" hard limit — bounds simultaneous exposure.

## Implementation Notes

Implemented as `max_positions_ok(request, config)` in `predicates.py` (FILE-002). Boundary verified by `test_predicates` (at limit blocks; one below passes).

## Relationships

### Guards
- [[Trade Validation Gate]]

### Validated By
- [[test_predicates]]

### Justified By
- [[ADR - Ontology Redesign]]
