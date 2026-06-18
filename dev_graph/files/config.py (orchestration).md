---
type: file
canonical_id: FILE-032
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/config.py"
related_files: []
related_tests:
  - "[[test_chain_engine]]"
  - "[[test_chain_determinism]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/orchestration/config.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# config.py (orchestration)

## Definition

The captured cross-cutting inputs the chain orchestrator (MOD-010) forwards into the chain:
`DEFAULT_OPERATIONAL_INPUT` (the v0 configured operational-readiness artifact, PRED-007) and
`DEFAULT_GUARD_CONFIG` (the v0 captured GATE-001 hard-limit config, gate c.4). Both are **explicit captured
values**, never read live on the replay path.

## Purpose

Provide the explicit "operational status" and "guard config" seams so a future live operational feed or real
env hard-limits can replace them — without the core ever reading a venue probe, `os.environ`, or the
wall-clock on the replay path. Captured instances of existing types — **no** new contract / `*_version`.

## Architecture Role

The configured-input seam of [[Chain Orchestrator]] (MOD-010). `DEFAULT_OPERATIONAL_INPUT` is a *configured
assumption* ("for paper v0, assume the venue is open"), distinct from `paper_runtime.load_operational`'s
default-**closed** fallback for an absent/malformed file. Fingerprinted into the ledger for audit.

## Constraints

- Captured instances only (no new policy type / `*_version`); fail-closed safety preserved independently
  (paper-only, GATE-001 enforced, `withdrawal_disabled` PRED-005 always on).
- The replay path uses these captured values; the operational CLI may instead load real env limits.

## Implementation Notes

`DEFAULT_OPERATIONAL_INPUT = OperationalInput(GLD, tradeable=True, venue_open=True, as_of=None)`;
`DEFAULT_GUARD_CONFIG` mirrors the BENCH-004 `_GUARD_OK` paper limits so the guard APPROVES a v0 paper trade
(a non-fill on the real corpus is then attributable to the AVOID stance, not the guard).

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Validated By
- [[test_chain_engine]]
- [[test_chain_determinism]]
