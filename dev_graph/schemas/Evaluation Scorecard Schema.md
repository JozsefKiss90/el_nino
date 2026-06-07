---
type: artifact_schema
canonical_id: SCHEMA-005
status: active
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-07
confidence: confirmed
evidence:
  - design
  - wiki
  - code
source_paths:
  - "wiki/agents/Supervisor Decision Engine.md"
  - "wiki/strategies/Paper Trading.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Decision Layer Re-grounding]]"
schema_id: "evaluation-scorecard"
schema_version: "0.1.0"
schema_path: "src/supervisor/decision_engine/models.py"
validated_by: []
consumed_by:
  - "[[Decision Engine]]"
produced_by: []
---

# Evaluation Scorecard Schema

## Definition

The performance-evidence contract the Supervisor Office consumes to decide whether — and how — to upgrade. This is the SCHEMA-005 reserved by Population Strategy §4.6, and the input contract of the Decision API (INT-006).

## Scope

This artifact belongs to the **Supervisor Office treasury-upgrade decision path** — it is the performance-evidence input to the *upgrade* Decision Engine, **not** a gold trading evaluation contract. Its four fields are reusable as components, but a future Gold evaluation scorecard will be a separate node with a new canonical identifier. Governed by [[ADR - Decision Layer Re-grounding]].

## Purpose

Gives the Decision Engine a canonical, versioned input shape: the realized metrics that drive both the early-exit ("office is already promotable") check and the weakness scoring of upgrade options.

## Architecture Role

Input schema of the Decision API (INT-006). Produced by the Evaluation Loop (Performance Scoring, CAP-013 — module not yet built); consumed by the Decision Engine (MOD-002).

## Schema Definition

| Field | Type | Notes |
|-------|------|-------|
| realized_pnl | number | Realized P&L over the evaluation window (drives early-exit + pnl weakness) |
| calibration | number | Calibration score in [0,1] (≥0.65 contributes to promotable) |
| drawdown | number | Drawdown magnitude in [0,1] (drawdown weakness) |
| disagreement | number | Inter-agent disagreement fraction in [0,1] (disagreement weakness) |

## Validation Rules

- `calibration`, `drawdown`, `disagreement` are expected in [0,1].
- All four fields are required (the scorer reads each dimension).

## Open Questions

- `produced_by` is empty: the Performance Scoring module (Evaluation Loop) is out of this slice; link it when built. The transport (Evaluation API, INT-007) is also deferred.
- Additional fields (latency, convergence, confidence) noted in the Supervisor Decision Engine spec are deferred until the scorer uses them.

## Relationships

### Used By
- [[Decision Engine]]
- [[Decision API]]
- [[models.py (supervisor)]]

### Justified By
- [[ADR - Ontology Redesign]]
