---
type: strategy
domain: strategies
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [VWAP Strategy, VWAP + EMA + RVOL Strategy]
confidence: single-source
tags: [strategy]
---

# VWAP Crossover Strategy

## Definition

An intraday trading strategy that uses price crossover of [[VWAP]] as the primary directional signal, confirmed by [[EMA Crossover]] momentum and [[Relative Volume Filter]] conviction. The canonical multi-indicator strategy in the Claude-assisted trading ecosystem.

## Purpose

Provides a systematic, rules-based entry/exit framework that can be fully automated. Designed by Claude Code through historical data analysis rather than human specification.

## Architecture Role

Default strategy implementation in [[Three-Layer Trading System]] and [[Trading Engine Pipeline]].

## Entry Rules (Long)

All conditions must be true simultaneously ([[Signal Confirmation]]):

1. Price crosses above [[VWAP]] → bullish trend direction
2. 9-period EMA above 21-period EMA → momentum confirmed ([[EMA Crossover]])
3. Current volume ≥ 1.5x average volume → conviction filter ([[Relative Volume Filter]])

## Exit Rules

- [[Stop-Loss Systems|Stop-loss]]: Fixed or trailing (configurable per deployment)
- Take-profit: Based on risk-reward ratio (target 1:2+)
- Time stop: Close before market close if intraday

## Validated Performance

| Metric | Pre-Validation | Post Walk-Forward |
|--------|---------------|-------------------|
| Win Rate | 74% | 53% |
| Risk-Reward | - | 1:2.3 |
| Expected Value | Suspect (overfitted) | Positive |

The 74% → 53% drop after [[Walk-Forward Optimization]] demonstrates that the initial strategy was overfitting. The validated 53%/1:2.3 profile represents a genuine edge.

Source: [[SRC - Claude Stock Trader]]

## Strategy Origin

Unique aspect: Claude was NOT told which indicators to use. The prompt asked it to "analyze the historical data and design its own strategy." Claude selected VWAP crossover + EMA + relative volume independently.

Source: [[SRC - Claude Stock Trader]]

## Dependencies

- [[VWAP]] — trend direction
- [[EMA Crossover]] — momentum confirmation
- [[Relative Volume Filter]] — conviction gate
- [[Position Sizing]] — capital allocation
- [[Stop-Loss Systems]] — risk management

## Failure Modes

- Choppy/sideways markets: VWAP crossovers are frequent and meaningless → Wednesday losses
- Low volume sessions: Relative volume filter may not save from poor signals
- Extended trends: May miss late-stage entries if VWAP diverges far from price

## Related Concepts

- [[Signal Confirmation]]
- [[Three-Layer Trading System]]
- [[Walk-Forward Optimization]]
- [[Overfitting Detection]]
- [[Backtesting Methodology]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — strategy design, validation, performance results
