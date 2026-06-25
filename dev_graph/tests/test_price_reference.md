---
type: test
canonical_id: TEST-036
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/execution/test_price_reference.py"
related_files:
  - "[[price_reference.py]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/execution/test_price_reference.py"
test_type: unit
covers:
  - "[[price_reference.py]]"
required_for: []
---

# test_price_reference

## Definition

Tests the `resolve_sim_exec_ref` derived-proxy resolver (ADR-014 §5.1): `exec_ref_gld_price =
gold_price_proxy × OZ_PER_SHARE`, the recorded `ts`/`basis` provenance, determinism (no live read), and
that the GLD-share reference is severed from gold spot.

## Purpose

Pin the versioned deterministic price source so a change is a documented re-pin, never silent drift.

## Relationships

### Validated By
- [[price_reference.py]]

### Used By
- [[price_reference.py]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]
