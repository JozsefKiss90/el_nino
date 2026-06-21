---
type: file
canonical_id: FILE-041
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "ops/actions.py"
related_files:
  - "[[core.py (ops)]]"
  - "[[audit.py (ops)]]"
related_tests:
  - "[[test_ops_actions]]"
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
file_path: "ops/actions.py"
language: "python"
module: "[[Operations Control Plane]]"
owns: []
used_by:
  - "[[app.py (ops)]]"
---

# actions.py (ops)

## Definition

The **Tier-2 safe (non-destructive) actions** (ADR-013 §3): `run_chain_now`, `rerun_calibration_readiness`,
`resync_neo4j`, plus the `SAFE_ACTIONS` registry. Each reuses a governed function, writes one audit
entry, and returns a structured `ActionResult` — **never raising**.

## Purpose

Let the operator run the routine, deterministic, idempotent operations on demand, audited but without an
extra confirm modal.

## Architecture Role

Sits between the TUI and the governed `src/` functions; the safety is **structural** (no live port/feed
is reachable here).

## Constraints

`run_chain_now` is hardwired to the deterministic `SimulatedBrokerAdapter` + `MarketCalendarFeed` (no
parameter/env can substitute a live port); the calibration re-run reuses the MOD-009 labeler (never bumps
a `*_version`); the Neo4j re-sync is an idempotent re-projection. Audit writes are guarded (the action
survives an audit-write failure); the full audit surface is secret-redacted.

## Implementation Notes

`_finish` builds + writes the audit entry (guarded) and redacts `args_summary`/`summary`/`detail`.
Subprocess actions take an injectable `runner` (the `ops/proc.py` shared helper is folded into the
[[Operations Control Plane]] module). On a successful chain run the summary carries the
verdict/direction/fill + state hashes.

## Relationships

### Depends On
- [[Operations Control Plane]]
- [[core.py (ops)]]
- [[audit.py (ops)]]

### Validated By
- [[test_ops_actions]]

### Constrained By
- [[No Wiki Mutation]]

### Justified By
- [[ADR - Operations Control Plane]]
