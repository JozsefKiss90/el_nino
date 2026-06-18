---
type: pattern
canonical_id: PAT-004
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Trading Engine Pipeline.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "pipeline"
pattern_type: structural
instances:
  - "[[Market Scanning]]"
  - "[[Feature Engineering]]"
  - "[[Gold Decision Generation]]"
  - "[[Order Management]]"
realized_by_capabilities:
  - "[[Market Scanning]]"
  - "[[Feature Engineering]]"
  - "[[Gold Decision Generation]]"
  - "[[Order Management]]"
realized_by_modules:
  - "[[Chain Orchestrator]]"
related_knowledge:
  - "[[Event Sourcing]]"
---

# Pipeline Pattern

## Definition

A linear sequence of processing stages where the output of each stage feeds as input to the next. Each stage has a single responsibility, defined inputs/outputs, and can be independently tested and replaced.

## Structural Constraints

1. Stages execute sequentially (no parallel branches within the pipeline)
2. Each stage has exactly one input type and one output type
3. Stages are independently deployable and testable
4. Failure in any stage halts the pipeline (fail-fast)
5. The pipeline can be extended by adding stages at the end

## When to Apply

Apply for any multi-step data transformation or processing flow: market data → features → snapshots → signals → orders.

## Relationships

### Provides
- Structural guidance for sequential processing flows

### Realized By
- [[Market Scanning]]
- [[Feature Engineering]]
- [[Gold Decision Generation]]
- [[Order Management]]
- [[Chain Orchestrator]]

### Originates From
- [[Event Sourcing]]
