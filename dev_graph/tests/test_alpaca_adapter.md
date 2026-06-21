---
type: test
canonical_id: TEST-028
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_alpaca_adapter.py"
related_files:
  - "[[alpaca_adapter.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
test_path: "tests/execution/test_alpaca_adapter.py"
test_type: unit
covers:
  - "[[Execution]]"
  - "[[alpaca_adapter.py]]"
required_for: []
---

# test_alpaca_adapter

## Definition

The live Alpaca **paper** `ExecutionPort` plug test (MOD-008 / INT-011, FILE-038): the fill echo (a stub
paper order maps to a `Fill` with realized slippage); the determinism-boundary flags
(`mode == ALPACA_PAPER`, `replayable is False`); fail-closed on a missing client / non-LONG direction /
non-filled order; the `paper_adapter_from_env` factory fail-closing on missing creds and **refusing a
non-paper base URL**; and the **quarantine** — through the pure `execute()` engine the adapter stamps
`replayable=False` onto the record, a no-fill path never touches the broker, and the default port stays
the deterministic `SimulatedBrokerAdapter`. The factory refusal covers spoofed sub-/super-domain, query-
and fragment-borne, and non-https URLs (parsed-hostname equality, not a substring match), while accepting a
mixed-case paper host. 20 tests; every broker is a stub — **no real network**.

## Purpose

Guard ADR-011 gate f: prove the live paper adapter is paper-only at the credential boundary, fail-closes
on every error path (never a synthetic fill, never a silent order), is non-replayable and quarantined off
the replay/benchmark path, and is built-but-dormant (it cannot fill until an approved LONG exists, ADR-011
§5). Mirrors [[test_execution_engine]] (TEST-018) for the simulated path.

## Constraints

Asserts over `AlpacaPaperAdapter` with a stub `AlpacaPaperBroker` (+ `monkeypatch` on the env-cred
factory) and through the pure `execute()` engine (no IO/clock/network/randomness). The broker call-count
asserts that no order is placed on a non-LONG or no-fill path.

## Relationships

### Used By
- [[Execution]]
- [[alpaca_adapter.py]]

### Justified By
- [[ADR - Execution Layer Planning]]
