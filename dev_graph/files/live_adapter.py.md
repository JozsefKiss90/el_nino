---
type: file
canonical_id: FILE-045
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
  - ADR
source_paths:
  - "src/execution/live_adapter.py"
related_files:
  - "[[alpaca_adapter.py]]"
  - "[[live_runtime.py]]"
related_tests:
  - "[[test_live_adapter]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "src/execution/live_adapter.py"
language: "python"
module: "[[Execution]]"
owns:
  - "LiveExecutionAdapter"
  - "LiveBrokerPort"
  - "LiveOrderOutcome"
  - "make_client_order_id"
  - "live_submit_mark"
  - "live_adapter_from_env"
used_by:
  - "[[live_runtime.py]]"
---

# live_adapter.py

## Definition

The broker-realistic, **side/order-based** LIVE Alpaca paper adapter + order state machine (ADR-014 §6).
It **supersedes** the v0 LONG-only [[alpaca_adapter.py]] `AlpacaPaperAdapter.fill` on the live path: the
live path is reconcile-driven (LONG→buy, FLAT→sell), so this adapter is `submit_buy` / `submit_sell` and
resolves fills from the broker **positions + orders reads**, never the synchronous POST echo.

## Purpose

Make a real async Alpaca paper order operable: treat `accepted`/`pending_new`/`new` as **QUEUED** (fixing
the v0 sync-fill raise), classify rejects/429/auth/timeouts as **EXECUTION_UNCERTAIN** (halt, no blind
retry), and a 422 duplicate `client_order_id` as an idempotent **NO_ACTION**. The raw broker body is always
captured (`raw_payload`).

## Architecture Role

Depends on a widened `LiveBrokerPort` Protocol (buy/sell + positions/open-orders/orders/account/asset);
every test injects a stub for the whole surface — never the network. `replayable = False` keeps it
quarantined off the deterministic replay/benchmark path (the `assert port.replayable` fence). Reached only
through [[live_runtime.py]] `operate_live`.

## Inputs / Dependencies

- The `LiveBrokerPort` client (paper-only, parsed-host guarded, inherited from [[alpaca_adapter.py]]); the
  account read (status gate + settled cash); the GLD asset read (`fractionable`).

## Outputs / Provides

- `LiveOrderOutcome` (status + `client_order_id`/`alpaca_order_id`/`filled_qty`/`filled_avg_price`/
  `raw_payload`/`halt`) mapping onto the additive SCHEMA-014 fields; a deterministic `client_order_id`.

## Constraints

- **Paper-only / KA-008 credential isolation** inherited from [[alpaca_adapter.py]] (same parsed-host
  guard; `live_adapter_from_env` fail-closes on missing creds / non-paper host).
- **Cash-cap binds to the literal settled-cash field** (`cash`), never any `*_buying_power` — "no margin"
  is structural (ADR-014 §6.4).
- Empirical preconditions B1/B2/B3 are documented constants (`_COID_MAXLEN`, `_SETTLED_CASH_FIELD`) —
  confirm against Alpaca docs before any live run.

## Implementation Notes

`resolve_order_qty` honours GLD `fractionable` (true → notional market+day; false → `floor(cash/mark)`).
`submit_*` classify the accept response into the state machine and never trust the echo; `resolve_fill`
reads the broker ORDER (FILLED/PARTIAL/QUEUED/UNCERTAIN). Typed errors (`HTTPError`/`URLError`) are caught,
the reject body parsed, and routed to EXECUTION_UNCERTAIN/halt — no reject silently dropped.

**Real GLD mark (ADR-014 §5.1, Blocker 1 — CLOSED).** `live_submit_mark(symbol)` reads the broker's
latest trade (`get_latest_trade` → the read-only market-data host `data.alpaca.markets`,
`/v2/stocks/{symbol}/trades/latest`, fields `trade.p`/`trade.t`) and returns an `ExecPriceRef`
(basis `BASIS_LIVE_SUBMIT`, pinned ts). Fail-closed: a missing / non-positive mark raises rather than
fabricate a 0 reference. The market-data host is **read-only — never an order path**; orders still go only
to the paper trading host behind the parsed-host guard. This is the live half of the `exec_ref` seam
([[price_reference.py]] is the sim half / derived proxy).

## Open Questions

- For a fractionable notional order the share qty is unknown at submit; the FILLED/PARTIAL contract treats
  a broker `filled` status at its `filled_qty` (resolved with `requested_qty=0.0` by [[live_runtime.py]]).

## Relationships

### Depends On
- [[alpaca_adapter.py]]
- [[Execution]]

### Validated By
- [[test_live_adapter]]

### Used By
- [[live_runtime.py]]

### Supersedes
- [[alpaca_adapter.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]

### Constrained By
- [[Canonical Ownership]]
