---
type: file
canonical_id: FILE-005
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - code
source_paths: []
related_files:
  - "[[models.py (supervisor)]]"
related_tests:
  - "[[test_scoring]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/supervisor/decision_engine/scoring.py"
language: "python"
module: "[[Decision Engine]]"
owns:
  - "weakness_severity"
  - "score_option"
  - "WEAKNESS_DIMENSIONS"
used_by: []
---

# scoring.py

## Definition

The deterministic weakness-scoring source file of the Decision Engine module (MOD-002). Pure functions mapping a scorecard + upgrade option to a cost-efficiency-weighted score.

## Purpose

Encodes how severely the office is weak in each dimension and scores upgrade options by `severity * expected_improvement / cost`. Realizes the scoring logic of the Supervisor Pattern (PAT-001).

## Architecture Role

Scoring library consumed by `DecisionEngine.decide()`.

## Constraints

- Pure functions, deterministic; severity clamped to [0, 1]; cost must be > 0.

## Implementation Notes

`WEAKNESS_DIMENSIONS` maps dimension → severity function (calibration, pnl, drawdown, disagreement); unknown dimensions score 0. Covered by `test_scoring.py` (5 tests).

## Relationships

### Depends On
- [[Decision Engine]]
- [[models.py (supervisor)]]

### Realizes
- [[Supervisor Pattern]]

### Validated By
- [[test_scoring]]
