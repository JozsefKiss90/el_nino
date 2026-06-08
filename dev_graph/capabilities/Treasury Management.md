---
type: capability
canonical_id: CAP-016
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
  - "wiki/governance/Treasury Policy System.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "treasury-management"
parent_system: "[[Supervisor Office]]"
implemented_by: []
interfaces:
  - "[[Treasury API]]"
---

# Treasury Management

## Definition

The capability to track treasury budget, enforce spend policy (spendLimit, available balance), approve or deny upgrade spend requests, and record treasury deductions.

## Purpose

Implements resource scarcity as a design constraint. Treasury limits force the supervisor to make economically rational decisions — failed upgrades burn treasury, preventing trial-and-error waste.

## Architecture Role

Governance capability of the Supervisor Office. Controls the financial gate that all upgrades must pass before execution.

## Inputs

- Spend requests from Decision Making
- Treasury state (budget, deployed, available, spendLimit)

## Outputs

- Approve / deny decisions
- Updated treasury state after deductions

## Treasury Model

- `budget`: Total allocated treasury
- `deployed`: Amount currently committed to upgrades
- `available`: `budget - deployed`
- `spendLimit`: Maximum single upgrade cost

## Policy Gates

1. `cost <= spendLimit` — single upgrade cost cap
2. `cost <= available` — sufficient balance check

## Constraints

- Every upgrade attempt deducts from treasury — successful or not (realistic accounting)
- Budget exhaustion permanently halts upgrades until replenished
- Audit trail tracks all deductions

## Relationships

### Contains
- (Forward: Treasury Approval Gate, Treasury Burn Rule constraint — Phase 6)

### Depends On

### Provides
- Spend decisions to [[Decision Making]]

### Realizes
- [[Treasury Approval Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Supervisor Pattern Methodology]]
