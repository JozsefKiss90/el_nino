---
type: artifact_schema
canonical_id: SCHEMA-004
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
schema_id: "decision-packet"
schema_version: "0.1.0"
schema_path: "src/supervisor/schemas/decision_packet.py"
validated_by: []
consumed_by: []
produced_by:
  - "[[Decision Engine]]"
---

# Decision Packet Schema

## Definition

The data contract for the deterministic decision output of the Supervisor Office: the selected upgrade (or none), the ranked option set with scores and block reasons, the rationale, and the post-decision treasury state.

## Purpose

Promotes the Decision Engine's output into a canonical, auditable shape so every upgrade decision is reproducible and reviewable. This is the SCHEMA-004 reserved by Population Strategy §4.6.

## Architecture Role

Output schema of the Decision API (INT-006). Produced by the Decision Engine (MOD-002); consumed downstream by the upgrade lifecycle (Upgrade Evaluation / Team Orchestration — out of the first implementation slice).

## Schema Definition

| Field | Type | Notes |
|-------|------|-------|
| selected_upgrade_id | string \| null | Chosen upgrade; null = "no upgrade needed" (early-exit / all blocked) |
| ranked_options | array | Each: { upgrade_id, score, allowed (bool), blocked_reason (string \| null) } |
| rationale | string | Human-readable decision explanation |
| treasury_state_after | object | { budget, deployed, available } after the decision is applied |

## Validation Rules

- `ranked_options` entries with `allowed = false` MUST carry a non-null `blocked_reason` (budget exhausted or excluded by institutional memory).
- `selected_upgrade_id`, when non-null, MUST appear in `ranked_options` with `allowed = true`.

## Open Questions

- `consumed_by` is empty: the upgrade-lifecycle consumer is out of the first implementation slice; link it when that module node exists.
- Whether `treasury_state_after` is embedded here or referenced from a separate Treasury Policy Schema (SCHEMA-006, deferred).

## Relationships

### Used By
- [[Decision Engine]]
- [[Decision API]]

### Justified By
- [[ADR - Ontology Redesign]]
