---
type: gate
canonical_id: GATE-002
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
gate_id: "gold-decision-gate"
gate_scope: "L3 gold-decision boundary — composes the guard outcomes a Gold DecisionPacket cites"
required_artifacts:
  - "[[Gold DecisionPacket v0 Schema]]"
blocking: false
---

# Gold Decision Gate

## Definition

The Layer-3 checkpoint that composes the six-guard taxonomy outcomes a Gold DecisionPacket cites in its `guard_refs` — the snapshot-derived `data_ok`/`freshness_ok`, the Layer-3 stubs `supervisor_ok`/`cooldown_ok`, and the two net-new L3 guards [[Duplicate OK]] (`duplicate_ok`) and [[Operational OK]] (`operational_ok`).

## Purpose

Give the (future) paper-trading runtime one named place to decide whether to act on a paper decision, separate from the deterministic decision core. The pure `build_decision` always produces a packet (guards are advisory L3 context); the gate is where guard outcomes are aggregated and enforced once the runtime exists.

## Architecture Role

Guards [[Gold Decision Generation]] (CAP-020). Composes [[Duplicate OK]] + [[Operational OK]] (+ the snapshot/stub guards). Consumes the packet's `guard_refs` (carried by [[Gold DecisionPacket v0 Schema]], SCHEMA-011).

## Constraints

- `blocking: false` in v0 — the gate is **advisory**: the pure builder still emits a packet with `guard_refs` (null for unevaluated guards). Promote to blocking when the stateful guards + the paper-trading runtime exist.
- Deterministic aggregation only; no clock/IO in the decision core (the stateful guard *inputs* live in the deferred runtime, not the builder).

## Implementation Notes

**Runtime computation is deferred** (ADR-006 Non-Goals). This node records the gate contract; the stateful guards ([[Duplicate OK]], [[Operational OK]]) and the aggregation logic are authored when the paper-trading runtime exists. For v0, `GuardRefs` carries `null` for unevaluated guards and the builder never blocks.

## Open Questions

- Whether `data_ok`/`freshness_ok` are echoed from the upstream snapshot guards (SCHEMA-001) or recomputed at L3 — resolved when the runtime is authored (the gold builder never reads raw SCHEMA-001 per ADR-006 §2, so they would arrive as guard inputs).

## Relationships

### Guards
- [[Gold Decision Generation]]

### Depends On
- [[Duplicate OK]]
- [[Operational OK]]

### Consumes
- [[Gold DecisionPacket v0 Schema]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]
