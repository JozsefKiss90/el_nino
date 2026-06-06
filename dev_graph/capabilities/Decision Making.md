---
type: capability
canonical_id: CAP-015
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
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
  - "raw/ows-dev-squad.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "decision-making"
parent_system: "[[systems/Supervisor Office]]"
implemented_by: []
interfaces:
  - "[[Decision API]]"
---

# Decision Making

## Definition

The capability to score upgrade opportunities, select the best option under treasury constraints, and produce deterministic decision packets that govern system evolution.

## Purpose

The core intelligence of the Supervisor Office. Evaluates weaknesses using a weighted multi-dimensional scoring function (weakness severity, confidence, convergence, cost efficiency, PnL capture) and selects the upgrade most likely to improve the system.

## Architecture Role

Primary capability of the Supervisor Office. Drives the upgrade lifecycle from weakness diagnosis through option evaluation to decision output.

## Inputs

- Current performance metrics from Evaluation Loop
- Upgrade catalog (available upgrades)
- Treasury state (budget, deployed, available, spendLimit)
- Institutional memory (excluded upgrade IDs from past failures)
- Paper trading scorecards (when available)

## Outputs

- Decision packet (selected upgrade_id, ranked options, scores, rationale)
- UpgradeDecided event (Phase 7)

## Constraints

- Scoring is deterministic — no randomness in decision-making
- Early exit: if scorecard shows >0 PnL and >=65% calibration, return "no upgrade needed"
- Institutional memory excludes previously failed upgrades from future rounds
- Budget exhaustion halts all upgrade activity

## Relationships

### Contains
- (Forward: Supervisor Agent, Budget Available predicate — Phase 5/6)

### Depends On
- [[Performance Scoring]] — evaluation data
- [[Treasury Management]] — budget availability

### Provides
- Upgrade decisions to [[systems/Trading Engine]] via Decision API

### Realizes
- [[Supervisor Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Supervisor Pattern Methodology]]
