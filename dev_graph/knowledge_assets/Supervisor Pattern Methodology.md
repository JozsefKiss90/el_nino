---
type: knowledge_asset
canonical_id: KA-003
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - external
source_paths:
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/agents/Supervisor Decision Engine.md"
  - "raw/ows-dev-squad.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
knowledge_id: "KA-003"
knowledge_type: methodology
source_wiki_pages:
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/agents/Multi-Agent Orchestration.md"
informs_decisions: []
informs_architecture:
  - "[[Context Map]]"
external_references:
  - "raw/ows-dev-squad.md"
---

# Supervisor Pattern Methodology

## Definition

The engineering methodology where a meta-agent (supervisor) assembles, evaluates, and upgrades a team of specialized worker agents under resource constraints. The supervisor IS the product — individual agents are replaceable components. Derived from the OWS Dev Squad architecture.

## Purpose

Explains WHY the Supervisor Office exists as a distinct bounded context with treasury management, upgrade evaluation, and team orchestration capabilities. The supervisor is not just an orchestrator — it is a resource-constrained decision maker that learns from interventions.

## Architecture Role

Foundational knowledge asset. Motivates the Supervisor Office system design, the Office Action Loop workflow, the Treasury Policy System, and the multi-agent coordination pattern.

## Core Principles

1. **The supervisor is the product**: Individual agents (Research, Strategy, Execution, Evaluator) are replaceable. The supervisor's ability to assemble and improve teams is the core value.
2. **Resource scarcity as design constraint**: Treasury limits force the supervisor to make economically rational decisions. Failed upgrades burn treasury — realistic accounting prevents trial-and-error waste.
3. **Evidence-based upgrades**: Paper trading results are the evidence that justifies upgrades. No upgrade proceeds without quantitative validation.
4. **Institutional memory**: The supervisor remembers which upgrades worked and which failed. Known-bad upgrades are excluded from future rounds.
5. **Deterministic evaluation**: Scoring functions use weighted multi-dimensional assessment (weakness severity, confidence, convergence, cost efficiency, PnL capture). No randomness in decision-making.
6. **Anti-theater layer**: The replay proof harness ensures the supervisor actually evaluates multiple upgrade paths, not just scripts a predetermined outcome.

## Architectural Constraints

- Every upgrade attempt deducts from treasury, successful or not
- Promotion requires quantitative thresholds: >=3 metrics improved, no regressions, >=12% average improvement
- The supervisor MUST have an early exit path: if the current scorecard is already promotable, no upgrade is needed
- Budget exhaustion halts all upgrade activity until treasury is replenished

## Relationships

### Provides
- Foundational methodology for multi-agent governance

### Used By
- [[Context Map]]

### Originates From
