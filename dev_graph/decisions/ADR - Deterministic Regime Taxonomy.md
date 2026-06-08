---
type: decision_record
canonical_id: ADR-007
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - code
  - ADR
  - layer2
source_paths:
  - "src/regime/regime_classifier/regime_classifier.py"
  - "src/regime/regime_classifier/taxonomy.py"
  - "tests/snapshot/fixtures/latest_snapshot_pass.json"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Feature Layer Contract]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
decision_id: "ADR-007"
decision_date: 2026-06-08
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Deterministic Regime Taxonomy

## Status

Active — enacted 2026-06-08 alongside the MOD-005 Market Regime Classifier implementation slice.

## Context

The data path is `SCHEMA-001 → MOD-003 Snapshot Consumer → MOD-004 Feature Builder (SCHEMA-009) → (future) Gold DecisionPacket v0`. [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) §8 lists five creation gates for the future Gold contract; gate **(d) "Regime taxonomy exists — `regime_class` values are enumerated and grounded"** was the explicit open gate. This ADR governs the layer that satisfies it.

[[ADR - Feature Layer Contract]] (ADR-005) §2 lists "inferred regimes" among the **forbidden feature classes**, explicitly noting such logic "belongs to a later, explicitly stateful node with its own ADR." This is that node — and it is **rule-based and deterministic, not inferred or learned**. There is no contradiction: ADR-005 keeps the *feature layer* pure (snapshot-local levels/spreads only); this ADR governs a *separate downstream classification layer* that consumes those pure features and applies an explicit, versioned rule table.

## Purpose

Introduce a governance-controlled, deterministic, replayable **Regime Taxonomy** layer — the canonical semantic abstraction between Feature Engineering (MOD-004) and the future Gold Decision Builder. It classifies every Layer-2 snapshot into exactly one macro-financial-conditions regime using only snapshot-local feature information, so the Gold layer consumes a single regime label + provenance instead of raw "feature spaghetti."

## Motivation

- ADR-006 gate (d) blocks the Gold contract until a grounded regime enumeration exists.
- A deterministic, enumerated abstraction is auditable and replayable where ad-hoc threshold logic scattered across a decision builder is not.
- Gold's primary macro drivers (real yields, the dollar, inflation expectations, volatility/stress, the curve) are exactly what the 14 grounded MOD-004 features express — so a macro-conditions taxonomy is both buildable and economically meaningful.

## Decision

1. **Macro-conditions taxonomy.** Because the 14 available features are point-in-time levels/spreads (no momentum/history is permitted), the regimes are macro-financial-conditions states, not price-action/trend states. Twelve enumerated values: `LIQUIDITY_STRESS, RISK_OFF, VOLATILE, RESTRICTIVE_RATES, REFLATION, DISINFLATION, CURVE_INVERSION, STRONG_USD, RISK_ON, LOW_VOL, NEUTRAL` (signal regimes) and `INDETERMINATE` (fail-closed terminal).
2. **Rule-selection engine.** The classifier is a deterministic, priority-ordered rule table (first match wins). The output's primary key is `matched_rule_id`; `regime` is a pure projection of the matched rule. Exactly one regime per snapshot; no overlapping definitions (mutual exclusion by priority, exhaustiveness by the unconditional `NEUTRAL` catch-all).
3. **`rule_margin`, not confidence.** The emitted scalar is a **rule-local activation margin** (normalized distance of the deciding feature past its threshold). It is explicitly **not** epistemic confidence and **not** comparable across rules; `rule_threshold` and `rule_scale` are carried so it is self-describing.
4. **Config-driven, versioned thresholds.** All decision thresholds and margin scales live in a versioned `RegimeConfig` (not free-floating code constants), identified by `taxonomy_version`. A fingerprint coherence check binds `taxonomy_version` to its threshold set; config loading is fail-closed (`RegimeConfigError`).
5. **NEUTRAL is the sole catch-all.** Conflict/ambiguity is surfaced as *trace metadata* (`secondary_matching_rules`, `near_matching_rules`), never as a separate label. There is no MIXED_SIGNAL regime.
6. **Independent explainability versioning.** Audit/trace fields (`evaluated_rule_ids`, `skipped_rule_ids`, `failed_required_features`, secondary/near matches) are versioned by an independent `classification_trace_version`, so explainability can evolve without disturbing decision replay.
7. **Fail closed.** A missing globally-required feature yields `INDETERMINATE` (margin 0.0, no provenance) — never a guessed or defaulted regime.

## Replay guarantees

- **Decision replay key:** same `snapshot_id` + `taxonomy_version` + `classifier_version` ⇒ identical decision (`matched_rule_id`, `regime`, `rule_margin`, `trigger_features`).
- **Full-serialization replay key:** + `classification_trace_version` ⇒ byte-identical `to_dict()`.
- Evidence: every available real snapshot replayed twice is byte-identical (BENCH-001 `determinism.all_replays_byte_identical = true`); a golden test pins the real PASS snapshot → `RESTRICTIVE_RATES`.

