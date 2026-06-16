---
type: decision_record
canonical_id: ADR-008
status: active
implementation_status: not-started
canonical: true
created: 2026-06-08
updated: 2026-06-16
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md"
  - "src/regime/regime_classifier/models.py"
  - "src/regime/regime_classifier/taxonomy.py"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Deterministic Regime Taxonomy]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Feature Layer Contract]]"
  - "[[ADR - Execution Layer Planning]]"
decision_id: "ADR-008"
decision_date: 2026-06-08
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Gold Decision Confidence Semantics

## Status

Active — accepted/enacted 2026-06-08. This is a **governance / design** decision record. It **closes [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) §8 gate (e)** ("Confidence semantics agreed") and finalizes gates **(c)** and **(b)**; gates (a)/(d) were already closed. It authors **no** schema, module, interface, guard, or code — ADR-006 §8 holds until every gate passes (now satisfied), at which point those are authored contract-first in the next, separate slice.

## Context

ADR-006 §8 lists five creation gates for the future Gold DecisionPacket v0. After the MOD-005 Regime Taxonomy slice, gates (a) Feature Builder and (d) Regime taxonomy are closed, and (b)/(c) are byproduct-closeable, but **(e) "Confidence semantics agreed" is the single genuinely-open, load-bearing gate**. ADR-006 §8 forbids authoring the Gold SCHEMA/module/code until *all* gates pass, so (e) blocks the entire lineage.

The regime layer deliberately did **not** supply an epistemic confidence. [[ADR - Deterministic Regime Taxonomy]] (ADR-007) §Decision-3 fixed `rule_margin` as a **rule-local activation margin** — `clamp01(direction·(x − threshold)/scale)` with a per-rule scale (`models.py:8-12`, `taxonomy.py:59-66`, `config.py` scales 0.5–50) — explicitly **not** epistemic confidence and **not** comparable across rules; it is `0.0` for NEUTRAL/INDETERMINATE by invariant (`models.py:124-141`). There is no `confidence`/`uncertainty` field anywhere in `RegimeClassification` (SCHEMA-010) or `FeatureVector` (SCHEMA-009). So the Gold packet's scalar confidence model is genuinely undefined and must be designed here, before any Gold contract is frozen.

[[ADR - Decision Layer Re-grounding]] (ADR-004) Future Work binds this design: the 3-component performance/calibration/sample_quality variant is **not** adopted into the frozen v0 scalar without a formal amendment, and the treasury `EvaluationScorecard` (SCHEMA-005: `realized_pnl`, `calibration`, `drawdown`, `disagreement`) is a **permanently-separate** bounded context.

## Purpose

Fix — at the level of *semantics and structure*, not calibrated weights — the Gold DecisionPacket v0 `confidence` (+`uncertainty`) scalar, so the future Gold contract has an agreed, deterministic, replay-safe trust model to populate. This is to the Gold confidence what ADR-007 was to the regime taxonomy: it fixes the **model**; the exact numeric policy lives in a versioned config bumped under governance.

## Decision

1. **Deterministic ordinal trust score, not a probability.** The v0 `confidence` is a scalar in `[0,1]` defined as a **deterministic ordinal trust score** over snapshot-local, versioned inputs. It is explicitly **not** a calibrated probability, frequency, or likelihood and carries no frequentist guarantee. Same `snapshot_id` + same upstream/version inputs ⇒ identical score: it inherits the regime layer's proven byte-identical replay and adds no clock, randomness, history, or IO.

2. **Anchor: within-rule normalized `rule_margin`.** The score is anchored on the matched rule's normalized `rule_margin` ∈ `[0,1]` (`models.py:125`), used **only as ordinal, within-matched-rule strength** — never as a cross-rule score and never derived from the raw per-rule `rule_scale` (scales 0.5–50 are not on one axis). A consumer must not compare two regimes' anchors as if comparable.

3. **Discount dimensions.** The anchor is discounted by four deterministic, snapshot-local penalty dimensions, all already present in SCHEMA-010 / SCHEMA-009:
   - **ambiguity** — `len(secondary_matching_rules)` (rules that also fired but lost on priority);
   - **fragility** — `len(near_matching_rules)` (rules within `near_band = 0.25·scale` of firing — the decision could flip on a small feature move);
   - **data quality** — the cited features' `revision_risk` (any) and `max_staleness_days` (max), read verbatim from MOD-004 provenance;
   - **coverage** — `failed_required_features` and `FeatureVector.unavailable_features` counts.

