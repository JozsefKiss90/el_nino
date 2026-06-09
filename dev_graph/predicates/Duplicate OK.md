---
type: predicate
canonical_id: PRED-006
status: active
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "GOLD_DECISIONPACKET_V0_BRIEF.md"
  - "src/gold/paper_runtime/predicates.py"
related_files:
  - "[[predicates.py (paper_runtime)]]"
related_tests:
  - "[[test_paper_runtime_guards]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
predicate_id: "duplicate-ok"
predicate_scope: "L3 idempotency guard — a snapshot_id must not have already produced a gold packet"
implemented_in: "src/gold/paper_runtime/predicates.py (duplicate_ok — once-ever on a prior ADMIT in the RuntimeLedger)"
validated_by:
  - "[[test_paper_runtime_guards]]"
---

# Duplicate OK

## Definition

Boolean L3 guard: `duplicate_ok` passes when the current `source_snapshot_id` has **not** already produced a Gold DecisionPacket (idempotency / de-duplication). It is one of ADR-004's six-guard taxonomy and one of the **two net-new Layer-3 guards** ADR-006 §6 names (`duplicate_ok`, `operational_ok`).

## Purpose

Prevent a replayed or re-published snapshot from emitting a second, redundant paper decision. It is a **decision-pipeline guard**, not a feature: it depends on cross-packet state (what has already been emitted), so it can never be a snapshot-local MOD-004 feature (ADR-006 §6 / ADR-005 snapshot-locality).

## Implementation Notes

**Implemented** in the paper-trading runtime (MOD-007) — [[ADR - Paper-Trading Runtime Planning]] (ADR-009) un-defers it. `duplicate_ok(packet, prior_ledger)` passes iff `not prior_ledger.has_admit(packet.source_snapshot_id)` — **once-ever**, keyed on a prior **ADMIT** (a prior HOLD/REJECT does not count as "already produced a packet"). It reads the explicit [[Runtime Ledger Schema]] (SCHEMA-013), never hidden state. The pure gold builder still leaves `guard_refs.duplicate_ok = null` (the wrap keeps the packet pure, ADR-009 §2); the computed outcome lives on the [[Runtime Decision Record Schema]] (SCHEMA-012).

## Relationships

### Guards
- [[Gold Decision Gate]]
- [[Runtime Admission Gate]]

### Validated By
- [[test_paper_runtime_guards]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
