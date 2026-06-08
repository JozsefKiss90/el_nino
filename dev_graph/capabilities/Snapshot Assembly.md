---
type: capability
canonical_id: CAP-003
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
  - "wiki/systems/Three-Layer Trading System.md"
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "snapshot-assembly"
parent_system: "[[Data Pipeline]]"
implemented_by: []
interfaces:
  - "[[Snapshot API]]"
---

# Snapshot Assembly

## Definition

The capability to assemble feature vectors into a deterministic Layer 2 Snapshot — the single source of truth consumed by all downstream systems.

## Purpose

Produces the foundational data contract of the system. The L2 Snapshot is the boundary object between Data Pipeline and Trading Engine. Everything downstream (signal generation, risk validation, execution) consumes this snapshot.

## Architecture Role

Terminal capability in the Data Pipeline. Produces the output that crosses the system boundary via the Snapshot API. The most critical data contract in the ontology.

## Inputs

- Feature vectors from Feature Engineering

## Outputs

- Layer 2 Snapshot (versioned, timestamped, self-contained analytical assessment)
- SnapshotCreated event (Phase 7)

## Constraints

- Assembly MUST be deterministic — same inputs produce identical outputs
- Snapshot schema changes require an ADR (breaking change)
- Each snapshot is temporally independent — no references to previous snapshots

## Relationships

### Contains

### Depends On
- [[Feature Engineering]]

### Provides
- L2 Snapshots to [[Trading Engine]] via Snapshot API

### Validated By

### Constrained By

### Realizes
- [[CQRS Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Layer 2 Design Principles]]
