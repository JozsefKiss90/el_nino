---
type: test
canonical_id: TEST-033
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_app.py"
related_files:
  - "[[app.py (ops)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operations Control Plane]]"
test_path: "tests/ops/test_app.py"
test_type: integration
covers:
  - "[[app.py (ops)]]"
required_for: []
---

# test_ops_app

## Definition

App-level tests for the Textual TUI [[app.py (ops)]] (FILE-040) — 4 tests, driven via Textual's headless
`run_test` driver (wrapped in `asyncio.run`; no pytest-asyncio).

## Purpose

Lock the TUI dispatch invariants: a safe action runs through the worker + audits; a **raising** action is
caught by the crash-proof worker (the app does NOT exit / stick on `[running]`); the gated confirm-modal
flow — `a` opens the modal, `y` confirms (runs + audits the fail-closed REFUSE), `n`/`escape` cancels
(no action, nothing audited).

## Constraints

Headless driver only (no real terminal); Alpaca env cleared so the gated run REFUSES safely.

## Implementation Notes

Monkeypatches a `SAFE_ACTIONS` entry to raise to prove the worker survives; uses `pilot.press` to exercise
the real key -> modal -> key flow; asserts the audit log state after confirm vs cancel.

## Relationships

### Used By
- [[app.py (ops)]]

### Justified By
- [[ADR - Operations Control Plane]]
