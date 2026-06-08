---
type: knowledge_asset
canonical_id: KA-005
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - external
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions: []
knowledge_id: "KA-005"
knowledge_type: principle
source_wiki_pages:
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
  - "wiki/strategies/Paper Trading.md"
informs_decisions:
  - "[[ADR - Implementation Substrate]]"
informs_architecture:
  - "[[Context Map]]"
external_references: []
---

# Guardrail Philosophy

## Definition

The engineering principle that autonomous agent autonomy MUST be preceded by hard, non-negotiable constraints that the agent cannot reason around. Guardrails are not suggestions — they are enforcement mechanisms that prevent dangerous actions regardless of the agent's reasoning.

## Purpose

Explains WHY the Risk Control system exists as a separate bounded context with its own enforcement capability, rather than as advisory guidance embedded in the Trading Engine. The LLM has an inherent action bias — it wants to trade. Guardrails counteract this bias with hard limits.

## Architecture Role

Foundational knowledge asset. Motivates the Guardrail Pattern, the Risk Control system boundary, all predicate and gate nodes, and the paper trading validation requirement.

## Core Principles

1. **Guardrails before autonomy**: No agent receives live trading capability until guardrails are validated. Paper trading is the mandatory precondition.
2. **Hard limits are non-negotiable**: Max position size, max concurrent positions, daily loss cap, withdrawal disabled — these cannot be overridden by agent reasoning.
3. **Soft limits are configurable**: Trailing stop percentages, conviction thresholds, and research token budgets can be adjusted per strategy without violating safety.
4. **The agent cannot reason around constraints**: Unlike human traders who might override their own rules, LLM agents must have constraints enforced externally at the system boundary, not internally via prompting.
5. **"Do nothing" is always valid**: Standing aside is an acceptable action. The agent is never forced to trade.
6. **Configuration is per-strategy**: Different strategies may have different risk parameters (scalping: 0.3% stops, swing: 3% stops), but all must operate within the hard limit envelope.

## Architectural Constraints

- Risk validation MUST occur at the system boundary (between Trading Engine and broker) — not within the Trading Engine's internal logic
- Guardrail configuration MUST be stored in environment variables and strategy files, not in agent memory (prevents agent modification)
- Every trade attempt MUST pass through the Trade Validation Gate before reaching the broker

## Relationships

### Provides
- Foundational principle for defensive constraint design

### Used By
- [[Context Map]]

### Originates From
