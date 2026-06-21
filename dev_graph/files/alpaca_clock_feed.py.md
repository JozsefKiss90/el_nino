---
type: file
canonical_id: FILE-037
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/alpaca_clock_feed.py"
related_files:
  - "[[operational_feed.py]]"
related_tests:
  - "[[test_alpaca_clock_feed]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/orchestration/alpaca_clock_feed.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# alpaca_clock_feed.py

## Definition

The live **Alpaca clock/calendar** `OperationalFeed` plug (MOD-010 seam): `AlpacaClockFeed` (implements
the `OperationalFeed` port from [[operational_feed.py]]), a thin `AlpacaCalendarClient` Protocol + a
stdlib-only REST client, and the `clock_feed_from_env` factory. It is the **non-replayable** sibling of
the deterministic `MarketCalendarFeed` behind the same port — the ADR-009 amendment's previously-deferred
live plug, now built **default-OFF**.

## Purpose

Close the **v0 holiday-calendar gap**: the fixed-date `MarketCalendarFeed` cannot model movable feasts
(Good Friday) or observed-date shifts; Alpaca's `/v2/calendar` (paper base URL) is the authoritative
venue calendar that can. `AlpacaClockFeed.read(as_of)` maps a scheduled trading day → a tradeable
`OperationalInput`, everything else → `closed()`. Read only on the live `run_once` path and **captured**
(`read_and_capture`) so replay threads the captured value and never re-reads Alpaca (the ADR-011 §2 /
gate-f quarantine).

## Architecture Role

An optional IO adapter of [[Chain Orchestrator]] (MOD-010), behind the same `OperationalFeed` seam as
[[operational_feed.py]] (FILE-036). Default-OFF: the deterministic `MarketCalendarFeed` stays canonical;
this plug is selected only by explicit operator opt-in (`orchestration.runtime --operational-feed-source
alpaca`) and is deliberately **not** re-exported from the `orchestration` package, so the default import
graph stays network-free. Governed by [[ADR - Paper-Trading Runtime Planning]] (the feed amendment) +
[[ADR - Execution Layer Planning]] (the §2 / gate-f quarantine + KA-008 credential isolation).

## Constraints

- **Replay-path quarantine** — read only in `run_once`; the produced `OperationalInput` is captured;
  `run_sequence` threads the captured value and never touches Alpaca.
- **Fail-closed (KA-008 + ADR-009)** — missing/non-paper creds, an API/auth error, or an
  ambiguous/unparseable `as_of` ⇒ `OperationalInput.closed()` (not tradeable); never fail-open.
- **Paper-only at the credential boundary** — `clock_feed_from_env` refuses any base URL that is not the
  Alpaca **paper** host (`paper-api.alpaca.markets`) and fail-closes on missing creds; never raises.
- **Credential isolation (KA-008)** — keys live in env / a git-ignored `.secrets` only — never in the
  repo, a memory file, a dev_graph node, a test, or any committed artifact.
- **No contract / `*_version` change** — additive IO only; the `OperationalInput` model is untouched, and
  the produced shape is drop-in identical to `MarketCalendarFeed`'s.

## Implementation Notes

`AlpacaClockFeed` is a frozen dataclass with an injected `client: AlpacaCalendarClient | None` (None ⇒
every `read` fail-closes). `read(as_of)` parses the ISO `as_of` to a `YYYY-MM-DD` venue date, queries the
client's `trading_days(day, day)`, and reports tradeable iff that date is a scheduled trading day —
`halt`/`degraded` are not modelled by a calendar (a real-time market-data feed would). `clock_feed_from_env`
reads `ALPACA_API_KEY_ID` / `ALPACA_API_SECRET_KEY` / optional `ALPACA_PAPER_BASE_URL` (default the paper
host) and refuses any non-paper host via a **parsed-hostname equality check** (`urlparse().hostname ==
paper-api.alpaca.markets` + `https`), **not a substring match** — so a sub-/super-domain, a query/fragment
carrying the host, or a cleartext URL cannot slip through (adversarial-review hardening, 2026-06-18). The
real client (`_AlpacaRestCalendarClient`) is stdlib `urllib` only (no third-party SDK) and is
never exercised in tests (the test injects a stub). Tested by [[test_alpaca_clock_feed]] (TEST-027).

## Open Questions

- Intraday `halt`/`degraded` would need a real-time market-data feed (Alpaca's clock/calendar does not
  surface per-symbol halts); out of scope for v0 — the calendar plug reports scheduled open/closed only.

## Relationships

### Depends On
- [[Chain Orchestrator]]
- [[operational_feed.py]]

### Validated By
- [[test_alpaca_clock_feed]]
