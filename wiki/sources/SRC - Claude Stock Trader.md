---
type: source
domain: sources
source_file: raw/claude_stock_trader.md
source_type: youtube_transcript
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
tags: []
---

# SRC - Claude Stock Trader

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/claude_stock_trader.md` |
| Type | YouTube transcript |
| Topic | Claude Code + Alpaca automated stock trading |
| Capital | $10,000 paper trading |
| Duration | 5 trading days |
| Date Ingested | 2026-05-09 |

## Summary

Documents building an automated stock trading system using Claude Code and Alpaca API in one afternoon (~4 hours). Claude designed its own strategy from historical data. Three-layer architecture: stock screener, strategy engine, execution engine. ~15 code files, all written by Claude. Tested for 5 days with 11.8% return.

## Key Concepts Extracted

- [[Three-Layer Trading System]] — screener / strategy / execution decomposition
- [[VWAP Crossover Strategy]] — Claude-designed strategy using VWAP + EMA + relative volume
- [[VWAP]] — "what institutional traders actually watch"
- [[EMA Crossover]] — 9/21 period configuration
- [[Relative Volume Filter]] — 1.5x threshold
- [[Walk-Forward Optimization]] — 74% → 53% win rate validation
- [[Overfitting Detection]] — "anything above 65% usually means overfitting"
- [[Backtesting Methodology]] — 12 months, 50 S&P 500 stocks
- [[Position Sizing]] — "based on account equity and risk parameters"
- [[Stop-Loss Systems]] — automatic stop-losses
- [[Alpaca API]] — "commission-free brokerage with free API"
- [[Claude Code]] — "AI coding agent, talk in plain English"
- [[Paper Trading]] — Alpaca paper trading environment

## Performance Data

| Day | Trades | Winners | Net P&L |
|-----|--------|---------|---------|
| Monday | 7 | 5 | +$338 |
| Tuesday | 9 | 6 | +$412 |
| Wednesday | 8 | 2 | -$271 |
| Thursday | - | - | +$487 |
| **Week Total** | | | **+$1,187 (11.8%)** |

## Key Claim

Walk-forward validated: 53% win rate with 1:2.3 risk-reward ratio = "extremely profitable" and "what an actual edge looks like."

## Caveats

- 5-day sample is not statistically significant
- Self-reported results from YouTube content creator
- No transaction cost accounting mentioned
