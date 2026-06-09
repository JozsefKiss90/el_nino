---
type: file
canonical_id: FILE-015
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-09
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/gold/decision_builder/models.py"
related_files: []
related_tests:
  - "[[test_decision_builder]]"
related_constraints: []
related_decisions:
  - "[[ADR - Gold Decision Confidence Semantics]]"
file_path: "src/gold/decision_builder/models.py"
language: "python"
module: "[[Gold Decision Builder]]"
owns: []
used_by: []
---

# models.py (gold)

## Definition

SCHEMA-011 dataclasses for the gold decision layer: `GoldDecisionPacket`, the `Direction` and `DecisionMode` enums, `FeatureCitation`, `ConfidenceInputs`, `GuardRefs`, and the **v0.2.0 additive `SnapshotGuards`** L1 provenance block (ADR-009 §3; distinct from `GuardRefs`), plus the byte-stable `to_dict()` and `compute_packet_id` (SHA-256 over the full identity tuple, mirroring `Snapshot.recompute_id` — excludes `snapshot_guards`/`as_of`).

## Purpose

Realize the [[Gold DecisionPacket v0 Schema]] (SCHEMA-011) as frozen, stdlib-only dataclasses with cross-field invariants (confidence/uncertainty ∈ [0,1]; paper_only; INDETERMINATE ⇒ WATCH).

## Implementation Notes

Basename-disambiguated as `models.py (gold)` (6th `models.py`: risk/supervisor/snapshot/features/regime/gold). Frozen dataclasses per ADR-003; confidence/uncertainty rounded to 6 dp at serialization.

## Relationships

### Depends On
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]

### Realizes
- [[Gold DecisionPacket v0 Schema]]
