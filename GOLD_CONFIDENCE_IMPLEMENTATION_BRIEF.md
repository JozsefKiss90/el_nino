# GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF

**Slice:** Gold Decision Confidence & Uncertainty Semantics — ADR-008 + ADR-006 §8(e) gate closure + CAP-004 canonical-ownership disposition.
**Date:** 2026-06-08. **Status:** STEP 0 — context-discovery complete; not yet implemented.
**Type:** Governance + ontology slice. **No application code, no schema freeze, no tests** — ADR-006 §8 forbids the Gold DecisionPacket SCHEMA/module/code until this gate closes.

This brief is the STEP 0 deliverable: it records what the slice touches and the architectural reconciliation it rests on, established via dev_graph + code discovery before any ADR is written. It mirrors `REGIME_IMPLEMENTATION_BRIEF.md`.

---

## 1. Objective

Close the single load-bearing open creation gate — **ADR-006 §8(e) "Confidence semantics agreed"** — so the Gold DecisionPacket v0 lineage becomes authorable. Gates (a) and (d) are closed; (b) and (c) are closeable as byproducts; (e) is genuinely OPEN. The regime slice deliberately fixed `rule_margin` as a **rule-local activation margin that is explicitly NOT epistemic confidence and NOT comparable across rules** (ADR-007 §Decision-3; `models.py:8-12`; SCHEMA-010 "NOT a global score"; margin is 0.0 for NEUTRAL/INDETERMINATE by invariant), so the Gold packet's scalar `confidence`/`uncertainty` model is undefined — real design work, not derivation.

Author **ADR-008** to FIX a single deterministic v0 `confidence` ∈ [0,1] + `uncertainty` companion, labelled a **deterministic ordinal trust score — not a probability / calibrated confidence**, derived purely from already-existing, replay-safe inputs:

- **anchor** — normalized within-matched-rule `rule_margin` (ordinal strength only, never cross-rule; anchor the [0,1] normalized value at `models.py:125`, never the raw per-rule scales 0.5–50)
- **ambiguity discount** — `len(secondary_matching_rules)`
- **fragility discount** — `len(near_matching_rules)` (within `near_band = 0.25·scale`)
- **data-quality discount** — cited-feature `revision_risk` / `max_staleness_days`
- **coverage discount** — `failed_required_features` / `unavailable_features` counts
- **floors** — NEUTRAL (confident-quiet) and INDETERMINATE (fail-closed → defined minimum confidence, maxed uncertainty)

Explicitly **REJECT** ADR-004's 3-component performance/calibration/sample_quality variant for the frozen v0 scalar: ADR-006 §8(e) requires a formal amendment to adopt it, and calibration/sample_quality belong to the treasury SCHEMA-005 EvaluationScorecard bounded context — they must not bleed into gold.

## 2. Affected modules

| Area | Change |
|------|--------|
| `src/**`, `tests/**`, `benchmarks/**` | **NONE** — no application code, no tests, no benchmark this slice. |
| MOD-001…005 | **unchanged** — referenced read-only. The regime classifier's output fields are the confidence-derivation inputs, but MOD-005 is not modified. |

## 3. Affected schemas

- **No schema authored or frozen.** The normative Gold DecisionPacket SCHEMA is deferred to Slice 2 (next free SCHEMA id, **never SCHEMA-004**; reserved 002/003/006 untouched).
- **SCHEMA-010 RegimeClassification** + **SCHEMA-009 FeatureVector** — referenced read-only as the confidence/uncertainty derivation inputs (all required fields already exist and are replay-safe). No shape change.
- **SCHEMA-005 EvaluationScorecard** — named only to **EXCLUDE** it: its calibration/sample_quality semantics must not be wired into the gold scalar (ADR-004 permanent separation).

## 4. Ontology impact

**New node:** **ADR-008 "Gold Decision Confidence Semantics"** (decision_record; `status: active`, `decision_status: active`; Justified By ADR-006/ADR-007/ADR-004; Constrained By [[Canonical Ownership]]).

**Updated nodes:**
- **ADR-006** — promote `status: draft → active` (log.md: "promote to active on acceptance"); re-mark §8(e) `materially advanced → satisfied`; add a 2026-06-08 note (ADR-008 closes (e); (c) closed; (b) gaps accepted); reconcile body "Proposed" vs `decision_status: active` (DEBT-18).
- **index.md / log.md** — add ADR-008 row; `decision_record` 7→8; total content nodes 124→125 (→126 only if a new gold capability node is also authored — see decision below); append writeback block; reconcile the headline-vs-tally stat drift (DEBT-05) while the file is open.

