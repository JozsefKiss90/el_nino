---
type: capability
canonical_id: CAP-001
status: active
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "market-scanning"
parent_system: "[[Data Pipeline]]"
implemented_by: []
interfaces:
  - "[[Market Data API]]"
---

# Market Scanning

## Definition

The capability to scan a universe of instruments, rank them by technical characteristics (momentum, volatility, ATR), and produce a focused watchlist for downstream analysis.

## Purpose

Reduces the signal-to-noise ratio. From 200+ instruments, produces 8-12 high-probability candidates that warrant detailed analysis. Without scanning, the strategy engine would waste tokens analyzing instruments with no trading potential.

## Architecture Role

First capability in the Data Pipeline. L1 (data ingestion) entry point. Feeds ranked watchlist to Feature Engineering.

## Inputs

- Alpaca Market Data API (daily and intraday candles)
- Universe definition (top 200 by volume in S&P 500)

## Outputs

- Ranked watchlist of 8-12 instruments
- Stored candle data in SQLite

## Constraints

- Scan must complete before market open (pre-market routine, ~6 AM)
- Universe size must be bounded to manage API rate limits

## Relationships

### Contains

### Depends On

### Provides
- Ranked watchlist to [[Feature Engineering]]

### Validated By

### Constrained By

### Realizes
- [[Pipeline Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
