---
type: knowledge_asset
canonical_id: KA-011
status: active
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - ADR
source_paths:
  - "ultimateplan.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
knowledge_id: "KA-011"
knowledge_type: principle
source_wiki_pages:
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
informs_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
informs_architecture:
  - "[[Market Regime Classification]]"
external_references: []
---

# Regime Taxonomy

## Definition

The engineering principle that a small, enumerated set of **market regimes** — deterministic, snapshot-local macro-financial-conditions states — should sit as a named abstraction layer between raw derived features and trade-decision logic. A regime is a coarse, human-legible label (e.g. RISK_OFF, RESTRICTIVE_RATES, REFLATION) that summarizes "what kind of market is this snapshot."

## Purpose

Explains WHY regimes exist, WHY execution should depend on a regime abstraction rather than on raw features, and WHY a deterministic enumeration is superior to ad-hoc threshold logic embedded in a decision builder.

## Architecture Role

Foundational knowledge asset for [[Market Regime Classification]] (CAP-019) and [[ADR - Deterministic Regime Taxonomy]] (ADR-007). It motivates the seam between the Feature Layer (MOD-004 / SCHEMA-009) and the future Gold Decision Builder.

## Core Principles

1. **Why market regimes exist.** A market's behaviour is conditioned on its macro state — the same trade thesis behaves differently under restrictive real rates than under a liquidity-stress flight-to-safety. Naming the state lets every downstream rule reason about "what kind of market is this" instead of re-deriving it from raw numbers.
2. **Why execution depends on regimes.** Strategy edge, position sizing, and risk posture are regime-conditional. A decision layer that consumes a single regime label + provenance is simpler, more auditable, and more stable than one that re-implements threshold logic over a dozen raw features at every decision site.
3. **Why a deterministic abstraction beats threshold spaghetti.** Thresholds scattered across a decision builder are duplicated, drift independently, and are hard to test. A single enumerated taxonomy with a versioned rule table is replayable, fingerprint-guarded, and testable in isolation — and it changes only via a governed version bump.
4. **Why it belongs between Features and Gold Decisions.** Features are pure, snapshot-local measurements; Gold decisions are actions. The regime layer is the *interpretation* step in between — it adds semantic meaning to measurements without taking any action, preserving the analysis/execution separation.
5. **Determinism is non-negotiable.** Because the abstraction feeds replay-first, counterfactual paper-trading evaluation, the same snapshot must always map to the same regime. This forbids learning, history, hidden state, and clocks (see ADR-007).

## Architectural Constraints

- Regimes are enumerated and grounded in real, versioned features — never learned or inferred.
- The taxonomy is versioned (`taxonomy_version`); changes require a governed bump and a new/updated ADR.
- The regime layer consumes the Feature Vector (SCHEMA-009), never raw snapshots, and produces a regime contract (SCHEMA-010) — it never trades.

## Relationships

### Provides
- The conceptual foundation for a deterministic, enumerated regime abstraction layer

### Used By
- [[Market Regime Classification]]
- [[Regime Classification Pattern]]

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]

### Originates From
- [[Layer 2 Design Principles]]
