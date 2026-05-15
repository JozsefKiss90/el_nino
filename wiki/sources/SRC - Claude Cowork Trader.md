---
type: source
domain: sources
source_file: raw/claude_cowork_trader.md
source_type: youtube_transcript
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
tags: []
---

# SRC - Claude Cowork Trader

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/claude_cowork_trader.md` |
| Type | YouTube transcript |
| Topic | Claude Co-work as crypto trading assistant |
| Exchange | Blofin |
| Date Ingested | 2026-05-09 |

## Summary

Introduces Claude Co-work as an agentic AI for crypto trading. Covers computer use, file access, scheduled tasks, cross-device continuity, and exchange API integration. Demonstrates connecting to Blofin exchange and TradingView webhook automation.

## Key Concepts Extracted

- [[Claude Co-work]] — agentic AI with computer use, file access, scheduling
- [[Exchange API Integration]] — Blofin API, futures account, API permissions
- [[Webhook Architecture]] — TradingView webhook → Claude Co-work → Exchange
- [[TradingView Integration]] — Pine Script generation via Claude
- [[API Credential Isolation]] — "enable trading, leave withdrawal disabled"
- [[EMA Crossover]] — trend following with EMA crossovers on 4-hour chart
- [[Stop-Loss Systems]] — 1% stop-loss, 3% take-profit configuration

## Claude Co-work vs. Regular Claude

| Feature | Regular Claude | Claude Co-work |
|---------|---------------|----------------|
| File access | No | Yes (folder-scoped) |
| Computer use | No | Yes (browser, apps) |
| Scheduled tasks | No | Yes (daily/weekly) |
| Cross-device | No | Yes |
| Memory | Per-session | Cross-session |

## Trading Use Cases

1. Market analysis on demand (4-hour chart analysis)
2. Trade journal and performance reports (CSV analysis)
3. Strategy research (EMA crossovers, Pine Script)
4. Daily briefings (scheduled 8 AM crypto news)
5. Direct exchange execution

## Key Security Insight

> "Enable trading permissions but leave withdrawal permission disabled. Even if something goes wrong your funds cannot be withdrawn."

## Caveats

- Promoted exchange (Blofin) with referral bonus — commercial content
- Computer use described as "research preview"
- Integration complexity may be underrepresented
