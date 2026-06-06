---
type: system
canonical_id: SYS-003
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
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "risk-control"
bounded_context: "Guardrail enforcement, exposure tracking, and circuit breaking. Provides the validation layer that all trades must pass before reaching the broker. Operates as a separate bounded context to ensure constraints cannot be bypassed by Trading Engine logic."
contains_capabilities:
  - "[[Guardrail Enforcement]]"
  - "[[Exposure Tracking]]"
upstream_systems:
  - "[[Trading Engine]]"
downstream_systems:
  - "[[Trading Engine]]"
---

# Risk Control

## Definition

Bounded context responsible for enforcing hard constraints, tracking portfolio exposure, and providing circuit-breaking capability. Every trade request from the Trading Engine must pass through Risk Control validation before reaching the broker. Risk Control exists as a SEPARATE system specifically because the LLM agent cannot be trusted to enforce constraints on itself.

## Purpose

Prevents runaway losses, unauthorized actions, and unbounded risk. The essential prerequisite before granting any agent autonomy. Implements the [[Guardrail Philosophy]] as a system boundary enforcement mechanism.

## Architecture Role

Cross-cutting validation layer. Receives trade validation requests from the Trading Engine and returns approve/block decisions. Positioned at the system boundary between the Trading Engine and broker APIs to ensure no trade bypasses validation.

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| Hard limit enforcement (position size, daily loss, max trades) | Signal generation |
| Exposure calculation and tracking | Order execution |
| Trade approval/rejection decisions | Strategy selection |
| Circuit breaking on threshold breach | Trade logging |
| Predicate evaluation (Position Size OK, Daily Loss Cap OK, etc.) | Performance scoring |

## Capabilities

2 capabilities (created in Phase 3):
1. **Guardrail Enforcement** (CAP-008) — evaluate predicates, enforce gates, approve/block trades
2. **Exposure Tracking** (CAP-009) — calculate current exposure, detect threshold breaches

## Key Interfaces

- **Risk Check API** (INT-003) — bidirectional with Trading Engine (receives validation requests, returns decisions)

## Constraints

- Risk validation MUST be external to the Trading Engine — the agent cannot validate its own trades
- Hard limits are non-negotiable — no reasoning can override max position size or daily loss cap
- Withdrawal capability is ALWAYS disabled at the credential level
- Configuration stored in environment variables and strategy files — not in agent-accessible memory

## Relationships

### Contains
- (Forward references: Guardrail Enforcement, Exposure Tracking — Phase 3)

### Depends On

### Provides
- Trade validation decisions to Trading Engine

### Constrained By

### Used By
- [[Trading Engine]]

### Originates From
- [[Guardrail Philosophy]]
- [[Agent Safety Principles]]
