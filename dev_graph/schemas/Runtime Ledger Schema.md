---
type: artifact_schema
canonical_id: SCHEMA-013
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
  - "[[test_paper_runtime_ledger]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
schema_id: "runtime-ledger"
schema_version: "0.1.0"
schema_path: "src/gold/paper_runtime/models.py"
validated_by:
  - "[[test_paper_runtime_ledger]]"
consumed_by:
  - "[[Paper-Trading Runtime]]"
produced_by:
  - "[[Paper-Trading Runtime]]"
---

# Runtime Ledger Schema

## Definition

The append-only, self-describing state artifact of the paper-trading runtime (MOD-007): a frozen
`RuntimeLedger` of `LedgerEntry` records, keyed by `source_snapshot_id`. It is **both** an input and an
output of `evaluate()` (the runtime threads `prior_ledger -> new_ledger`), making the stateful runtime
a pure function of explicit values (ADR-009 §4/§5).

## Purpose

Hold the runtime's dedup/admission state as an explicit value, not ambient process memory (the KA-009
Wake-Execute-Sleep / file-mediated discipline). **Self-describing** so the ledger alone is sufficient
replay state: each entry records everything needed to reproduce its own decision.

## Architecture Role

Consumed and produced by MOD-007 [[Paper-Trading Runtime]]. Persisted/loaded only at the IO boundary
shell (`runtime.py`), never inside the pure core. Per ADR-003: frozen stdlib dataclasses.

## Schema Definition

**RuntimeLedger**: `ledger_schema_version` (string), `entries` (ordered array&lt;LedgerEntry&gt;).
Methods: `empty()`, `has_admit(snapshot_id)` (prior **ADMIT** of that id — the once-ever dedup test),
`append(entry)` → a NEW frozen ledger (`seq = len(entries)`), `state_hash()` (SHA-256 over canonical
JSON — the ledger identity that threads into `record_id`).

**LedgerEntry** (self-describing)

| Field | Type | Notes |
|-------|------|-------|
| source_snapshot_id | string | the idempotency key (the replay anchor) |
| source_packet_id | string | the packet that produced this entry |
| as_of | string \| null | echoed from the packet (deterministic clock) |
| verdict | string | `ADMIT` / `HOLD` / `REJECT` |
| triggered_guard | string \| null | the guard that forced a non-ADMIT |
| snapshot_guards_digest | string | SHA-256 of the packet's forwarded `snapshot_guards` (or `null`) |
| operational_fingerprint | string | the `OperationalInput.fingerprint()` for this evaluation |
| seq | int | length-derived insertion index — stable across persist/reload |

## Validation Rules

- **Append-only**: `append` returns a new ledger; existing entries are never mutated or deleted.
- **Idempotency**: `has_admit` counts only prior `ADMIT` entries of a `source_snapshot_id`; a prior
  HOLD/REJECT does not block a later genuine admission (PRED-006 once-ever semantics).
- **Determinism (ADR-009 §5)**: `to_dict()` emits entries in insertion order with alphabetical entry
  keys; `state_hash()` over `json.dumps(..., sort_keys=True, separators=(",",":"))`. Replaying the same
  sequence from the same starting ledger yields a byte-identical ending ledger + `state_hash`.
- `from_dict` is fail-closed (a malformed entry raises `RuntimeContractError`).

## Open Questions

- v0 is a single local JSON ledger (one instrument, `GLD`). Multi-instrument / alternative persistence
  backends are deferred (ADR-009 Non-Goals).

## Relationships

### Produced By
- [[Paper-Trading Runtime]]

### Consumed By
- [[Paper-Trading Runtime]]

### Used By
- [[models.py (paper_runtime)]]

### Validated By
- [[test_paper_runtime_ledger]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Stateless Agent Architecture]]
