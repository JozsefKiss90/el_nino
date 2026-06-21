---
type: test
canonical_id: TEST-027
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_alpaca_clock_feed.py"
related_files:
  - "[[alpaca_clock_feed.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/orchestration/test_alpaca_clock_feed.py"
test_type: integration
covers:
  - "[[Chain Orchestrator]]"
  - "[[alpaca_clock_feed.py]]"
required_for: []
---

# test_alpaca_clock_feed

## Definition

The live Alpaca clock/calendar `OperationalFeed` plug test (MOD-010 seam, FILE-037): the calendar-driven
open/closed decision; the **holiday-gap closure** (Good Friday 2026 — a weekday the fixed-date
`MarketCalendarFeed` wrongly reports open, `AlpacaClockFeed` correctly reports closed); fail-closed on a
client error / missing client / unparseable `as_of`; the `clock_feed_from_env` factory fail-closing on
missing creds and **refusing a non-paper base URL** — including spoofed sub-/super-domain, query- and
fragment-borne, and non-https URLs (parsed-hostname equality, not a substring match), while accepting a
mixed-case paper host; and the **replay-path quarantine** (the captured Alpaca-produced `OperationalInput`
reloads via `load_operational` and `run_sequence` threads it without re-reading the feed). 17 tests; every
client is a stub — **no real network**.

## Purpose

Guard the ADR-009 amendment + ADR-011 §2 / gate-f quarantine for the live plug: prove the feed closes the
v0 holiday gap, fail-closes on every error path, never reaches a non-paper endpoint, and is read only on
the IO path with the produced value captured + replay-reconstructable — mirroring [[test_operational_feed]]
(TEST-026) for the deterministic feed.

## Constraints

Asserts over `AlpacaClockFeed` with a stub `AlpacaCalendarClient` (and a raising stub for the fail-closed
path) + `monkeypatch` on the env-cred factory; no clock / network / randomness. Uses the real corpus
fixture (`952cc83a…`, a trading-day Friday) for the `run_sequence` capture/quarantine integration.

## Relationships

### Used By
- [[Chain Orchestrator]]
- [[alpaca_clock_feed.py]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
- [[ADR - Execution Layer Planning]]
