---
type: interface
canonical_id: INT-006
status: active
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-07
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Decision Layer Re-grounding]]"
interface_id: "decision-api"
interface_version: "0.1.0"
parent_capability: "[[Decision Making]]"
input_schema: "[[Evaluation Scorecard Schema]]"
output_schema: "[[Decision Packet Schema]]"
implemented_by:
  - "[[Decision Engine]]"
stability: evolving
---

# Decision API

## Definition

The contract by which the Supervisor Office emits an upgrade decision to the rest of the system. This is the INT-006 interface reserved by Population Strategy §4.6 (Supervisor Office → Trading Engine).

## Scope

This artifact belongs to the **Supervisor Office treasury-upgrade decision path**. It is **not** the future Gold Trading Decision contract (DecisionPacket v0). The Gold Trading Decision branch will be introduced as separate ontology objects with new canonical identifiers, justified by deterministic Layer-2-derived features. Governed by [[ADR - Decision Layer Re-grounding]].

## Purpose

Exposes the Decision Engine's deterministic upgrade selection as a versioned, auditable contract that the upgrade lifecycle consumes.

## Architecture Role

Boundary interface of the Decision Making capability (CAP-015). Implemented by the Decision Engine (MOD-002); produces the Decision Packet Schema (SCHEMA-004).

## Contract

- **Operation**: `decide(state) -> decision_packet` — evaluates current performance, catalog, treasury, and institutional memory.
- **Input**: [[Evaluation Scorecard Schema]] (SCHEMA-005) — performance evidence from the Evaluation Loop. Plus intra-system inputs (upgrade catalog, treasury state, institutional memory) passed as internal value objects.
- **Output**: Decision Packet Schema (selected upgrade, ranked options, rationale, treasury state).
- **Semantics**: Deterministic — no randomness in decision-making.

## Error Modes

- Budget exhausted or all options excluded → returns a no-op packet (`selected_upgrade_id: null`).
- Early exit when the latest scorecard is promotable (PnL > 0 and calibration ≥ 65%) → no-op packet.

## Stability

`experimental` / `interface_version: 0.1.0` — output contract is concretely implied; the input contract firms up when the Evaluation Scorecard Schema is created (deferred).

## Open Questions

- `input_schema` set to [[Evaluation Scorecard Schema]] (SCHEMA-005), created 2026-06-06 for the Decision Engine slice. The transport interface (Evaluation API, INT-007) remains deferred.

## Relationships

### Consumes
- [[Evaluation Scorecard Schema]]

### Produces
- [[Decision Packet Schema]]

### Validated By
- [[test_decision_engine]]

### Justified By
- [[ADR - Ontology Redesign]]
