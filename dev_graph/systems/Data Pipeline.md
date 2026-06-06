---
type: system
canonical_id: SYS-001
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
  - "wiki/systems/Architecture Overview.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "data-pipeline"
bounded_context: "Market data ingestion, feature engineering, and snapshot assembly. Owns the L1 (data) and L2 (analysis) layers. Produces the Layer 2 Snapshot — the single source of truth consumed by all downstream systems."
contains_capabilities:
  - "[[Market Scanning]]"
  - "[[Feature Engineering]]"
  - "[[Snapshot Assembly]]"
upstream_systems: []
downstream_systems:
  - "[[Trading Engine]]"
---

# Data Pipeline

## Definition

Bounded context responsible for acquiring market data from external providers, engineering features from raw data, and assembling deterministic Layer 2 Snapshots that serve as the single source of truth for the entire trading pipeline.

## Purpose

Transforms raw market data into structured, analytical snapshots that downstream systems consume for decision-making. The Data Pipeline owns the read model in the CQRS separation — it builds analytical views that the Trading Engine consumes.

## Architecture Role

First system in the pipeline. Maps to Layer 1 (Data Ingestion) and Layer 2 (Analysis & Strategy) in the [[Layer Model]]. Bounded on the upstream by external data providers (Alpaca API, TradingView, Perplexity) and on the downstream by the Trading Engine via the Snapshot API.

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| Market data acquisition from APIs | Order execution |
| Candle data storage (SQLite) | Position management |
| Feature engineering (indicators, rankings) | Risk validation |
| Watchlist generation (8-12 stocks) | Trade logging |
| Snapshot assembly and versioning | Agent memory |
| Indicator calculation (VWAP, EMA, RVOL) | Strategy selection |

## External Dependencies

- Alpaca Market Data API — real-time and historical price data
- TradingView — charting, signals, Pine Script indicators
- Perplexity API — market news and catalyst research

## Capabilities

3 capabilities (created in Phase 3):
1. **Market Scanning** (CAP-001) — scan universe, rank by momentum/volatility/ATR, produce watchlist
2. **Feature Engineering** (CAP-002) — calculate indicators, build feature vectors
3. **Snapshot Assembly** (CAP-003) — assemble L2 snapshot from features, version and publish

## Key Interfaces

- **Snapshot API** (INT-001, Phase 4) — downstream contract with Trading Engine
- **Market Data API** — upstream integration with Alpaca/TradingView (external)

## Constraints

- Snapshot assembly MUST be deterministic — same inputs produce same outputs
- The L2 Snapshot Schema is the most critical data contract in the system
- Data staleness must be detectable — snapshots carry timestamps

## Relationships

### Contains
- (Forward references: Market Scanning, Feature Engineering, Snapshot Assembly — Phase 3)

### Depends On

### Provides
- Layer 2 Snapshots to Trading Engine via Snapshot API

### Constrained By

### Used By
- [[Trading Engine]]

### Originates From
- [[CQRS]]
- [[Layer 2 Design Principles]]
- [[Event Sourcing]]
