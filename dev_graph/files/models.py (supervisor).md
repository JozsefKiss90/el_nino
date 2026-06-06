---
type: file
canonical_id: FILE-006
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - code
source_paths: []
related_files: []
related_tests:
  - "[[test_scoring]]"
  - "[[test_decision_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/supervisor/decision_engine/models.py"
language: "python"
module: "[[Decision Engine]]"
owns:
  - "EvaluationScorecard"
  - "UpgradeOption"
  - "TreasuryState"
  - "RankedOption"
  - "DecisionPacket"
  - "DecisionConfig"
used_by: []
---

# models.py (supervisor)

## Definition

The data-model source file of the Decision Engine module (MOD-002), at `src/supervisor/decision_engine/models.py`. (Named with a `(supervisor)` suffix to disambiguate from the Risk Control `models.py` / FILE-003.)

## Purpose

Realizes SCHEMA-005 (`EvaluationScorecard`, input) and SCHEMA-004 (`DecisionPacket` + `RankedOption`, output), plus the internal value objects `UpgradeOption`, `TreasuryState`, and `DecisionConfig`. Dependency-free stdlib dataclasses per ADR-003.

## Architecture Role

Shared data layer for the Decision Engine; consumed by `scoring.py` and `decision_engine.py`.

## Constraints

- `RankedOption` and `DecisionPacket` enforce the SCHEMA-004 invariants at construction (blocked options carry a reason; a selected id must be an allowed option).
- Frozen dataclasses — immutable and value-equal (enables deterministic comparison in tests).

## Implementation Notes

`TreasuryState.available` is derived (`budget - deployed`); `after_spend()` returns a new state. Exercised by both supervisor test files.

## Relationships

### Depends On
- [[Decision Engine]]

### Produces
- [[Decision Packet Schema]]
- [[Evaluation Scorecard Schema]]

### Validated By
- [[test_scoring]]
- [[test_decision_engine]]
