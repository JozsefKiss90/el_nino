---
type: artifact_schema
canonical_id: SCHEMA-007
status: planned
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: inferred
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
schema_id: "trade-validation-request"
schema_version: "0.1.0"
schema_path: "src/risk/schemas/trade_validation_request.py"
validated_by: []
consumed_by:
  - "[[Guardrail Engine]]"
produced_by: []
---

# Trade Validation Request Schema

## Definition

The data contract for a proposed-trade validation request submitted to the Risk Check API. It carries the trade parameters plus the portfolio context required to evaluate hard-limit guardrail predicates.

## Purpose

Defines exactly what the Guardrail Engine consumes so that predicate evaluation is total and deterministic. Promotes the implicit "proposed trade parameters + portfolio state" inputs of Guardrail Enforcement into a canonical, versioned shape.

## Architecture Role

Input schema of the Risk Check API (INT-003). Produced by the trade-proposing module (Signal Generation / Order Management — out of the first implementation slice), consumed by the Guardrail Engine (MOD-001).

## Schema Definition

| Field | Type | Notes |
|-------|------|-------|
| symbol | string | Ticker of the proposed trade |
| direction | enum(buy, sell) | Trade side |
| size | number | Proposed position size (USD or shares) |
| strategy_id | string | Originating strategy identifier |
| current_equity | number | Portfolio equity at evaluation time |
| daily_pnl | number | Realized + unrealized P&L for the day |
| trades_today | integer | Count of trades already executed today |
| open_positions | integer | Current count of open positions |

## Validation Rules

- `size` > 0; `direction` in {buy, sell}.
- All portfolio-context fields (`current_equity`, `daily_pnl`, `trades_today`, `open_positions`) are required — a missing value fails closed (treated as a BLOCK), never silently relaxed.

## Open Questions

- `produced_by` is empty: the trade-proposing module (Signal Generation / Order Management) is out of the first implementation slice; link it when that module node is created.
- Exact units of `size` (USD vs shares) to be fixed when the Guardrail Engine is coded.

## Relationships

### Used By
- [[Guardrail Engine]]
- [[Risk Check API]]

### Justified By
- [[ADR - Ontology Redesign]]
