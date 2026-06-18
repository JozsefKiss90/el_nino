---
type: predicate
canonical_id: PRED-008
status: active
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/gold/paper_runtime/predicates.py"
related_files:
  - "[[predicates.py (paper_runtime)]]"
related_tests:
  - "[[test_paper_runtime_guards]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
predicate_id: "cooldown-ok"
predicate_scope: "L3 computed cooldown guard — min gap (hours) since the last ADMIT of a DIFFERENT snapshot"
implemented_in: "src/gold/paper_runtime/predicates.py (cooldown_ok — computed from RuntimeLedger.last_admit_as_of + the snapshot as_of; v0.2.0)"
validated_by:
  - "[[test_paper_runtime_guards]]"
---

# Cooldown OK

## Definition

Boolean L3 guard: `cooldown_ok` passes when at least `cooldown_window_hours` has elapsed — measured by
the snapshot `as_of` (never wall-clock) — since the last **ADMIT** of a **different** snapshot. One of the
six-guard taxonomy; **computed** at runtime as of **v0.2.0** (2026-06-18), replacing the prior v0.1.0
**echo** of the L2 snapshot's `cooldown_ok` flag (ADR-009 §6 deferred the computed cooldown; the
[[ADR - Paper-Trading Runtime Planning]] 2026-06-18 amendment lifts it).

## Purpose

Pace paper admissions: prevent a second ADMIT of a *distinct* decision within the cooldown window
(anti-over-trading), while leaving exact re-presentations to [[Duplicate OK]] (PRED-006). It is a
**runtime-state** guard (it reads the ledger's prior ADMIT timing), so — like `duplicate_ok` /
`operational_ok` — it can never be a snapshot-local MOD-004 feature.

## Implementation Notes

**Implemented** in the paper-trading runtime (MOD-007). `cooldown_ok(packet, prior_ledger, config)` reads
`prior_ledger.last_admit_as_of(exclude_snapshot_id=packet.source_snapshot_id)` (the most recent ADMIT of a
*different* snapshot — **no SCHEMA-013 change**; the ledger already records each entry's `as_of`) and
compares the gap to `config.cooldown_window_hours`. **Deterministic** (the only time source is the snapshot
`as_of`); **fail-closed** (missing / unparseable / out-of-order negative-gap timing ⇒ `False`); no prior
ADMIT ⇒ `True`. `duplicate_ok` is evaluated **first** among the required guards, so an exact re-presentation
attributes to idempotency, not cooldown. Required to ADMIT iff `config.require_cooldown` (default `True`).
The pure gold builder still leaves `guard_refs.cooldown_ok = null`; the computed outcome lives on the
[[Runtime Decision Record Schema]] (SCHEMA-012). The L2 snapshot's `cooldown_ok` stays as forwarded
`snapshot_guards` provenance (its existing role).

## Relationships

### Guards
- [[Gold Decision Gate]]
- [[Runtime Admission Gate]]

### Validated By
- [[test_paper_runtime_guards]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
