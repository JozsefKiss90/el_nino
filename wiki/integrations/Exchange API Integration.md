---
type: integration
domain: integrations
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Exchange APIs, BitGet API, Blofin API]
confidence: confirmed
tags: [integration]
---

# Exchange API Integration

## Definition

The pattern for connecting Claude-based trading systems to cryptocurrency exchanges via REST APIs. Covers authentication, order execution, and security practices across multiple exchanges.

## Purpose

Enables programmatic crypto trading. The exchange API is the execution venue for crypto strategies, analogous to [[Alpaca API]] for US equities.

## Architecture Role

Execution layer in [[Claude-Assisted Trading Stack]] for crypto assets. Connects to [[Trading Engine Pipeline]] Stage 4.

## Supported Exchanges

| Exchange | Auth Model | Key Features | Source |
|----------|-----------|-------------|--------|
| BitGet | API Key + Secret + Passphrase | Futures, spot, copy trading | [[SRC - Claude TradingView Integration]] |
| Blofin | API Key + Secret | Futures, TRC20 USDT deposits | [[SRC - Claude Cowork Trader]] |
| Binance | API Key + Secret | Largest exchange, broad asset coverage | Referenced as alternative |

## Authentication Pattern

Three-factor authentication (BitGet model):
1. **API Key**: Identifies the application
2. **Secret Key**: Signs requests
3. **Passphrase**: Additional authentication layer

**Critical Security**:
- Enable: trading permissions
- **DISABLE**: withdrawal permissions
- "Even if something goes wrong your funds cannot be withdrawn"

Source: [[SRC - Claude Cowork Trader]]

## Configuration

```
BITGET_API_KEY=...
BITGET_SECRET_KEY=...
BITGET_PASSPHRASE=...
BITGET_API_URL=https://api.bitget.com
```

Store ONLY in environment variables. See [[API Credential Isolation]].

## API Operations

| Operation | Description |
|-----------|-------------|
| Check balance | Verify account connectivity and available funds |
| Place order | Market/limit order with leverage, TP, SL |
| Cancel order | Remove pending orders |
| Get positions | List open positions |
| Get history | Trade history for logging |

## Example Trade Command

> "Open a long position on Bitcoin with $10 using five times leverage, set a take-profit at 3% and a stop-loss at 1%"

Source: [[SRC - Claude Cowork Trader]]

## Spot vs. Futures

For crypto trading, funds must typically be transferred from spot to futures account before API trading can begin. "Transfer it from your spot account to your futures account. This is important: your API will pull funds from your futures account."

Source: [[SRC - Claude Cowork Trader]]

## Inputs

- API credentials (from env vars)
- Order parameters (symbol, side, size, leverage, TP, SL)

## Outputs

- Order confirmation
- Position data
- Account balance

## Dependencies

- [[Claude Code]] or [[Claude Co-work]] — runtime
- [[Environment Variable Management]] — credential storage
- [[Position Sizing]] — order quantity
- [[Stop-Loss Systems]] — SL/TP configuration

## Failure Modes

- API key rotation invalidates existing credentials
- Rate limiting on high-frequency requests
- Exchange maintenance/downtime
- Network connectivity issues
- Incorrect fund transfer (spot vs. futures)

## Related Concepts

- [[Alpaca API]] — equities equivalent
- [[Claude-Assisted Trading Stack]]
- [[API Credential Isolation]]
- [[Trading Engine Pipeline]]
- [[Paper Trading]]

## Source References

- Source: [[SRC - Claude TradingView Integration]] — BitGet API setup, permissions, ENV configuration
- Source: [[SRC - Claude Cowork Trader]] — Blofin API setup, spot-to-futures transfer, trade execution
