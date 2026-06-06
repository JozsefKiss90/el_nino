---
type: pattern
canonical_id: PAT-010
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/agents/Multi-Agent Orchestration.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "multi-agent-coordination"
pattern_type: coordination
instances:
  - "[[Team Orchestration]]"
realized_by_capabilities:
  - "[[Team Orchestration]]"
realized_by_modules: []
related_knowledge:
  - "[[Supervisor Pattern Methodology]]"
---

# Multi-Agent Coordination Pattern

## Definition

Multiple specialized agents are organized into functional desks (Research, Strategy, Execution, Evaluator) under centralized coordination. Each desk has a defined domain, upgrade target, and version state. Coordination is serialized through a single orchestrator.

## Structural Constraints

1. Each agent has a defined domain (desk) — no overlap between desks
2. Coordination flows through a single orchestrator — no peer-to-peer agent communication
3. Agent versions are tracked — each upgrade produces a new team version
4. Agents are stateless — continuity via shared memory files, not agent state
5. Only one upgrade is applied at a time — serialized change management

## When to Apply

Apply when multiple AI agents must work on different aspects of the same system with centralized governance and version control.

## Relationships

### Provides
- Structural guidance for multi-agent team management

### Realized By
- [[Team Orchestration]]

### Originates From
- [[Supervisor Pattern Methodology]]
