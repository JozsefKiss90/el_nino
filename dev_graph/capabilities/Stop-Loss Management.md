---
type: capability
canonical_id: CAP-006
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
  - "wiki/execution/Stop-Loss Systems.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "stop-loss-management"
parent_system: "[[systems/Trading Engine]]"
implemented_by: []
interfaces: []
---

# Stop-Loss Management

## Definition

The capability to place, monitor, and adjust stop-loss orders for all open positions using multiple stop types: fixed percentage, trailing, and floor-ratcheting.

## Purpose

Limits downside risk per position. Mandatory for every open position. Operates on a 5-minute monitoring cadence during market hours with a midday management routine.

## Architecture Role

Defensive capability within the Trading Engine. Runs continuously during market hours. Interacts with broker API for stop order placement and adjustment.

## Inputs

- Open position data from Position Tracking
- Stop configuration per strategy (fixed %, trailing %, floor-ratchet parameters)

## Outputs

- Stop orders placed/adjusted via broker API
- StopTriggered event when a stop is hit (Phase 7)

## Constraints

- Stop-loss placement is mandatory for every position — no position may exist without a stop
- Stop configuration is per-strategy (scalping: 0.3%, swing: 3%, trailing: 10%)
- Floor ratcheting: stop floor never moves down, only up as price rises

## Relationships

### Contains

### Depends On
- [[Position Tracking]]

### Provides
- Downside protection for all positions

### Realizes
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
