---
type: artifact_schema
canonical_id: SCHEMA-012
status: active
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/gold/paper_runtime/models.py"
related_files:
  - "[[models.py (paper_runtime)]]"
related_tests:
  - "[[test_paper_runtime_engine]]"
  - "[[test_paper_runtime_determinism]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
schema_id: "runtime-decision-record"
schema_version: "0.1.0"
schema_path: "src/gold/paper_runtime/models.py"
validated_by:
  - "[[test_paper_runtime_engine]]"
  - "[[test_paper_runtime_determinism]]"
consumed_by: []
produced_by:
  - "[[Paper-Trading Runtime]]"
---

# Runtime Decision Record Schema

## Definition

The output contract of the paper-trading runtime's pure `evaluate()` (MOD-007): a frozen
`RuntimeDecisionRecord` that **wraps** a pure [[Gold DecisionPacket v0 Schema]] (SCHEMA-011) by
reference (`source_packet_id`) and carries the runtime's evaluated six-guard block plus a fail-closed
`ADMIT`/`HOLD`/`REJECT` verdict. It is a **net-new, permanently separate** artifact_schema with a new
canonical_id (ADR-009 §1) — a paper-trading admission decision, **not** a live order, broker
instruction, or the treasury Decision Packet (SCHEMA-004).

## Purpose

Realize the **wrap, not enrich-in-place** decision (ADR-009 §2): the planning packet stays pure
(`packet_id` is a content hash that excludes `guard_refs`), so the stateful guard outcomes
(`duplicate_ok`/`operational_ok` + echoes) live on this separate record. One record is emitted per
`evaluate()`, keyed for replay by `record_id`.

## Architecture Role

Output schema of MOD-007 [[Paper-Trading Runtime]], produced via [[Paper Runtime API]] (INT-010) and
governed by [[Runtime Admission Gate]] (GATE-003). It composes the L3 guard outcomes that
[[Duplicate OK]] (PRED-006), [[Operational OK]] (PRED-007), and the snapshot echoes produce. Per
ADR-003: a frozen stdlib dataclass with byte-stable `to_dict()`.

## Schema Definition

**RuntimeDecisionRecord**

| Field | Type | Notes |
|-------|------|-------|
| record_id | string | `paper-v0:` + 16 hex of SHA-256 over `source_packet_id` + `runtime_policy_fingerprint` + `as_of` + `operational_fingerprint` + `snapshot_guards_digest` + `prior_ledger_state_hash`. A **per-evaluation** identity (binds prior state), distinct from the snapshot/idempotency key. |
| record_schema_version | string | this contract-shape version (`0.1.0`) |
| source_packet_id | string | the wrapped pure packet (never embedded/mutated) |
| source_snapshot_id | string | the replay anchor (echoed from the packet) |
| decision_mode | enum | `paper_only` (fixed — explicit non-execution) |
| verdict | enum(Verdict) | `ADMIT` / `HOLD` / `REJECT` |
| triggered_guard | string \| null | the guard (or `actionable_stance`) that forced a non-ADMIT; `null` iff ADMIT |
| reason | string | deterministic, templated explanation |
| guard_outcomes | array&lt;GuardOutcome&gt; | the full six-guard block in canonical `_GUARD_NAMES` order; each `{name, passed (bool\|null), reason}` |
| runtime_policy_version | string | the runtime policy axis (governed; bumped on a require-flag change) |
| as_of | string \| null | echoed from the packet (= `snapshot.clock_ts`); never wall-clock |
| prior_ledger_state_hash | string | the ledger `state_hash` before this evaluation |
| new_ledger_state_hash | string | the ledger `state_hash` after appending this entry |
| non_execution_notice | string | fixed assertion: paper-trading admission, not an order |
| constraints | array&lt;string&gt; | invariants the record asserts it honored |

**GuardOutcome**: `name`, `passed` (`bool | null`), `reason` — the single (name, passed, reason)
source of truth. `supervisor_ok` carries `passed = null` (no supervisor — an explicit stub).

## Validation Rules

- **Fail-closed verdict** (`__post_init__`): `verdict == ADMIT` ⇔ `triggered_guard is null`; a non-ADMIT
  MUST name its triggering guard. `decision_mode` MUST be `paper_only`.
- **Determinism (ADR-009 §4):** same (`source_packet_id`, `runtime_policy` (version + fingerprint),
  `as_of`, operational input, snapshot-guards digest, prior ledger state) ⇒ identical record;
  `to_dict()` emits alphabetical keys with `guard_outcomes` as an ordered list → byte-stable JSON.
- No field depends on wall-clock, environment, network, randomness, or hidden state.

## Open Questions

- `consumed_by` is empty: a downstream paper-execution/evaluation layer is deferred (ADR-009 Non-Goals).
- The record does not echo `direction`/`regime` (referenced via `source_packet_id`); a future
  amendment may add them if a consumer needs them without the join.

## Relationships

### Produced By
- [[Paper-Trading Runtime]]

### Used By
- [[models.py (paper_runtime)]]

### Validated By
- [[test_paper_runtime_engine]]
- [[test_paper_runtime_determinism]]

### Consumes
- [[Gold DecisionPacket v0 Schema]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Stateless Agent Architecture]]
