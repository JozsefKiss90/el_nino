---
type: file
canonical_id: FILE-021
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-09
updated: 2026-06-09
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

The L3 guard predicates: `duplicate_ok` (PRED-006), `operational_ok` (PRED-007), and the snapshot
echoes `data_ok`/`freshness_ok`/`cooldown_ok`. Each is a pure function returning `(passed, reason)`.

## Purpose

Compute the two stateful L3 guards + echo the packet's forwarded snapshot guards — the inputs to the
admission verdict.

## Implementation Notes

`duplicate_ok` passes iff `not prior_ledger.has_admit(packet.source_snapshot_id)` (once-ever).
`operational_ok` checks instrument match + tradeable/venue_open/not-halt/not-degraded. Echoes read
`packet.snapshot_guards` (default-closed when absent). The `(passed, reason)` shape and short-circuit
conjunction mirror the Risk Control predicates — **pattern only; never imported** (Context Map /
ARCH-001 bounded-context hygiene). `supervisor_ok` is a `None` stub added by the engine, not here.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_guards]]
