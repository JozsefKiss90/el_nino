---
type: test
canonical_id: TEST-032
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_gated.py"
related_files:
  - "[[gated.py (ops)]]"
related_tests: []
related_constraints:
  - "[[Withdrawal Disabled]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
test_path: "tests/ops/test_gated.py"
test_type: unit
covers:
  - "[[gated.py (ops)]]"
required_for: []
---

# test_ops_gated

## Definition

Headless unit tests for the Tier-3 gated-live actions [[gated.py (ops)]] (FILE-042) — 13 tests, mocked
adapter + runner (no network, no PowerShell).

## Purpose

Lock the gated-tier invariants: the Alpaca run **REFUSES** (no order) when the adapter is dormant; when
creds-present it threads the live paper port WITHOUT hitting the network (AVOID -> no fill -> broker stub
never called); the calibration bump **only ever DEFERs** and never mutates the golden / a `*_version`
(`executed=False` on both branches); register/unregister audit success + failure; structural never-raise
(raising factory / audit-write failure); no credential value in the audit log.

## Constraints

No live-money path exercised; the broker stub asserts-on-call to prove no network; deterministic clock.

## Implementation Notes

Injects `AlpacaPaperAdapter(client=None)` (dormant) and `AlpacaPaperAdapter(client=stub)` (creds-present);
asserts the committed golden bytes are unchanged after a bump attempt; covers the precondition-line text.

## Relationships

### Used By
- [[gated.py (ops)]]

### Constrained By
- [[Withdrawal Disabled]]

### Justified By
- [[ADR - Operations Control Plane]]
