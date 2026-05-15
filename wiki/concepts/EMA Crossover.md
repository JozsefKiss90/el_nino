---
type: concept
domain: concepts
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [EMA, Exponential Moving Average Crossover]
confidence: confirmed
tags: [concept]
---

# EMA Crossover

## Definition

Exponential Moving Average crossover signal. Uses two EMAs of different periods (fast and slow) to detect momentum shifts. When the fast EMA crosses above the slow EMA, it signals bullish momentum; when it crosses below, bearish.

## Purpose

Momentum confirmation layer in the indicator stack. Used in conjunction with [[VWAP]] and [[Relative Volume Filter]] for [[Signal Confirmation]].

## Architecture Role

Component of [[Three-Layer Trading System]] Layer 2 and [[Trading Engine Pipeline]] signal generation stage.

## Standard Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Fast EMA | 9-period | [[SRC - Claude Stock Trader]] |
| Slow EMA | 21-period | [[SRC - Claude Stock Trader]] |
| Alt: Fast EMA | 8-period | [[SRC - Claude TradingView Integration]] |

## Signal Logic

```
BUY: EMA_fast > EMA_slow (price above fast EMA in uptrend)
SELL: EMA_fast < EMA_slow (price below fast EMA in downtrend)
```

### As Trend Confirmation
- Price above 8 EMA confirms uptrend → used in scalping strategy safety filter
- Combined with VWAP: "price is above the VWAP AND price is above the EMA"

Source: [[SRC - Claude TradingView Integration]]

## Calculation

```
EMA = Price × k + EMA_prev × (1 - k)
k = 2 / (period + 1)
```

## Inputs

- Price series (close prices)
- Period parameter (fast and slow)

## Outputs

- Fast EMA line
- Slow EMA line
- Crossover signal (boolean: bullish/bearish)

## Dependencies

- Historical price data
- Timeframe selection (1min, 4hr, daily)

## Failure Modes

- **Whipsaw**: In ranging markets, EMAs cross frequently → false signals
- **Lag**: EMAs are lagging indicators → may signal after move has started
- **Timeframe sensitivity**: Different timeframes produce different signals

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Short periods (9/21) | More responsive but more whipsaw |
| Long periods (50/200) | Less noise but misses short-term moves |
| EMA vs. SMA | EMA weights recent data more; SMA is simpler |

## Related Concepts

- [[VWAP]]
- [[Relative Volume Filter]]
- [[Signal Confirmation]]
- [[VWAP Crossover Strategy]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — 9/21 EMA crossover for momentum confirmation
- Source: [[SRC - Claude TradingView Integration]] — 8 EMA uptrend confirmation in scalping strategy
- Source: [[SRC - Claude Cowork Trader]] — EMA crossover strategy research, Pine Script generation
