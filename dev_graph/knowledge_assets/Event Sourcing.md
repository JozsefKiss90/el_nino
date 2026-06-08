---
type: knowledge_asset
canonical_id: KA-001
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - design
source_paths:
  - "wiki/systems/Architecture Overview.md"
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
knowledge_id: "KA-001"
knowledge_type: principle
source_wiki_pages:
  - "wiki/systems/Architecture Overview.md"
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/governance/Trade Logging.md"
informs_decisions:
  - "[[ADR - Ontology Redesign]]"
informs_architecture:
  - "[[Runtime Topology]]"
external_references: []
---

# Event Sourcing

## Definition

The engineering principle that system state changes are captured as an immutable sequence of domain events rather than mutable state snapshots. Each event represents a fact that happened at a specific time. The current state is derived by replaying the event history.

## Purpose

Explains WHY the trading engine architecture is event-driven. Event sourcing enables replay (debugging past trades), audit trails (compliance), and temporal queries (what was the portfolio state at time T?).

## Architecture Role

Foundational knowledge asset. Motivates the event-driven runtime topology, trade logging requirements, and the design of domain events (SnapshotCreated, SignalGenerated, OrderPlaced, TradeLogged, etc.).

## Engineering Implications

1. **Every state change is an event**: Trade placement is an OrderPlaced event, not a mutation of a positions table. Stop triggering is a StopTriggered event, not a deletion.
2. **Events are immutable**: Once emitted, an event cannot be changed. Corrections are new events (OrderCancelled, TradeAdjusted).
3. **State is derived**: Current portfolio state is the result of replaying all trade events. This enables point-in-time queries.
4. **Audit trail is inherent**: The event log IS the audit trail. No separate compliance logging needed — trade logging captures everything.
5. **Replay enables debugging**: When a trade goes wrong, replay the event sequence to understand the decision chain.

## Architectural Constraints

- Modules MUST emit events at system boundaries (not internally)
- Events MUST carry sufficient payload to reconstruct state without side-channel data
- Event schemas MUST be versioned (breaking payload changes require a new event type)
- The trade log (Agent Runtime) is the canonical event store for the trading pipeline

## Relationships

### Provides
- Foundational principle for event-driven architecture

### Used By
- [[Runtime Topology]]

### Originates From
