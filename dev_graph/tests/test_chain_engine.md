---
type: test
canonical_id: TEST-023
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/orchestration/test_chain_engine.py"
related_files:
  - "[[engine.py (orchestration)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
test_path: "tests/orchestration/test_chain_engine.py"
test_type: e2e
covers:
  - "[[Chain Orchestrator]]"
  - "[[engine.py (orchestration)]]"
required_for: []
---

# test_chain_engine

## Definition

The chain orchestrator core (MOD-010) behavioral test over the real consumable fixture: ADMIT + no-fill on
the monochromatic AVOID corpus; the in-hand price/direction forwarding (ADR-011 D1); wrap-not-enrich (the
packet stays pure, ADR-009 §2); forwarded snapshot provenance + `as_of`; the GATE-001 guard-wiring with
block attribution; the non-ADMIT → no-execute branch; end-to-end idempotency; the fail-closed
ADMIT-without-price guard; and bounded-context hygiene (only the orchestrator imports `src/risk`). 12 tests.

## Purpose

Guard the pure `run_chain` composition: that it threads the layers correctly, forwards the in-hand values,
gates execution on ADMIT, runs the guard in the orchestrator, and stays deterministic — without re-deriving
or enriching anything.

## Constraints

Asserts over the pure core; reuses the real corpus (`952cc83a…`, `packet_id gold-v0:5653d07a0b3949d5`) and a
gold-stripped snapshot for the defensive `ChainContractError` branch. No clock / network / randomness.

## Relationships

### Used By
- [[Chain Orchestrator]]
- [[engine.py (orchestration)]]

### Justified By
- [[ADR - Execution Layer Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
