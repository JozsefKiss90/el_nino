---
type: predicate
canonical_id: PRED-006
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
predicate_id: "duplicate-ok"
predicate_scope: "L3 idempotency guard — a snapshot_id must not have already produced a gold packet"
implemented_in: "src/gold/decision_builder/models.py (GuardRefs.duplicate_ok carries the outcome; stateful computation deferred)"
validated_by: []
---

# Duplicate OK

## Definition

Boolean L3 guard: `duplicate_ok` passes when the current `source_snapshot_id` has **not** already produced a Gold DecisionPacket (idempotency / de-duplication). It is one of ADR-004's six-guard taxonomy and one of the **two net-new Layer-3 guards** ADR-006 §6 names (`duplicate_ok`, `operational_ok`).

## Purpose

Prevent a replayed or re-published snapshot from emitting a second, redundant paper decision. It is a **decision-pipeline guard**, not a feature: it depends on cross-packet state (what has already been emitted), so it can never be a snapshot-local MOD-004 feature (ADR-006 §6 / ADR-005 snapshot-locality).

## Implementation Notes

**Runtime computation is deferred** (ADR-006 Non-Goals — no paper-trading runtime / dedup store in v0). The Gold DecisionPacket (SCHEMA-011) carries the outcome in `guard_refs.duplicate_ok` (`bool | None`); v0 packets carry `null` (unevaluated). The stateful check is authored when the paper-trading runtime exists. `build_decision` accepts the outcome as an optional input (ADR-006 §2 permits future L3 guard outputs) and never computes it.

## Relationships

### Guards
- [[Gold Decision Gate]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]
