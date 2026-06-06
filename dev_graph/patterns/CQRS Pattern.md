---
type: pattern
canonical_id: PAT-009
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Three-Layer Trading System.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "cqrs"
pattern_type: structural
instances:
  - "[[Snapshot Assembly]]"
realized_by_capabilities:
  - "[[Snapshot Assembly]]"
realized_by_modules: []
related_knowledge:
  - "[[CQRS]]"
  - "[[Layer 2 Design Principles]]"
---

# CQRS Pattern

## Definition

The read model (analytical snapshots) is separated from the write model (order execution). Each model is independently optimized: the read model for analytical breadth and query performance, the write model for transactional correctness and order state management.

## Structural Constraints

1. Read model and write model have separate data stores
2. Read model is eventually consistent — may lag real-time by seconds to minutes
3. Write model is immediately consistent — ACID properties for order state
4. Cross-model communication uses defined interfaces (Snapshot API)
5. Schema changes to read model are independent of write model changes

## When to Apply

Apply when the data model optimized for reading (analysis, queries, dashboards) is fundamentally different from the model optimized for writing (transactions, state mutations, order management).

## Relationships

### Provides
- Structural guidance for read/write model separation

### Realized By
- [[Snapshot Assembly]]

### Originates From
- [[CQRS]]
- [[Layer 2 Design Principles]]
