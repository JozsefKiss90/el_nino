---
type: module
canonical_id: MOD-006
status: active
implementation_status: tested
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - code
source_paths:
  - "src/gold/decision_builder/builder.py"
related_files:
  - "[[models.py (gold)]]"
  - "[[config.py (gold)]]"
  - "[[policy.py]]"
  - "[[builder.py]]"
related_tests:
  - "[[test_decision_builder]]"
  - "[[test_gold_bench]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
  - "[[ADR - Decision Layer Re-grounding]]"
module_name: "decision_builder"
module_path: "src/gold/decision_builder"
responsibility: "Turn a FeatureVector + RegimeClassification into a deterministic, paper-only Gold DecisionPacket"
depends_on:
  - "[[Feature Builder]]"
  - "[[Market Regime Classifier]]"
provides:
  - "[[Gold Decision API]]"
---

# Gold Decision Builder

## Definition

The deterministic, snapshot-local builder that turns a Feature Vector (SCHEMA-009) + a Regime Classification (SCHEMA-010) into a frozen, paper-only `GoldDecisionPacket` (SCHEMA-011). The fourth stage of the analysis path: `SCHEMA-001 → MOD-003 → MOD-004 → MOD-005 → [Gold Decision Builder]`. Realizes [[Gold Decision Generation]] (CAP-020).

## Purpose

Produce the gold `direction` stance + ADR-008 `confidence`/`uncertainty` trust score + cited features + guard references that the (deferred) paper-trading runtime consumes — replay-safe, provenance-tagged, fail-closed, paper-only. It is **not** a live trade signal, order, or the treasury Decision Engine (MOD-002); permanently separate (ADR-004).

## Architecture Role

Realizes the gold decision layer governed by [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) + [[ADR - Gold Decision Confidence Semantics]] (ADR-008); realizes the [[Pipeline Pattern]]. Consumes SCHEMA-009 + SCHEMA-010; produces SCHEMA-011 via [[Gold Decision API]] (INT-009). Pure functions, zero runtime dependencies (ADR-003).

## Inputs (or Dependencies)

- A `RegimeClassification` (SCHEMA-010) from [[Market Regime Classifier]] (MOD-005) — primary input.
- A `FeatureVector` (SCHEMA-009) from [[Feature Builder]] (MOD-004) — coverage + citation.
- Optional L3 guard outcomes (`GuardRefs`) + a versioned `DecisionPolicyConfig`. Never a raw snapshot, path, or external API.

## Outputs (or Provides)

- A `GoldDecisionPacket` (SCHEMA-011): `direction`, `confidence`/`uncertainty`, `regime`, `cited_features`, `guard_refs`, provenance + the replay-key versions + `decision_policy_version`, and a deterministic full-key `packet_id`.

## Constraints

- **Pure / stateless / deterministic** — same snapshot + same regime versions + same `decision_policy_version` + same configuration ⇒ identical packet; byte-identical `to_dict()`.
- **Snapshot-local only** — no history, learning, hidden state, clock, randomness, or IO.
- **Fail-closed** — INDETERMINATE ⇒ `direction = WATCH`, min confidence / max uncertainty; a FeatureVector/RegimeClassification snapshot_id mismatch raises.
- **Input boundary** — consumes only SCHEMA-009 + SCHEMA-010 + optional guards; never raw SCHEMA-001 (ADR-006 §2).
- **Confidence** — the ADR-008 ordinal trust score; never a probability; never wired to SCHEMA-005 treasury calibration.
- **Config-driven policy** — confidence weights + regime→direction table live in the versioned `DecisionPolicyConfig`; `decision_policy_fingerprint` ↔ `decision_policy_version` coherence prevents un-versioned drift.

## Implementation Notes

- `models.py` — SCHEMA-011 dataclasses (`GoldDecisionPacket`, `Direction`/`DecisionMode` enums, `FeatureCitation`, `ConfidenceInputs`, `GuardRefs`) + `to_dict()` + `compute_packet_id` (SHA-256 over the full identity tuple, mirroring `Snapshot.recompute_id`).
- `config.py` — `DecisionPolicyConfig` (confidence weights + floors + regime→direction table + `decision_policy_version`), `DEFAULT_DECISION_POLICY_CONFIG`, fail-closed `from_mapping`/`load_config` (`DecisionPolicyConfigError`), and `decision_policy_fingerprint()`.
- `policy.py` — pure `trust_score` (ADR-008: anchor on within-rule `rule_margin`, four structural discounts, NEUTRAL/INDETERMINATE floors, uncertainty as penalty aggregate) + `direction_for`.
- `builder.py` — `build_decision(fv, rc, guards, config, as_of)`: snapshot-id consistency check → trust score → direction lookup → cited features → templated rationale → packet.
- Real PASS fixture → RESTRICTIVE_RATES / direction AVOID / confidence 0.39744 / uncertainty 0.136 / `packet_id gold-v0:5653d07a0b3949d5`. 29 gold tests (20 builder + 6 bench + 3 e2e); benchmark BENCH-002 byte-identical replay = true.

## Open Questions

- The downstream consumer (paper-trading runtime) is deferred (ADR-006 Non-Goals); SCHEMA-011 is exposed via INT-009.
- The regime→direction table is domain-anchored / provisional; economic recalibration is a future `decision_policy_version` bump. v0 finalized 2026-06-08: DISINFLATION → FLAT (the real-yield channel offsets the inflation-expectations headwind); the 4-way enum is kept (AVOID is an informational headwind, not SHORT, on a long-only GLD proxy).
- `LIQUIDITY_STRESS → LONG` assumes the safe-haven bid, which is the base case for a daily macro strategy; acute "dash-for-cash" episodes (Sep 2008, Mar 2020) can see gold sold first. Left LONG for v0; revisit with a real historical corpus.
- The stateful L3 guards ([[Duplicate OK]], [[Operational OK]]) are authored as contracts; their runtime computation is deferred.

## Relationships

### Implements
- [[Gold Decision API]]

### Consumes
- [[Feature Vector Schema]]
- [[Regime Classification Schema]]

### Produces
- [[Gold DecisionPacket v0 Schema]]

### Contains
- [[models.py (gold)]]
- [[config.py (gold)]]
- [[policy.py]]
- [[builder.py]]

### Validated By
- [[test_decision_builder]]
- [[test_gold_bench]]

### Depends On
- [[Feature Builder]]
- [[Market Regime Classifier]]

### Realizes
- [[Pipeline Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Gold Decision Confidence Semantics]]
