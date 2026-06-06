---
type: capability
canonical_id: CAP-009
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
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "exposure-tracking"
parent_system: "[[systems/Risk Control]]"
implemented_by: []
interfaces: []
---

# Exposure Tracking

## Definition

The capability to calculate current portfolio exposure, detect threshold breaches, and trigger circuit-breaking behavior when risk limits are approached or exceeded.

## Purpose

Provides the quantitative risk state that Guardrail Enforcement uses for validation decisions. Tracks aggregate exposure across all positions and strategies.

## Architecture Role

Supporting capability within Risk Control. Feeds exposure data to Guardrail Enforcement for predicate evaluation.

## Inputs

- Current portfolio state from Trading Engine
- Position sizes, correlations, sector concentrations

## Outputs

- Aggregate exposure metrics
- Threshold breach alerts

## Relationships

### Contains

### Depends On

### Provides
- Exposure data to [[Guardrail Enforcement]]

### Realizes
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
