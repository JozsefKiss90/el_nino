# Trade Logging

## Definition

The mandatory practice of recording every trade action — executed, blocked, or failed — with complete metadata for compliance, performance evaluation, and strategy refinement.

## Purpose

Serves three functions: (1) accounting/tax compliance, (2) performance evaluation, (3) learning and strategy refinement. No trade should occur without a log entry.

## Architecture Role

Persistence layer in [[Trading Engine Pipeline]] Stage 5 (Journaling). Feeds into evaluation and [[Agent Memory Architecture]].

## Log Structure

Every trade log entry contains:

| Field | Description |
|-------|-------------|
| Timestamp | Exact time of action |
| Symbol/Pair | Instrument traded |
| Exchange | Where trade occurred |
| Action | Buy/Sell/Block |
| Entry Price | Price at entry |
| Exit Price | Price at exit (when closed) |
| Quantity | Position size |
| P&L | Profit/loss on trade |
| Strategy Signals | Which indicators triggered |
| Block Reason | If blocked, which condition failed and actual value |
| Notes | Agent reasoning, market context |

## Accounting Optimization

The TradingView integration generates trade logs specifically optimized for accountant consumption at tax time:

> "A system that logs for accounting purposes every single trade and every transaction. It's also going to be optimized exactly for how your accountant will need it when tax time comes."

Source: [[SRC - Claude TradingView Integration]]

## Block Logging

Even blocked trades are logged with:
- Which condition(s) failed
- Actual observed values
- Reason string

This enables strategy debugging. Example:
> "Blocked: RSI was 38.26, needs to be below 30 for buy signal"

Source: [[SRC - Claude TradingView Integration]]

## Inputs

- Trade execution data
- Signal/indicator values at decision time
- Block reasons (if applicable)
- Market context

## Outputs

- Trade log file (markdown or CSV)
- Performance metrics (aggregated)
- Tax-ready transaction records

## Dependencies

- [[Trading Engine Pipeline]] — provides trade data
- [[Agent Memory Architecture]] — stores log files
- [[Signal Confirmation]] — provides signal metadata

## Related Concepts

- [[Agent Memory Architecture]]
- [[Trading Engine Pipeline]]
- [[Autonomous Trading Risk Model]]
- [[Guardrail Architecture]]

## Source References

- Source: [[SRC - Claude TradingView Integration]] — accounting-optimized logs, block logging
- Source: [[SRC - Claude Opus Trader]] — trade log as memory file, EOD summaries
- Source: [[SRC - Claude Stock Trader]] — performance tracking (P&L per day)
