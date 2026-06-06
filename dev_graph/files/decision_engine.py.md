---
type: file
canonical_id: FILE-004
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
  - "[[scoring.py]]"
related_tests:
  - "[[test_decision_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
file_path: "src/supervisor/decision_engine/decision_engine.py"
language: "python"
module: "[[Decision Engine]]"
owns:
  - "DecisionEngine"
used_by: []
---

# decision_engine.py

## Definition

The orchestrator source file of the Decision Engine module (MOD-002). Defines `DecisionEngine.decide()` — early-exit, exclusion + budget filtering, deterministic ranking, and packet emission.

## Purpose

Implements the Decision API (INT-006): consumes an `EvaluationScorecard` plus catalog/treasury/excluded inputs, produces a `DecisionPacket`.

## Architecture Role

Entry point of the Decision Engine module within the Supervisor Office. Deterministic and side-effect-free.

## Constraints

- Deterministic ranking: score descending, `upgrade_id` ascending tie-break.
- Treasury is decremented (`after_spend`) only for the selected upgrade.

## Implementation Notes

`decide()` short-circuits on the promotable early-exit, then scores via `scoring.score_option`, applies exclusion and `cost > available` filters (recording `blocked_reason`), ranks, and selects the highest-scoring allowed option. Covered by `test_decision_engine.py` (7 tests).

## Relationships

### Depends On
- [[Decision Engine]]
- [[models.py (supervisor)]]
- [[scoring.py]]

### Implements
- [[Decision API]]

### Validated By
- [[test_decision_engine]]
