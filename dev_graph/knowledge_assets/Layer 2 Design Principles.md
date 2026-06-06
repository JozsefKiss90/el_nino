---
type: knowledge_asset
canonical_id: KA-006
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
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
knowledge_id: "KA-006"
knowledge_type: principle
source_wiki_pages:
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/systems/Architecture Overview.md"
informs_decisions: []
informs_architecture:
  - "[[Layer Model]]"
  - "[[Context Map]]"
external_references: []
---

# Layer 2 Design Principles

## Definition

The engineering principles governing the Layer 2 (Strategy Engine / Analysis) snapshot system — the deterministic truth layer that bridges data ingestion (L1) and execution (L3). The snapshot is a point-in-time analytical assessment that serves as the single source of truth for all downstream decisions.

## Purpose

Explains WHY the Layer 2 Snapshot is the foundational data contract of the entire system, and WHY changes to it are treated as breaking changes that cascade through the pipeline.

## Architecture Role

Foundational knowledge asset. Motivates the Snapshot Assembly capability, the Snapshot API interface, the Layer 2 Snapshot Schema, and the CQRS separation between analysis and execution.

## Core Principles

1. **The snapshot is truth**: The L2 snapshot represents the system's analytical assessment of the market at a point in time. All downstream decisions (signals, risk checks, order sizing) consume this snapshot, not raw market data.
2. **Deterministic assembly**: Given the same input data, the snapshot assembly process MUST produce the same output. No randomness, no external state dependencies beyond the input features.
3. **Schema stability**: The snapshot schema is the most critical contract in the system. Schema changes are breaking changes. Every downstream consumer must be updated when the schema changes.
4. **Temporal independence**: Each snapshot is independent — it contains everything needed for decision-making without reference to previous snapshots. This enables parallel processing and eliminates ordering dependencies.
5. **Separation from execution**: The snapshot layer does not know about positions, orders, or portfolio state. It analyzes the market; it does not trade.

## Architectural Constraints

- The L2 Snapshot Schema must be versioned (schema_version field on the artifact_schema node)
- Changes to the snapshot schema require an ADR
- All downstream modules must list the snapshot schema in their Consumes relationship section
- The snapshot must be fully self-contained — no side-channel data allowed

## Relationships

### Provides
- Foundational principle for the snapshot-as-truth-layer architecture

### Used By
- [[Layer Model]]
- [[Context Map]]

### Originates From
