---
type: system
canonical_id: SYS-006
status: active
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
  - external
source_paths:
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/governance/Treasury Policy System.md"
  - "wiki/workflows/Office Action Loop.md"
  - "raw/ows-dev-squad.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "supervisor-office"
bounded_context: "Decision making, treasury management, upgrade evaluation, and team orchestration. The meta-governance system that decides HOW the trading system evolves. The supervisor is the product — individual agents are replaceable components."
contains_capabilities:
  - "[[Decision Making]]"
  - "[[Treasury Management]]"
  - "[[Upgrade Evaluation]]"
  - "[[Team Orchestration]]"
upstream_systems:
  - "[[Evaluation Loop]]"
  - "[[Agent Runtime]]"
downstream_systems:
  - "[[Trading Engine]]"
---

# Supervisor Office

## Definition

Bounded context responsible for meta-governance of the trading system: evaluating weaknesses, allocating treasury under policy constraints, selecting and applying upgrades, and orchestrating the agent team. Implements the Syndicate Squad architecture where the supervisor IS the product.

## Purpose

Governs system evolution. While other systems execute the trading pipeline, the Supervisor Office decides whether and how the pipeline should change. It manages the upgrade lifecycle from weakness diagnosis through treasury approval to evaluation and promotion/rejection.

## Architecture Role

Meta-governance system. Receives evaluation results from the Evaluation Loop, makes upgrade decisions constrained by treasury policy, and sends upgrade specifications to the Trading Engine. Operates on a longer cadence than the trading pipeline — upgrades are periodic, not per-trade.

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| Weakness diagnosis and scoring | Signal generation |
| Treasury budget management (budget, deployed, available, spendLimit) | Order execution |
| Upgrade option evaluation and selection | Risk validation |
| Upgrade simulation with deterministic deltas | Market data acquisition |
| Team version management | Trade logging |
| Office Action Loop state machine | Performance metric calculation |
| Institutional memory (excluded upgrade tracking) | Context assembly |

## Capabilities

4 capabilities (created in Phase 3):
1. **Decision Making** (CAP-015) — score upgrades, select best option, manage decision lifecycle
2. **Treasury Management** (CAP-016) — track budget, enforce spend policy, approve/deny spend requests
3. **Upgrade Evaluation** (CAP-017) — simulate upgrades, run paper trading, evaluate outcomes
4. **Team Orchestration** (CAP-018) — manage agent desk assignments, coordinate upgrade application

## Key Interfaces

- **Decision API** (INT-006) — downstream to Trading Engine (sends upgrade decisions)
- **Evaluation API** (INT-007) — upstream from Evaluation Loop (receives scorecards)
- **Treasury API** (INT-008) — internal (treasury policy enforcement)

## Constraints

- Every upgrade attempt deducts from treasury — successful or not
- Budget exhaustion halts all upgrade activity
- Spend limit caps individual upgrade cost
- Institutional memory excludes known-bad upgrades from future rounds
- The supervisor must have an early exit path — no upgrade needed if scorecard is already promotable

## Relationships

### Contains
- (Forward references: Decision Making, Treasury Management, Upgrade Evaluation, Team Orchestration — Phase 3)
- [[Office Action Loop]] workflow (Phase 6)
- [[Paper Trading Work Cycle]] workflow (Phase 6)

### Depends On
- [[Evaluation Loop]] — receives evaluation results
- [[Agent Runtime]] — reads agent memory

### Provides
- Upgrade decisions to Trading Engine
- Team management and version control

### Constrained By

### Used By

### Originates From
- [[Supervisor Pattern Methodology]]
- [[Office Action Methodology]]
