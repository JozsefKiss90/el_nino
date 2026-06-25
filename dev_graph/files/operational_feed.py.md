---
type: file
canonical_id: FILE-036
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/operational_feed.py"
related_files:
  - "[[alpaca_clock_feed.py]]"
  - "[[live_runtime.py]]"
related_tests:
  - "[[test_operational_feed]]"
  - "[[test_operator_halt]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "src/orchestration/operational_feed.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# operational_feed.py

## Definition

The live operational-status feed adapter (MOD-010 seam): the `OperationalFeed` Protocol port, the
deterministic `MarketCalendarFeed` (the v0 source), and the capture mechanism (`persist_operational` +
`read_and_capture`). Lifts ADR-009's deferred "live operational feed".

## Purpose

**Read** venue readiness and **produce** an `OperationalInput` on the live `run_once` path only, and
**capture** it (a JSON artifact in the `load_operational` format) so any replay threads the captured value
and never re-reads the feed — the ADR-011 §2 / gate-f non-replayable-adapter quarantine. The pure cores
(`evaluate` / `run_chain`) keep taking `OperationalInput` as an explicit value — **unchanged contract**.

## Architecture Role

An IO adapter of [[Chain Orchestrator]] (MOD-010), behind the explicit `OperationalInput` seam. Feeds the
`operational_ok` guard (PRED-007 / [[Operational OK]]) computed by [[Paper-Trading Runtime]] (MOD-007).
Governed by [[ADR - Paper-Trading Runtime Planning]] (the guard + model) + [[ADR - Execution Layer Planning]]
(the §2 / gate-f quarantine).

## Constraints

- **Replay-path quarantine** — the feed is read only in `run_once`; `run_sequence` has no feed parameter;
  replay reconstructs the operational decision from the captured artifact, never the feed.
- **Fail-closed** — unavailable / ambiguous / unparseable ⇒ `OperationalInput.closed()` (not tradeable).
- **No contract / `*_version` change** — additive IO only; the `OperationalInput` model is untouched.
- **Credential isolation (KA-008)** — the v0 calendar feed needs no credentials; the live Alpaca feed (now
  built in the sibling [[alpaca_clock_feed.py]] FILE-037, **default-OFF**) keeps its keys in env /
  git-ignored `.secrets` only, never in the repo / a memory / a node.

## Implementation Notes

`MarketCalendarFeed.read(as_of)` parses the ISO `as_of` (deterministic, never wall-clock): a trading day is
a non-holiday weekday ⇒ tradeable/venue_open; weekend / listed holiday / unparseable ⇒ closed. The holiday
set is a deterministic v0 approximation (fixed-date New Year / Juneteenth / Independence / Christmas), **not**
a full NYSE calendar — that gap is now closed by the live [[alpaca_clock_feed.py]] (FILE-037,
`AlpacaClockFeed`, default-OFF) behind this same `OperationalFeed` port. `read_and_capture(feed, as_of, path)`
reads once and persists the produced `OperationalInput` (temp + `os.replace`) — the replay source.

**Operator kill switch (ADR-014 §6.6).** `OperatorHaltFeed` decorates any `OperationalFeed` and, when
`operator_halt_active(path)` reports the kill switch engaged (a persisted halt marker; absent ⇒ run,
present-halt ⇒ honored, unreadable ⇒ fail-closed-halt), **forces `halt=True`** on the produced
`OperationalInput` — so the **existing** `operational_ok` predicate REJECTs the next live cycle. No new
honor path / no new predicate; the forced value is captured like any other, so the honored halt is
replay-safe. The write/governance side is the ADR-013 gated Tier-2 halt action (`ops/gated.py`,
`set_operator_halt`).

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Used By
- [[live_runtime.py]]

### Validated By
- [[test_operational_feed]]
- [[test_operator_halt]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
