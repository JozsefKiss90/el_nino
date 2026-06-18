---
type: decision_record
canonical_id: ADR-012
status: draft
implementation_status: not-started
canonical: true
created: 2026-06-17
updated: 2026-06-17
confidence: confirmed
evidence:
  - design
  - ADR
  - code
  - layer2
source_paths:
  - "EPOCH_B_CALIBRATION_RUNBOOK.md"
  - "EPOCH_B_CORPUS_RUNBOOK.md"
  - "src/regime/regime_classifier/config.py"
  - "src/gold/decision_builder/config.py"
  - "src/gold/decision_builder/policy.py"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Feature Layer Contract]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
decision_id: "ADR-012"
decision_date: 2026-06-17
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Empirical Calibration Methodology

## Status

**Draft** — authored 2026-06-17 (epoch (b) calibration-governance slice). This is a **governance and
methodology** record, mirroring [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006) and
[[ADR - Paper-Trading Runtime Planning]] (ADR-009). It does **not** bump any `*_version`, change any
threshold / weight / direction-table cell, edit any config, or re-pin any benchmark. It fixes the
**method and the gate** by which the provisional, domain-anchored regime thresholds, confidence
weights, and regime→direction table may *later* be converted to empirically-grounded values once the
real snapshot corpus is large and diverse enough to justify it.

It is `draft` until the operator accepts it. Until accepted (and until each target's readiness gate
passes), the provisional v0/v1 values stand unchanged.

## Context

[[ADR - Deterministic Regime Taxonomy]] (ADR-007 §Consequences) and
[[ADR - Gold Decision Confidence Semantics]] (ADR-008 §7, §Consequences) both close with the same
honest admission: the shipped numbers are **domain-anchored, not data-fitted**, because no real
corpus existed to fit to. ADR-007 §"No adaptive learning rationale": *"Recalibration, if ever needed,
is an explicit `taxonomy_version` bump, not an online update."* ADR-008 §7: *"Empirical recalibration
against a future real snapshot corpus is an **expected v1 amendment**: the v0 weights are
domain-anchored and explicitly provisional."*

Epoch (b) **operationalized** the corpus (dev_graph log 2026-06-11; `EPOCH_B_CORPUS_RUNBOOK.md`):
one immutable, SCHEMA-001-conformant PIT snapshot is banked per day into two content-id-keyed sinks
(`layer2_truth.db`; `Mr-Ripley/runtime/snapshots/*.json`). That slice deliberately did **not**
calibrate — it stated plainly that calibration *"remains a later, separately-governed bump gated on N
real snapshots existing."* This ADR governs that later step.

The single most important thing this ADR must prevent is **overfitting a tiny, low-diversity corpus**.
Calibrating thresholds, weights, or a direction table from a handful of same-regime snapshots is
statistical malpractice that would silently destroy the provisional values' deliberate, auditable
domain anchoring and replace it with noise. So the load-bearing artifact here is the **readiness gate**
(§Empirical-Readiness Gate), not a calibration.

### Corpus assessment as of 2026-06-17 (evidence — Step 1, read-only)

The real Layer-3 chain (`consume → build_features → classify → build_decision`) was run over **every**
honestly-banked PIT snapshot (truth DB + runtime archives). Verbatim result:

| # | snapshot_id8 | clock_ts | regime | direction | confidence | provenance |
|---|---|---|---|---|---|---|
| 1 | `952cc83a` | 2026-05-01T22:00Z | RESTRICTIVE_RATES | AVOID | 0.39744 | el_nino committed fixture |
| 2 | `05c8369d` | 2026-06-11T22:00Z | RESTRICTIVE_RATES | AVOID | 0.57120 | Mr-Ripley runtime archive |
| 3 | `7d39aa8f` | 2026-06-13T22:00Z | RESTRICTIVE_RATES | AVOID | 0.53856 | Mr-Ripley runtime archive |
| 4 | `e0e44caf` | 2026-06-14T22:00Z | RESTRICTIVE_RATES | AVOID | 0.52734 | Mr-Ripley runtime archive |
| 5 | `c1fe5a02` | 2026-06-15T22:00Z | RESTRICTIVE_RATES | AVOID | 0.56682 | Mr-Ripley runtime archive |

