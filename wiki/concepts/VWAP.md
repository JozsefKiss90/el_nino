---
type: concept
domain: concepts
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Volume Weighted Average Price]
confidence: confirmed
tags: [concept]
---

# VWAP

## Definition

Volume Weighted Average Price. The average price of an instrument weighted by volume over a given period. Represents the "fair value" benchmark that institutional traders monitor for intraday trading decisions.

## Purpose

Primary trend direction indicator in the autonomous trading stack. Price relative to VWAP determines bullish/bearish bias for intraday trades.

## Architecture Role

Core component of [[Signal Confirmation]] in [[Trading Engine Pipeline]] Stage 2. Used in:
- [[VWAP Crossover Strategy]]
- [[Three-Layer Trading System]] Layer 2
- Safety filter validation (price must be within threshold of VWAP)

## Calculation

```
VWAP = Σ(Price × Volume) / Σ(Volume)
```

Computed from session open. Resets daily for equities; may use rolling window for crypto.

## Usage in System

### As Trend Filter
- **Price > VWAP**: Bullish bias → look for long entries
- **Price < VWAP**: Bearish bias → look for short entries or stay out

### As Entry Signal (VWAP Crossover)
- Price crossing above VWAP with volume confirmation → long entry
- Price crossing below VWAP → potential exit or short

### As Safety Gate
The TradingView integration uses VWAP proximity as a validation criterion:
- "Price is within 1.5% of VWAP" — required for trade approval

Source: [[SRC - Claude TradingView Integration]]

## Inputs

- Intraday price data (OHLC)
- Intraday volume data
- Session start time

## Outputs

- Single VWAP line value per timestamp
- Price-to-VWAP deviation

## Dependencies

- Market data feed ([[Alpaca API]] or [[TradingView Integration]])
- Volume data availability

## Failure Modes

- **Low volume sessions**: VWAP becomes unreliable with thin volume
- **Pre-market data**: Including pre-market volume can skew VWAP
- **Crypto sessions**: No natural session boundary → must define window

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Session VWAP vs. rolling | Session resets daily; rolling provides continuity |
| Standalone vs. combined | VWAP alone has low signal quality; best with [[EMA Crossover]] and [[Relative Volume Filter]] |

## Related Concepts

- [[VWAP Crossover Strategy]]
- [[EMA Crossover]]
- [[Relative Volume Filter]]
- [[Signal Confirmation]]
- [[Three-Layer Trading System]]

## Implementation Notes

- Institutional traders "actually watch" VWAP — it has self-fulfilling properties due to wide adoption
- Best used on liquid instruments with consistent volume profiles
- Programmatic computation preferred over LLM estimation (see [[LLM Failure Modes in Trading]])

## Source References

- Source: [[SRC - Claude Stock Trader]] — "VWAP crossover for intraday trend direction... what institutional traders actually watch"
- Source: [[SRC - Claude TradingView Integration]] — VWAP as safety filter condition
