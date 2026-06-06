---
type: pattern
canonical_id: PAT-001
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/agents/Supervisor Decision Engine.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "supervisor"
pattern_type: coordination
instances:
  - "[[Decision Making]]"
  - "[[Team Orchestration]]"
  - "[[Upgrade Evaluation]]"
realized_by_capabilities:
  - "[[Decision Making]]"
  - "[[Team Orchestration]]"
  - "[[Upgrade Evaluation]]"
realized_by_modules: []
related_knowledge:
  - "[[Supervisor Pattern Methodology]]"
---

# Supervisor Pattern

## Definition

A meta-agent governs a team of specialized worker agents under resource constraints. The supervisor evaluates weaknesses, allocates resources, selects and applies upgrades, and records whether upgrades improved the system. The supervisor IS the product — individual agents are replaceable.

## Structural Constraints

1. Single supervisor with authority over all worker agents
2. Resource-constrained decision making (treasury limits)
3. Evidence-based evaluation (paper trading / benchmarks before upgrade)
4. Institutional memory (past failures excluded from future attempts)
5. Deterministic scoring (no randomness in decisions)

## When to Apply

Apply when multiple autonomous agents need coordinated governance with resource scarcity constraints and evidence-based evolution.

## Relationships

### Composes
- [[Multi-Agent Coordination Pattern]]
- [[Treasury Approval Pattern]]

### Provides
- Structural guidance for multi-agent governance systems

### Realized By
- [[Decision Making]]
- [[Team Orchestration]]
- [[Upgrade Evaluation]]

### Originates From
- [[Supervisor Pattern Methodology]]
