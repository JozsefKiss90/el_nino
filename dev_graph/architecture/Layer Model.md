---
type: architecture
canonical_id: ARCH-003
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
  - "wiki/systems/Architecture Overview.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
architecture_type: layer_model
scope: "L1 (data) → L2 (analysis) → L3 (execution) architectural layer definitions"
---

# Layer Model

## Definition

Formal definition of the three architectural layers that structure the autonomous trading engine: Layer 1 (Data Ingestion), Layer 2 (Analysis & Strategy), and Layer 3 (Execution). Each layer has distinct responsibilities, data contracts, and failure modes.

## Purpose

Defines the canonical decomposition of the trading pipeline into layers with clear separation of concerns. The Layer 2 Snapshot is the foundational data contract — the single source of truth that connects analysis to execution.

## Architecture Role

Third architecture artifact. Defines the vertical decomposition (layers) that complements the horizontal decomposition (bounded contexts in Context Map). Systems span layers; layers span systems.

## Layer Definitions

### Layer 1: Data Ingestion

Responsibility: Acquire, clean, and store market data from external sources.

| Aspect | Definition |
|--------|-----------|
| Inputs | Raw market data from Alpaca API, TradingView, web research |
| Outputs | Cleaned candle data, ranked watchlist, feature vectors |
| Systems | Data Pipeline (primary) |
| Capabilities | Market Scanning, Feature Engineering |
| Data store | SQLite (candle history), in-memory (current features) |
| Failure modes | API rate limits, stale data, data provider outage |
| Cadence | Pre-market (daily scan), intraday (real-time feeds) |

### Layer 2: Analysis & Strategy (The Snapshot Layer)

Responsibility: Analyze market data and produce deterministic analytical snapshots that serve as the single source of truth for execution decisions.

| Aspect | Definition |
|--------|-----------|
| Inputs | Feature vectors from L1, indicator calculations |
| Outputs | Layer 2 Snapshot — point-in-time analytical assessment |
| Systems | Data Pipeline (Snapshot Assembly), Trading Engine (Signal Generation) |
| Capabilities | Snapshot Assembly, Signal Generation |
| Key contract | Layer 2 Snapshot Schema (SCHEMA-001) — the foundational data contract |
| Failure modes | Indicator miscalculation, stale features, overfitting to historical patterns |
| Cadence | Per-scan (new snapshot per market scan cycle) |

The Layer 2 Snapshot is the most important data contract in the system. Everything downstream (signal generation, risk validation, execution) consumes snapshots. Changes to the snapshot schema are breaking changes that cascade through the entire pipeline.

### Layer 3: Execution

Responsibility: Execute trades based on Layer 2 signals, manage positions, enforce risk constraints.

| Aspect | Definition |
|--------|-----------|
| Inputs | Signals from L2, risk parameters, portfolio state |
| Outputs | Orders placed, positions managed, trades logged |
| Systems | Trading Engine (primary), Risk Control (validation), Agent Runtime (logging) |
| Capabilities | Order Management, Stop-Loss Management, Position Tracking, Guardrail Enforcement |
| External | Alpaca API, Exchange APIs (broker integration) |
| Failure modes | Order rejection, partial fills, stop-loss gaps, API timeouts |
| Cadence | Real-time during market hours |

## Layer Interaction Model

```
L1 (Data) ──→ L2 (Analysis) ──→ L3 (Execution)
    ↑                                    │
    └────────── Feedback Loop ───────────┘
              (evaluation, refinement)
```

Data flows downward (L1 → L2 → L3). Feedback flows upward (evaluation results refine strategy, which refines data requirements). This feedback loop is the closed-loop continuum at the implementation level.

## Mapping to Systems

| Layer | Primary System | Supporting Systems |
|-------|---------------|-------------------|
| L1 | Data Pipeline | (external data providers) |
| L2 | Data Pipeline + Trading Engine | Risk Control (validation rules) |
| L3 | Trading Engine | Risk Control, Agent Runtime, Evaluation Loop |

## Constraints

- Layer boundaries are inviolable — L3 must never bypass L2 to access L1 data directly
- The L2 Snapshot Schema is the sole data contract between analysis and execution
- Each layer must be independently testable

## Relationships

### Depends On
- [[Context Map]]

### Provides
- Vertical decomposition model for the trading pipeline

### Contains

### Constrained By

### Used By
- System nodes (layer assignment)
- Interface nodes (layer boundary contracts)
- Schema nodes (layer data contracts)

### Originates From
