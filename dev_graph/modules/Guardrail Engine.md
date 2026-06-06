---
type: module
canonical_id: MOD-001
status: planned
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: inferred
evidence:
  - design
  - wiki
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
module_name: "guardrail_engine"
module_path: "src/risk/guardrail_engine"
responsibility: "Evaluate trade-validation predicates and return approve/block decisions at the Risk Control boundary"
depends_on: []
provides:
  - "[[Risk Check API]]"
---

# Guardrail Engine

## Definition

The code boundary that implements the Guardrail Enforcement capability: it evaluates a conjunction of hard-limit trade-validation predicates and returns a single approve/block decision plus the identity of the first failing predicate.

## Purpose

Realizes the [[Guardrail Pattern]] in code and operationalizes the [[Guardrail Philosophy]] — an external validator the trading agent cannot reason around. Implements the [[Risk Check API]].

## Architecture Role

Primary module of [[Guardrail Enforcement]] within [[systems/Risk Control]]. Sits at the Trading-Engine → broker boundary. Stateless and synchronous: the caller blocks until a decision is returned.

## Inputs (or Dependencies)

- A [[Trade Validation Request Schema]] instance (trade params + portfolio context).
- Guardrail configuration from environment variables and the strategy file (`MAX_TRADE_SIZE`, `MAX_TRADES_PER_DAY`, `PORTFOLIO_VALUE`, `max_position_pct`).

## Outputs (or Provides)

- A [[Trade Validation Decision Schema]] instance: APPROVE or BLOCK, the triggering predicate, and a reason.
- (Phase 7) TradeApproved / TradeBlocked events.

## Constraints

- Hard limits are non-negotiable; no reasoning path overrides them (config lives outside agent-accessible memory).
- Predicate evaluation is a conjunction — ALL predicates must pass to APPROVE (Guardrail Pattern).
- Evaluation is synchronous and deterministic; identical inputs yield identical decisions.
- Missing configuration fails closed (BLOCK); withdrawal capability is always disabled at the credential level.

## Implementation Notes

Concrete plan (grounded in `wiki/risk/Guardrail Architecture.md` Hard Limits table + env/strategy config, and `wiki/risk/Autonomous Trading Risk Model.md` Risk Parameters):

1. Define a `Predicate` protocol: `evaluate(request, config) -> (passed: bool, reason: str)`.
2. Implement hard-limit predicates as pure functions in `predicates.py`:
   - `position_size_ok`: `request.size <= min(request.current_equity * max_position_pct, MAX_TRADE_SIZE)` (default `max_position_pct` = 5%).
   - `daily_loss_cap_ok`: `request.daily_pnl > -daily_loss_cap`.
   - `max_trades_ok`: `request.trades_today < MAX_TRADES_PER_DAY`.
   - `max_positions_ok`: `request.open_positions < max_positions` (default 3–5).
   - `withdrawal_disabled`: constant assertion (withdrawal flag ALWAYS false).
3. `guardrail_engine.py` `GuardrailEngine.validate(request)` evaluates the predicate list as a short-circuit conjunction: first failure → BLOCK with that predicate's reason; all pass → APPROVE.
4. Config loader reads env vars + strategy file; a missing value fails closed (never silently relax a limit).
5. Pure-function predicates make each independently unit-testable (`test_predicates.py`); the engine is integration-testable (`test_guardrail_engine.py`).

The predicate → gate mapping (Position Size OK / Daily Loss Cap OK / Withdrawal Disabled) will be promoted to gate/predicate nodes in Phase 6; not modeled here.

## Open Questions

- `related_tests` is empty by design — tests are produced by the first coding session (writeback), per the Phase 5 authoring rules.
- Whether circuit-breaking (Exposure Tracking, CAP-009) is composed here or kept a separate module.

## Relationships

### Implements
- [[Risk Check API]]

### Consumes
- [[Trade Validation Request Schema]]

### Produces
- [[Trade Validation Decision Schema]]

### Realizes
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Guardrail Philosophy]]