- **N = 5** PASS-banked PIT snapshots (`engine gold-v3.3.0 / config 1.1.0`); **1** is a committed
  el_nino consumable (the 2026-05-01 fixture), **4** are producer-only (Mr-Ripley truth DB + runtime
  archive). The forward corpus is only **4 trading days** (2026-06-11/13/14/15; 06-12 and 06-16 were
  fail-closed no-bank days; 06-17 not yet run). The 2026-05-01 row is a backfill anchor, not a
  forward day.
- **Regime distribution: `{RESTRICTIVE_RATES: 5}`** — **1 of 12 regimes** observed. Never seen:
  LIQUIDITY_STRESS, RISK_OFF, VOLATILE, REFLATION, DISINFLATION, CURVE_INVERSION, STRONG_USD, RISK_ON,
  LOW_VOL, NEUTRAL, INDETERMINATE.
- **Direction distribution: `{AVOID: 5}`** — **1 of 4 directions**. Never seen: **LONG, FLAT, WATCH**
  (a LONG/fill has **never** occurred in the real corpus).
- **Confidence range:** 0.39744 – 0.57120 (mean 0.520). All five are driven by the **same** rule
  (`R04_restrictive_rates`); the only competing regime ever near is `R08_strong_usd` (secondary or
  near in 4/5). Every snapshot has **zero** staleness, **zero** revision-risk, and **zero**
  unavailable-feature penalty — so the staleness, revision, and coverage weights have **no real
  variation to fit**.

The corpus is **monochromatic**: one regime, one direction, one deciding rule, no penalty-dimension
variation. This is the explicit "do-not-calibrate" condition. (KA-010 [[Paper Trading Validation]]
already flags that *"5-day paper trading results are encouraging but not statistically significant"* —
we have effectively four forward days.)

## Purpose

Fix the **method and the readiness gate** for converting the provisional values to empirical ones —
the same way ADR-007 fixed the regime *model* and ADR-008 fixed the confidence *model* while leaving
the numbers to a versioned config. This ADR fixes *how and when* those numbers may move, never the
numbers themselves.

## Decision

### 1. Version-axis mapping (never cross the axes)

Each calibration target maps to exactly one version axis, and the axes are **never** crossed:

| Target | Version axis | Authority | Fingerprint | Re-pin on bump |
|---|---|---|---|---|
| Regime **thresholds** + margin scales + required-feature gate | **`taxonomy_version`** | ADR-007 §Decision-4; `src/regime/regime_classifier/config.py` `_DECISION_FIELDS` | `RegimeConfig.decision_fingerprint()` | BENCH-001 (and BENCH-002 + downstream if the regime change cascades) |
| Gold **confidence weights** / floors | **`decision_policy_version`** | ADR-008 §7 | `DecisionPolicyConfig.decision_policy_fingerprint()` | BENCH-002 |
| **Regime→direction table** | **`decision_policy_version`** | `src/gold/decision_builder/config.py` (table is decision-policy config, not an ADR); ADR-008 lineage | `DecisionPolicyConfig.decision_policy_fingerprint()` | BENCH-002 (and BENCH-003/004 iff a direction change cascades into admission/execution) |

- A change to a regime threshold and a change to the trust model are **different governance acts**
  (ADR-008 §7) and must stay independently replayable. Changing the confidence weights or the
  direction table **bumps `decision_policy_version`, never `taxonomy_version`**. Changing a regime
  threshold/scale **bumps `taxonomy_version`, never `decision_policy_version`**.
- `classifier_version` and `classification_trace_version` are **not** calibration axes — they version
  the engine and the explainability fields, not the domain values. They are out of scope here.

### 2. A bump is a config-version amendment, never a rebuild

