---
type: module
canonical_id: MOD-002
status: active
implementation_status: tested
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files:
  - "[[decision_engine.py]]"
  - "[[scoring.py]]"
  - "[[models.py (supervisor)]]"
related_tests:
  - "[[test_decision_engine]]"
  - "[[test_scoring]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
module_name: "decision_engine"
module_path: "src/supervisor/decision_engine"
responsibility: "Score upgrade options under treasury constraints and emit a deterministic decision packet"
depends_on:
  - "[[Performance Scoring]]"
  - "[[Treasury Management]]"
provides:
  - "[[Decision API]]"
---

# Decision Engine

## Definition

The code boundary that implements the Decision Making capability: it scores candidate upgrades against current office weaknesses under treasury constraints and returns a deterministic decision packet selecting the best upgrade (or "no upgrade needed").

## Purpose

Realizes the [[Supervisor Pattern]] in code — the algorithmic core of the Supervisor Office that turns evaluation evidence and budget state into an auditable, reproducible upgrade decision. Implements the [[Decision API]].

## Architecture Role

Primary module of [[Decision Making]] within [[systems/Supervisor Office]]. Consumes evaluation scorecards and treasury state; produces a [[Decision Packet Schema]] consumed downstream to drive the upgrade lifecycle.

## Inputs (or Dependencies)

- Current performance metrics + evaluation scorecards (from [[Performance Scoring]]).
- Upgrade catalog (options with costs).
- Treasury state (budget, deployed, available, spendLimit) from [[Treasury Management]].
- Institutional memory: excluded upgrade IDs from past failures.

## Outputs (or Provides)

- A [[Decision Packet Schema]] instance: selected upgrade_id, ranked options with scores + allowed/blocked status, rationale, treasury state.
- (Phase 7) UpgradeDecided event.

## Constraints

- Scoring is deterministic — no randomness in decision-making.
- Early exit: if the latest scorecard shows PnL > 0 AND calibration ≥ 65%, return "no upgrade needed".
- Institutional memory excludes previously failed upgrades from future rounds.
- Treasury is burned on EVERY attempt; budget exhaustion halts upgrade activity.

## Implementation Notes

Concrete plan (grounded in `wiki/agents/Supervisor Decision Engine.md` Decision Algorithm, Scoring Function, and Treasury Mechanics):

1. `scoring.py`: pure weighted scoring over weakness dimensions — disagreement, confidence, convergence, cost efficiency, PnL capture. With scorecard evidence, adjust by realized PnL, drawdown, latency, disagreement %, calibration.
2. `decision_engine.py` `DecisionEngine.decide(state)`:
   a. Early-exit check (PnL > 0 and calibration ≥ 65%) → return NOOP packet.
   b. Score every catalog option via `scoring.py`.
   c. Budget + exclusion filter: drop options exceeding available treasury or in excluded-IDs memory; record a `blocked_reason`.
   d. Rank remaining options by weighted score; select the highest.
   e. Emit the decision packet (selected upgrade_id, ranked options, rationale, treasury_state_after).
3. Treasury accounting: every `decide()` that applies an upgrade decrements treasury, including failed experiments ("you pay for failed experiments").
4. Determinism enables exact-output unit tests (`test_scoring.py`, `test_decision_engine.py`) with fixed inputs.

## Open Questions

- Implemented and tested 2026-06-06 (12 tests green): `[[decision_engine.py]]`, `[[scoring.py]]`, `[[models.py (supervisor)]]`; `[[test_decision_engine]]`, `[[test_scoring]]`. Status advanced planned/not-started → active/tested.
- Decision API `input_schema` resolved → [[Evaluation Scorecard Schema]] (SCHEMA-005), created this slice.
- Whether the multi-round evolution loop lives here or in Upgrade Evaluation (CAP-017).

## Relationships

### Implements
- [[Decision API]]

### Consumes
- [[Evaluation Scorecard Schema]]

### Produces
- [[Decision Packet Schema]]

### Contains
- [[decision_engine.py]]
- [[scoring.py]]
- [[models.py (supervisor)]]

### Validated By
- [[test_decision_engine]]
- [[test_scoring]]

### Depends On
- [[Performance Scoring]]
- [[Treasury Management]]

### Realizes
- [[Supervisor Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Supervisor Pattern Methodology]]
