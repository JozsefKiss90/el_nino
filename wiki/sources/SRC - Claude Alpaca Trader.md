---
type: source
domain: sources
source_file: raw/calude_alpaca_trader.md
source_type: youtube_transcript
date_ingested: 2026-05-15
created: 2026-05-15
updated: 2026-05-15
status: active
confidence: single-source
tags: []
---

# SRC - Claude Alpaca Trader

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/calude_alpaca_trader.md` |
| Type | YouTube transcript |
| Topic | Three levels of Claude + Alpaca trading: basic setup, copy trading bot, options Wheel Strategy |
| Capital | $50,000 paper trading (custom balance) |
| Date Ingested | 2026-05-15 |

## Summary

Three-tiered tutorial covering Claude Desktop + Alpaca stock trading at increasing sophistication. Level 1: basic Alpaca paper trading setup with custom $50K balance, Claude Desktop connection, credential file persistence, simple buy/sell via conversation. Level 2: trailing stop bot with floor ratcheting (10% stop, 5% trail), `/schedule` command for 5-minute cron monitoring, ladder buying on dips. Level 2b: copy trading using [[Capital Trades Integration]] to track congressional stock filings, MCP plug-in for data access, automatic replication of politician trades, 2.2x S&P 500 return over 1-year backtest. Level 3: options fundamentals (calls, puts, premiums, strike, expiration), selling options as income generation, [[Wheel Strategy]] (sell cash-secured puts → assignment → sell covered calls → shares called away → repeat), Claude monitors positions every 15 minutes, picks expirations, rolls contracts.

## Key Concepts Extracted

- [[Alpaca API]] — paper trading with custom balance ($50K), credential file persistence, multiple paper accounts
- [[Paper Trading]] — custom balance accounts, strategy isolation via separate accounts
- [[Stop-Loss Systems]] — trailing stop with floor ratcheting logic, dynamic floor adjustment
- [[Position Sizing]] — ladder buying (scale-in) at predetermined dip levels
- [[Claude Routines]] — `/schedule` command, 5-minute and 15-minute monitoring intervals
- [[Options Trading]] — calls, puts, premiums, strike prices, expiration, insurance analogy, selling options
- [[Wheel Strategy]] — sell CSP → assignment → sell CC → called away → repeat
- [[Copy Trading Strategy]] — politician trade tracking, smart money concept, filing replication
- [[Capital Trades Integration]] — MCP-based congressional trade data service

## Strategies Demonstrated

| Strategy | Level | Account | Key Mechanics |
|----------|-------|---------|---------------|
| Trailing Stop Bot | 2 | Trading Claude ($50K) | Floor ratcheting, ladder buys, 5-min monitoring |
| Copy Trading | 2b | Son account (separate) | Capital Trades MCP, politician selection, daily check |
| Wheel Strategy | 3 | Trading Claude ($50K) | CSP → CC cycle, 15-min checks, premium tracking |

## Key Insights

- Multiple paper trading accounts enable strategy isolation
- Credential persistence in project files eliminates re-entry per session
- `/schedule` command creates ad-hoc cron jobs directly from conversation
- Congress disclosure delay does not negate edge because positions are long-duration (months/years, not day trades)
- Claude handles all Wheel Strategy management: picking expirations, rolling contracts, monitoring assignments
- Hard rules: "Never sell a put without cash to buy shares; never sell a call below cost basis"

## Performance Claims

- Copy trading strategy: 2.2x S&P 500 return over 1 year ($9,650 vs $7,000 gain on $50K starting capital)
- Politician Michael McCaul selected as copy target by algorithm (most active, top trader)

## Contradictions with Existing Wiki

- [[Guardrail Architecture]] states "No options ever" as behavioral rule (from [[SRC - Claude Opus Trader]])
- This source demonstrates full options-based [[Wheel Strategy]]
- Resolution: "No options ever" is a per-user/per-strategy guardrail configuration, not a universal system constraint

## Caveats

- Performance claim is backtested, not live-traded
- Self-reported results from YouTube content creator
- Congressional trading data has disclosure delay (up to 45 days)
- Options trading carries assignment risk and margin requirements
- No mention of options approval level requirements from brokerage
- Wheel Strategy example uses single stock (Tesla) — no portfolio diversification demonstrated
