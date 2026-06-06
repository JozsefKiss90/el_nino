---
type: pattern
canonical_id: PAT-003
status: active
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
pattern_id: "evaluation-loop"
pattern_type: behavioral
instances:
  - "[[Performance Scoring]]"
  - "[[Upgrade Evaluation]]"
realized_by_capabilities:
  - "[[Performance Scoring]]"
  - "[[Upgrade Evaluation]]"
realized_by_modules: []
related_knowledge:
  - "[[Paper Trading Validation]]"
---

# Evaluation Loop Pattern

## Definition

A cyclical pattern where system output is measured against defined metrics, scored into a structured scorecard, and fed back to governance for promotion or evolution decisions. The loop closes when evaluation results trigger new architectural decisions.

## Structural Constraints

1. Measurement uses quantitative metrics — not subjective assessment
2. Scorecards have defined healthy ranges and thresholds
3. Promotion requires passing defined criteria (not "looks good")
4. Results feed back to decision-making (closed loop)
5. Statistical significance must be assessed — short samples are flagged

## When to Apply

Apply whenever a system needs evidence-based evolution: strategy promotion, upgrade evaluation, performance benchmarking.

## Relationships

### Provides
- Structural guidance for evidence-based feedback loops

### Realized By
- [[Performance Scoring]]
- [[Upgrade Evaluation]]

### Originates From
- [[Paper Trading Validation]]
