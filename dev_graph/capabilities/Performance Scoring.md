---
type: capability
canonical_id: CAP-013
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
  - "wiki/backtesting/Backtesting Methodology.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "performance-scoring"
parent_system: "[[systems/Evaluation Loop]]"
implemented_by: []
interfaces: []
---

# Performance Scoring

## Definition

The capability to calculate performance metrics from trade log data and produce evaluation scorecards that quantify strategy effectiveness.

## Purpose

Generates the EVIDENCE that drives promotion decisions. Without performance scoring, the system cannot distinguish good strategies from bad ones.

## Architecture Role

Analytical capability of the Evaluation Loop. Consumes trade data from Agent Runtime, produces scorecards consumed by Promotion Validation and Supervisor Office.

## Inputs

- Structured trade log from Trade Logging
- Benchmark comparison data (when available)

## Outputs

- Evaluation scorecard (win rate, Sharpe ratio, max drawdown, profit factor, expected value)
- EvaluationCompleted event (Phase 7)

## Key Metrics

| Metric | Healthy Range |
|--------|--------------|
| Win rate | 45-60% (with good risk-reward) |
| Risk-reward ratio | >= 1:2 |
| Sharpe ratio | > 1.0 |
| Max drawdown | < 20% |
| Profit factor | > 1.5 |

## Relationships

### Contains

### Depends On
- [[Trade Logging]] — trade data source

### Provides
- Scorecards to [[Promotion Validation]] and [[systems/Supervisor Office]]

### Realizes
- [[Evaluation Loop Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
