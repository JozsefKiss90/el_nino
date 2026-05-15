---
type: backtesting
domain: backtesting
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Backtesting, Historical Simulation]
confidence: single-source
tags: []
---

# Backtesting Methodology

## Definition

The process of evaluating a trading strategy by simulating its execution on historical market data. The primary tool for assessing strategy viability before live deployment.

## Purpose

Determines whether a strategy has a statistical edge before risking capital. Feeds into [[Walk-Forward Optimization]] and [[Overfitting Detection]] as the first validation step.

## Architecture Role

Validation stage in [[Trading Engine Pipeline]]. Gates promotion from development to [[Paper Trading]].

## Standard Backtesting Protocol

1. **Define universe**: Select instruments (e.g., 50 S&P 500 stocks)
2. **Define period**: Minimum 12 months of daily data
3. **Apply strategy**: Run strategy rules against historical data
4. **Record trades**: Log every entry, exit, P&L
5. **Compute metrics**: Win rate, risk-reward, Sharpe, max drawdown
6. **Validate**: Apply [[Walk-Forward Optimization]] if results look too good

Source: [[SRC - Claude Stock Trader]] — "back test this on the last 12 months of daily data across 50 S&P 500 stocks"

## Key Metrics

| Metric | Definition | Healthy Range |
|--------|-----------|---------------|
| Win Rate | % of profitable trades | 45-60% (with good R:R) |
| Risk-Reward Ratio | Average win / average loss | ≥ 1:2 |
| Sharpe Ratio | Risk-adjusted return | > 1.0 |
| Max Drawdown | Largest peak-to-trough decline | < 20% |
| Profit Factor | Gross profit / gross loss | > 1.5 |
| Expected Value | (WR × AvgWin) - (LR × AvgLoss) | > 0 |

## Inputs

- Historical price/volume data
- Strategy rules and parameters
- Transaction cost model

## Outputs

- Trade-by-trade results
- Aggregate performance metrics
- Equity curve
- Drawdown analysis

## Dependencies

- Historical data source ([[Alpaca API]], [[TradingView Integration]])
- Strategy definition
- [[Walk-Forward Optimization]] — for validation

## Failure Modes

- **[[Overfitting Detection|Overfitting]]**: Strategy memorizes past, fails in future
- **Look-ahead bias**: Accidentally using future information
- **Survivorship bias**: Only testing on surviving instruments
- **Transaction cost neglect**: Ignoring commissions, slippage, spreads
- **Small sample size**: Too few trades for statistical significance

## Related Concepts

- [[Walk-Forward Optimization]]
- [[Overfitting Detection]]
- [[Paper Trading]]
- [[Trading Engine Pipeline]]
- [[VWAP Crossover Strategy]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — backtesting on 12 months, 50 stocks, overfitting detection
