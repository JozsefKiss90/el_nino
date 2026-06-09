---
type: artifact_schema
canonical_id: SCHEMA-011
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "GOLD_DECISIONPACKET_V0_BRIEF.md"
  - "src/gold/decision_builder/models.py"
related_files:
  - "[[models.py (gold)]]"
related_tests:
  - "[[test_decision_builder]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
schema_id: "gold-decision-packet"
schema_version: "0.2.0"
schema_path: "src/gold/decision_builder/models.py"
validated_by:
  - "[[test_decision_builder]]"
consumed_by:
  - "[[Paper-Trading Runtime]]"
produced_by:
  - "[[Gold Decision Builder]]"
---

# Gold DecisionPacket v0 Schema

## Definition

The deterministic output contract of the Gold Decision Builder (MOD-006): a frozen `GoldDecisionPacket` derived purely from one Feature Vector (SCHEMA-009) + one Regime Classification (SCHEMA-010). It is a **paper-trading planning artifact** — `decision_mode: paper_only`, instrument = gold/GLD proxy — **not** a live trade signal, order, or broker instruction (ADR-006 §1, Non-Goals). This is a **net-new** artifact_schema with a new canonical_id (**never SCHEMA-004**, the Supervisor treasury packet); it is permanently separate from the treasury branch (ADR-004).

Authored contract-first (`status: planned` / `not-started`); bumped to implemented when MOD-006 lands.

## Purpose

Give the (future, deferred) paper-trading layer one versioned, replay-safe gold-decision shape: a `direction` stance (the regime→direction policy) + `confidence`/`uncertainty` (the ADR-008 ordinal trust score) + the concrete features the decision cites + the L3 guard outcomes it honored — anchored to the producing `snapshot_id` so the same snapshot + same versions always reproduce the same packet.

## Architecture Role

Output schema of MOD-006 Gold Decision Builder; inputs are SCHEMA-009 (a FeatureVector) + SCHEMA-010 (a RegimeClassification, obtained via INT-007), plus optional L3 guard outcomes (ADR-006 §2). It never consumes raw SCHEMA-001, raw JSON, external APIs, hidden state, or history. Governed by [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) + [[ADR - Gold Decision Confidence Semantics]] (ADR-008).

## Schema Definition

**GoldDecisionPacket** — field groups:

*Decision* (keyed by `decision_policy_version` + the echoed regime version-triple)

| Field | Type | Notes |
|-------|------|-------|
| packet_id | string | `gold-v0:` + short SHA-256 digest over the **full identity tuple** (`source_snapshot_id`, `source_feature_schema_version`, `regime_taxonomy_version`, `regime_classifier_version`, `decision_policy_version`, `decision_policy_fingerprint`) — deterministic, never uuid/clock; mirrors `Snapshot.recompute_id` newline-hash. Closes id-collision across version/config bumps. |
| packet_schema_version | string | this contract-shape version (e.g. `0.1.0`) |
| instrument | string | the v0 fixed gold proxy (`GLD`) |
| decision_mode | enum | `paper_only` (fixed — explicit non-execution) |
| regime | enum(Regime) | echoed from the RegimeClassification |
| direction | enum(Direction) | `LONG` / `FLAT` / `AVOID` / `WATCH` — from the regime→direction policy table |
| confidence | number [0,1] | ADR-008 deterministic ordinal trust score (NOT a probability) |
| uncertainty | number [0,1] | ADR-008 structural-penalty aggregate (NOT strictly `1−confidence`) |
| rationale | string | deterministic, templated from regime + direction + cited drivers (no free LLM text) |

*Provenance / identity*

| Field | Type | Notes |
|-------|------|-------|
| source_snapshot_id | string | replay anchor back to SCHEMA-001 (echoed from the vector/classification) |
| source_feature_schema_version | string | echoed SCHEMA-009 version |
| regime_taxonomy_version | string | echoed from the RegimeClassification |
| regime_classifier_version | string | echoed from the RegimeClassification |
| regime_classification_trace_version | string | echoed from the RegimeClassification |
| matched_rule_id | string | the deciding regime rule (echoed) |
| cited_features | array&lt;FeatureCitation&gt; | concrete MOD-004 features the decision rests on (§5: only the 14 real features) |
| as_of | string \| null | deterministic caller-supplied (= `snapshot.clock_ts`); never wall-clock |
| snapshot_guards | object \| null | **v0.2.0 additive (ADR-009 §3)** — the snapshot's L1 guard provenance (`data_ok`/`freshness_ok`/`cooldown_ok`) forwarded by the chain orchestrator so a downstream consumer reads it from the packet, never the raw snapshot. **Distinct from `guard_refs`** (the L3-outcome block). `null` for a pre-runtime caller. Excluded from `packet_id`. |

