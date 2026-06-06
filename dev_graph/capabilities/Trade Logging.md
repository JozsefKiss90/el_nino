---
type: capability
canonical_id: CAP-012
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
  - "wiki/governance/Trade Logging.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "trade-logging"
parent_system: "[[systems/Agent Runtime]]"
implemented_by: []
interfaces:
  - "[[Trade Log API]]"
---

# Trade Logging

## Definition

The capability to record structured trade journals for compliance, performance evaluation, and agent learning. Every trade — entry, exit, P&L, rationale — is logged as an immutable record.

## Purpose

Serves three purposes: compliance (audit trail), evaluation (performance scoring input), and learning (agent reviews past trades to refine strategy). The trade log IS the event store for the trading pipeline.

## Architecture Role

Logging capability of Agent Runtime. Consumes trade data from all execution activity, produces structured logs consumed by the Evaluation Loop.

## Inputs

- Trade execution data from Trading Engine (orders, fills, stops, closes)

## Outputs

- Structured trade log entries
- TradeLogged event (Phase 7)

## Constraints

- Trade logging is mandatory — no trade may go unlogged
- Log entries are append-only (immutable once written)
- Log format must support both human review and programmatic scoring

## Relationships

### Contains

### Depends On
- [[systems/Trading Engine]] — trade data source

### Provides
- Trade data to [[Performance Scoring]]

### Realizes
- [[Event Sourcing Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
