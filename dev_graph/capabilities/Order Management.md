---
type: capability
canonical_id: CAP-005
status: active
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/execution/Position Sizing.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "order-management"
parent_system: "[[Trading Engine]]"
implemented_by: []
interfaces:
  - "[[Execution API]]"
---

# Order Management

## Definition

The capability to route trade signals to broker APIs, calculate position sizes, manage order lifecycle (placed → filled → cancelled), and handle partial fills and rejections.

## Purpose

Executes the trading decisions. Translates signals into broker API calls with correct position sizing, order types (market/limit), and error handling.

## Architecture Role

Central execution capability. Receives validated signals, calculates position size within guardrail limits, routes orders to broker, and tracks order state.

## Inputs

- Validated trade signals from Signal Generation (after Risk Control approval)
- Account state (equity, buying power, open positions)

## Outputs

- Placed orders via Execution API (broker)
- OrderPlaced, OrderFilled events (Phase 7)

## Constraints

- Position size MUST respect hard limits (max % of portfolio, max trade size)
- Orders MUST pass Risk Control validation before reaching broker
- Broker API failures must be handled gracefully (retry, queue, or stand aside)

## Relationships

### Contains

### Depends On
- [[Signal Generation]] — _DEPRECATED (CAP-004); live order routing is itself deferred (ADR-006 Non-Goals). The gold v0 successor [[Gold Decision Generation]] is paper-only and does NOT feed Order Management._
- [[Risk Control]] — trade validation

### Provides
- Executed orders to broker
- Order data to [[Trade Logging]]

### Realizes
- [[Pipeline Pattern]]
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
