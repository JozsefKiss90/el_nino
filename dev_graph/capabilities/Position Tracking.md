---
type: capability
canonical_id: CAP-007
status: active
implementation_status: in-progress
canonical: true
created: 2026-06-06
updated: 2026-06-16
confidence: confirmed
evidence:
  - design
  - wiki
  - ADR
  - code
source_paths:
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests:
  - "[[test_execution_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Execution Layer Planning]]"
capability_id: "position-tracking"
parent_system: "[[Trading Engine]]"
implemented_by:
  - "[[Execution]]"
interfaces: []
---

# Position Tracking

## Definition

The capability to track all open positions, monitor real-time P&L, detect position exits (fills, stops, manual closes), and maintain current portfolio state.

## Purpose

Provides the real-time view of what the system currently holds. Essential for position sizing (prevents over-concentration), stop-loss management (knows which positions need stops), and trade logging (records exits).

## Architecture Role

State-tracking capability within the Trading Engine. Consumes fill and stop events, maintains the current portfolio view that other capabilities query. Re-grounded by [[ADR - Execution Layer Planning]] (ADR-011 §4 / gate e) as the realizing capability of the [[Portfolio State Schema]] (SCHEMA-015) — the append-only, self-describing portfolio/position state the execution layer threads (consuming the [[Execution Record Schema]], SCHEMA-014); implemented by the portfolio module (candidate MOD-009) at STEP 3.

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

### Consumes
- [[Execution Record Schema]]

### Produces
- [[Portfolio State Schema]]

### Implemented By
- [[Execution]]

### Validated By
- [[test_execution_determinism]]

### Provides
- Portfolio state to [[Stop-Loss Management]], [[Order Management]], [[Trade Logging]]

### Realizes
- [[Event Sourcing Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
- [[ADR - Execution Layer Planning]]
