<!-- triage: ready-for-agent -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# PRD — Operable Alpaca Paper Execution Adapter v1

> Status: **ready-for-agent**. Derived from **ADR-014** (Accepted as the binding constraint set for this
> work; this PRD does not re-open its decisions). Implement under ADR-014's invariants; where this PRD and
> ADR-014 appear to differ, ADR-014 governs.

## Problem Statement

The Layer-3 chain runs end-to-end today and persists an append-only runtime ledger plus
portfolio/execution state, but the live Alpaca **paper** execution adapter is **built-but-dormant and not
operable**. As the operator, I cannot actually let the system place paper orders against a real broker,
because the moment a LONG fired the live path would misbehave in several concrete ways:

- The adapter submits a one-shot market BUY and then **raises unless the synchronous response says
  `filled`** — but real Alpaca market orders come back `accepted`/`pending_new` and fill **asynchronously**,
  so the live path would raise on essentially every real order.
- There is **no startup reconcile**: the adapter never reads broker positions, account, open orders, or
  assets before acting, so it would blind-buy and could double-act across runs or after a crash.
- The **execution price reference is wrong**: the chain forwards `gold_price` (gold spot, ~$4,624/oz) into
  a GLD **share** order (~$300–600/share), producing nonsense slippage (~−9,300 bps) and marking
  `avg_cost`/`unrealized_pnl` in $/oz against GLD share units, on **both** the simulator and the live path.
  It is latent only because no LONG fires today.
- The adapter is **LONG-only and buy/accumulate-only**: there is no SELL, no `FLAT→exit`, no realized P&L.
- There is **no deterministic idempotency for the live broker** (no `client_order_id`), **no cash-cap**,
  **no typed error handling** (a 4xx `HTTPError` propagates raw and the broker reject body is discarded),
  **no 429/`Retry-After` handling**, **no account-status gate**, and **no operator kill switch**.
- The guard inputs are **mislabeled "daily"**: `daily_pnl` is all-time (and ≈0 forever on a buy-only path)
  and `trades_today` is the **lifetime** fill count, so `max_trades_per_day` silently becomes a lifetime cap
  that blocks forever after enough fills.

I need the dormant stub turned into an **operable** paper adapter — reconcile-then-act, `FLAT→exit`,
deterministic idempotency, cash-cap, and a queued/partial/uncertain state machine, with the GLD price
reference fixed — **without** disturbing the deterministic replay spine, **without** a second source of
truth, and **without** weakening the determinism / paper-only / fail-closed boundary.

## Solution

Add the operability as an **additive delta** in two clean buckets, exactly as ADR-014 specifies:

- **(i) Contained shared changes (versioned).** Fix the execution price reference to a **source-pluggable
  GLD share price** (`exec_ref_gld_price`); thread the snapshot `as_of` into the guard so the "daily" inputs
  are actually day-scoped; add a cheap `assert port.replayable` fence on the canonical entrypoints; and add
  the additive SCHEMA-014/015 fields these require. Each change is additive and versioned; old goldens stay
  byte-reproducible; the execution and chain benchmarks re-pin where a replay key changes.

- **(ii) Live-plug-only additions.** Everything broker-realistic — a **separate non-replayable
  `operate_live` entrypoint**, reconcile-then-act, the SELL-fold and realized P&L, the
  QUEUED/PARTIAL/EXECUTION_UNCERTAIN state machine, the cash-cap against settled cash, `client_order_id`
  idempotency, the reconcile-heal entry, and a side/order-based adapter — lives **inside the default-OFF,
  non-replayable Alpaca plug**, reached **only** through `operate_live`, never through the canonical
  `fill()` port or the deterministic core.

The deterministic simulator, the pure cores, the orchestrator, and the replay benchmarks stay
**structurally unchanged** as the canonical replay path (re-pinned only for the two versioned key changes).
The live path persists to **physically separate** ledger/portfolio files. The operator enables the live
plug only via the existing ADR-013 ops-console gated-live action (confirm + audit + paper-host
precondition), past the `assert port.replayable` fence. When execution is refused for safety, the
decision/observation/labeling chain keeps running, so the calibration corpus never stalls.

