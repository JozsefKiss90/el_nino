---
type: gate
canonical_id: GATE-003
status: active
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/gold/paper_runtime/engine.py"
related_files:
  - "[[engine.py]]"
related_tests:
  - "[[test_paper_runtime_engine]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
gate_id: "runtime-admission-gate"
gate_scope: "L3 runtime admission boundary — composes the evaluated guards into an ADMIT/HOLD/REJECT verdict over the runtime record"
required_artifacts:
  - "[[Runtime Decision Record Schema]]"
blocking: true
---

# Runtime Admission Gate

## Definition

The blocking Layer-3 checkpoint over the **runtime record** (SCHEMA-012): it composes the evaluated
six-guard block into a fail-closed `ADMIT`/`HOLD`/`REJECT` verdict, enforced in `evaluate()` and the
`RuntimeDecisionRecord.__post_init__` invariant. It governs the runtime's *record*, not the pure
packet — distinct from the advisory [[Gold Decision Gate]] (GATE-002), which stays advisory over the
still-pure packet (whose `guard_refs` remain all-`null`).

## Purpose

Give the paper-trading runtime one named, blocking place to decide admission, now that the stateful
guards are actually computed. A non-ADMIT verdict MUST name its triggering guard (idempotency,
operational, or data); ADMIT must not.

## Architecture Role

Guards [[Paper-Trade Admission]] (CAP-021). Composes [[Duplicate OK]] (PRED-006) + [[Operational OK]]
(PRED-007) + (as of v0.2.0) the computed [[Cooldown OK]] (PRED-008) + the snapshot echoes
(`data_ok`/`freshness_ok`); `supervisor_ok` is a `None` stub (not gating in v0). Consumes/produces the
[[Runtime Decision Record Schema]] (SCHEMA-012).

## Constraints

- `blocking: true` — a required-but-failed guard yields REJECT; a WATCH/INDETERMINATE packet yields
  HOLD; only an all-required-pass actionable packet ADMITs. The fail-closed invariant is enforced at
  record construction.
- **Required guards** (config-governed): `duplicate_ok` (evaluated FIRST — idempotency precedence), then
  `cooldown_ok` (computed, **v0.2.0**), `data_ok`, `freshness_ok`, `operational_ok` in canonical
  `_GUARD_NAMES` order. `supervisor_ok` (stub) is informational. (Pre-v0.2.0, `cooldown_ok` was an echo and
  informational.)
- Deterministic aggregation only; no clock/IO in the verdict logic (state arrives as an explicit
  ledger; operational state as an explicit versioned input).

## Implementation Notes

Implemented in `src/gold/paper_runtime/engine.py` (`evaluate`) + `models.py`
(`RuntimeDecisionRecord.__post_init__`). The first failing required guard (short-circuit, in
`_GUARD_NAMES` order) names the verdict. Validated by [[test_paper_runtime_engine]].

## Relationships

### Guards
- [[Paper-Trade Admission]]

### Depends On
- [[Duplicate OK]]
- [[Operational OK]]
- [[Cooldown OK]]

### Consumes
- [[Runtime Decision Record Schema]]

### Validated By
- [[test_paper_runtime_engine]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
