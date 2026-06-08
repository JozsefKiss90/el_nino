---
type: knowledge_asset
canonical_id: KA-002
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - design
source_paths:
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/systems/Architecture Overview.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
knowledge_id: "KA-002"
knowledge_type: principle
source_wiki_pages:
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/systems/Architecture Overview.md"
informs_decisions:
  - "[[ADR - Ontology Redesign]]"
informs_architecture:
  - "[[Layer Model]]"
  - "[[Context Map]]"
external_references: []
---

# CQRS

## Definition

Command Query Responsibility Segregation — the engineering principle that the model used to read data (queries) should be separated from the model used to write data (commands). In the trading engine, the read model (Layer 2 snapshots) is fundamentally different from the write model (order execution in Layer 3).

## Purpose

Explains WHY the Layer 2 snapshot is a read-only analytical assessment separate from the Layer 3 execution state. The snapshot is optimized for decision-making (query); the execution engine is optimized for order management (command).

## Architecture Role

Foundational knowledge asset. Motivates the separation between Data Pipeline (builds read models) and Trading Engine (executes commands). The Layer 2 Snapshot Schema is the canonical read model contract.

## Engineering Implications

1. **Snapshot ≠ portfolio state**: The L2 snapshot represents analytical truth (what the market looks like). Portfolio state represents execution truth (what positions we hold). These are different models with different update cadences.
2. **Read model is eventually consistent**: Snapshots may lag real-time market data by seconds to minutes. The execution engine must tolerate this.
3. **Write model is immediately consistent**: Order placement and fill recording must be transactional. No stale reads allowed in execution.
4. **Different optimization goals**: The snapshot model is optimized for analytical breadth (many indicators, many symbols). The execution model is optimized for transactional correctness (ACID properties, order state machines).

## Architectural Constraints

- The snapshot read model MUST be the sole input to signal generation — the execution engine does not independently read market data
- Order execution MUST NOT depend on the freshness of the snapshot — it uses the snapshot as a decision input but validates against real-time broker state before placing orders
- Schema changes to the snapshot read model are managed independently from execution model changes

## Relationships

### Provides
- Foundational principle for read/write model separation

### Used By
- [[Layer Model]]
- [[Context Map]]

### Originates From