## User Stories

1. As the operator, I want the live adapter to treat `accepted`/`pending_new`/`new` order responses as a
   normal **QUEUED** state, so that a real async market order does not raise and abort the run.
2. As the operator, I want order fills resolved by reading broker positions and orders on the next
   reconcile (never from the synchronous POST echo), so that asynchronous fills are recorded correctly.
3. As the operator, I want a **mandatory startup reconcile** before any new action, so that the system
   always acts on the broker's actual position rather than a blind assumption.
4. As the operator, I want the adapter to compute a **delta** to a cash-capped target and act only on that
   delta, so that it never blind-buys and never double-acts across runs.
5. As the operator, I want an **open-orders-aware** reconcile where a queued order that already covers the
   target **nets to NO_ACTION**, so that a catch-up/backfill/multi-run with more than one ADMITting snapshot
   between two market opens does not stack duplicate orders.
6. As the operator, I want a deterministic `client_order_id` so that a **same-order duplicate submit** is
   rejected by the broker (422) idempotently, so that a retry never creates a second order.
7. As the operator, I want the **broker treated as authority for position truth** and the **local portfolio
   state as authority for decision lineage + idempotency**, so that each source owns what it is actually
   trustworthy for.
8. As the operator, I want any **unexplained divergence** between broker and local state to
   **terminal-refuse execution only** (no auto-flatten), so that evidence is preserved and a real-money
   instinct never destroys the audit trail.
9. As the operator, I want divergence to **heal via an append-only reconcile entry** (observed broker qty +
   avg entry price + a reconcile marker), so that the broker's truth is recorded without faking an
   execution record.
10. As the operator, I want adopting an unexplained non-zero broker position to be an **ops-console-gated
    governed action**, never automatic, so that I stay in control of what the system treats as "mine".
11. As the operator, I want the **decision/observation/labeling chain to keep running even when execution is
    refused**, so that the calibration corpus does not stall on an execution problem.
12. As the operator, I want the live cash-cap bound to the **literal settled-cash field** (never any
    `*_buying_power`), so that "no margin" is structural on any account type, even a margin-default paper
    account.
13. As the operator, I want the **effective reconcile target = min(configured notional, settled cash)**, so
    that the reconcile loop converges and never tries to exceed available cash.
14. As the operator, I want the adapter to honor GLD **fractionability** (`fractionable: true` → notional
    market+day order; `false` → integer shares = floor(cash-capped notional / live submit mark)), so that
    orders are valid for the instrument.
15. As the operator, I want a **side/order-based** live adapter (submit market buy / submit market sell)
    driven by the reconcile delta — LONG→buy, FLAT→sell, AVOID/WATCH→NO_ACTION resolved **before** the
    adapter — so that exits actually happen and stances map to broker actions.
16. As the operator, I want a **live SELL-fold** that realizes P&L (`realized_pnl += qty × (exit_fill −
    avg_cost)`; position → 0) on the live path only, so that exits produce real realized P&L without
    teaching the simulator to sell.
17. As the operator, I want the **simulated/replay portfolio to stay accumulate-only** with `realized_pnl`
    fixed at 0.0, so that the determinism vehicle and the benchmarks are never disturbed.
18. As the operator, I want the simulator's accumulate-only `unrealized_pnl` **labeled non-strategic** and
    **excluded from every performance / ops-console reading**, so that a plausible-but-wrong number never
    misleads me.
19. As the operator, I want the execution price/slippage reference to be the **GLD share price**
    (`exec_ref_gld_price`), so that slippage is GLD-vs-GLD and positions are marked in $/share rather than
    $/oz.
20. As the operator, I want the price reference to be **source-pluggable**: a **versioned deterministic
    derived proxy** (`gold_price_proxy × oz_per_share`) on the simulator/replay path, and the **real live
    GLD mark** on the Alpaca path, so that replay stays deterministic while the live path uses a real mark.
21. As the operator, I want the live GLD reference **timestamp pinned and labeled** (submit/EOD mark vs
    open/routing mark), so that I can tell overnight-gap slippage from pure execution slippage.
