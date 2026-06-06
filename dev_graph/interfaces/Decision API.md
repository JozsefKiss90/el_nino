---
type: interface
canonical_id: INT-006
status: planned
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: inferred
evidence:
  - design
  - wiki
source_paths:
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
interface_id: "decision-api"
interface_version: "0.1.0"
parent_capability: "[[Decision Making]]"
input_schema: null
output_schema: "[[Decision Packet Schema]]"
implemented_by:
  - "[[Decision Engine]]"
stability: experimental
---

# Decision API

## Definition

The contract by which the Supervisor Office emits an upgrade decision to the rest of the system. This is the INT-006 interface reserved by Population Strategy §4.6 (Supervisor Office → Trading Engine).

## Purpose

Exposes the Decision Engine's deterministic upgrade selection as a versioned, auditable contract that the upgrade lifecycle consumes.

## Architecture Role

Boundary interface of the Decision Making capability (CAP-015). Implemented by the Decision Engine (MOD-002); produces the Decision Packet Schema (SCHEMA-004).

## Contract

- **Operation**: `decide(state) -> decision_packet` — evaluates current performance, catalog, treasury, and institutional memory.
- **Input**: not yet a formal schema — the Evaluation Scorecard Schema (SCHEMA-005) is out of the first implementation slice; `input_schema: null` for now.
- **Output**: Decision Packet Schema (selected upgrade, ranked options, rationale, treasury state).
- **Semantics**: Deterministic — no randomness in decision-making.

## Error Modes

- Budget exhausted or all options excluded → returns a no-op packet (`selected_upgrade_id: null`).
- Early exit when the latest scorecard is promotable (PnL > 0 and calibration ≥ 65%) → no-op packet.

## Stability

`experimental` / `interface_version: 0.1.0` — output contract is concretely implied; the input contract firms up when the Evaluation Scorecard Schema is created (deferred).

## Open Questions

- `input_schema: null` until Evaluation Scorecard Schema (SCHEMA-005) exists.

## Relationships

### Produces
- [[Decision Packet Schema]]

### Justified By
- [[ADR - Ontology Redesign]]
