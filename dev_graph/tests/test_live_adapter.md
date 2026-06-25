---
type: test
canonical_id: TEST-035
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_live_adapter.py"
related_files:
  - "[[live_adapter.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/execution/test_live_adapter.py"
test_type: unit
covers:
  - "[[live_adapter.py]]"
required_for: []
---

# test_live_adapter

## Definition

Stub-only tests of the side/order-based live adapter + order state machine (ADR-014 §6): the account-status
gate, cash-capped + fractionable sizing, the deterministic `client_order_id`, the submit state machine
(QUEUED on accept; EXECUTION_UNCERTAIN on reject/timeout/429/auth; NO_ACTION on a 422 duplicate), the
typed-error path (4xx reject body parsed + persisted, never dropped), and fill resolution from the broker
ORDER read (never the synchronous POST echo).

## Purpose

Prove every broker-realistic behaviour at the adapter seam with a full `LiveBrokerPort` stub — never the
network.

## Constraints

No network; the parsed-host / fail-closed credential boundary is exercised via `live_adapter_from_env`.

## Relationships

### Validated By
- [[live_adapter.py]]

### Used By
- [[live_adapter.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