22. As the operator, I want `gold_price` (spot, $/oz) **severed from execution** and kept as a pure
    decision-context feature, so that a decision feature is never silently reused as an execution price.
23. As the operator, I want the guard's `daily_pnl` and `trades_today` inputs **day-scoped by the snapshot
    `as_of`** (mirroring the runtime cooldown discipline), so that `max_trades_per_day` is a genuine daily
    cap rather than a lifetime cap that blocks forever.
24. As the operator, I want a cheap **`assert port.replayable`** on the canonical `run_once`/`run_sequence`,
    so that a non-replayable broker port is **structurally barred** from the replay entrypoint and reachable
    only through `operate_live`.
25. As the operator, I want the live path to thread a **separate (ledger, portfolio) pair**, physically
    distinct from the canonical replay files, so that live broker state never contaminates the deterministic
    files.
26. As the operator, I want a **typed error path**: wrap the order call in try/except for HTTP/URL errors,
    parse the broker reject body, route to EXECUTION_UNCERTAIN/halt, and persist the raw payload, so that no
    reject is silently dropped and I can diagnose insufficient-BP / wash / forbidden rejects.
27. As the operator, I want **429/`Retry-After`** honored with no blind resend, so that rate limits are
    respected even at low volume.
28. As the operator, I want a **startup account-status gate** requiring
    `status == "ACTIVE" && !trading_blocked && !account_blocked`, so that the system refuses to trade on a
    blocked account.
29. As the operator, I want a **PARTIAL** state when `filled_qty < requested` (corrected on the next
    reconcile), so that partial fills are tracked rather than mistaken for full fills.
30. As the operator, I want a timeout / no-response to become **EXECUTION_UNCERTAIN** and **halt that
    instrument** (no blind retry), so that uncertainty never triggers a duplicate order.
31. As the operator, I want an **audited Tier-2 halt kill switch** that writes `halt=True` (which the
    operational feed already honors), so that I have one governed mechanism to stop execution.
32. As the operator, I want **broker-traceability fields** (`alpaca_order_id`, `raw_payload`,
    `client_order_id`) persisted on the execution record, so that every live order has an audit lineage.
33. As the operator, I want the new execution statuses **{QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION}**
    representable on the execution record, so that the live state machine is captured in the persisted state.
