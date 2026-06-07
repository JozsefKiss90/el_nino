---
type: decision_record
canonical_id: ADR-006
status: draft
implementation_status: not-started
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - design
  - ADR
source_paths:
  - "ultimateplan.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Feature Layer Contract]]"
decision_id: "ADR-006"
decision_date: 2026-06-07
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Gold DecisionPacket v0 Planning

## Status

**Proposed** (awaiting acceptance) — 2026-06-07.

This is a **governance and architectural-boundary** record. It does **not** author, define, or freeze the Gold DecisionPacket v0 schema. It establishes the constraints under which such a contract may *later* be created. (The dev_graph `status` enum has no `proposed` value; this node carries `status: draft` as its governed equivalent until accepted.)

## Context

The data path is `SCHEMA-001 → MOD-003 Snapshot Consumer → MOD-004 Feature Builder → (future) Gold DecisionPacket v0`. [[ADR - Decision Layer Re-grounding]] (ADR-004) gated any Gold DecisionPacket v0 on the prior existence of **real, deterministic, SCHEMA-001-derived features**, and [[ADR - Feature Layer Contract]] (ADR-005) operationalised that determinism for the feature layer. With MOD-004 [[Feature Builder]] implemented and tested and [[Feature Vector Schema]] (SCHEMA-009) published, that gate is now satisfied (dev_graph log, 2026-06-07: *"Gold DecisionPacket v0 is now grounded… a planning ADR for v0 is unblocked"*).

This ADR answers a deliberately narrow question:

> **Under what governance constraints may a Gold DecisionPacket contract be created?**

It does **not** answer *"what is the final Gold DecisionPacket contract?"* — that is left to a future, dedicated normative SCHEMA node authored only when the Creation Gates below are met.

The Gold Trading Decision layer must never be conflated with the **Supervisor Office treasury-upgrade decision branch** — [[Decision Engine]] (MOD-002), [[Decision API]] (INT-006), [[Decision Packet Schema]] (SCHEMA-004), and [[Evaluation Scorecard Schema]] (SCHEMA-005). Those nodes carry treasury-upgrade semantics (`selected_upgrade_id`, `ranked_options`, `treasury_state_after`), not gold trading semantics. They remain a **permanently separate** bounded context and are unchanged by this ADR.

## Decision

The following governance constraints bind any future Gold DecisionPacket v0. They are invariants of record; the contract, when authored, must satisfy them.

### 1. Bounded context & permanent separation
The Gold Trading Decision layer is a **net-new, permanently separate** bounded context, implemented with **new ontology objects and new canonical identifiers**. A Gold DecisionPacket is a *paper-trading planning artifact*. It is **not** a live execution command, **not** an order, **not** a broker instruction, **not** the treasury Decision Packet, and **not** INT-006 / SCHEMA-004 / MOD-002. The Supervisor Office decision artifacts and the Gold decision layer never merge, and neither is ever reclassified into the other.

### 2. Dependency rules / input boundary
A Gold DecisionPacket may consume **only**:
- deterministic [[Feature Vector Schema]] (SCHEMA-009) FeatureVectors,
- explicit, versioned schemas/artifacts, and
- future Layer-3 guard outputs (if and when those guards are authored).

It MUST NEVER consume:
- raw [[Layer 2 Snapshot Schema]] (SCHEMA-001) snapshots directly,
- raw snapshot JSON,
- external APIs,
- implicit or hidden runtime state,
- unversioned files, or
- history-dependent signals — unless a future, explicitly stateful ADR governs them.

### 3. Determinism / replay invariants
A Gold DecisionPacket must be **reproducible from versioned upstream artifacts only**. The binding replay invariant is:

> **Same `snapshot_id` + same `feature_schema_version` + same `model_version` + same `decision_policy_version` + same `configuration` ⇒ identical packet.**

No clock, randomness, external API call, or hidden state may influence a packet unless it is modelled as an explicit, versioned input above. This extends ADR-005's `(snapshot_id, schema_version) ⇒ identical feature vector` rule from the feature layer to the decision layer.

