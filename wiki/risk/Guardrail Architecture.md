# Guardrail Architecture

## Definition

The system of hard constraints, soft limits, and behavioral rules that prevent the autonomous trading agent from taking dangerous or unintended actions. Guardrails are non-negotiable — the LLM cannot reason its way around them.

## Purpose

Prevents runaway losses, unauthorized actions, and unbounded risk. The essential prerequisite before granting any agent autonomy.

## Architecture Role

Cross-cutting constraint layer enforced at [[Trading Engine Pipeline]] validation stage, [[Position Sizing]], and [[Stop-Loss Systems]].

## Guardrail Categories

### Hard Limits (Non-Negotiable)

| Guardrail | Type | Example |
|-----------|------|---------|
| Max position size | % of portfolio | 5% per position |
| Max concurrent positions | Count | 3-5 positions |
| Daily loss cap | Dollar/% | Configurable |
| Max trades per day | Count | Configurable |
| Withdrawal disabled | Boolean | ALWAYS false |
| Paper trading gate | Boolean | Must validate before live |

### Soft Limits (Configurable)

| Guardrail | Type | Example |
|-----------|------|---------|
| Trailing stop | % | 10% |
| Fixed stop-loss | % | 0.3% - 3% |
| Conviction threshold | Score | High (all indicators agree) |
| Research depth | Tokens | Budgeted per routine |

### Behavioral Rules

| Rule | Description |
|------|-------------|
| No options trading (configurable) | Per-strategy rule. Default: "No options ever." Can be overridden for options-based strategies like [[Wheel Strategy]]. See Contradictions below. |
| Max new positions/week | "Only buy three new positions per week" |
| Explicit "do nothing" | Standing aside is a valid action |
| Human review period | Monitor every run during initial deployment |

Source: [[SRC - Claude Opus Trader]]

## Why Guardrails Are Critical

> "Because the agent is going to be autonomous, it's going to be eager. If you don't give it guardrails it might just kind of start to go off the rails."

Source: [[SRC - Claude Opus Trader]]

The LLM has an action bias — it wants to trade. Without hard limits, it will find reasons to enter positions even when standing aside is optimal. See [[LLM Failure Modes in Trading]] — "Eager Agent Syndrome."

## Implementation

### Environment Variables
```
PAPER_TRADING=true
PORTFOLIO_VALUE=500
MAX_TRADE_SIZE=99
MAX_TRADES_PER_DAY=10
```

### Strategy File
```
max_position_pct: 5%
stop_loss_pct: 1%
trailing_stop_pct: 10%
min_conviction: all_indicators_agree
```

### CLAUDE.md
Agent identity file contains behavioral rules that are always loaded first:
- Trading restrictions
- Asset class limitations
- Operational hours
- Notification requirements

## Inputs

- Configuration (env vars, strategy files, CLAUDE.md)
- Current portfolio state
- Proposed trade parameters

## Outputs

- APPROVE or BLOCK decision
- Block reason (which guardrail triggered)
- Logged validation event

## Dependencies

- [[Position Sizing]] — enforces size limits
- [[Stop-Loss Systems]] — enforces stop placement
- [[Paper Trading]] — gates live deployment
- [[Agent Memory Architecture]] — stores guardrail config
- [[Environment Variable Management]] — parameter storage

## Failure Modes

- Guardrails coded as suggestions rather than hard constraints → LLM negotiates around them
- Configuration drift — guardrails accidentally relaxed over time
- Missing guardrail for new risk type

## Contradictions

### Options Trading Constraint

**Claim A**: "No options ever" — hard behavioral rule.
Source: [[SRC - Claude Opus Trader]]

**Claim B**: Full options-based [[Wheel Strategy]] demonstrated with Claude monitoring positions, picking expirations, and rolling contracts.
Source: [[SRC - Claude Alpaca Trader]]

**Resolution**: "No options ever" is a per-user/per-strategy guardrail configuration, not a universal system constraint. The Guardrail Architecture is designed to be configurable — different strategy profiles can enable or disable asset classes including options. Options-based strategies require explicit enablement and carry additional risk considerations documented in [[Options Trading]] and [[Autonomous Trading Risk Model]].

#contradiction

## Related Concepts

- [[Autonomous Trading Risk Model]]
- [[Position Sizing]]
- [[Stop-Loss Systems]]
- [[Paper Trading]]
- [[LLM Failure Modes in Trading]]
- [[Agent Self-Verification]]
- [[Options Trading]]
- [[Wheel Strategy]]

## Source References

- Source: [[SRC - Claude Opus Trader]] — guardrail philosophy, "eager agent," configuration approach
- Source: [[SRC - Claude TradingView Integration]] — safety filter, paper trading toggle, env var configuration
- Source: [[SRC - Claude Cowork Trader]] — withdrawal disabled, testing before live
- Source: [[SRC - Claude Alpaca Trader]] — options trading demonstrated as valid strategy, "no options" clarified as per-strategy config
