---
type: file
canonical_id: FILE-018
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/decision_builder/builder.py"
related_files: []
related_tests:
  - "[[test_decision_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
file_path: "src/gold/decision_builder/builder.py"
language: "python"
module: "[[Gold Decision Builder]]"
owns: []
used_by: []
---

# builder.py

## Definition

`build_decision(fv, rc, guards=None, config=DEFAULT, as_of=None) -> GoldDecisionPacket` — the public Gold Decision API (INT-009) driver: the pure, total, fail-closed assembly of a paper-only Gold DecisionPacket from a FeatureVector + RegimeClassification.

## Purpose

Compose the contract: snapshot-id consistency check (fail-closed) → `trust_score` → `direction_for` → cited features (from the regime provenance) → deterministic templated rationale → full-key `packet_id` → frozen packet.

## Implementation Notes

Snapshot-id / feature-schema-version mismatch between `fv` and `rc` raises (fail-closed). `guards=None` ⇒ `GuardRefs` all-null. No IO/clock/randomness/history (ADR-006 §3). Implements [[Gold Decision API]] (INT-009).

## Relationships

### Depends On
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]

### Implements
- [[Gold Decision API]]
