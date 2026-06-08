---
type: capability
canonical_id: CAP-004
status: deprecated
implementation_status: deprecated
canonical: true
created: 2026-06-06
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/strategies/Signal Confirmation.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "signal-generation"
parent_system: "[[systems/Trading Engine]]"
implemented_by: []
interfaces: []
---

# Signal Generation

> **DEPRECATED (2026-06-08).** Superseded by [[Gold Decision Generation]] (CAP-020). This capability described a wiki-derived intraday **indicator-stack** signal generator (VWAP/EMA/RVOL over raw L2 snapshots → buy/sell/hold trade signals routed to Order Management). It was never implemented, and its concept is obsolete against the realized deterministic pipeline (SCHEMA-001 → MOD-003 → MOD-004 → MOD-005 → Gold), which consumes versioned FeatureVectors + RegimeClassification and emits a paper-trading DecisionPacket, not a live trade signal. Decision recorded in [[ADR - Gold Decision Confidence Semantics]] §10; retained (not deleted) per the Deprecation Procedure; excluded from context packs by admissibility check #2. Permanently separate from the treasury [[Decision Making]] (CAP-015) per [[ADR - Decision Layer Re-grounding]].

## Definition

The capability to apply strategy rules to Layer 2 Snapshots and produce actionable trade signals with conviction scores.

## Purpose

Transforms analytical snapshots into trading decisions. Applies the indicator stack (VWAP crossover, EMA confirmation, RVOL conviction) and outputs buy/sell/hold signals with associated confidence.

## Architecture Role

First capability in the Trading Engine. Consumes L2 Snapshots from Data Pipeline, produces signals consumed by Order Management. Bridges L2 (analysis) and L3 (execution).

## Inputs

- L2 Snapshot from Snapshot Assembly (via Snapshot API)

## Outputs

- Trade signals (symbol, direction, conviction score, strategy rationale)
- SignalGenerated event (Phase 7)

## Constraints

- Signal generation MUST consume snapshots, not raw market data directly (CQRS separation)
- Multiple indicators must agree for high-conviction signals (Signal Confirmation pattern)

## Relationships

### Contains

### Depends On
- [[Snapshot Assembly]] — via Snapshot API

### Provides
- Trade signals to [[Order Management]]

### Realizes
- [[Pipeline Pattern]]
- [[Event Sourcing Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
