---
type: file
canonical_id: FILE-021
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/paper_runtime/predicates.py"
related_files: []
related_tests:
  - "[[test_paper_runtime_guards]]"
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
file_path: "src/gold/paper_runtime/predicates.py"
language: "python"
module: "[[Paper-Trading Runtime]]"
owns: []
used_by: []
---

# predicates.py (paper_runtime)

## Definition

The L3 guard predicates: `duplicate_ok` (PRED-006), `operational_ok` (PRED-007), the **computed**
`cooldown_ok` (PRED-008, v0.2.0), and the snapshot echoes `data_ok`/`freshness_ok`. Each is a pure
function returning `(passed, reason)`.

## Purpose

Compute the stateful L3 guards (dedup, operational, cooldown) + echo the packet's forwarded
data/freshness guards — the inputs to the admission verdict.

## Implementation Notes

`duplicate_ok` passes iff `not prior_ledger.has_admit(packet.source_snapshot_id)` (once-ever).
`operational_ok` checks instrument match + tradeable/venue_open/not-halt/not-degraded. `cooldown_ok`
(**v0.2.0, computed** — replaces the prior echo) reads `prior_ledger.last_admit_as_of(exclude_self)` and
the snapshot `as_of` (via `_parse_as_of`): passes iff the gap ≥ `config.cooldown_window_hours`;
fail-closed on missing/unparseable/negative-gap timing; deterministic (never wall-clock). `data_ok`/
`freshness_ok` echoes read `packet.snapshot_guards` (default-closed when absent). The `(passed, reason)`
shape and short-circuit conjunction mirror the Risk Control predicates — **pattern only; never imported**
(Context Map / ARCH-001 bounded-context hygiene). `supervisor_ok` is a `None` stub added by the engine.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_guards]]
