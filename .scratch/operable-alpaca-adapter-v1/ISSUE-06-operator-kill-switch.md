<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 6 — Operator kill switch (audited Tier-2 halt)

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (ii). Governed by ADR-014.

## What to build

Give the operator one governed mechanism to stop execution: an **audited Tier-2 halt** action that writes `halt=True`. The operational feed already **honors** `halt` (the read path exists and is captured for replay), so this slice delivers the **write/governance** side — a Tier-2 governed action that flips the halt flag with an audit record, no new read path and no standalone rate limiter.

## Acceptance criteria

- [ ] An audited Tier-2 action sets `halt=True` and writes an audit record for the action.
- [ ] With `halt=True`, the operational feed refuses execution on the next cycle (existing honor path), verified by a test.
- [ ] The halt is the single chosen governed kill mechanism (no second mechanism, no standalone rate limiter introduced).
- [ ] The decision/observation/labeling chain behavior under halt matches the existing operational-feed semantics (no regression to the captured-for-replay halt path).

## Blocked by

None - can start immediately.
