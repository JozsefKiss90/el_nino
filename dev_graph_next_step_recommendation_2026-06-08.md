# Dev Graph — Next Development Step Recommendation

**Date:** 2026-06-08
**Question:** What is the next development step for the el_nino dev_graph after the Deterministic Regime Taxonomy slice (MOD-005)?
**Method:** Evidence fan-out (4 lenses: ADR-006 gate status, candidate enumeration, code/entry-point ground truth, retrieval readiness) → lead-architect synthesis → 3-angle adversarial refutation (governance-gate, data-realism, architecture-dependency) → finalize. Read-only against primary sources (ADR-004/005/006/007, SCHEMA-009/010, INT-007, `src/regime/*`, `src/features/*`, `dev_graph/index.md`, both prior audits). No nodes, files, or commits modified.

---

## BLUF

> **Build the Gold DecisionPacket v0 lineage — the keystone the entire ADR chain has been building toward — but sequence it as a tight 3-slice arc, governance-first. Do NOT freeze the Gold schema yet: the single load-bearing open gate is ADR-006 §8(e) "confidence semantics," and it is genuinely unsettled (the regime layer's `rule_margin` is explicitly *not* epistemic confidence). Close gate (e) and wire a structural gold entry point first; freeze the contract second; build third.**

The Regime Taxonomy slice that the 2026-06-07 stabilization audit named as the highest-value next step is **done** (MOD-005, passed its own audit 97/100). It closed ADR-006 §8 gate **(d)** and materially advanced **(b)/(c)/(e)**. The frontier is now the Gold lineage, with exactly one real design decision blocking the contract.

---

## The decisive finding: gate (e) is open, not "materially advanced"

ADR-006 §8 forbids authoring the normative Gold DecisionPacket SCHEMA until **all** Creation Gates pass, and its "Alternatives Considered → freeze now" is explicitly **Rejected**. Current gate status, verified against primary sources:

| Gate | Text (abbrev.) | Status | Basis |
|---|---|---|---|
| (a) | MOD-004 Feature Builder implemented | **CLOSED** | MOD-004 active/tested; 14 grounded features |
| (b) | Deterministic feature coverage validated for regime/**confidence/direction** | **MATERIALLY ADVANCED** | 14 features exercised by the classifier; sufficiency confirmed for *regime* only — confidence/direction sufficiency not yet signed off |
| (c) | Replay requirements finalized (full v0 key + `model_version`/`decision_policy_version`/`configuration`) | **MATERIALLY ADVANCED** | Regime replay key pinned; the decision-builder's portion of the key is undefined |
| (d) | Regime taxonomy enumerated & grounded | **CLOSED** | ADR-007 / SCHEMA-010 / INT-007; 11 signal regimes + NEUTRAL + INDETERMINATE |
| **(e)** | **Confidence semantics agreed — scalar `confidence`(+`uncertainty`) model fixed** | **OPEN** | The regime layer fixed `rule_margin` as a *rule-local activation margin*, explicitly **"not epistemic confidence and not comparable across rules"** (ADR-007 §3; `regime/regime_classifier/models.py:10`). The Gold packet's `confidence` scalar is therefore genuinely undefined. |

The 2026-06-08 ADR-006 update's claim that (e) is "materially advanced … the scalar is fixed as a rule-local `rule_margin`" is a **conflation**: `rule_margin` measures how far the winning rule fired past its own threshold — orthogonal to how *confident* the decision is. A barely-matched RESTRICTIVE_RATES can have low margin; a far-from-anything NEUTRAL can have high margin. Neither is confidence. **Gate (e) is real, unfinished design work and is the load-bearing blocker.**

Good news from code ground truth: the gap is *design*, not *data*. A deterministic, replay-safe confidence scalar **can** be composed entirely from fields that already exist and are frozen — no history, no calibration data required:

- **strength** — `rule_margin`, normalized **per rule** (because it is rule-local, not cross-comparable);
- **contention** — `secondary_matching_rules` / `near_matching_rules` (many competitors ⇒ lower confidence);
- **data quality** — per-feature `max_staleness_days`, `revision_risk`;
- **coverage** — `unavailable_features`, `failed_required_features`.

What is missing is an *agreed functional form*, which is exactly what a gate-(e) ADR settles.

---

## Recommendation — Gold DecisionPacket v0, as a 3-slice arc

### Slice 1 — Governance & structure (contract-first, no Gold schema yet)

1. **Author a new gate-(e) ADR** (next free id, e.g. ADR-008) that fixes the Gold packet's scalar `confidence`(+`uncertainty`) as the **deterministic margin/contention/coverage composite** above. Author it as a *new* ADR (mirroring how ADR-007 closed gate (d)), then edit ADR-006 §8(e) to "satisfied" — do **not** stuff the contract into ADR-006, which is a boundary record scoped to *not* author the schema.
   - **Frame it explicitly as a deterministic composite, NOT a calibrated probability.** Record "empirical calibration deferred to real-corpus accumulation" as an accepted gap (the same honest trade-off ADR-007 made for domain-anchored thresholds). This neutralizes the data-realism objection.
2. **Author a new, explicitly-bounded gold-decision Capability under SYS-002 (Option A), and dispose of CAP-004 separately.** Reading the actual CAP-004 "Signal Generation" node shows it is *genuinely distinct* from a gold-decision capability on three axes — it consumes the **L2 Snapshot directly via Snapshot API** (gold consumes only SCHEMA-009 + SCHEMA-010, never raw SCHEMA-001); it runs an **intraday technical indicator stack (VWAP/EMA/RVOL)** that ADR-005 forbids in the macro snapshot-local pipeline; and it emits **live per-symbol signals to Order Management** (gold emits a paper DecisionPacket, execution deferred). Because it is a *different concept*, **repurpose-in-place is the wrong move** (it would overwrite distinct semantics and leave the node name and every body section wrong). Instead:
   - Author a new gold-decision capability (next free CAP id, re-derived at authoring), explicitly bounded against CAP-004, consuming SCHEMA-009 + INT-007/SCHEMA-010 → paper DecisionPacket. This fixes the stabilization audit's Part 10 retrieval-misfire (a "build the Gold builder" query currently routes to the treasury branch CAP-015 under SYS-006 because no gold entry node exists) and makes bounded-context separation graph-structural, not prose-only. The capability node itself can land in **Slice 2** alongside the builder/schema, keeping Slice 1 purely governance.
   - **Dispose of CAP-004: deprecate-and-supersede it** (resolved from repo evidence, not left as an open user choice). A search of the *current* authoritative docs settles it: ADR-005 forbids the history-dependent indicators (VWAP/EMA/RVOL) CAP-004 is built on; ADR-007 explicitly rejects a trend/price-action taxonomy on the same grounds; ADR-006 §5 pins inputs to 14 macro series and its Non-Goals defer both rolling-window features and live execution / Order Management (CAP-004's method *and* its output sit in the deferred zone); the realized code is macro-only on a single gold/GLD paper instrument; and CAP-004 traces only to two stale wiki pages with no current-chain ADR and empty `implemented_by`/`interfaces` — i.e. a speculative `active`/`not-started` placeholder the population strategy says shouldn't exist. The only non-derivable residue is whether the team holds an *unstated* intention to add an intraday/technical desk later; the architecture leaves no room for one, so absent that intention, deprecation is the supported call. Record the deprecation + supersession (new gold capability) in ADR-008's separation language. *(This collision was the one genuine omission the adversarial pass caught — its disposition must be recorded, not skipped.)*
4. **Ride-along hygiene that the gold epoch is the first to actually need** — the gold layer is the first consumer of a *trustworthy* Neo4j / Graph-RAG export:
   - **DEBT-01** — rename `snapshot_publisher.py:625` `H_get_engine_version()` → `_get_engine_version` (restores the broken producer leg; guaranteed `NameError` today).
   - **DEBT-02/03/07** — drop MOD-003's `provides`/`Implements` on INT-001, fix MOD-002's upward module→capability `Depends On`, normalize mixed bare-vs-path wikilink forms (these silently drop ≥6 export edges).
   - **Trailing micro-step (review separately so it doesn't dilute the gate reasoning):** DEBT-04 (10/10 KA→ADR `informs_decisions` back-links), DEBT-05 (index statistics) and **DEBT-13** (index Modules table still labels MOD-001/002 "(plan only)" despite tested code).

### Slice 2 — Freeze the contract (no code)

5. **Freeze the Gold DecisionPacket v0 SCHEMA** as **SCHEMA-011** (ADR-007 already names SCHEMA-011 as the Gold candidate — *not* "next after 010") and the **Gold Decision API** interface as **INT-009** (INT-008 is reserved for the Supervisor Treasury API). Inputs are **only** SCHEMA-009 FeatureVector + SCHEMA-010 RegimeClassification — never raw SCHEMA-001 — with provenance tracing to `source_snapshot_id`. Pin the full v0 replay key (closes the remainder of gate (c)).

### Slice 3 — Build (code + tests + benchmark + writeback)

6. **Build the Gold Decision Builder module** (next free MOD id) + the **L3 guards `duplicate_ok` / `operational_ok`** (sanctioned by ADR-006 §6 / ADR-004's six-guard taxonomy — these are L3 module guards, **not** MOD-004 features). Deterministic, fail-closed, stdlib-only, per established discipline: tests, a benchmark, and full writeback (log.md + index.md + 11 lint checks). Add the deferred paper-trading E2E test (snapshot → FeatureVector → RegimeClassification → Gold packet) now that INT-007 is consumed.

---

## The one open design question

**What functional form does `confidence` take?** The inputs are settled and deterministic; the decision is how to combine normalized-per-rule `rule_margin`, rule contention, provenance staleness/revision risk, and coverage into one scalar (and its `uncertainty` companion) — and how to bucket or normalize the rule-local margin so it is comparable across regimes. Three sub-choices the ADR must pin: (1) how normalized `rule_margin` maps to a confidence anchor without becoming a cross-rule score; (2) whether `uncertainty` is `1 − confidence` or a separate penalty aggregate; (3) what the NEUTRAL (confident-quiet) vs INDETERMINATE (fail-closed) floors mean. Sanity-check the chosen floors and anchor against the one real consumable snapshot (RESTRICTIVE_RATES, `rule_margin` 0.46) before freezing. This is the substance of the Slice 1 gate-(e) ADR.

---

## Explicitly deferred (matches ADR-006 Non-Goals — not in this arc)

Execution, broker integration, order routing, position sizing, paper-trading *runtime*, learned/history-dependent regimes, and real-corpus accumulation. The data corpus (one consumable real snapshot today; 10/11 regimes synthetic-only) is an honestly-recorded caveat for *calibration*, **not** a blocker on authoring a deterministic contract — gates (b)/(e) are design-sufficiency gates, not data-volume gates.

---

## Alternatives considered and rejected

| Alternative | Why rejected |
|---|---|
| **Freeze the Gold v0 schema now** | Forbidden by ADR-006 §8 ("freeze now" = Rejected) while gate (e) is open. Would hard-code an unsettled confidence semantic. |
| **Accumulate a real snapshot corpus first** | The contract is deterministic over already-frozen fields; authoring does not depend on data volume. Corpus work is deferred calibration, parallelizable, and gated on DEBT-01. |
| **Do CAP-002/CAP-003 seam re-grounding first** | Audit classifies these as *correctly governed deferrals, explicitly "NOT debt."* They do not block the Gold builder, which consumes FeatureVector + RegimeClassification (both tested today). |
| **Do only hygiene this epoch** | Leaves the keystone unbuilt; the 0-blocking debt items are cheap enough to ride along with Slice 1. |
| **One big Gold slice (schema + capability + API + builder + guards)** | Violates the minimal-additive-slice discipline and reviews load-bearing gate-(e) reasoning alongside implementation. The 3-slice split keeps each review clean. |

---

## Verification trail

- **Gate status** independently audited against ADR-006/007/005, SCHEMA-010, INT-007, and the regime source — gate (e) confirmed open; rule_margin ≠ confidence quoted from code.
- **Code ground truth** confirmed the Gold lineage is greenfield (only `risk`, `supervisor`, `snapshot`, `features`, `regime` packages; no gold/builder/`duplicate_ok`/`operational_ok` anywhere in `src/`), the confidence composite is derivable from existing frozen fields, and authoring the v0 contract is purely additive.
- **Adversarial refutation** (governance-gate, data-realism, architecture-dependency) returned **refuted=false on all three angles**; the recommendation survived. Refinements folded in above: gate-(e) as a *new* ADR; confidence framed as deterministic-not-calibrated; the CAP-004 overlap resolution (the one real omission); hygiene split; and the SCHEMA-011 / INT-009 id corrections.

*Read-only analysis. This document is a planning recommendation; it authors no dev_graph nodes and freezes no contract.*
