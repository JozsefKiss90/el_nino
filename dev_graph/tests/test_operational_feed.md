---
type: test
canonical_id: TEST-026
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_operational_feed.py"
related_files:
  - "[[operational_feed.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/orchestration/test_operational_feed.py"
test_type: integration
covers:
  - "[[Chain Orchestrator]]"
  - "[[operational_feed.py]]"
required_for: []
---

# test_operational_feed

## Definition

The live operational-status feed adapter test (MOD-010 seam, FILE-036): the deterministic
`MarketCalendarFeed` (open on a trading day; fail-closed on weekend / weekday-holiday / unparseable / absent),
the capture round-trip (the produced `OperationalInput` reloads via `load_operational`), and — the
non-negotiable — the **replay-path quarantine**: capture freezes the value at read time and a `run_sequence`
replay threads it without ever re-reading the feed (a stub feed's call-count stays at 1). 10 tests.

## Purpose

Guard the ADR-009 / ADR-011 §2 quarantine: prove the live feed is read only on the IO path, the produced
`OperationalInput` is captured and replay-reconstructable, the feed fail-closes, and the replay path is
independent of the (possibly-changing) live feed — mirroring the execution layer's captured-config
env-independence test.

## Constraints

Asserts over the deterministic feed + the capture/quarantine seam (using `tmp_path` + a mutable stub feed);
no clock / network / randomness. Uses the real corpus (`952cc83a…`, a Friday/trading-day fixture) for the
`run_once` + `run_sequence` integration.

## Relationships

### Used By
- [[Chain Orchestrator]]
- [[operational_feed.py]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
- [[ADR - Execution Layer Planning]]