A calibration bump amends a versioned config value and increments its version string and fingerprint.
It creates **no** new ontology object and changes **no** `canonical_id`. The affected nodes are
exactly the existing config file nodes ([[config.py (regime)]] FILE-013, [[config.py (gold)]] FILE-016),
the policy helper ([[policy.py]] FILE-017), and the benchmark nodes that re-pin (BENCH-001/002, and
BENCH-003/004 only on a cascading direction change). Canonical IDs are immutable across a bump
([[Canonical Ownership]] CON-003).

### 3. Empirical-Readiness Gate (the load-bearing rule)

No target may be recalibrated until **its** gate passes. The three targets have **different data
appetites**; a gate that passes for one does **not** authorize another. Quantities below are anchored
on KA-010 (5 days ⇒ "not statistically significant") and on out-of-sample / walk-forward discipline
(wiki *Walk-Forward Optimization*); they are themselves revisable under governance, but they are floors,
not targets to rush toward.

**Gate G0 — corpus floor (necessary for any target).** `N ≥ 60` distinct, honestly-banked, PASS PIT
snapshots (≈ one calendar quarter of trading days at ~1/day), **forward-accumulated** (no
back-fabricated history — see §5). Below G0, **nothing** is eligible. With today's N = 5, G0 fails.

**Gate G1 — regime thresholds (`taxonomy_version`).** Per threshold/rule to be moved:
  - the regime(s) on **both sides** of that boundary are each observed in `≥ 20` real snapshots, with
    real observations **straddling** the boundary (you may not move a boundary you have only ever seen
    one side of); and
  - `≥ 3` distinct regimes are present in the corpus overall (a monochromatic corpus can calibrate
    nothing); and
  - a **temporally-disjoint** validation slice (walk-forward: fit on the earlier window, validate on
    the later) confirms the moved threshold does not degrade classification on held-out days.
  Any rule/regime not meeting this keeps its domain-anchored default. With 1/12 regimes observed, G1
  fails for **all** rules today.

**Gate G2 — confidence weights (`decision_policy_version`).** Each penalty dimension a weight governs
must exhibit **real variation**: `≥ 30` snapshots spanning `≥ 3` distinct regimes that, between them,
actually exercise secondary matches (ambiguity), near matches (fragility), non-zero cited-feature
staleness, revision risk, and ≥1 unavailable feature (coverage). A weight whose dimension shows **no
real variation may not be moved** (you cannot fit `staleness_weight` to a corpus with zero staleness).
Validation is **ordinal-monotonicity** on a held-out slice — confidence is a deterministic ordinal
*trust score*, **not** a probability (ADR-008 §1); it is **not** fit to realized PnL or any outcome,
and the treasury `EvaluationScorecard` (SCHEMA-005) is **never** wired in (ADR-008 §6, ADR-004
permanent separation). With zero staleness/revision/coverage variation today, G2 fails.

**Gate G3 — regime→direction table (`decision_policy_version`).** Per cell (regime) to be revised:
  - that regime is observed in `≥ 20` real PIT snapshots; **and**
  - a **forward gold-return evaluation harness** (paper-trading per KA-010: out-of-sample directional
    accuracy per regime) demonstrates the revised cell beats the provisional cell **out-of-sample**
    under the KA-010 criteria (`≥ 3` metrics improved, no regressions, `≥ 12%` average relative
    improvement).
  A cell for a regime not meeting this keeps its domain-anchored thesis. G3 has the **highest** wall-clock
  appetite — each regime must actually occur in real data **and** accumulate enough subsequent gold
  returns to judge its thesis. The forward-return **labeling harness now exists**
  ([[Gold Forward-Return Labeler]] / [[Gold Forward-Return Label Set]], built 2026-06-17 — see §7);
  the per-regime *coverage* it needs does not. With 11/12 cells never exercised, G3 fails.

**Until a target's gate passes, its provisional domain-anchored values stand** and this ADR mandates
**no** change to them.

### 4. Calibration method (when a gate passes — deterministic, rule-based only)

