---
type: decision_record
canonical_id: ADR-004
status: active
implementation_status: implemented
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - design
  - code
  - layer2
source_paths:
  - "ultimateplan.md"
  - "population_strategy.md"
  - "final_strategic_review.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Implementation Substrate]]"
decision_id: "ADR-004"
decision_date: 2026-06-07
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Decision Layer Re-grounding

## Status

Active — enacted 2026-06-07. The clarify-in-place updates to MOD-002 / INT-006 / SCHEMA-004 / SCHEMA-005 were applied in the same session that recorded this decision.

## Context

The ontology used the single word **"Decision"** for two distinct engineering concepts:

1. **Supervisor Office treasury-upgrade selection** — choosing which office self-improvement upgrade to buy under a treasury budget. This is what is actually implemented today: MOD-002 Decision Engine (`src/supervisor/decision_engine/`), INT-006 Decision API (`decide(state) -> decision_packet`), SCHEMA-004 Decision Packet (`selected_upgrade_id`, `ranked_options`, `rationale`, `treasury_state_after`), and SCHEMA-005 Evaluation Scorecard (`realized_pnl`, `calibration`, `drawdown`, `disagreement`).
2. **Gold trading decision generation** — the El Niño gold DecisionPacket v0 (`regime_class`, `allowed_actions`, `preferred_action`, scalar `confidence`+`uncertainty`, `invalidation_condition`, `duplicate_protection_key`, and a six-guard taxonomy). This does **not** exist as a node and is specified only in prose (`ultimateplan.md`), which flags the drift as the plan's greatest governance risk.

A read-only multi-agent audit (7 parallel audits → synthesis → 3 adversarial verifiers) confirmed: all four current nodes carry treasury-upgrade semantics, not gold trading. The same audit's adversarial pass **rejected** a proposed "Guard Mapper" next slice as redundant with the already-implemented `Snapshot Consumer.is_consumable()` gate and as emitting guard verdicts into a vacuum (no consumer until v0). Meanwhile, the upstream is now solid: SCHEMA-001 Layer 2 Snapshot + INT-001 Snapshot API provide a grounded, deterministic Layer-2 input, and MOD-003 Snapshot Consumer is implemented and tested.

Leaving the two concepts to share the name "Decision" invites a context pack or a future contributor to wire gold logic onto the treasury branch — the exact mis-grounding this graph is meant to prevent.

## Decision

1. **Designation.** MOD-002, INT-006, SCHEMA-004, and SCHEMA-005 are officially the **Supervisor Office treasury-upgrade decision branch**. Each was clarified in place with a `## Scope` section stating it is not the gold contract. Semantics, code, tests, and **canonical_ids are unchanged**.
2. **Separation.** The **Gold Trading Decision branch** SHALL be implemented as a separate bounded context with **new ontology objects and new canonical identifiers** (e.g. a Gold DecisionPacket v0 schema as a new `SCHEMA-00x`, never SCHEMA-004). The two branches coexist; an explicit mapping is documented when both exist.
3. **Immutability & no in-place reclassification.** Per [[Canonical Ownership]] and CLAUDE.md (canonical_id "NEVER changes, even if renamed or moved"), no canonical_id is reassigned. A node's type/semantics are **never reclassified in place**; a genuine type change requires the formal Split procedure (new ids + deprecate original + ADR). None of the four require a split — they are keep / clarify only.
4. **Deferred renames.** File renames (e.g. SCHEMA-005 → "Upgrade Weakness Scorecard") are deferred to avoid wikilink churn; they happen, if ever, at the moment the parallel gold node is created, so the link update is paid once.
5. **Gold v0 determinism invariant** (see below) is adopted as a binding design constraint for the future branch.
6. **Next slice.** The next deterministic implementation slice is **MOD-004 Feature Builder** (SCHEMA-001 → MOD-003 → MOD-004 → future Gold DecisionPacket v0). It is the smallest grounded slice and produces exactly the Layer-2-derived features required to later justify the v0 contract.

## Gold DecisionPacket Design Constraints (invariant of record)

> Gold DecisionPacket v0 may depend **only** on deterministic features derived from SCHEMA-001 and explicitly versioned upstream artifacts.

It MUST NEVER depend directly on: raw snapshot payloads, implicit runtime state, mutable caches, hidden memory, or non-versioned external context. This invariant exists to guarantee **deterministic replay and counterfactual evaluation** — the same `snapshot_id` (+ same versioned feature/contract definitions) must always reproduce the same decision. Of the six v0 guards, only `data_ok` and `freshness_ok` are directly snapshot-derived; `supervisor_ok` and `cooldown_ok` are Layer-3-filled stubs; `duplicate_ok` and `operational_ok` are new Layer-3 responsibilities — this asymmetry must be explicit when v0 is authored.

## Alternatives Considered

- **In-place reclassification** of the four nodes to gold semantics. **Rejected** — violates canonical_id immutability and the no-in-place-reclassify rule; would also throw away working, tested treasury code.
- **Rename the files now.** **Deferred** — a rename keeps the canonical_id but forces synchronous wikilink updates across several nodes for a cosmetic gain; do it just-in-time when the gold counterpart appears.
- **Guard Mapper as the next slice.** **Rejected** by adversarial verification — redundant with `Snapshot Consumer.is_consumable()`, the snapshot guards are already booleans (nothing to compute), and it would emit into a vacuum since v0 is deferred.
- **Author Gold DecisionPacket v0 now.** **Rejected** — premature; no deterministic SCHEMA-001-derived features yet exist to justify its `regime_class`/`confidence` inputs (just-in-time / contract-justified-by-features).

## Consequences

### Positive
- Preserves canonical_id immutability and the existing (tested) implementation investment.
- Eliminates the treasury-vs-gold semantic ambiguity at the point of retrieval (the `## Scope` notes are embedded in node bodies).
- Enables replay-safe trading decision contracts via the determinism invariant.
- Keeps ontology evolution governed (this ADR is the priority-0 record).

### Negative / Trade-offs
- Temporary coexistence of two decision branches under related names.
- Additional ontology objects later (the whole gold branch).
- An explicit mapping between the branches will be required.

### Risks
- The gold v0 spec remains prose-only until authored — drift risk persists; mitigated by the determinism invariant above and by gating v0 authoring on real derived features.

## Future Work

Gold Trading Decision artifacts are introduced **only after** deterministic Layer-2-derived features exist (the MOD-004 Feature Builder slice). They must never depend directly on raw Layer-2 payloads — only on versioned feature definitions and SCHEMA-001 identity. The three-component confidence variant (performance / calibration / sample_quality) is NOT adopted into the frozen v0 scalar `confidence`+`uncertainty` model without a formal amendment.

## Relationships

### Constrains
- [[Decision Engine]]
- [[Decision API]]
- [[Decision Packet Schema]]
- [[Evaluation Scorecard Schema]]

### Depends On
- [[Layer 2 Snapshot Schema]]
- [[Snapshot Consumer]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Layer 2 Design Principles]]
