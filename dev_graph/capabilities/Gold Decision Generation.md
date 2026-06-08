---
type: capability
canonical_id: CAP-020
status: active
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "GOLD_DECISIONPACKET_V0_BRIEF.md"
  - "src/gold/decision_builder/builder.py"
related_files: []
related_tests:
  - "[[test_decision_builder]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
  - "[[ADR - Decision Layer Re-grounding]]"
capability_id: "gold-decision-generation"
parent_system: "[[systems/Trading Engine]]"
implemented_by:
  - "[[Gold Decision Builder]]"
interfaces:
  - "[[Gold Decision API]]"
---

# Gold Decision Generation

## Definition

The capability to turn a Feature Vector (SCHEMA-009) + a Regime Classification (SCHEMA-010) into a deterministic, paper-trading **Gold DecisionPacket** (SCHEMA-011): a gold `direction` stance (the regime→direction policy) + `confidence`/`uncertainty` (the ADR-008 ordinal trust score) + the cited MOD-004 features + the L3 guard outcomes the packet honored. It produces a **paper-only planning artifact** (`decision_mode: paper_only`, instrument = gold/GLD proxy) — **not** a live trade signal, order, or broker instruction.

## Purpose

Give the (deferred) paper-trading runtime a single, replay-safe, auditable gold decision per snapshot, reasoning over the enumerated regime + features rather than re-deriving logic from raw data. Closes the gold lineage that [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) planned, now that all §8 Creation Gates pass.

## Architecture Role

An L3 decision capability under [[systems/Trading Engine]] (SYS-002). It **supersedes** the deprecated [[Signal Generation]] (CAP-004) as the Trading Engine's decision-producing pipeline stage, but with a fundamentally different basis: deterministic FeatureVector + RegimeClassification inputs (never raw snapshots or an indicator stack) and a paper-only DecisionPacket output (never a live order to Order Management). It is the gold counterpart to the treasury [[Decision Making]] (CAP-015, under SYS-006) and is **permanently separate** from it (ADR-004). Realizes the [[Pipeline Pattern]] (the successor pipeline stage); governed by ADR-006 + [[ADR - Gold Decision Confidence Semantics]] (ADR-008).

## Inputs

- A `RegimeClassification` (SCHEMA-010) from [[Market Regime Classification]] (CAP-019), via [[Regime Classification API]] (INT-007) — the primary input.
- A `FeatureVector` (SCHEMA-009) from [[Feature Engineering]] / Feature Builder (MOD-004) — for the confidence `coverage` term and feature citation.
- Optional L3 guard outcomes (ADR-006 §2/§6) + a versioned `DecisionPolicyConfig`.

## Outputs

- A `GoldDecisionPacket` (SCHEMA-011): `direction`, `confidence`/`uncertainty`, `regime`, cited features, `guard_refs`, provenance + the replay-key versions, via [[Gold Decision API]] (INT-009).

## Constraints

- **Deterministic, pure, fail-closed** — same snapshot + same versions ⇒ identical packet; INDETERMINATE ⇒ `direction = WATCH`.
- **Snapshot-local only** — no history, momentum, learning, hidden state, clock, randomness, or IO.
- **Input boundary** — consumes only SCHEMA-009 + SCHEMA-010 + optional L3 guards; never raw SCHEMA-001 (ADR-006 §2).
- **Feature grounding** — cites only the 14 real MOD-004 features (ADR-006 §5).
- **Confidence** — the ADR-008 ordinal trust score; never a probability; never wired to the treasury SCHEMA-005 calibration (ADR-004 separation).
- **Paper-only** — produces a planning artifact, never a live order; does not feed Order Management.

## Open Questions

- `implemented_by` → [[Gold Decision Builder]] (MOD-006), authored and tested (`implementation_status: tested`).

## Relationships

### Supersedes
- [[Signal Generation]]

### Provides
- [[Gold Decision API]]

### Consumes
- [[Feature Vector Schema]]
- [[Regime Classification Schema]]

### Produces
- [[Gold DecisionPacket v0 Schema]]

### Implemented By
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]

### Depends On
- [[Market Regime Classification]]

### Realizes
- [[Pipeline Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Gold Decision Confidence Semantics]]

### Originates From
- [[Layer 2 Design Principles]]
