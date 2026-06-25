---
type: test
canonical_id: TEST-034
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_live_runtime.py"
related_files:
  - "[[live_runtime.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/orchestration/test_live_runtime.py"
test_type: integration
covers:
  - "[[live_runtime.py]]"
required_for: []
---

# test_live_runtime

## Definition

Behavioural tests of the live reconcile-then-act core (ADR-014 §6) across three seams, all stub-driven (no
network): `plan_reconcile` (pure delta/discrepancy), `reconcile_and_act` (account gate, cash-capped buy,
FLAT SELL-fold realized P&L, discrepancy → terminal-refuse + reconcile-heal, idempotency bifurcation), and
`operate_live` end-to-end over the real AVOID fixture (NO_ACTION before the adapter, separate live paths,
the chain advancing, idempotency, guard-block refusal).

## Purpose

Prove the live path is operable + fail-closed + determinism-non-contaminating without a real broker.

## Constraints

Asserts external behaviour at the seam (record / portfolio / reason strings), never private internals;
the broker is always a stub.

## Implementation Notes

Synthetic `Direction.LONG`/`FLAT` ADMIT records drive the buy/sell/heal cases the monochromatic AVOID
corpus cannot; the real fixture drives the end-to-end wiring.

## Relationships

### Validated By
- [[live_runtime.py]]

### Used By
- [[live_runtime.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
