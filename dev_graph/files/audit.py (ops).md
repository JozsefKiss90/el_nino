---
type: file
canonical_id: FILE-043
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/audit.py"
related_files: []
related_tests:
  - "[[test_ops_audit]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
file_path: "ops/audit.py"
language: "python"
module: "[[Operations Control Plane]]"
owns: []
used_by:
  - "[[actions.py (ops)]]"
  - "[[gated.py (ops)]]"
  - "[[core.py (ops)]]"
---

# audit.py (ops)

## Definition

The **append-only audit log** for the Operations Control Plane (ADR-013 §7): `make_entry` /
`write_entry` / `append_audit` / `read_audit` over `runtime/ops/audit_log.jsonl`.

## Purpose

Record one entry — timestamp, action, args-summary, result, ok — for every mutating/live console action,
and provide the read surface the Log pane tails.

## Architecture Role

Stdlib-only leaf module (no Textual, no `src/` import). Imported by both action tiers (write side) and by
`ops/core.py` (read side, `read_audit`).

## Constraints

Append-only; **ASCII** JSON lines (`ensure_ascii=True`) so the file is encoding-safe on any console and
cannot carry raw non-ASCII; entries must contain **no credential value** (callers pass only safe
summaries; the surface is secret-redacted before it reaches here). It is an operational journal of console
actions, never a second source of truth for pipeline state ([[No Wiki Mutation]] / ADR-013 §11).

## Implementation Notes

`make_entry` builds the entry with no IO (so a caller can hold it even if the write fails); `write_entry`
appends (may raise `OSError` — callers guard); `read_audit` tails N entries and skips malformed lines.
The clock is injectable for deterministic test timestamps.

## Relationships

### Depends On
- [[Operations Control Plane]]

### Validated By
- [[test_ops_audit]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
