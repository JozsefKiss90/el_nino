---
type: test
canonical_id: TEST-040
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_replayable_fence.py"
related_files:
  - "[[live_runtime.py]]"
  - "[[runtime.py (orchestration)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/orchestration/test_replayable_fence.py"
test_type: integration
covers:
  - "[[live_runtime.py]]"
required_for: []
---

# test_replayable_fence

## Definition

Tests the ADR-014 §5.3 fence: `run_once`/`run_sequence` structurally refuse a non-replayable broker port
(`assert port.replayable`), so a live port is reachable only via `operate_live`; and that `operate_live`
accepts the `LiveExecutionAdapter`, stamps records non-replayable, and threads a **separate**
`(ledger, portfolio)` pair — never touching the canonical replay files (on the AVOID corpus the broker is
never contacted).

## Purpose

Prove the structural quarantine that keeps the live plug off the deterministic replay/benchmark path.

## Relationships

### Validated By
- [[live_runtime.py]]

### Used By
- [[live_runtime.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
