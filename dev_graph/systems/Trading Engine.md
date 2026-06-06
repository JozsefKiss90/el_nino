---
type: system
canonical_id: SYS-002
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
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/execution/Position Sizing.md"
  - "wiki/execution/Stop-Loss Systems.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "trading-engine"
bounded_context: "Signal generation from snapshots, order management, position tracking, and stop-loss management. Owns the L3 (execution) layer. Consumes L2 Snapshots and produces trades via broker APIs."
contains_capabilities:
  - "[[Signal Generation]]"
  - "[[Order Management]]"
  - "[[Stop-Loss Management]]"
  - "[[Position Tracking]]"
upstream_systems:
  - "[[Data Pipeline]]"
  - "[[Risk Control]]"
  - "[[Supervisor Office]]"
downstream_systems:
  - "[[Agent Runtime]]"
---

# Trading Engine

## Definition

Bounded context responsible for transforming Layer 2 analytical snapshots into trading decisions, executing orders through broker APIs, managing open positions, and enforcing stop-loss rules. The core execution system of the trading pipeline.

## Purpose

Converts analysis into action. Consumes snapshots from the Data Pipeline, generates signals, validates them against Risk Control, executes orders through broker APIs, and manages the lifecycle of each position from entry through exit.

## Architecture Role

Central system in the pipeline. Maps to Layer 3 (Execution) in the [[Layer Model]]. Bounded on the upstream by the Data Pipeline (Snapshot API) and Risk Control (Risk Check API), and on the downstream by broker APIs (Execution API) and Agent Runtime (Trade Log API).

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| Signal generation from L2 snapshots | Market data acquisition |
| Order routing and execution | Feature engineering |
| Position sizing calculation | Guardrail rule definition |
| Stop-loss placement and management | Performance scoring |
| Position lifecycle tracking | Treasury management |
| Broker API integration | Agent memory persistence |

## Capabilities

4 capabilities (created in Phase 3):
1. **Signal Generation** (CAP-004) — apply strategy rules to snapshots, produce trade signals
2. **Order Management** (CAP-005) — route orders, size positions, manage execution
3. **Stop-Loss Management** (CAP-006) — place and adjust stops (fixed, trailing, floor-ratcheting)
4. **Position Tracking** (CAP-007) — track open positions, monitor P&L, detect exits

## Key Interfaces

- **Snapshot API** (INT-001) — upstream from Data Pipeline (consumes snapshots)
- **Execution API** (INT-002) — downstream to broker (places orders)
- **Risk Check API** (INT-003) — lateral to Risk Control (validates trades)
- **Trade Log API** (INT-005) — downstream to Agent Runtime (logs trades)
- **Decision API** (INT-006) — upstream from Supervisor Office (receives upgrade decisions)

## Constraints

- Every trade MUST pass Risk Control validation before reaching the broker
- Position sizing MUST respect hard limits (max position %, max concurrent positions)
- Stop-loss placement is mandatory for every position
- The engine must tolerate broker API failures gracefully (retry, queue, or stand aside)

## Relationships

### Contains
- (Forward references: Signal Generation, Order Management, Stop-Loss Management, Position Tracking — Phase 3)

### Depends On
- [[Data Pipeline]] — consumes snapshots
- [[Risk Control]] — validates trades

### Provides
- Trade execution to broker APIs
- Trade data to Agent Runtime

### Constrained By

### Used By
- [[Agent Runtime]]
- [[Evaluation Loop]]

### Originates From
- [[Event Sourcing]]
- [[Layer 2 Design Principles]]
- [[Guardrail Philosophy]]
