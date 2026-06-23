<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 4 — Widened broker Protocol + side-based adapter + state machine + typed errors (stub-only)

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`), bucket (ii). Governed by ADR-014.

## What to build

Turn the dormant LONG-only buy-stub into a broker-realistic, side/order-based adapter, **driven entirely through a stubbed broker Protocol — never the network**. This is the broker-mechanics slice; wiring it into `operate_live` is Slice 5.

- **Widen the broker Protocol** from `submit_market_buy` to the full surface the reconcile loop needs: `submit_market_buy`, `submit_market_sell`, `get_positions`, `get_open_orders`, `get_orders`, `get_account`, `get_asset`. Tests inject a stub for all of it.
- **Side/order-based adapter**: `submit_market_buy` / `submit_market_sell` driven by a reconcile delta — LONG→buy, FLAT→sell, AVOID/WATCH→NO_ACTION (resolved before the adapter). The v0 `fill(direction)` (LONG-only, raises on non-LONG) is **superseded on the live path** — repurpose/remove it, do not extend it.
- **State machine**: `accepted`/`pending_new`/`new` = **QUEUED** (not an error, not resent — fixes the v0 sync-fill raise; fills resolve via positions+orders reads, never the synchronous POST echo). `filled_qty < requested` = **PARTIAL**. Timeout / no-response = **EXECUTION_UNCERTAIN** + halt that instrument (no blind retry). Auth error = halt.
- **Typed error handling**: wrap the order call in try/except for HTTP/URL errors, parse the broker reject body, route to EXECUTION_UNCERTAIN/halt, and persist `raw_payload` (v0 discards it) — add an explicit 4xx test.
- **429 / `Retry-After`**: honor it, no blind resend (part of the state machine).
- **Startup account-status gate**: require `status == "ACTIVE" && !trading_blocked && !account_blocked`.
- **`client_order_id`**: deterministic id so a same-order duplicate submit is rejected by the broker (422) idempotently.
- **Cash-cap + fractionable**: cash-cap binds to the literal settled-cash field (never any `*_buying_power`); `fractionable: true` → notional market+day order; `false` → integer shares = `floor(cash_capped_notional / live_submit_mark)`.
- **Order model**: market + `time_in_force=day` (queue-to-next-open) — not OPG, not broker-side conditional orders.
- **Security**: keep the existing parsed-hostname env guard; the roadmap's `"paper-api" in base_url` substring check stays **rejected** (credential-exfil bypass).
- **SCHEMA-014**: add the statuses `{QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION}` and broker-traceability fields (`alpaca_order_id`, `raw_payload`, `client_order_id`) on the execution record.

Empirical preconditions to close before live code runs (document the assumed values used by the stub): B1 `client_order_id` length/charset; B2 GLD `fractionable` value; B3 settled-cash field name (+ `multiplier`); positions ∪ orders response shapes for queued/partial/filled.

## Acceptance criteria

- [ ] The broker Protocol exposes buy, sell, get_positions, get_open_orders, get_orders, get_account, get_asset; the test stub implements all of it and no test path reaches the network.
- [ ] `accepted`/`pending_new`/`new` → QUEUED (no raise, no resend); a fill is resolved from positions/orders, never the POST echo.
- [ ] Short fill → PARTIAL; timeout/no-response → EXECUTION_UNCERTAIN + instrument halt with no blind retry; auth error → halt.
- [ ] `HTTPError`/`URLError` is caught, the reject body parsed, routed to EXECUTION_UNCERTAIN/halt, and `raw_payload` persisted — covered by a 4xx test.
- [ ] 429/`Retry-After` is honored with no resend; account-status gate refuses to trade unless ACTIVE && !trading_blocked && !account_blocked.
- [ ] A deterministic `client_order_id` produces idempotent 422 dedup on duplicate submit.
- [ ] Cash-cap reads the literal settled-cash field (never `*_buying_power`); fractionable true → notional market+day, false → floor(notional / mark) integer shares.
- [ ] Orders are market + time_in_force=day; the parsed-hostname env guard is intact and the substring check is not reintroduced.
- [ ] SCHEMA-014 represents {QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION} and persists `alpaca_order_id`, `raw_payload`, `client_order_id`.
- [ ] The v0 LONG-only `fill(direction)` is superseded on the live path (not extended); the simulator replay contract is untouched.

## Blocked by

- Slice 1 — GLD execution price reference (`.scratch/operable-alpaca-adapter-v1/ISSUE-01-exec-ref-gld-price.md`): the live adapter resolves its submit mark through the `exec_ref_gld_price` seam.
