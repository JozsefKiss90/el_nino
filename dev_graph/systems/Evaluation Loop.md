---
type: system
canonical_id: SYS-005
status: active
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/strategies/Paper Trading.md"
  - "wiki/backtesting/Walk-Forward Optimization.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "evaluation-loop"
bounded_context: "Performance scoring, promotion validation, and system lifecycle management. Evaluates trading results, determines whether strategies are ready for live deployment, and manages the system's lifecycle state machine."
contains_capabilities:
  - "[[Performance Scoring]]"
  - "[[Promotion Validation]]"
upstream_systems:
  - "[[Agent Runtime]]"
downstream_systems:
  - "[[Supervisor Office]]"
---

# Evaluation Loop

## Definition

Bounded context responsible for evaluating trading performance, validating promotion readiness, and managing the system lifecycle state machine. Consumes trade data from the Agent Runtime, produces evaluation scorecards, and communicates promotion decisions to the Supervisor Office.

## Purpose

Closes the feedback loop in the engineering continuum. Without evaluation, the system cannot distinguish good strategies from bad ones, cannot promote from paper to live trading, and cannot trigger evolution. The Evaluation Loop is where EVIDENCE is generated.

## Architecture Role

Feedback system that connects implementation (Trading Engine results) back to governance (Supervisor Office decisions). Owns the System Lifecycle workflow that governs the entire system's operational state.

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| Performance metric calculation (win rate, Sharpe, drawdown, profit factor) | Trade execution |
| Scorecard generation | Signal generation |
| Promotion criteria evaluation (>=3 metrics improved, no regressions, >=12% improvement) | Treasury management |
| System lifecycle state management | Upgrade evaluation |
| Walk-forward validation support | Agent memory |

## Capabilities

2 capabilities (created in Phase 3):
1. **Performance Scoring** (CAP-013) — calculate metrics, generate evaluation scorecards
2. **Promotion Validation** (CAP-014) — evaluate promotion criteria, manage Paper Trading Promotion Gate

## Key Interfaces

- **Evaluation API** (INT-007) — downstream to Supervisor Office (sends evaluation results)
- Consumes trade data from Agent Runtime via Trade Log API

## Constraints

- Promotion requires quantitative thresholds — not subjective judgment
- Short sample periods must be explicitly flagged as statistically insignificant
- Walk-forward optimization (in-sample/out-of-sample) is the gold standard for overfitting defense

## Relationships

### Contains
- (Forward references: Performance Scoring, Promotion Validation — Phase 3)
- [[System Lifecycle]] workflow

### Depends On
- [[Agent Runtime]] — trade data source

### Provides
- Evaluation scorecards to Supervisor Office
- Promotion/rejection decisions

### Constrained By

### Used By
- [[Supervisor Office]]

### Originates From
- [[Paper Trading Validation]]
- [[Guardrail Philosophy]]