4. **Floors.** Two regimes are floored rather than read from the anchor (whose margin is `0.0` for them):
   - **NEUTRAL (confident-quiet)** — a successfully-classified quiet market is **not** assigned naive-zero confidence; it receives a defined non-trivial floor (a quiet tape is a real, trustworthy state, not an absence of signal).
   - **INDETERMINATE (fail-closed)** — floored to the defined **minimum** confidence with **maximum** uncertainty (a missing required feature is maximal epistemic doubt, never a guess).

5. **Uncertainty companion.** Every packet carries an `uncertainty` companion to `confidence`, defined as a **structural-penalty aggregate** of the §3 discount dimensions (ambiguity + fragility + data-quality + coverage) — i.e. uncertainty rises with ambiguity/fragility/staleness/missing-coverage independently of the anchor. It is **not** asserted to be the strict arithmetic complement `1 − confidence`, and like confidence carries no frequentist meaning.

6. **Exclusions (ADR-004 separation).** The v0 scalar **rejects** ADR-004's 3-component performance/calibration/sample_quality variant; adopting it requires a formal ADR amendment. The treasury `EvaluationScorecard` (SCHEMA-005) `calibration` / `sample_quality` / `realized_pnl` **must not** be wired into the Gold confidence — they are a separate bounded context (ADR-004 permanent separation). Gold confidence depends **only** on snapshot-local regime/feature signals.

7. **Versioning & binding revisability.** The confidence/uncertainty **form and weights are governed by `decision_policy_version`** (a Gold-builder version, distinct from `taxonomy_version` / `classifier_version`). Any change to the confidence form or weights **bumps `decision_policy_version`, never `taxonomy_version`** — changing a regime threshold and changing the trust model are different governance acts and must stay independently replayable. Empirical recalibration against a future real snapshot corpus is an **expected v1 amendment**: the v0 weights are domain-anchored and explicitly provisional, mirroring ADR-007's domain-anchored thresholds.

8. **Replay-key finalization (closes gate c).** The Gold replay invariant (ADR-006 §3) is finalized as: `snapshot_id + feature_schema_version + classifier_version + taxonomy_version + decision_policy_version + configuration ⇒ identical packet`. For the rule-based v0 builder, **`model_version` is N/A** (there is no learned model; `decision_policy_version` subsumes policy identity) and is recorded as such; `configuration` is the versioned Gold-builder config (confidence weights + any thresholds). The regime version-triple (`taxonomy_version`, `classifier_version`, `classification_trace_version`) **composes into** this key unchanged.

9. **Feature-coverage acceptance (closes gate b).** The 14 MOD-004 features are confirmed sufficient for v0 confidence/uncertainty/direction; the **7 reserved features are explicitly accepted as out of scope for v0** — `real_yield_5y`, `breakeven_10y`, `breakeven_5y`, `curve_5s10s`, `policy_spread`, `gold_price`, `gold_flow` (redundant tenors, no distinct snapshot-local signal, or no defensible absolute-level anchor; `taxonomy.py:83-90`). The single-real-snapshot / synthetic-coverage caveat is recorded honestly; full data-validation is deferred to the real-corpus work and is **not** a prerequisite to authoring the v0 contract (ADR-006 §8(b) permits "gaps explicitly accepted").

10. **Bounded-context separation — CAP-004 deprecate-and-supersede.** The future gold-decision capability is a **net-new bounded context** under the Trading Engine (SYS-002). [[Signal Generation]] (CAP-004) — a `not-started`, wiki-derived intraday **indicator-stack** capability (VWAP/EMA/RVOL over raw L2 snapshots → buy/sell/hold signals routed to Order Management) — is **superseded** by it. CAP-004's concept is obsolete against the realized deterministic pipeline (SCHEMA-001 → MOD-003 → MOD-004 → MOD-005 → Gold), which consumes versioned FeatureVectors + RegimeClassification and emits a **paper-trading DecisionPacket**, not a live trade signal. Per [[Canonical Ownership]] (one concept = one node) and the CLAUDE.md Deprecation Procedure, CAP-004 will be set `status: deprecated` and the new gold-decision capability will carry `### Supersedes → [[Signal Generation]]`. **This ADR records the decision; the node-state flip and the `### Supersedes` edge are executed in the next slice when the gold-decision capability node is authored** (deprecate-with-successor — no dangling deprecation). CAP-004 is **not** kept as legacy and **not** repurposed in place. This is distinct from [[Decision Making]] (CAP-015, the treasury-upgrade branch under SYS-006), which is untouched and permanently separate (ADR-004).

11. **No schema/code in this slice.** Consistent with ADR-006 §8, this ADR authors no Gold DecisionPacket SCHEMA, no builder module, no Gold Decision API, no L3 guards, and no code. With gate (e) closed (and (b)/(c) finalized, (a)/(d) already closed), those become authorable contract-first in the next slice.

## Confidence model (illustrative, non-normative)