## Determinism guarantees

`classify()` is a pure, total function: no global state, caches, singletons, randomness, wall-clock, IO, external/LLM/ML calls, or history. Any timestamp is a deterministic caller-supplied `as_of`, never a wall-clock read. Float thresholds use documented strict/inclusive inequalities and 6-dp margin rounding at serialization — no epsilon bands (they would add hidden non-determinism).

## No adaptive learning rationale

Regime boundaries are fixed, domain-anchored constants in a versioned config — never learned, fitted online, or updated in-loop. Learning would make the same snapshot classify differently across runs, breaking replay and counterfactual evaluation (ADR-004's invariant). Recalibration, if ever needed, is an explicit `taxonomy_version` bump, not an online update.

## No hidden state rationale

The classifier holds no buffers, caches, or accumulators and reads no prior snapshot. Every input is the current FeatureVector plus the versioned config. Hidden state would be unversioned, non-replayable, and would smuggle history into a snapshot-local layer.

## Regime stability principles

A regime is a function of the snapshot alone; identical snapshots always yield identical regimes regardless of order or surrounding snapshots (temporal independence inherited from SCHEMA-001). Stability across *time* is therefore a property of the data, not of hidden smoothing — the layer adds none.

## Gold Layer dependency

This layer satisfies ADR-006 gate (d) and contributes to gates (b) feature-coverage, (c) replay-finalization, and (e) confidence-semantics by pinning the regime contract (SCHEMA-010) and its replay key. The Gold DecisionPacket builder is **not** built here (ADR-006 §8 holds); SCHEMA-010 is exposed via INT-007 as the canonical upstream contract it will consume.

## Paper Trading dependency

Deterministic regime classification is a prerequisite for replay-first paper-trading evaluation and regime-stratified analysis: a paper-trading run must be able to reproduce, for any historical snapshot, exactly the regime that was in force. BENCH-001 provides the determinism evidence and a (synthetic, clearly-labelled) distribution because no real historical corpus exists in-repo yet.

## Canonical-id note (SCHEMA-010)

ADR-006 §7 named SCHEMA-010 a *non-binding candidate* for the future Gold DecisionPacket. SCHEMA-010 is consumed here for `RegimeClassification`; the Gold DecisionPacket candidate therefore shifts to the next free id (SCHEMA-011), assigned only when that node is authored — consistent with ADR-006's "ids reserved at authoring time."

## Alternatives Considered

- **Trend/price-action taxonomy** (TREND_UP/DOWN, MEAN_REVERSION, BREAKOUT). **Rejected** — requires direction/history the snapshot-local feature set cannot provide and ADR-005 forbids; would be non-deterministic or fabricated.
- **Learned/clustered regimes (HMM, k-means).** **Rejected** — "inferred regimes" are forbidden (ADR-005); breaks replay and auditability.
- **A `MIXED_SIGNAL` label for conflicted snapshots.** **Rejected** — ambiguity is better expressed as metadata (`secondary_matching_rules` / `near_matching_rules`) keeping NEUTRAL the single catch-all; avoids a label whose meaning overlaps NEUTRAL.
- **`confidence` scalar.** **Rejected** — threshold distance is not epistemic confidence; renamed to `rule_margin` and made self-describing via `rule_threshold`/`rule_scale`.
- **Hard-coded thresholds in code.** **Rejected** — thresholds are config-driven and versioned so changes are governed and fingerprint-checked.
- **Fold regime onto the Supervisor treasury decision branch.** **Rejected** — violates ADR-004 permanent separation; the regime layer feeds the Gold branch only.

## Consequences

### Positive
- Closes ADR-006 gate (d); gives the Gold layer a single, replay-safe, auditable upstream contract.
- Deterministic, fail-closed, fully tested (TEST-008/009) and benchmarked (BENCH-001).
- Config-driven thresholds + fingerprint coherence prevent silent drift.

### Negative / Trade-offs
- Domain-anchored (not data-fitted) thresholds are coarse until a real corpus enables governed recalibration.
- Twelve macro states are intentionally minimal; richer sub-states wait for a future, versioned extension.

### Risks
- Threshold edits without a `taxonomy_version` bump — mitigated by the fingerprint coherence test (CI fails).
- Misuse of `rule_margin` as a cross-rule score — mitigated by naming, the carried threshold/scale, and ADR text.

## Relationships

### Constrains
- [[Market Regime Classifier]]
- [[Regime Classification Schema]]
- [[Regime Classification API]]

### Depends On
- [[Feature Vector Schema]]
- [[Feature Builder]]

### Justified By
- [[ADR - Feature Layer Contract]]
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Regime Taxonomy]]
- [[Layer 2 Design Principles]]
