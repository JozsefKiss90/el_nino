---
type: capability
canonical_id: CAP-018
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
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/agents/Multi-Agent Orchestration.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "team-orchestration"
parent_system: "[[systems/Supervisor Office]]"
implemented_by: []
interfaces: []
---

# Team Orchestration

## Definition

The capability to manage agent desk assignments, coordinate upgrade application across the agent team, and maintain team version state.

## Purpose

Operationalizes the supervisor's decisions. Once an upgrade is approved and evaluated, Team Orchestration applies it to the appropriate agent desk (Research, Strategy, Execution, Evaluator) and tracks the resulting team version.

## Architecture Role

Execution capability of the Supervisor Office. Translates high-level upgrade decisions into concrete agent team changes.

## Inputs

- Approved upgrade specification
- Current team composition and desk assignments

## Outputs

- Updated agent desk assignments
- Team version increment
- Applied upgrade record

## Constraints

- Only one upgrade may be applied at a time (serialized application)
- Team state must be persisted to session store after each change

## Relationships

### Contains
- (Forward: Action Orchestrator module — Phase 5)

### Depends On
- [[Decision Making]] — approved upgrades
- [[Upgrade Evaluation]] — validated upgrades

### Provides
- Team management to Supervisor Office

### Realizes
- [[Multi-Agent Coordination Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Supervisor Pattern Methodology]]
