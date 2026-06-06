---
type: pattern
canonical_id: PAT-007
status: active
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
pattern_id: "treasury-approval"
pattern_type: governance
instances:
  - "[[Treasury Management]]"
realized_by_capabilities:
  - "[[Treasury Management]]"
realized_by_modules: []
related_knowledge:
  - "[[Supervisor Pattern Methodology]]"
  - "[[Office Action Methodology]]"
---

# Treasury Approval Pattern

## Definition

A two-gate financial approval process where resource spend requests must pass both a per-item limit check (spendLimit) and an available balance check before approval. Failed attempts still deduct from the budget (realistic accounting).

## Structural Constraints

1. Two sequential gates: cost <= spendLimit AND cost <= available
2. Deduction occurs on attempt, not on success (burn-on-attempt)
3. Budget exhaustion permanently halts activity until replenishment
4. Audit trail records all deductions with rationale
5. Spend requests are serialized — no concurrent spending

## When to Apply

Apply for any resource allocation decision where scarcity is a design constraint and failed attempts have real cost.

## Relationships

### Provides
- Structural guidance for resource-constrained approval processes

### Realized By
- [[Treasury Management]]

### Originates From
- [[Supervisor Pattern Methodology]]
- [[Office Action Methodology]]
