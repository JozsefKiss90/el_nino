# Position Sizing

## Definition

The calculation of how much capital to allocate to each individual trade, based on account equity, risk parameters, and strategy-specific constraints. A core risk management mechanism.

## Purpose

Controls per-trade risk exposure. Prevents any single trade from causing catastrophic portfolio damage.

## Architecture Role

Component of [[Trading Engine Pipeline]] Stage 3 (Validation) and Stage 4 (Execution). Enforced by [[Guardrail Architecture]].

## Standard Parameters

| Parameter | Typical Value | Source |
|-----------|--------------|--------|
| Max portfolio % per position | 5% | [[SRC - Claude Opus Trader]] |
| Max single trade size | Configurable ($99, $100 in examples) | [[SRC - Claude TradingView Integration]] |
| Max concurrent positions | 3-5 | [[SRC - Claude Opus Trader]] |

## Sizing Logic

```
position_size = min(
    account_equity × max_position_pct,
    max_single_trade_size,
    risk_budget / stop_distance
)
```

The execution engine "calculates position size based on account equity and risk parameters."

Source: [[SRC - Claude Stock Trader]]

## Configuration via Environment

Position sizing parameters are stored in environment variables (`.env`):
```
PORTFOLIO_VALUE=500
MAX_TRADE_SIZE=99
MAX_TRADES_PER_DAY=67
```

These can be updated conversationally: "tell Claude to change it and it will just do it."

Source: [[SRC - Claude TradingView Integration]]

## Inputs

- Account equity (from [[Alpaca API]] or exchange)
- Risk parameters (from strategy/env)
- Stop-loss distance
- Current portfolio exposure

## Outputs

- Dollar amount for position
- Number of shares/contracts
- Remaining portfolio capacity

## Dependencies

- [[Stop-Loss Systems]] — stop distance determines risk-based sizing
- [[Guardrail Architecture]] — hard limits on position size
- [[Alpaca API]] or [[Exchange API Integration]] — account balance query

## Failure Modes

- **Stale balance**: Sizing based on outdated account equity
- **Concentration risk**: Multiple positions in correlated instruments
- **Sizing override**: LLM agent ignoring size limits (see [[LLM Failure Modes in Trading]])

## Related Concepts

- [[Stop-Loss Systems]]
- [[Guardrail Architecture]]
- [[Autonomous Trading Risk Model]]
- [[Trading Engine Pipeline]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — "calculates position size based on account equity and risk parameters"
- Source: [[SRC - Claude Opus Trader]] — max 5% per position
- Source: [[SRC - Claude TradingView Integration]] — configurable via env vars
