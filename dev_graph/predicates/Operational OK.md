---
type: predicate
canonical_id: PRED-007
status: planned
implementation_status: not-started
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: inferred
evidence:
  - design
  - ADR
source_paths:
  - "GOLD_DECISIONPACKET_V0_BRIEF.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
predicate_id: "operational-ok"
predicate_scope: "L3 operational guard — instrument/venue tradeable and operational preconditions hold"
implemented_in: "src/gold/decision_builder/models.py (GuardRefs.operational_ok carries the outcome; operational computation deferred)"
validated_by: []
---

# Operational OK

## Definition

Boolean L3 guard: `operational_ok` passes when operational preconditions for acting on a gold decision hold — e.g. the instrument/venue is tradeable, the runtime is healthy, and no operational halt is in force. The second of ADR-006 §6's two net-new Layer-3 guards.

## Purpose

Keep operational readiness out of the deterministic, snapshot-local decision core. Operational state is external/runtime context (not derivable from a snapshot), so it can never be a MOD-004 feature (ADR-006 §6 / ADR-005 snapshot-locality) and is carried as a guard outcome the packet cites.

## Implementation Notes

**Runtime computation is deferred** (ADR-006 Non-Goals — no paper-trading runtime in v0). The Gold DecisionPacket (SCHEMA-011) carries the outcome in `guard_refs.operational_ok` (`bool | None`); v0 packets carry `null` (unevaluated). `build_decision` accepts the outcome as an optional input and never computes it (it would require non-deterministic external context).

## Relationships

### Guards
- [[Gold Decision Gate]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]