When and only when a target's gate passes:
  - Derive the candidate values from the corpus by an **explicit, deterministic, documented rule**
    (e.g. boundary placement at an economically-motivated quantile/separation of the observed feature
    distribution for thresholds; penalty magnitudes from the observed frequency/spread of each
    structural condition for weights; per-regime out-of-sample directional accuracy for the table).
    **No learned, fitted-online, history-dependent, or ML model** is permitted at runtime or in the
    derivation that ships — ADR-005 forbids "inferred regimes" and ADR-007 forbids learned/online
    boundaries; the calibrated config remains a static, versioned, fail-closed value set.
  - Use **walk-forward / out-of-sample** discipline: fit on an earlier window, validate on a strictly
    later, held-out window; report in-sample **and** out-of-sample behavior. Reject the candidate if it
    does not generalize.
  - Recompute the fingerprint, bump the **one** correct version, and update the relevant config node(s).

### 5. Determinism & replay preservation (non-negotiable)

The version is part of the replay key (ADR-006 §3: *snapshot_id + feature_schema_version +
classifier_version + taxonomy_version + decision_policy_version + configuration ⇒ identical packet*;
ADR-005 feature-layer rule; ADR-009 §4 runtime ledger rule). Therefore on any future bump:
  - **Old versions stay byte-reproducible.** A bump adds a new version's values; it never edits an old
    version's meaning. Any snapshot replayed at the old `*_version` + old config still yields the
    byte-identical historical output. Old goldens are **retained**, not overwritten.
  - **Re-pin under the new version.** Re-run the affected benchmark(s) and pin the new golden artifact
    **labelled with the new version**, keeping the prior golden for the prior version (per the §1 re-pin
    column). `taxonomy_version` ⇒ BENCH-001 (+ BENCH-002 & downstream if it cascades);
    `decision_policy_version` ⇒ BENCH-002 (+ BENCH-003/004 iff a direction change cascades).
  - **Assert determinism both ways:** byte-identical replay at the **new** version, and **unchanged**
    replay at every **prior** version.
  - **PIT honesty.** Calibrate **only** on honestly-banked, forward-accumulated PIT snapshots. Never
    back-fabricate history (data fetched now for a past date is not what was known then —
    `EPOCH_B_CORPUS_RUNBOOK.md` §6). The ~40 lost producer-outage days are **not** reconstructed.

### 6. Process binding

A calibration bump is **human-review-required** (a value/version change, per the dev_graph MCP policy
and CLAUDE.md Config Evolution procedure). The executing session must: re-derive the next free ids from
`index.md` (no id reuse), keep Neo4j read-only and re-sync the markdown after writeback, and **MUST
NOT** modify `wiki/**` or `raw/**` ([[No Wiki Mutation]] CON-001). Each bump is recorded in `log.md`
under the Config Evolution procedure and documented by updating this ADR (or a successor ADR if the
method itself changes).

### 7. G3 prerequisite — forward-return labeling harness (built 2026-06-17)

G3's stated prerequisite (a forward gold-return evaluation harness producing per-regime out-of-sample
outcome data) is now **built and verified** as the [[Gold Forward-Return Labeler]] (MOD-009), emitting
the committed golden [[Gold Forward-Return Label Set]] (BENCH-005). It is a **measurement tool only**,
strictly **downstream and read-only** w.r.t. the decision chain (look-ahead containment per §5,
enforced by a static import guard): it labels already-produced decisions with the return realized
**after** their timestamp and never feeds any forward value back onto the decision path. Building it
**does not** calibrate the direction table or change any value/version — **G3 remains deferred** until
the per-regime coverage in G3 above accrues (today the labeler correctly emits all-pending /
no_exit_in_tolerance labels over the monochromatic corpus). It is **not** a realization of
[[Performance Scoring]] (CAP-013) — that is the trade-log-driven treasury/promotion bounded context
(ADR-004/ADR-008 permanent separation); the labeler is a standalone calibration tool governed by this
ADR. Operational detail: `EPOCH_B_CALIBRATION_RUNBOOK.md`.

## Non-Goals

- **No learned / ML / online / history-dependent model** — at runtime or in the shipped derivation
  (ADR-005, ADR-007). The calibrated config is a static, versioned, fail-closed value set.