> As with ADR-006's field sketch, the following is **illustrative and provisional**, not frozen. §1–§5 fix the *structure*; the exact form and weights are pinned at builder authoring as `decision_policy_version` v0 and are revisable per §7.

A v0 trust score *might* be a multiplicative composite, clamped to `[0,1]`:

`confidence = base · ambiguity · fragility · data_quality · coverage`, where `base = rule_margin` (signal regimes) or a fixed NEUTRAL floor; `ambiguity = 1 − min(1, wₐ·|secondary|)`; `fragility = 1 − min(1, w_f·|near|)`; `data_quality = (revision_risk ? w_r : 1)·(1 − min(c, wₛ·max_staleness_days))`; `coverage = 1 − min(c, w_c·|unavailable|)`; and `INDETERMINATE ⇒ confidence = 0, uncertainty = 1`.

## Sanity check (evidence — the one real snapshot)

Traced against the sole consumable real snapshot (`952cc83a…`) via `consume → build_features → classify`:

- regime **RESTRICTIVE_RATES** (R04, priority 4); `rule_margin` **0.46** (real_yield_10y 1.96 vs 1.50 threshold, scale 1.0);
- `secondary_matching_rules` = ∅; `near_matching_rules` = `{R08_strong_usd}` (USD near its strong band); `failed_required_features` = ∅; `unavailable_features` = ∅;
- provenance: real_yield_10y `max_staleness_days = 2`, `revision_risk = False`.

Under the illustrative weights the snapshot scores **confidence ≈ 0.40 / uncertainty ≈ 0.60** — qualitatively correct: a genuine but modest restrictive-rates call (real yield only 0.46·scale past threshold) with one competing regime nearby (fragility from `R08_strong_usd`) earns middling trust, not false certainty. The floors behave (NEUTRAL floored above zero; INDETERMINATE ⇒ 0/1). This validates the **structure**; it does not freeze the weights.

## Alternatives Considered

- **Reuse `rule_margin` directly as confidence.** Rejected — it is rule-local and non-comparable (ADR-007 §Decision-3) and `0.0` for NEUTRAL/INDETERMINATE; as a global score it would assign zero confidence to a confidently-quiet market.
- **Adopt ADR-004's 3-component performance/calibration/sample_quality model.** Rejected for v0 — requires a formal amendment (ADR-004 Future Work) and pulls calibration/sample_quality from the treasury SCHEMA-005 bounded context across the ADR-004 separation boundary.
- **A calibrated/probabilistic confidence.** Rejected — only one real snapshot is consumable (10/11 regimes synthetic); a probability claim is unbacked. v0 is an ordinal trust score with a binding revisability clause.
- **Freeze the Gold DecisionPacket SCHEMA in this slice.** Rejected — ADR-006 §7/§8 forbid it until the gates pass; this ADR closes the last gate but defers the contract to the next slice (contract-first discipline).
- **Defer confidence semantics to the builder implementation.** Rejected — it is a governance decision with a permanent-separation hazard (SCHEMA-005 bleed); letting it emerge from code risks exactly the cross-context coupling ADR-004 forbids.
- **Repurpose CAP-004 in place / keep it as legacy.** Rejected — repurpose-in-place would silently reclassify a node's semantics (against the spirit of canonical ownership), and keeping a near-duplicate "produce directional signal + confidence under SYS-002" capability alongside the gold one risks a CON-003 violation; deprecate-and-supersede is the clean resolution.

## Consequences

### Positive
- Closes the last open ADR-006 Creation Gate (e); finalizes (c) and accepts (b) → the Gold DecisionPacket v0 contract becomes authorable contract-first in the next slice.
- Gives the Gold layer a deterministic, replay-safe, auditable trust model grounded in signals that already exist in SCHEMA-009/SCHEMA-010.
- Holds the treasury/gold separation (no SCHEMA-005 bleed) and the determinism invariant.

### Negative / Trade-offs
- v0 weights are domain-anchored (not data-fitted) and provisional until a real corpus enables governed `decision_policy_version` recalibration.
- A second governed version axis (`decision_policy_version`) coexists with `taxonomy_version` / `classifier_version`; their independence must be respected.

### Risks
- Confidence-weight edits without a `decision_policy_version` bump — to be mitigated at builder authoring by a fingerprint coherence test mirroring the regime `decision_fingerprint`.
- Misuse of the ordinal trust score as a probability — mitigated by the name ("trust score"), the explicit non-probability clause (§1), and the carried `uncertainty`.

## Relationships

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Deterministic Regime Taxonomy]]
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Feature Layer Contract]]

### Depends On
- [[Regime Classification Schema]]
- [[Feature Vector Schema]]

### Constrained By
- [[Canonical Ownership]]
