---
type: capability
canonical_id: CAP-008
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
capability_id: "guardrail-enforcement"
parent_system: "[[systems/Risk Control]]"
implemented_by:
  - "[[Guardrail Engine]]"
interfaces:
  - "[[Risk Check API]]"
---

# Guardrail Enforcement

## Definition

The capability to evaluate trade validation predicates, enforce quality gates, and issue approve/block decisions for every trade request from the Trading Engine.

## Purpose

Implements the [[Guardrail Philosophy]] as a runtime enforcement mechanism. Evaluates predicates (Position Size OK, Daily Loss Cap OK, Withdrawal Disabled) and guards the Trade Validation Gate.

## Architecture Role

Primary capability of Risk Control. Positioned at the system boundary between Trading Engine and broker to ensure no trade bypasses validation.

## Inputs

- Trade validation requests from Trading Engine (symbol, direction, size, strategy)
- Current portfolio state (exposure, daily P&L, position count)
- Guardrail configuration (env vars, strategy files)

## Outputs

- TradeApproved / TradeBlocked decisions
- TradeApproved, TradeBlocked events (Phase 7)

## Constraints

- Hard limits are non-negotiable — no reasoning overrides them
- Validation is synchronous — the Trading Engine blocks until Risk Control responds

## Relationships

### Contains
- (Forward: Trade Validation Gate, Position Size OK predicate, Daily Loss Cap OK predicate, Withdrawal Disabled predicate — Phase 6)

### Depends On

### Provides
- Trade validation decisions to [[systems/Trading Engine]]

### Realizes
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Guardrail Philosophy]]
