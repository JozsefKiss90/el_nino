---
type: capability
canonical_id: CAP-021
status: active
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/gold/paper_runtime/engine.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_engine]]"
  - "[[test_paper_runtime_ledger]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
capability_id: "paper-trade-admission"
parent_system: "[[Trading Engine]]"
implemented_by:
  - "[[Paper-Trading Runtime]]"
interfaces:
  - "[[Paper Runtime API]]"
---

# Paper-Trade Admission

## Definition

The capability to **admit** a pure Gold DecisionPacket (SCHEMA-011) for paper trading against explicit
runtime state — computing the stateful L3 guards [[Duplicate OK]] (`duplicate_ok`) + [[Operational OK]]
(`operational_ok`), echoing the snapshot guards, and emitting an `ADMIT`/`HOLD`/`REJECT`
[[Runtime Decision Record Schema]] (SCHEMA-012) plus a new ledger. A paper-only admission decision —
**not** a live order, fill, or broker instruction.

## Purpose

Give the gold lineage its first stateful step: turn a per-snapshot planning packet into a deduped,
operationally-gated admission, replay-safe via an explicit append-only ledger (ADR-009).

## Architecture Role

An L3 admission capability under [[Trading Engine]] (SYS-002), **downstream of** [[Gold Decision
Generation]] (CAP-020) — it consumes CAP-020's packet and adds the stateful admission layer. Realizes
the [[Pipeline Pattern]]; originates from [[Stateless Agent Architecture]] (KA-009).

**Complementary to, but distinct from, [[Guardrail Enforcement]] (CAP-008)** (Risk Control / SYS-003 —
hard risk-limit *enforcement*). CAP-021 is runtime/operational *admission* of a gold decision in the
Trading Engine (dedup + operational readiness). The two are distinct layers — a complete trade would
pass both — and CAP-021 does **not** link to, merge with, or supersede CAP-008 (recorded without a
coupling edge, per ADR-009). It is also permanently separate from the treasury [[Decision Making]]
(CAP-015) (ADR-004).

## Inputs

- A `GoldDecisionPacket` (SCHEMA-011) with forwarded `snapshot_guards` + `as_of`, from CAP-020.
- The prior `RuntimeLedger` (SCHEMA-013), a versioned `OperationalInput`, and a `RuntimePolicyConfig`.

## Outputs

- A `RuntimeDecisionRecord` (SCHEMA-012) + a new `RuntimeLedger` (SCHEMA-013), via [[Paper Runtime API]]
  (INT-010), gated by [[Runtime Admission Gate]] (GATE-003).

## Constraints

- **Wrap, not enrich-in-place** — the planning packet stays pure; guard outcomes live on the record.
- **Deterministic + stateful** — same (packet, prior ledger, operational input, policy) ⇒ identical
  record + ledger; state is explicit (no hidden memory / wall-clock).
- **Fail-closed** — WATCH/INDETERMINATE ⇒ HOLD; required-but-failed guard ⇒ REJECT.
- **Bounded-context hygiene** — never imports `src/risk`; never feeds Order Management (paper-only).

## Open Questions

- `implemented_by` → [[Paper-Trading Runtime]] (MOD-007), authored and tested.
- Computed cooldown, a live operational feed, and downstream execution/evaluation are deferred.

## Relationships

### Provides
- [[Paper Runtime API]]

### Consumes
- [[Gold DecisionPacket v0 Schema]]
- [[Runtime Ledger Schema]]

### Produces
- [[Runtime Decision Record Schema]]

### Implemented By
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_engine]]
- [[test_paper_runtime_ledger]]

### Depends On
- [[Gold Decision Generation]]

### Realizes
- [[Pipeline Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]

### Originates From
- [[Stateless Agent Architecture]]