**Open canonical-ownership decision (CON-003) — must be consciously resolved, not bypassed.** **CAP-004 "Signal Generation"** (capability, `not-started`, parent_system [[systems/Trading Engine]] SYS-002) is defined as *"apply strategy rules to Layer 2 Snapshots → buy/sell/hold signals with associated confidence"* — semantically adjacent to a gold-decision capability and **co-located under SYS-002** (whereas CAP-015 "Decision Making" is treasury, under SYS-006). The prior recommendation disambiguated only against CAP-015 and missed this. Pick one:

- **(A) Distinct + bound (recommended).** Author a new gold-decision capability (next free CAP id — re-derive at authoring, do not hard-assume CAP-020) consuming SCHEMA-009 + INT-007/SCHEMA-010, explicitly bounded against CAP-004: *CAP-004 = legacy intraday indicator-stack equity signals → Order Management; gold capability = deterministic macro feature+regime → paper DecisionPacket (no live trade signal)*. They differ on inputs, outputs, and lifecycle. Author as a thin same-session companion, or defer to Slice 2 with the builder.
- **(B) Repurpose CAP-004.** If the legacy indicator-stack framing is deemed obsolete under the macro-gold pivot, re-scope CAP-004 in place (retains canonical_id, avoids a near-duplicate).

Either resolves "one concept = one node"; silently authoring a second SYS-002 signal capability would risk a CON-003 violation.

## 5. Replay impact

Closes **ADR-006 §8(c)** as a byproduct. ADR-008 pins the Gold-level replay-key components ADR-006 §3 requires (`decision_policy_version`, `configuration`, and whether `model_version` applies to a rule-based v0 builder) and shows the regime version-triple (`taxonomy_version`, `classifier_version`, `classification_trace_version`) composes into the Gold replay key. The confidence scalar is a pure deterministic composite over fields that are **already byte-identical-replayable** (`classify()` proven byte-identical; FeatureVector keyed by `snapshot_id + schema_version`), so it inherits replay-safety with no new mechanism. **Binding revisability clause:** any change to the confidence FORM/weights bumps `decision_policy_version` (never `taxonomy_version`); empirical recalibration against a future real corpus is an expected v1 amendment.

## 6. Benchmark impact

None this slice (no code to benchmark). One cheap, deterministic **sanity check** is in scope: validate the NEUTRAL/INDETERMINATE floors and the discount terms against the single consumable real snapshot (`snapshot_id 952cc83a…`, classifies RESTRICTIVE_RATES, `rule_margin 0.46`, with its actual secondary/near sets) — the only place one real data point is informative. A confidence-distribution benchmark is deferred to Slice 2 (when the builder exists).

## 7. Migration risk

**Low.** Additive governance node + node-frontmatter edits; no `src`/`tests`/schema changes; no `wiki/**` or `raw/**` mutation. The one substantive risk is the CAP-004 canonical-ownership call (§4) — a conscious architectural decision, not a silent edit. The data caveat (one real snapshot; 10/11 regimes synthetic) is honestly carried as "gaps explicitly accepted" per ADR-006 §8(b), not hidden; the v0 scalar is labelled provisional and recalibratable.

## 8. Governance impact

- **Closes gate (e)**; closes (c); accepts (b)'s gaps explicitly (names the 7 reserved features — `real_yield_5y`, `breakeven_10y/5y`, `curve_5s10s`, `policy_spread`, `gold_price`, `gold_flow` — as not needed for v0). → all ADR-006 §8 gates pass → the Gold DecisionPacket SCHEMA/module/API/guards become authorable contract-first in Slice 2.
- **Permanent separation upheld (ADR-004):** the gold confidence scalar must not import SCHEMA-005 calibration/sample_quality; gold remains net-new canonical_ids, never the treasury branch.
- **Scope discipline:** governance + structure only. The heavier hygiene clusters (DEBT-02/03/07 Neo4j export edges; DEBT-04 KA→ADR backlinks) are **SPLIT into a separate pass** before the gold epoch's first trusted graph export — NOT folded here. DEBT-01 (publisher `NameError`) rides with the real-corpus work, off this slice's path.

## 9. Verification summary

No `pytest` (no code). Verification =

- the **11 dev_graph lint checks** on touched nodes (frontmatter, enums, ≥1 inbound link, broken wikilinks, canonical_id uniqueness, evidence-confidence coherence, type-content alignment);
- **gate-board coherence** — ADR-006 §8 reads all-pass with no advanced-vs-satisfied contradiction (admissibility check #7);
- **CON-003 disposition recorded** for CAP-004 (option A or B);
- ADR-008 ↔ ADR-006/007/004 cross-links resolve.

Gold SCHEMA/module/code remain intentionally absent (ADR-006 §8 honored).

---

**Next (Slice 2, unblocked once this lands):** author contract-first the normative Gold DecisionPacket v0 SCHEMA (next free id), the gold builder module, the Gold Decision API (next free INT id — re-derive; do not assume INT-009), tests + a confidence-distribution benchmark, and wire INT-007's empty `output_schema consumed_by` to the builder.