34. As the operator, I want the **existing parsed-hostname env guard kept** and the roadmap's `"paper-api"
    in base_url` substring check **rejected**, so that the credential-exfil bypass is never reintroduced.
35. As the operator, I want **no new SQLite stores** (no `fill_record`, no `scorecard` table); execution
    outcomes stay on the additive SCHEMA-014/015 fields and per-regime accuracy stays in the calibration
    labeler, so that there is never a second source of truth.
36. As the operator, I want the live order model to be **market + time_in_force=day** (queue-to-next-open),
    not OPG and not broker-side conditional orders, so that exits stay in our deterministic evaluator.
37. As the operator, I want the **once-ever idempotency guard bifurcated by path** — `has_execution` remains
    the sole idempotency on the sim/replay path; the live path additionally owns reconcile-delta +
    open-orders awareness + `client_order_id` dedup — so that crash-consistency is preserved and the live
    path gets the extra protections without weakening the sim path.
38. As the operator, I want the live plug to remain **default-OFF**, enabled only via the ADR-013 gated-live
    action (confirm + audit + paper-host precondition), so that nothing reaches the network without an
    explicit governed enable.
39. As the operator, I want all simulator BENCH goldens to **re-pin only** for the two versioned key changes
    (the price source and the `as_of` field) and otherwise stay byte-identical, so that I can trust the
    determinism suite still proves determinism.
40. As a future maintainer, I want the optional **real-GLD-share-price snapshot ingest** to plug into the
    same `exec_ref_gld_price` seam with zero rework, so that a fidelity upgrade later requires no
    re-architecture.
41. As the operator, I want **live-money execution, short, margin, a second instrument, and
    confidence-scaled sizing** to remain structurally out of scope, so that v1 stays a paper-only, long-or-
    flat, fixed-size adapter.

## Implementation Decisions

> Modules and contracts are named by concept; concrete file paths are deliberately omitted (they drift).
> The two buckets below mirror ADR-014 §5 (shared/versioned) and §6 (live-plug-only).

### Architecture

- **Additive delta, simulator-unchanged, broker-realism quarantined.** The deterministic spine — the pure
  execution core, the Simulated Broker Adapter, the Chain Orchestrator, the Paper-Trading Runtime, and the
  execution/chain replay benchmarks — stays structurally unchanged as the canonical replay path. All broker
  realism lives inside the **default-OFF, non-replayable Alpaca plug**, reached through a **separate
  non-replayable `operate_live` entrypoint**, never through the canonical `fill()` port.
- **Inherited, not re-decided:** the ADR-011 gate-(f) boundary; the **parsed-hostname env guard**; the
  `ExecutionPort` Protocol (`fill()` + `mode`/`replayable`) + pure execution core + Simulated Broker Adapter
  as the canonical replay path; the runtime ledger schema; the append-only-JSON once-ever idempotency
  (`source_snapshot_id` / `has_execution`); the Chain Orchestrator; the Paper-Trading Runtime (incl. the
  snapshot-`as_of` cooldown predicate); the calibration labeler + methodology as the observation/performance
  gate; the ADR-013 ops console as the gated-live enable surface; fixed size (sizing deferred).

### Bucket (i) — Contained shared changes (versioned)

- **GLD price reference — `exec_ref_gld_price`, source-pluggable (one seam, two implementations).**
  - Simulator / replay path → a **versioned deterministic derived proxy**:
    `exec_ref_gld_price = gold_price_proxy × oz_per_share`, where `gold_price_proxy` is the existing real
    XAUUSD spot series ($/oz) and `oz_per_share` is a **versioned constant** (GLD's approximate gold content
    per share). Derived from the snapshot per the replay discipline — **never a live read** on the replay
    path. Simulator slippage stays a model number (the flat `slippage_bps` applied to the derived ref) and
    is **labeled** synthetic/derived.
  - Live Alpaca path → the **real live GLD mark** (read live, non-replayable). Slippage stays "recorded, not
    modelled" against the orchestrator's mark — v1 changes only *which* mark (the GLD mark). The reference
    timestamp is **pinned + labeled** (submit/EOD vs open/routing); the paper-account no-liquidity-impact
    caveat is noted.
  - `gold_price` (spot, $/oz) is **severed from execution** and stays a pure decision-context feature.
    After this change `slippage_bps` is GLD-vs-GLD and `avg_cost`/`unrealized_pnl` are marked in $/share.
  - **Versioning:** introduce a dedicated `exec_price_source_version` axis (distinct from the current
    execution-policy fingerprint fields and from the fill-model version), or an `execution_policy_version`
    bump if the operator prefers one axis. Re-pin the **execution-layer benchmark** and the **chain
    benchmark** (both pin the instrument price at 4624.5 today). Old goldens stay byte-reproducible under
    the prior version.

- **Daily-guard `as_of` threading.** Thread the snapshot `as_of` into the guard-request builder and add an
  **`as_of` field on the execution entry** (a portfolio-state schema change), then **day-scope** both guard
  inputs (`daily_pnl`, `trades_today`) — mirroring the runtime cooldown discipline that keys off the
  snapshot `as_of`, never wall-clock. This is a cross-layer **mirror** of the discipline, not an import of
  the runtime predicates. Re-pin the execution + chain benchmarks (the new field changes the replay key).

- **`assert port.replayable` precondition + separate ledger/portfolio paths.** The `replayable` flag already
  exists on the port; what is net-new is the **enforcing precondition** — a cheap `assert port.replayable`
  on the canonical `run_once` and `run_sequence`, so a non-replayable broker port is structurally barred
  from the replay entrypoint and reachable only via `operate_live`. The live path must thread a **separate
  (ledger_path, portfolio_path) pair**, physically distinct from the canonical replay files.

- **Additive SCHEMA-014 / SCHEMA-015 fields (no new table).**
  - **Execution record (SCHEMA-014)** gains, additively: `exec_ref_gld_price` (+ `exec_ref_gld_price_ts` and
    an `exec_ref_gld_price_basis` label for the pinned/labeled live reference timestamp), `client_order_id`,
    `alpaca_order_id`, `raw_payload`, and the statuses `{QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION}`.
  - **Portfolio state / execution entry (SCHEMA-015)** gains `as_of`, plus a **new append-only
    reconcile-entry kind** — distinct from the execution entry, because a reconcile observation has no
    `source_record_id` and no `guard_result`.
  - All additive + versioned; simulator records keep working; no SQLite, no second source of truth.

### Bucket (ii) — Live-plug-only additions (all behind `operate_live`)

- **Parallel non-replayable live entrypoint.** `live_runtime.operate_live`, mirroring the chain `run_once`,
  is the only path to the live plug. It **reuses** the deterministic decision + the GATE-001 guard + the
  idempotency layer; **only broker mechanics are new**. `ExecutionPort.fill()` stays the LONG-only replay
  contract, untouched, exercised only by the simulator.

- **Reconcile authority, heal, idempotency bifurcation, discrepancy.**
  - Authority split: **broker = position truth**; **local portfolio state = decision lineage + idempotency**.
  - Reconcile-then-act: read positions (∪ open orders), compute the delta to the cash-capped target, act on
    the delta — never a blind buy. Mandatory startup reconcile before any new action.
  - Heal via a **new append-only reconcile-entry kind** (observed broker qty + avg entry price + a reconcile
    marker), not an execution record/entry. Live-path-only.
  - Idempotency **bifurcation, not demotion**: `has_execution(source_snapshot_id)` stays the sole idempotency
    on the sim/replay path; the live path additionally owns reconcile-delta + open-orders awareness +
    `client_order_id` 422 dedup.
  - Discrepancy → **terminal-refuse execution only** (no auto-flatten). "Refuse" scopes to execution only —
    the decision/observation/labeling chain keeps running. Adopting an unexplained non-zero broker position
    is a **governed adopt** (ops-console-gated), never automatic.

- **In-flight / queue window ownership.** Open-orders-aware reconcile owns the **cross-snapshot queue**:
  `delta = target − position − Σ(expected-lineage open-order qty)`; a queued order that nets to zero →
  **NO_ACTION**. `client_order_id` 422 owns **same-order duplicate-submit only**. An **unexpected** open
  order (wrong qty/side or unknown `client_order_id`) is **not netted** → it is a discrepancy →
  terminal-refuse → governed adopt.

- **Sizing + cash-cap.** Cash-cap binds to the **literal settled-cash field** from the account read (never
  any `*_buying_power`). Fixed-notional is **live-plug-only** (the sim keeps fixed-qty `default_size`; a
  notional on the sim path would change the state hash and break the benchmarks — accept the sim(fixed-qty)
  vs live(fixed-notional) asymmetry: it diverges P&L *magnitude*, not *direction*). Effective reconcile
  target = `min(configured_notional, settled_cash)`. **Fractionable:** `true` → notional market+day; `false`
  → integer shares = `floor(cash_capped_notional / live_submit_mark)`.

- **Accumulate-only sim, sell-fold, side-based adapter.** The simulated/replay portfolio is a buy-only
  determinism vehicle (`realized_pnl` stays 0.0; its `unrealized_pnl` is a labeled non-strategic artifact
  kept out of all performance/ops readings). The **sell-fold is live-only**, in `live_runtime`, never in the
  pure core: `realized_pnl += qty × (exit_fill − avg_cost); position → 0`. The live adapter is
  **side/order-based** (`submit_market_buy` / `submit_market_sell`) driven by the reconcile delta —
  LONG→buy, FLAT→sell, AVOID/WATCH→NO_ACTION (resolved before the adapter). The v0 `fill(direction)`
  (LONG-only, raises on non-LONG) is **superseded on the live path** — repurpose/remove it, do not extend
  it.

- **Order/state machine + typed error handling.**
  - Order model: market + `time_in_force=day` (queue-to-next-open). Not OPG, not broker-side conditional
    orders.
  - State machine: `accepted`/`pending_new`/`new` = **QUEUED** (not an error, not resent; next reconcile
    sees the fill) — this fixes the v0 sync-fill raise. Fills resolve via positions + orders reads, never
    the synchronous POST echo. `filled_qty < requested` = **PARTIAL** (next reconcile corrects); timeout /
    no-response = **EXECUTION_UNCERTAIN** + halt that instrument (no blind retry); auth error = halt.
  - Typed error handling: wrap the order call in try/except for HTTP/URL errors, parse the reject body,
    route to EXECUTION_UNCERTAIN/halt, and persist `raw_payload` (v0 discards it).
  - 429 / `Retry-After`: honor it, no blind resend; 429 is part of the state machine.
  - Account-status gate: startup reconcile requires `status == "ACTIVE" && !trading_blocked &&
    !account_blocked`.
  - Operator kill switch: an **audited Tier-2 halt** that writes `halt=True` (the operational feed already
    honors `halt`) — the single chosen governed kill mechanism.

### Interfaces / contracts

- **Broker port (the primary live seam).** The thin broker Protocol the live adapter depends on widens from
  `submit_market_buy` to the full surface the reconcile loop needs: `submit_market_buy`, `submit_market_sell`,
  `get_positions`, `get_open_orders`, `get_orders`, `get_account`, `get_asset`. Tests inject a stub for all
  of it — never the network.
- **`operate_live` entrypoint.** Mirrors the chain `run_once` signature shape (snapshot, **separate**
  ledger/portfolio paths, configs, port), but is the non-replayable live path; it performs the startup
  reconcile, runs the reused decision + guard + idempotency layer, drives the side-based adapter on the
  reconcile delta, and persists to the separate files. It must never be reachable from `run_once`/
  `run_sequence` (the `assert port.replayable` fence enforces this).

### Empirical preconditions (close before any live code runs)

- B1: `client_order_id` length/charset accepted by the broker.
- B2: GLD `fractionable` flag value.
- B3: the **settled-cash field name** (and `multiplier`) on the account read.
- The live order-lifecycle facts: positions ∪ orders response shapes for queued/partial/filled.

## Testing Decisions

**What makes a good test here:** assert **external behavior at a seam**, not internals. For the broker
mechanics that means driving the adapter / `operate_live` through a **stubbed broker Protocol** and asserting
the resulting execution record, portfolio state, persisted files, and reason strings — never reaching the
network and never asserting on private helpers. For the deterministic bucket that means asserting
byte-identical records and identical `state_hash`es across replays, and that benchmark goldens change **only**
where a documented versioned replay key changed.

**Seams (confirmed):**

- **Primary live seam — the broker Protocol.** Widen the existing stub-broker pattern (today `_StubBroker`
  in the alpaca adapter test) to cover the full broker surface. All broker realism is exercised here and at
  the adapter level with stubs: QUEUED on `accepted`/`pending_new`; fills resolved from positions/orders not
  the POST echo; PARTIAL on short fill; EXECUTION_UNCERTAIN on timeout/no-response; `HTTPError`/`URLError`
  caught with the reject body parsed and `raw_payload` persisted (add a **4xx test** — the v0 suite stubs
  only terminal sync statuses); 429/`Retry-After` honored with no resend; the account-status gate;
  `client_order_id` 422 duplicate-submit dedup; cash-cap against the settled-cash field; fractionable
  true/false sizing.
- **Live integration seam — `operate_live`.** Drive it end-to-end with a stub broker + temp ledger/portfolio
  paths (mirroring the chain `run_once` tests): mandatory startup reconcile; reconcile delta → side-based
  buy/sell/NO_ACTION; open-orders netting → NO_ACTION; an unexpected open order → discrepancy →
  terminal-refuse-execution while the decision/labeling chain still advances; reconcile-heal appends a
  reconcile entry; the separate-paths threading; the live SELL-fold realizes P&L; the kill-switch
  `halt=True` stops execution.
- **Shared deterministic seams (reused, no new ones).** The pure execution core, `run_sequence`, `run_chain`,
  and `build_guard_request`, plus the existing determinism + benchmark vehicles: assert the `assert
  port.replayable` fence rejects a non-replayable port from `run_once`/`run_sequence`; assert the
  `as_of`-scoped guard inputs are day-scoped; assert the `exec_ref_gld_price` resolver returns the derived
  proxy on the sim path and the live mark on the live path; re-pin the execution + chain benchmark goldens
  for the two versioned key changes and assert they are otherwise byte-identical; assert the simulator
  portfolio stays accumulate-only (`realized_pnl == 0.0`).

**Modules tested:** the Alpaca paper adapter + its broker Protocol; the new `live_runtime` / `operate_live`;
the execution core + runtime (guard-request `as_of`, `assert port.replayable`); the chain orchestrator
(benchmark re-pin); the execution + portfolio schemas (additive fields, reconcile-entry kind); the
`exec_ref_gld_price` resolver.

**Prior art:** `tests/execution/test_alpaca_adapter.py` (stub-broker pattern, fail-closed, quarantine
flags, parsed-hostname spoof matrix); `tests/execution/test_execution_determinism.py` and
`test_execution_bench.py` (replay/golden vehicles); `tests/execution/test_execution_guards.py` (guard
wiring); `tests/orchestration/test_chain_engine.py`, `test_chain_determinism.py`, `test_chain_bench.py`
(end-to-end `run_once`/replay); `tests/orchestration/test_alpaca_clock_feed.py` and
`test_operational_feed.py` (default-OFF live-plug + capture pattern). Baseline suite is **~1050 tests**;
every relevant item must be green before paper accumulation goes live.

## Out of Scope

- Live-money execution (structurally blocked — Phase D).
- Short selling; margin; a second instrument (e.g. oil); confidence-scaled sizing.
- Broker-side conditional orders; OPG / market-on-open (market+day queue-to-next-open is the chosen path).
- WebSocket `trade_updates` streaming (the reconcile poll is the chosen mechanism).
- The real-GLD-share-price snapshot ingest (an optional fidelity upgrade that plugs into the same
  `exec_ref_gld_price` seam later, with zero rework — **not** a v1 dependency; the former "A8 / Mr-Ripley
  first" blocker is overruled).
- A standalone rate limiter (the 429 handler is the real safeguard at single-instrument daily volume).
- Teaching the simulator to sell or marking a portfolio `value`.
- New SQLite `fill_record` / `scorecard` stores (rejected — second source of truth).
- Zapier; the Alpaca NL MCP server; a Phase-D live-money ADR + canary plan.
- Re-opening any ADR-014 / ADR-011 decision (e.g. reverting the parsed-hostname guard to a substring check).

## Further Notes

- **Deferred audit findings (documented, not actioned in v1):** early-close/half-days at session
  granularity (immaterial at day granularity); clock-feed TZ normalization near 00:00–05:00 UTC (not
  triggered by US-afternoon UTC data + fail-closed; a fix must touch both feeds together to keep the
  feed-equivalence test green); an audit `actor`/`who` field (single operator); a GDPR/CCPA "N-A" governance
  note (paper-only / virtual-money / single-operator / no custody); the standalone rate limiter.
- **Determinism is binding.** Threading any live broker read into the shared deterministic guard input is
  **forbidden** — a live account read folded into the guard request would contaminate the replay key and
  break the execution + chain benchmarks. The live cash-cap account read lives only on the `operate_live`
  path.
- **Sequencing:** adapter-v1 code only after ADR-014 is Accepted; the gated-live enable stays behind the
  ADR-013 HARD PAUSE; calibration target bumps stay DEFER until the ADR-012 performance gate passes; the
  empirical flags B1/B2/B3 + the live order-lifecycle facts close before any live code path runs.
- **Suggested slice order** (each independently shippable and green): (1) `exec_ref_gld_price` resolver +
  severing `gold_price` from execution + SCHEMA-014 price fields + benchmark re-pin; (2) guard `as_of`
  threading + SCHEMA-015 `as_of` + benchmark re-pin; (3) `assert port.replayable` fence + separate-paths
  plumbing; (4) widened broker Protocol + side-based adapter + state machine + typed errors (stub-only);
  (5) `operate_live` + reconcile-then-act + reconcile-heal entry + discrepancy/terminal-refuse +
  cash-cap/fractionable; (6) operator kill switch (audited Tier-2 halt).
