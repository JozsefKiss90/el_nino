---
type: pattern
canonical_id: PAT-005
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Architecture Overview.md"
  - "wiki/governance/Trade Logging.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "event-sourcing"
pattern_type: behavioral
instances:
  - "[[Trade Logging]]"
  - "[[Position Tracking]]"
realized_by_capabilities:
  - "[[Trade Logging]]"
  - "[[Position Tracking]]"
realized_by_modules: []
related_knowledge:
  - "[[Event Sourcing]]"
---

# Event Sourcing Pattern

## Definition

State changes are captured as an immutable, append-only sequence of domain events. Current state is derived by replaying the event history. The event log is both the state store and the audit trail.

## Structural Constraints

1. Events are immutable — once emitted, never modified
2. Events carry sufficient payload to reconstruct state without side-channel data
3. Current state is DERIVED from event replay, not stored independently
4. Event schemas are versioned — breaking changes require new event types
5. The event log is append-only — corrections are new events, not edits

## When to Apply

Apply for trade logging, position tracking, and any subsystem where audit trail, replay, and temporal queries are valuable.

## Relationships

### Provides
- Structural guidance for immutable event-driven state management

### Realized By
- [[Trade Logging]]
- [[Position Tracking]]

### Originates From
- [[Event Sourcing]]
