<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 1 — GLD execution price reference (`exec_ref_gld_price`)

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (i). Governed by ADR-014.

## What to build

Replace the wrong execution price reference with a **source-pluggable GLD share-price seam**, `exec_ref_gld_price`, with one seam and two implementations:

- **Simulator / replay path** → a **versioned deterministic derived proxy**: `exec_ref_gld_price = gold_price_proxy × oz_per_share`, where `gold_price_proxy` is the existing real XAUUSD spot series ($/oz) and `oz_per_share` is a versioned constant. Derived from the snapshot per the replay discipline — never a live read. Simulator slippage stays a model number (flat `slippage_bps` against the derived ref) and is labeled synthetic/derived.
- **Live Alpaca path** → the **real live GLD mark** (read live, non-replayable), with the reference timestamp pinned + labeled (submit/EOD vs open/routing).

Sever `gold_price` (spot, $/oz) from execution — it stays a pure decision-context feature. After this change `slippage_bps` is GLD-vs-GLD and `avg_cost`/`unrealized_pnl` are marked in $/share, not $/oz.

Add the additive SCHEMA-014 fields this requires (`exec_ref_gld_price`, `exec_ref_gld_price_ts`, `exec_ref_gld_price_basis`) and introduce a dedicated `exec_price_source_version` axis (or bump `execution_policy_version` if the operator prefers one axis). Re-pin the execution-layer and chain benchmark goldens (both pin the instrument price today); old goldens stay byte-reproducible under the prior version. The seam must be shaped so the optional real-GLD-share-price snapshot ingest plugs in later with zero rework.

## Acceptance criteria

- [ ] An `exec_ref_gld_price` resolver returns the **derived proxy** (`gold_price_proxy × oz_per_share`) on the sim/replay path and the **live GLD mark** on the Alpaca path, asserted by tests at the seam.
- [ ] `gold_price` is no longer forwarded as the execution price anywhere; it remains available as a decision-context feature.
- [ ] SCHEMA-014 gains `exec_ref_gld_price`, `exec_ref_gld_price_ts`, `exec_ref_gld_price_basis` additively; existing simulator records still deserialize.
- [ ] A versioned price-source axis (`exec_price_source_version` or an `execution_policy_version` bump) is recorded on the execution record; old goldens remain byte-reproducible under the prior version.
- [ ] Execution + chain benchmark goldens are re-pinned for this versioned key change and are otherwise byte-identical; the determinism suite is green.
- [ ] The simulator portfolio stays accumulate-only with `realized_pnl == 0.0`; its `unrealized_pnl` is labeled non-strategic.
- [ ] `oz_per_share` is a versioned constant; the live-mark reference timestamp is pinned and labeled (submit/EOD vs open/routing).

## Blocked by

None - can start immediately.