- **No live-money trading** — the corpus and all calibration are paper-only / PIT-replay.
- **No schema, canonical_id, or ontology change** — a bump is a config-version amendment, not a rebuild.
- **No recalibration of a target whose gate has not passed** — the primary failure mode this epoch must
  avoid. Overfitting the tiny corpus is prohibited.
- **No outcome/PnL fit for confidence** and **no SCHEMA-005 (treasury) bleed** into Gold confidence
  (ADR-008 §6, ADR-004 separation).
- **No crossing of version axes** — `taxonomy_version` and `decision_policy_version` move independently.

## Alternatives Considered

- **Calibrate now from N = 5.** Rejected — monochromatic corpus (1/12 regimes, 1/4 directions, no
  penalty variation); any "fit" is noise and would destroy the auditable domain anchoring. This is the
  exact malpractice the ADR exists to forbid.
- **One shared version for all three targets.** Rejected — ADR-007/008 deliberately separate
  `taxonomy_version` from `decision_policy_version`; collapsing them would couple independent
  governance acts and break independent replay.
- **A single global N gate for all targets.** Rejected — thresholds, weights, and the direction table
  have materially different data appetites (boundary-straddling vs penalty-variation vs forward-return
  evaluation); one number would be wrong for two of them.
- **Calibrate confidence against realized gold returns.** Rejected — confidence is an ordinal trust
  score, not a probability (ADR-008 §1); outcome-fitting would import the treasury bounded context
  across the ADR-004 separation boundary.
- **Back-fill the ~40 missing days to grow N fast.** Rejected — destroys PIT honesty
  (`EPOCH_B_CORPUS_RUNBOOK.md` §6); only forward accumulation is admissible.
- **Learn regime boundaries (HMM/k-means) once N is large.** Rejected — ADR-005/007 forbid learned
  regimes; the layer must stay deterministic and replayable.

## Consequences

### Positive

- The provisional→empirical transition now has an explicit, governed, overfitting-proof gate; the
  numbers can mature **without** any session quietly fitting noise.
- The version-axis mapping is written down once, so a future calibrating session cannot accidentally
  cross `taxonomy_version` and `decision_policy_version` or re-pin the wrong golden.
- Replay determinism and PIT honesty are preserved by construction across every future bump.
- Today's honest verdict (defer all three) is recorded with its evidence, so the decision is auditable.

### Negative / Trade-offs

- The gate is conservative: meaningful calibration is **months** away (G0 alone needs ≈ a quarter of
  forward days, and G1/G3 need regime diversity the macro tape may not supply quickly). The provisional
  domain-anchored values carry the system until then.
- Three independent gates add governance overhead versus a single "recalibrate everything" pass — but
  that overhead is the point (it prevents the cross-axis and overfitting failure modes).

### Risks

- **Premature calibration** under operator pressure before a gate passes — mitigated by §3 being a hard
  precondition and the bump being human-review-required.
- **Corpus diversity never arrives** (the tape stays in one regime) — then thresholds/table for unseen
  regimes simply remain domain-anchored indefinitely, which is the correct, honest outcome, not a bug.
- **Gate numbers themselves are provisional** — mitigated by marking them revisable under governance and
  anchoring them to KA-010 + walk-forward discipline rather than to convenience.

## Relationships

### Justified By
- [[ADR - Deterministic Regime Taxonomy]]
- [[ADR - Gold Decision Confidence Semantics]]
- [[ADR - Gold DecisionPacket v0 Planning]]

### Depends On
- [[config.py (regime)]]
- [[config.py (gold)]]
- [[policy.py]]

### Constrains
- [[config.py (regime)]]
- [[config.py (gold)]]
- [[Regime Distribution Benchmark]]
- [[Gold Decision Distribution Benchmark]]
- [[Gold Forward-Return Labeler]]
- [[Gold Forward-Return Label Set]]

### Originates From
- [[Paper Trading Validation]]
- [[Regime Taxonomy]]

### Constrained By
- [[Canonical Ownership]]
- [[No Wiki Mutation]]
