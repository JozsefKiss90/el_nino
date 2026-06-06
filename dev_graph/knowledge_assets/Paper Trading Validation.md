---
type: knowledge_asset
canonical_id: KA-010
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
source_paths:
  - "wiki/strategies/Paper Trading.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
knowledge_id: "KA-010"
knowledge_type: methodology
source_wiki_pages:
  - "wiki/strategies/Paper Trading.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/backtesting/Walk-Forward Optimization.md"
informs_decisions: []
informs_architecture:
  - "[[Context Map]]"
external_references: []
---

# Paper Trading Validation

## Definition

The engineering methodology that requires every trading strategy to pass simulated execution with real market data before live capital deployment. Paper trading is not optional — it is the mandatory evidence generation stage that justifies promotion to live trading.

## Purpose

Explains WHY the Evaluation Loop system includes a Paper Trading Promotion Gate, WHY the Syndicate Squad requires paper trading evidence for upgrades, and WHY the system lifecycle includes a PaperTrading state before Validated.

## Architecture Role

Foundational knowledge asset. Motivates the Evaluation Loop Pattern, the Promotion Pattern, the Paper Trading Promotion Gate, and the system lifecycle state machine.

## Core Principles

1. **Paper trading is mandatory**: No strategy bypasses simulated validation. This is a hard gate, not a suggestion.
2. **Real market data, virtual capital**: Paper trading uses the same API, same signals, same execution logic — only the capital is virtual. This minimizes behavior divergence between paper and live.
3. **Quantitative promotion criteria**: Promotion requires measurable evidence, not subjective judgment. Syndicate Squad thresholds: >=3 metrics improved, no regressions, >=12% average relative improvement.
4. **Strategy isolation**: Separate paper accounts per strategy enable independent performance tracking against each strategy's own starting capital.
5. **Walk-forward validation**: Beyond simple paper trading, strategies should pass walk-forward optimization — in-sample/out-of-sample validation that defends against overfitting.
6. **Statistical significance**: Short sample periods are explicitly flagged. 5-day paper trading results are encouraging but not statistically significant.

## Architectural Constraints

- The Paper Trading Promotion Gate MUST verify quantitative thresholds before allowing live deployment
- Paper trading mode MUST use the same code paths as live trading (only the broker endpoint differs)
- Paper trading duration must be sufficient for statistical significance (strategy-dependent minimum)

## Relationships

### Provides
- Foundational methodology for evidence-based strategy validation

### Used By
- [[Context Map]]

### Originates From
