---
type: capability
canonical_id: CAP-014
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
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "promotion-validation"
parent_system: "[[Evaluation Loop]]"
implemented_by: []
interfaces: []
---

# Promotion Validation

## Definition

The capability to evaluate whether a strategy's scorecard meets promotion criteria and to manage the Paper Trading Promotion Gate that controls the PaperTrading → Validated lifecycle transition.

## Purpose

Controls the most critical gate in the system lifecycle: the transition from simulated to live trading. Ensures no strategy goes live without quantitative evidence of viability.

## Architecture Role

Governance capability of the Evaluation Loop. Guards the promotion gate in the System Lifecycle workflow.

## Inputs

- Evaluation scorecard from Performance Scoring
- Promotion criteria thresholds

## Outputs

- Promotion decision (promote / reject)
- PromotionDecided event (Phase 7)

## Promotion Criteria (Syndicate Squad)

- >= 3 metrics improved over baseline
- No metric regressions
- >= 12% average relative improvement
- Statistical significance (minimum sample period)

## Constraints

- Promotion requires quantitative thresholds — not subjective judgment
- Short sample periods must be flagged as statistically insignificant

## Relationships

### Contains
- (Forward: Paper Trading Promotion Gate, Promotable Scorecard predicate, Paper Trading Mode predicate — Phase 6)

### Depends On
- [[Performance Scoring]]

### Provides
- Promotion decisions to [[Supervisor Office]]

### Realizes
- [[Promotion Pattern]]
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Paper Trading Validation]]
