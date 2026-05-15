---
type: execution
domain: execution
created: 2026-05-09
updated: 2026-05-15
status: active
aliases: [Stop-Loss, Trailing Stop, Stop Loss]
confidence: confirmed
tags: []
---

# Stop-Loss Systems

## Definition

Automatic exit mechanisms that close a position when the price moves against the trade beyond a defined threshold. Limits downside loss per trade.

## Purpose

Fundamental risk control. Ensures no single trade can cause unbounded loss. Required component of every strategy in the ecosystem.

## Architecture Role

Enforced in [[Trading Engine Pipeline]] Stage 4 (Execution) and monitored during position management. Part of [[Guardrail Architecture]].

## Stop-Loss Types

### Fixed Stop
Exit at a fixed percentage below entry price.
- Typical: 1-3% from entry
- Scalping variant: 0.3% from entry

### Trailing Stop
Stop level follows price upward, locking in profits as the trade progresses.
- Configuration: 10% trailing stop
- "Set 10% trailing stops" on market open routine

Source: [[SRC - Claude Opus Trader]]

#### Floor Ratcheting Logic

Advanced trailing stop variant where the floor only moves upward, never down:

1. **Initial floor**: Set at a fixed percentage below entry (e.g., 10% below)
2. **Ratchet trigger**: When stock rises, floor moves up to a tighter percentage below current price (e.g., 5% below)
3. **One-way ratchet**: Floor NEVER moves down — "the floor only goes up, never down"
4. **Automatic monitoring**: Agent checks every 5 minutes during market hours and adjusts floors

**Example**:
- Buy at $100, initial floor at $90 (10% stop)
- Stock rises to $110 → floor ratchets to $105 (5% below current)
- Stock dips to $105 → sell, still up $5 profit
- If stock drops immediately from $100 → hits $90 floor, sell, loss limited to $10

The floor ratcheting ensures that profits are progressively locked in as the trade moves favorably, while the initial stop limits maximum downside from entry.

Source: [[SRC - Claude Alpaca Trader]]

### Time-Based Stop
Exit position after a maximum holding period regardless of P&L.
- Used in paper trading: positions hit "target/stop/timeout"

Source: [[SRC - OWS Dev Squad]]

## Configuration by Strategy

| Strategy | Stop Type | Value | Source |
|----------|-----------|-------|--------|
| Equities (Claude Code) | Automatic | Per strategy | [[SRC - Claude Stock Trader]] |
| Routines (Opus) | Trailing | 10% | [[SRC - Claude Opus Trader]] |
| Scalping (TradingView) | Fixed | 0.3% | [[SRC - Claude TradingView Integration]] |
| Crypto (Co-work) | Fixed | 1% | [[SRC - Claude Cowork Trader]] |
| Trailing Stop Bot (Alpaca) | Trailing + Ratchet | 10% stop, 5% trail ratchet | [[SRC - Claude Alpaca Trader]] |

## Midday Routine Stop Management

The midday routine (noon) implements dynamic stop management:
- "Cut -7% losers and tighten stops on winners"
- This is an active portfolio management action, not just passive stop placement

Source: [[SRC - Claude Opus Trader]]

## Inputs

- Entry price
- Stop-loss percentage or dollar amount
- Position direction (long/short)

## Outputs

- Stop-loss order placed with exchange/broker
- Exit execution when stop is hit
- P&L at exit

## Dependencies

- [[Alpaca API]] or [[Exchange API Integration]] — order placement
- [[Position Sizing]] — stop distance influences position size
- [[Trade Logging]] — exit must be logged

## Failure Modes

- **Gap risk**: Price gaps through stop level → worse exit than expected
- **Stop hunting**: Market makers target common stop levels
- **API failure**: Stop order not placed → unlimited downside
- **Trailing stop in volatile market**: Premature exit on noise

## Related Concepts

- [[Position Sizing]]
- [[Guardrail Architecture]]
- [[Autonomous Trading Risk Model]]
- [[Trading Engine Pipeline]]
- [[Trade Logging]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — automatic stop-losses in execution engine
- Source: [[SRC - Claude Opus Trader]] — 10% trailing stops, midday stop management
- Source: [[SRC - Claude TradingView Integration]] — 0.3% fixed stop for scalping
- Source: [[SRC - Claude Cowork Trader]] — 1% stop-loss, 3% take-profit configuration
- Source: [[SRC - Claude Alpaca Trader]] — trailing stop with floor ratcheting, 5-minute monitoring schedule
