---
type: test
canonical_id: TEST-012
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/gold/test_e2e_pipeline.py"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
test_path: "tests/gold/test_e2e_pipeline.py"
test_type: e2e
covers:
  - "[[Snapshot Consumer]]"
  - "[[Feature Builder]]"
  - "[[Market Regime Classifier]]"
  - "[[Gold Decision Builder]]"
required_for: []
---

# test_e2e_pipeline

## Definition

The full-chain end-to-end determinism test: `snapshot → MOD-003.consume → MOD-004.build_features → MOD-005.classify → MOD-006.build_decision`. 3 tests asserting (1) the final `GoldDecisionPacket` is byte-identical across two independent runs; (2) the golden real packet (RESTRICTIVE_RATES → AVOID / confidence 0.39744 / `packet_id gold-v0:5653d07a0b3949d5` / paper_only); (3) the `snapshot_id` threads every stage unchanged (the single replay anchor) and the consumed snapshot's `recompute_id()` matches the published id.

## Purpose

Close the Regime Taxonomy audit's Warning 4 (no snapshot→…→Gold end-to-end test) now that all five Layer-3 modules exist, and prove the determinism cascade composes across the whole pipeline, not just per-module.

## Relationships

### Used By
- [[Snapshot Consumer]]
- [[Feature Builder]]
- [[Market Regime Classifier]]
- [[Gold Decision Builder]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