*Versions*: `decision_policy_version` — the gold builder's policy axis (confidence weights + direction table), governed per ADR-008 §7 (bump it, never `taxonomy_version`).

*Trust trace* (auditability of the confidence scalar)

| Field | Type | Notes |
|-------|------|-------|
| confidence_inputs | object | anchor `rule_margin`, `secondary_count`, `near_count`, `max_staleness_days`, `revision_risk`, `unavailable_count` |

*Guards* (ADR-006 §6 — the six-guard taxonomy; the packet **cites** outcomes, does not compute them as features)

| Field | Type | Notes |
|-------|------|-------|
| guard_refs | object | `data_ok`, `freshness_ok`, `supervisor_ok`, `cooldown_ok`, `duplicate_ok`, `operational_ok` — each `bool \| null`; `null` = not-yet-evaluated stub |

*Safety*

| Field | Type | Notes |
|-------|------|-------|
| non_execution_notice | string | fixed assertion: paper-trading plan, not an order |
| constraints | array&lt;string&gt; | invariants the packet asserts it honored (snapshot-local; cited ⊆ 14 features; deterministic) |

**FeatureCitation**: `name`, `value`, `inputs` (SCHEMA-001 series_ids), `max_staleness_days`, `revision_risk` (mirrors SCHEMA-010 `FeatureProvenance`).

## Validation Rules

- `confidence`, `uncertainty` ∈ [0,1]. `direction` ∈ the closed enum; `decision_mode == paper_only`; `instrument == GLD`.
- INDETERMINATE regime ⇒ `direction == WATCH` (fail-closed) and `confidence` at the defined minimum / `uncertainty` maxed (ADR-008 floors).
- `cited_features[*].name` ∈ the 14 MOD-004 features (ADR-006 §5); each citation read verbatim from the FeatureVector (never inferred).
- `regime` == the RegimeClassification's regime; `matched_rule_id` echoed; the three regime versions echoed unchanged.
- **Determinism:** `(source_snapshot_id, source_feature_schema_version, regime_taxonomy_version, regime_classifier_version, decision_policy_version, configuration)` determines the entire packet (ADR-006 §3 / ADR-008 §8; `model_version` N/A for the rule-based v0; `configuration` = the `decision_policy_fingerprint`). `packet_id` is the SHA-256 digest over exactly this identity tuple (`gold-v0:` + first 16 hex), so it cannot collide across version/config bumps. `to_dict()` emits alphabetically-sorted keys + 6-dp-rounded confidence/uncertainty → byte-stable JSON.
- No field depends on history, cross-snapshot state, external context, clock, or randomness.

## Direction Policy (versioned config — provisional)

`direction` is a **deterministic table lookup** over the 12 `Regime` values, pinned in the versioned `DecisionPolicyConfig` under `decision_policy_version` v0 (fingerprinted alongside the confidence weights; a coherence test asserts the table is total over all regimes and that INDETERMINATE → `WATCH`). It is decision-policy config, not a separate ADR — it carries no separation/governance hazard comparable to confidence (gold-internal, paper-only, structurally identical to the regime thresholds). The per-regime gold thesis is **domain-anchored and provisional**; economic calibration is deferred to the real corpus (a future `decision_policy_version` bump). See `GOLD_DECISIONPACKET_V0_BRIEF.md` for the illustrative v0 table.

## Open Questions

- `produced_by` → [[Gold Decision Builder]] (MOD-006), now authored and tested (`status: active` / `implemented`).
- `consumed_by` → [[Paper-Trading Runtime]] (MOD-007), authored under ADR-009: the runtime wraps the pure packet (it never enriches `guard_refs`). The **v0.2.0 additive `snapshot_guards` block** + populated `as_of` forward the snapshot's L1 provenance + deterministic clock onto the packet so the runtime consumes only SCHEMA-011 (`packet_id` is unchanged — it excludes both).
- The stateful L3 guards (`duplicate_ok`, `operational_ok`) are now **implemented** in the runtime (PRED-006/007); the packet's `guard_refs` still carries `null` (the wrap keeps the planning packet pure), and the computed outcomes live on the [[Runtime Decision Record Schema]] (SCHEMA-012).

## Relationships

### Produced By
- [[Gold Decision Builder]]

### Consumed By
- [[Paper-Trading Runtime]]

### Used By
- [[models.py (gold)]]

### Validated By
- [[test_decision_builder]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Gold Decision Confidence Semantics]]

### Consumes
- [[Feature Vector Schema]]
- [[Regime Classification Schema]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Layer 2 Design Principles]]
