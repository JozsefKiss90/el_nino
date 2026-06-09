---
type: predicate
canonical_id: PRED-007
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
predicate_id: "operational-ok"
predicate_scope: "L3 operational guard — instrument/venue tradeable and operational preconditions hold"
implemented_in: "src/gold/paper_runtime/predicates.py (operational_ok — instrument match + tradeable/venue_open/not-halt/not-degraded, from a versioned OperationalInput)"
validated_by:
  - "[[test_paper_runtime_guards]]"
---

# Operational OK

## Definition

Boolean L3 guard: `operational_ok` passes when operational preconditions for acting on a gold decision hold — e.g. the instrument/venue is tradeable, the runtime is healthy, and no operational halt is in force. The second of ADR-006 §6's two net-new Layer-3 guards.

## Purpose

Keep operational readiness out of the deterministic, snapshot-local decision core. Operational state is external/runtime context (not derivable from a snapshot), so it can never be a MOD-004 feature (ADR-006 §6 / ADR-005 snapshot-locality) and is carried as a guard outcome the packet cites.

## Implementation Notes

**Implemented** in the paper-trading runtime (MOD-007) — [[ADR - Paper-Trading Runtime Planning]] (ADR-009) un-defers it. `operational_ok(packet, op)` passes iff the instrument matches and the venue is tradeable + open + not halted + not degraded, read from an **explicit, versioned `OperationalInput`** (a deterministic, caller/file-supplied artifact — **not** a live venue probe, which stays a Non-Goal). Default-closed: an absent/malformed operational input resolves to not-tradeable. Determinism is preserved because the operational state is an explicit replay input, fingerprinted into the record and the ledger entry. The pure gold builder still leaves `guard_refs.operational_ok = null` (the wrap keeps the packet pure).

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
