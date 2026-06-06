---
type: capability
canonical_id: CAP-011
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
  - "wiki/memory/Context Budget Engineering.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "context-assembly"
parent_system: "[[systems/Agent Runtime]]"
implemented_by: []
interfaces: []
---

# Context Assembly

## Definition

The capability to assemble the context window for each agent invocation within the token budget, prioritizing the most relevant information for the current task.

## Purpose

Manages the finite token budget (~200K per routine). Decides what to load: structural memory (~10%), operational memory (~15%), API calls (~20%), reasoning (~30%), output (~10%). Prevents context overflow while maximizing reasoning quality.

## Architecture Role

Intelligence capability of Agent Runtime. Determines what each agent session "sees" — the most critical influence on session quality.

## Inputs

- Available memory files and their token costs
- Current task type and requirements
- Token budget allocation model

## Outputs

- Assembled context window within budget
- Excluded items list (over budget)

## Constraints

- Context pack should target <50% of available context window for reasoning
- Prioritize: constraints > decisions > in-scope files > tests > related modules > docs
- If over budget, trim optional reads first

## Relationships

### Contains

### Depends On
- [[State Persistence]] — provides memory files to select from

### Provides
- Assembled context to executing agent

### Realizes
- [[Context Assembly Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Context Engineering]]
