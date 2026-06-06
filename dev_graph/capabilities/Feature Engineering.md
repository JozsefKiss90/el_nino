---
type: capability
canonical_id: CAP-002
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
  - "wiki/concepts/VWAP.md"
  - "wiki/concepts/EMA Crossover.md"
  - "wiki/concepts/Relative Volume Filter.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "feature-engineering"
parent_system: "[[systems/Data Pipeline]]"
implemented_by: []
interfaces: []
---

# Feature Engineering

## Definition

The capability to calculate technical indicators from raw market data and assemble them into structured feature vectors for each watchlist candidate.

## Purpose

Transforms raw price/volume data into analytical features that the strategy engine can evaluate. Indicator stack includes VWAP, EMA crossovers (9/21), and relative volume filters (>1.5x average).

## Architecture Role

Middle capability in the Data Pipeline. Bridges Market Scanning (raw data) and Snapshot Assembly (structured output). Part of L2 (analysis) layer.

## Inputs

- Watchlist from Market Scanning
- Raw candle data from SQLite

## Outputs

- Feature vectors per instrument (VWAP position, EMA state, RVOL ratio, momentum score)

## Constraints

- Indicator calculations must be deterministic — same input data produces same features
- Feature vectors must carry timestamps for staleness detection

## Relationships

### Contains

### Depends On
- [[Market Scanning]]

### Provides
- Feature vectors to [[Snapshot Assembly]]

### Validated By

### Constrained By

### Realizes
- [[Pipeline Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
