<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 2 — Day-scoped guard inputs via snapshot `as_of`

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (i). Governed by ADR-014.

## What to build

The guard's "daily" inputs are mislabeled today: `daily_pnl` is all-time (≈0 forever on a buy-only path) and `trades_today` is the lifetime fill count, so `max_trades_per_day` silently becomes a lifetime cap that blocks forever after enough fills.

Thread the snapshot `as_of` into the guard-request builder and add an additive `as_of` field on the execution entry (SCHEMA-015), then **day-scope** both guard inputs (`daily_pnl`, `trades_today`) — mirroring the runtime cooldown discipline that keys off the snapshot `as_of`, never wall-clock. This is a cross-layer **mirror** of the discipline, not an import of the runtime predicates. Threading any **live** broker read into this shared deterministic guard input is forbidden (it would contaminate the replay key) — only the snapshot `as_of` is threaded here.

Re-pin the execution + chain benchmark goldens (the new field changes the replay key); old goldens stay byte-reproducible under the prior version.

## Acceptance criteria

- [ ] The guard-request builder receives the snapshot `as_of`; `daily_pnl` and `trades_today` are computed day-scoped to that `as_of`, not lifetime.
- [ ] `max_trades_per_day` behaves as a genuine per-day cap (a new trading day resets the count), asserted by tests across snapshots spanning two days.
- [ ] SCHEMA-015 execution entry gains an `as_of` field additively; existing portfolio states still deserialize.
- [ ] No live broker read is folded into the guard request; the day-scoping derives only from snapshot data.
- [ ] Execution + chain benchmark goldens are re-pinned for this versioned key change and are otherwise byte-identical; the determinism suite is green.

## Blocked by

None - can start immediately.
