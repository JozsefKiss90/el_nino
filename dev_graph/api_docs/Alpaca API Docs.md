---
type: api_doc_source
canonical_id: API-001
status: active
implementation_status: not-started
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - external
source_paths:
  - "wiki/integrations/Alpaca API.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
provider: "Alpaca"
doc_source: "https://docs.alpaca.markets"
doc_scope: "Trading API v2, Market Data API, Paper Trading API"
allowed_for_tasks:
  - "order execution implementation"
  - "position management"
  - "market data integration"
  - "paper trading setup"
  - "portfolio tracking"
freshness_requirement: required
---

# Alpaca API Docs

## Definition

API documentation source node for the Alpaca trading API. Canonical reference for all Alpaca integration code.

## Purpose

Ensures Claude Code sessions use current Alpaca API documentation rather than potentially stale training data when implementing trading operations.

## Architecture Role

Primary trading API documentation source. Alpaca is the brokerage layer for the autonomous trading engine, providing commission-free US equities trading with paper and live modes.

## API Scope

- **Trading API v2**: Orders (market, limit, stop, bracket), positions, portfolio, account
- **Market Data API**: Bars (OHLCV), quotes, trades, snapshots — both real-time and historical
- **Paper Trading API**: Sandbox environment using same API with different base URL
- **Crypto Trading**: Cryptocurrency trading via Alpaca

## Retrieval Method

**Primary**: context7 MCP
1. `resolve-library-id` with query "alpaca trading api"
2. Select best match
3. `query-docs` with specific implementation question

**Fallback**: Web fetch from `https://docs.alpaca.markets`

## Authentication

- API Key + Secret Key via environment variables
- Paper trading: separate key pair from live
- Withdrawal disabled by architecture (see wiki security governance)

## Wiki Reference

See `wiki/integrations/Alpaca API.md` for trading system integration patterns and architectural context.

## Version Notes

- API v2 is current
- Paper trading uses same endpoints with paper-api base URL
- Rate limits apply — check docs for current limits

## Relationships

### Depends On

### Provides
- Alpaca API documentation for implementation context packs

### Validated By

### Constrained By
- [[API Documentation Policy]]

### Supersedes

### Used By
- Future trading engine module nodes
- Future order execution file nodes

### Produces

### Consumes
