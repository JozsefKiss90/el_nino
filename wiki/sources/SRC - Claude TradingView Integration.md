---
type: source
domain: sources
source_file: raw/claude_tradingview.md
source_type: youtube_transcript
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
tags: []
---

# SRC - Claude TradingView Integration

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/claude_tradingview.md` |
| Type | YouTube transcript |
| Topic | Claude + TradingView + BitGet automated crypto trading |
| Platform | Mac (Windows/Linux tutorials in GitHub) |
| Date Ingested | 2026-05-09 |

## Summary

Documents connecting Claude to TradingView for chart reading and signal analysis, then to BitGet exchange for automated crypto trade execution. Features a "one-shot prompt" onboarding agent, Railway deployment for 24/7 operation, paper trading mode, safety filters, and accounting-optimized trade logging.

## Key Concepts Extracted

- [[TradingView Integration]] — MCP connection, chart reading, strategy development
- [[Exchange API Integration]] — BitGet API setup, permissions, 3-factor auth
- [[Webhook Architecture]] — TradingView → Claude → Exchange pipeline
- [[Railway Deployment]] — cloud hosting for 24/7 operation
- [[Signal Confirmation]] — VWAP + EMA + RSI scalping strategy
- [[Stop-Loss Systems]] — 0.3% fixed stop for scalping
- [[Paper Trading]] — paper trading mode toggle via env var
- [[Trade Logging]] — accounting-optimized logs for tax compliance
- [[Guardrail Architecture]] — safety filter that logs blocked trades with reason + values
- [[Position Sizing]] — configurable via env vars (portfolio value, max trade size, max trades/day)
- [[Environment Variable Management]] — .env file management, Railway env vars
- [[API Credential Isolation]] — withdrawal disabled, key security

## Architecture Pattern

Claude sits in the middle between TradingView and Exchange:
- TradingView and Exchange never talk directly
- Claude applies strategy rules and safety filters
- Blocked trades logged with specific failed condition and value

## One-Shot Prompt Pattern

Single prompt turns Claude into an onboarding agent that:
1. Sets up Whisper Flow (optional)
2. Chooses exchange, gets API keys
3. Opens .env file for editing
4. Configures guardrails via conversation
5. Connects TradingView
6. Deploys to Railway
7. Sets up trade logging
8. Tests with paper trading

## Strategy Scraping Pattern

Uses Apify API to scrape YouTube channel transcripts, then Claude deduces trading strategy from transcripts. Novel approach to strategy sourcing.

## Caveats

- Strategy described as "pulled out of my butt" — explicitly not financial advice
- Scalping on 1-minute charts is high-risk
- Railway costs for 24/7 operation
