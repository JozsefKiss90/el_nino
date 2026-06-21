---
type: file
canonical_id: FILE-038
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/alpaca_adapter.py"
related_files:
  - "[[adapters.py]]"
related_tests:
  - "[[test_alpaca_adapter]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/alpaca_adapter.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# alpaca_adapter.py

## Definition

The live Alpaca **paper** `ExecutionPort` plug (ADR-011 gate f / STEP 5): `AlpacaPaperAdapter` (implements
the `ExecutionPort` port from [[adapters.py]], `mode = ALPACA_PAPER`, `replayable = False`), a thin
`AlpacaPaperBroker` Protocol + `PaperOrderResult`, a stdlib-only REST broker, the `AlpacaExecutionError`
fail-closed error, and the `paper_adapter_from_env` factory. The non-replayable sibling of the
deterministic `SimulatedBrokerAdapter` behind the same port — the previously-deferred gate-f plug, now
built **default-OFF / built-but-dormant**.

## Purpose

Provide the optional live virtual-money execution path: `fill()` submits a paper market BUY to Alpaca's
**paper** endpoint and echoes the paper fill into a `Fill`. It is **quarantined off** the replay /
benchmark path (`replayable = False`) — live runs are logged, never replayed (ADR-011 §2). It is
**built-but-dormant**: `execute()` calls `fill()` only for an approved LONG, and the provisional decision
logic emits no LONG until calibration lands (ADR-011 §5), so it ships behind the port unused until then.

## Architecture Role

An optional adapter of [[Execution]] (MOD-008) behind [[Execution API]] (INT-011), the non-replayable
plug interchangeable with `SimulatedBrokerAdapter`. The deterministic simulator stays the hard-wired
default port (`_DEFAULT_PORT`) everywhere; this plug is reached only when a caller passes it explicitly to
`run_once` (the live IO path), and is deliberately **not** re-exported from the `execution` package.
Governed by [[ADR - Execution Layer Planning]] (§2 quarantine, §3 paper_only, gate f) + KA-008 credential
isolation + PRED-005 [[Withdrawal Disabled]].

## Constraints

- **Non-replayable quarantine (ADR-011 §2)** — `mode = ALPACA_PAPER`, `replayable = False`; never on
  `run_sequence` / benchmarks; the default port stays `SimulatedBrokerAdapter` (replay-safe).
- **Paper-only ALWAYS (ADR-011 §3, PRED-005)** — submits virtual-money orders to the Alpaca **paper**
  endpoint only; `paper_adapter_from_env` refuses any non-paper base URL; withdrawals never enabled.
- **Fail-closed** — a missing client, a non-LONG direction, or a broker order that does not confirm
  filled raises `AlpacaExecutionError` — **no order silently placed, no synthetic fill returned**; the
  error propagates loudly out of `execute` / `run_once`.
- **Credential isolation (KA-008)** — keys live in env / a git-ignored `.secrets` only — never in the
  repo, a memory file, a dev_graph node, a test, or any committed artifact.
- **Default-OFF / no auto-enable** — enabling the live execution path is an explicit operator opt-in
  (HARD PAUSE); nothing wires this adapter by default.

## Implementation Notes

`AlpacaPaperAdapter` is a frozen dataclass with an injected `client: AlpacaPaperBroker | None` (None ⇒
every `fill` raises). `fill()` guards `direction is LONG`, calls `client.submit_market_buy(symbol, qty)`,
requires a filled status, then maps `filled_avg_price` / `filled_qty` to a `Fill` with realized slippage
echoed vs the orchestrator's mark (ADR-011 D1). `paper_adapter_from_env` reads `ALPACA_API_KEY_ID` /
`ALPACA_API_SECRET_KEY` / optional `ALPACA_PAPER_BASE_URL` (default the paper host) and fail-closes
(`client=None`) on missing creds or a non-paper host — a **parsed-hostname equality check**
(`urlparse().hostname == paper-api.alpaca.markets` + `https`), **not a substring match**, so sub-/super-domain
& query/fragment spoofs cannot slip through (adversarial-review hardening, 2026-06-18). The real broker (`_AlpacaRestPaperBroker`) is stdlib
`urllib` only (no third-party SDK) and is never exercised in tests (the test injects a stub). Through the
pure `execute()` engine the adapter stamps `execution_mode=alpaca_paper` + `replayable=False` onto the
`ExecutionRecord`; a no-fill path (blocked guard / non-LONG / already-executed) never calls the broker.
Tested by [[test_alpaca_adapter]] (TEST-028).

## Open Questions

- Dormant until calibration produces a LONG (ADR-011 §5 / ADR-012); BENCH-004 grounds replay in the
  offline simulator only. A real paper fill is observable only once the macro tape yields a LONG regime.

## Relationships

### Depends On
- [[Execution]]
- [[adapters.py]]

### Implements
- [[Execution API]]

### Validated By
- [[test_alpaca_adapter]]