### 4. Provenance requirements
Every packet must trace to its `source_snapshot_id` and to the MOD-004 feature provenance of each feature it cites — `inputs` (SCHEMA-001 series_ids), `max_staleness_days`, and `revision_risk` per SCHEMA-009. Stale or revisable inputs must remain honestly flagged through to the decision; provenance is read from upstream artifacts, never inferred.

### 5. Feature grounding
Where a packet's `regime_class`, `confidence`, or `rationale` rests on quantitative evidence, it must cite **concrete MOD-004 features**. The features currently available from the v0.1.0 registry are exactly these 14 (no others may be invented here):

`real_yield_10y`, `real_yield_5y`, `breakeven_10y`, `breakeven_5y`, `breakeven_5y5y_fwd`, `curve_2s10s`, `curve_5s10s`, `policy_spread`, `usd_level`, `vol_level`, `rates_vol`, `equity_level`, `gold_price`, `gold_flow`.

If a decision needs a signal not in this set, it is **deferred** (see Non-Goals) — recorded as a gap, never fabricated and never added to MOD-004 as a history-dependent feature.

### 6. Guard separation
`duplicate_ok` and `operational_ok` are **future Layer-3 guards**, not snapshot-derived features. They MUST NOT be added to MOD-004 [[Feature Builder]]. They belong to ADR-004's six-guard taxonomy (`data_ok`, `freshness_ok` — snapshot-derived; `supervisor_ok`, `cooldown_ok` — Layer-3 stubs; `duplicate_ok`, `operational_ok` — new Layer-3 responsibilities). This ADR may *name* them as future required guard outputs, but authors **no guard implementation** and **no guard node** in this slice.

### 7. No schema freeze
This ADR does **not** define or freeze the Gold DecisionPacket contract. The normative contract is a **future, dedicated artifact_schema node** carrying a **new canonical_id** — **never SCHEMA-004**. SCHEMA-002 / SCHEMA-003 / SCHEMA-006 remain reserved; the likely next-free id is `SCHEMA-010`, named here as a **non-binding candidate** only — formal assignment happens at the moment the node is authored. The same applies to the future builder module, gold decision interface, and L3 guard nodes: candidates may be named, none are reserved or created now.

### 8. Creation Gates
A normative Gold DecisionPacket SCHEMA node may be authored **only after ALL** of the following hold:

a. **MOD-004 Feature Builder implemented** — ✅ satisfied (active/tested as of 2026-06-07).
b. **Deterministic feature coverage validated** — the available features are confirmed sufficient (or the gaps explicitly accepted) for the intended regime/confidence/direction outputs.
c. **Replay requirements finalized** — the full replay key (§3) and the meaning of `model_version` / `decision_policy_version` / `configuration` are pinned.
d. **Regime taxonomy exists** — `regime_class` values are enumerated and grounded.
e. **Confidence semantics agreed** — the scalar `confidence` (+`uncertainty`) model is fixed (see ADR-004: the 3-component performance/calibration/sample_quality variant is **not** adopted into the frozen scalar model without a formal amendment).

Until every gate passes, no Gold DecisionPacket SCHEMA node, module, guard, or implementation code is created.

## Illustrative Field Sketch (non-normative)

> **The following is illustrative, provisional, and non-normative. It is not a schema and does not constrain the future SCHEMA node.** It exists only to show the *shape* a v0 packet might take, so the constraints above have a concrete referent. The actual contract is authored later, contract-first, under the Creation Gates.

A future Gold DecisionPacket v0 *might* carry fields such as:

