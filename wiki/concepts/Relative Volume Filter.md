# Relative Volume Filter

## Definition

A conviction filter that compares current trading volume to the average volume over a lookback period. Trades are only taken when relative volume exceeds a minimum threshold, filtering out low-conviction setups.

## Purpose

Ensures trades are only executed when market participation confirms the signal. Prevents entering positions during low-liquidity, low-interest periods.

## Architecture Role

Final gate in [[Signal Confirmation]] chain: VWAP direction → EMA momentum → volume conviction. Part of [[Three-Layer Trading System]] Layer 2.

## Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Minimum relative volume | 1.5x average | [[SRC - Claude Stock Trader]] |

## Signal Logic

```
PASS: current_volume >= 1.5 × average_volume
FAIL: current_volume < 1.5 × average_volume → "filters out the low conviction setups"
```

## Inputs

- Current period volume
- Average volume over lookback window
- Threshold multiplier

## Outputs

- Boolean: pass/fail
- Relative volume ratio (current/average)

## Dependencies

- Volume data from [[Alpaca API]] or [[TradingView Integration]]
- Historical volume for average calculation

## Failure Modes

- **Opening volume spike**: First minutes of trading always have elevated volume → false conviction signal
- **News-driven volume**: Volume spike from news may not indicate a tradeable pattern
- **Thin instruments**: Average volume too low for meaningful relative comparison

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| 1.5x threshold | Filters weak setups but may miss moderate-conviction opportunities |
| Higher threshold (2x+) | Fewer trades, higher conviction, may miss opportunities |
| Time-of-day adjustment | More accurate but more complex |

## Related Concepts

- [[VWAP]]
- [[EMA Crossover]]
- [[Signal Confirmation]]
- [[Three-Layer Trading System]]
- [[Trading Engine Pipeline]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — "relative volume indicator to only enter when the volume is at least 1.5 times the average... filters out the low conviction setups"
