---
type: test
canonical_id: TEST-024
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_chain_determinism.py"
related_files:
  - "[[runtime.py (orchestration)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/orchestration/test_chain_determinism.py"
test_type: e2e
covers:
  - "[[Chain Orchestrator]]"
  - "[[runtime.py (orchestration)]]"
required_for: []
---

# test_chain_determinism

## Definition

The chain orchestrator determinism + IO round-trip test (MOD-010): byte-identical end-to-end replay through
`run_sequence` (all five record types + ending ledger + portfolio state), end-to-end admission idempotency,
the captured-input replay invariant (the replay path never reads `os.environ`), and the `run_once` IO shell
— persist (portfolio-then-ledger) + reload round-trip, the non-consumable → `None` fail-closed branch, and
on-disk idempotency. 7 tests.

## Purpose

Guard the §2/§4 determinism invariant end-to-end and the IO-shell contract: that replay is byte-identical,
that re-presenting a snapshot cannot double-admit or double-fill, that the captured guard config is immune to
env poisoning, and that the shell persists/reloads consistently and fail-closes on a non-consumable snapshot.

## Constraints

Asserts over the pure `run_sequence` + the `run_once` shell (using `tmp_path`); no clock / network /
randomness on the replay path. Uses `monkeypatch` only to prove env-independence.

## Relationships

### Used By
- [[Chain Orchestrator]]
- [[runtime.py (orchestration)]]

### Justified By
- [[ADR - Execution Layer Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
