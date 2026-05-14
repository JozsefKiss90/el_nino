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