- `packet_id` — packet identity
- `packet_schema_version` — version of the (future) packet schema
- `source_snapshot_id` — replay anchor back to SCHEMA-001
- `source_feature_schema_version` — the SCHEMA-009 version consumed
- deterministic-timestamp policy — only if a timestamp is later required (no wall-clock reads)
- `decision_mode` — `paper_only`
- `instrument` — gold / gold proxy
- `regime_class` — from a future, enumerated regime taxonomy
- `confidence` — scalar (with `uncertainty`); reconciles with ADR-004's frozen scalar model
- `direction` — `long` / `flat` / `avoid` / `watch` (reconciles with ADR-004's `allowed_actions` / `preferred_action`)
- `rationale` — human-readable explanation
- `cited_features` — the concrete MOD-004 features the decision rests on (§5)
- `guard_refs` — references to the six-guard taxonomy outcomes (§6)
- `duplicate_ok` — future L3 guard outcome (not a feature)
- `operational_ok` — future L3 guard outcome (not a feature)
- `provenance` — snapshot/feature provenance + the replay-key components (§3)
- `constraints` — invariants the packet asserts it honoured
- `non_execution_notice` — explicit statement that the packet is a paper-trading plan, not an order

Field names, types, and presence are all subject to change; the normative SCHEMA node is the single source of truth once authored.

## Non-Goals (explicitly deferred)

This ADR and the v0 slice it plans explicitly defer:
- live execution, broker integration, order routing,
- position sizing, fills, P&L accounting,
- learned regimes,
- momentum / rolling-window / z-score features (and any history-dependent feature),
- secondary stateful feature layers,
- backtest / paper-trading runtime,
- a real-time scheduler, and
- the **normative v0 SCHEMA node, builder module, L3 guard nodes, and all implementation code**.

No execution, order, broker, position, or trade nodes are created in this slice.

## Alternatives Considered

- **Freeze the v0 schema now.** **Rejected** — the Creation Gates (§8) are not all met (regime taxonomy and confidence semantics are unsettled), and a frozen contract authored prematurely would drift from the features that justify it. The just-in-time, contract-justified-by-features discipline of ADR-004/ADR-005 is preserved.
- **Fold gold decisions onto the treasury branch** (reuse MOD-002 / INT-006 / SCHEMA-004). **Rejected** — violates ADR-004's permanent-separation mandate and canonical_id immutability; the two carry incompatible semantics.
- **Add `duplicate_ok` / `operational_ok` to MOD-004 as features.** **Rejected** — they are Layer-3 guard responsibilities, not pure snapshot-local transforms; adding them would break ADR-005's snapshot-locality and the determinism boundary.

## Consequences

### Positive
- Establishes the gold decision layer's boundary, dependency rules, and replay invariants **before** any contract is frozen — eliminating the prose-only drift risk ADR-004 flagged.
- Keeps the Supervisor Office treasury branch permanently and unambiguously separate.
- Gives a clear, gated path to the normative SCHEMA node (Creation Gates), so authoring is justified by real features and finalized semantics.

### Negative / Trade-offs
- The concrete contract remains unwritten; downstream design must wait on the Creation Gates.
- Two decision branches with related names coexist until the gold branch is built; an explicit mapping will be required when both exist.

### Risks
- The v0 contract stays prose/illustrative until authored — residual drift risk; mitigated by the determinism invariant (§3), the input boundary (§2), and the Creation Gates (§8) recorded here.

## Future Work

The path to a normative Gold DecisionPacket v0 runs through the Creation Gates (§8). When all gates pass, a later slice will author — contract-first, with new canonical_ids — the future objects this ADR only names as deferred candidates:
- a Gold DecisionPacket **artifact_schema** node (new `SCHEMA-0xx`, never SCHEMA-004),
- a gold **decision builder module**,
- the Layer-3 **guards** (`duplicate_ok`, `operational_ok`, and the rest of the six-guard taxonomy), and
- a **regime taxonomy** + the agreed confidence semantics.

Each must honour the dependency, determinism, provenance, and separation constraints above.

## Relationships

### Depends On
- [[Feature Vector Schema]]
- [[Feature Builder]]
- [[Layer 2 Snapshot Schema]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Feature Layer Contract]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Layer 2 Design Principles]]
