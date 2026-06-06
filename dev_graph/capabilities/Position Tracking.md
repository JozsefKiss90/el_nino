---
type: capability
canonical_id: CAP-007
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
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "position-tracking"
parent_system: "[[systems/Trading Engine]]"
implemented_by: []
interfaces: []
---

# Position Tracking

## Definition

The capability to track all open positions, monitor real-time P&L, detect position exits (fills, stops, manual closes), and maintain current portfolio state.

## Purpose

Provides the real-time view of what the system currently holds. Essential for position sizing (prevents over-concentration), stop-loss management (knows which positions need stops), and trade logging (records exits).

## Architecture Role

State-tracking capability within the Trading Engine. Consumes fill and stop events, maintains the current portfolio view that other capabilities query.

## Inputs

- Order fill confirmations from broker
- Stop trigger notifications
- Account state from broker API

## Outputs

- Current portfolio state (positions, sizes, P&L)
- PositionOpened, TradeClosed events (Phase 7)

## Constraints

- Position count must not exceed max concurrent positions guardrail
- Portfolio state must be consistent with broker state (reconciliation)

## Relationships

### Contains

### Depends On
- [[Order Management]] — fill data

### Provides
- Portfolio state to [[Stop-Loss Management]], [[Order Management]], [[Trade Logging]]

### Realizes
- [[Event Sourcing Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
