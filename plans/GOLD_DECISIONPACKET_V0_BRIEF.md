# GOLD_DECISIONPACKET_V0_BRIEF

**Slice:** Gold DecisionPacket v0 lineage — contract-first build (SCHEMA-011, INT-009, CAP-020 + CAP-004 deprecation, MOD-006 builder, PRED-006/007 L3 guards, GATE-002, tests + BENCH-002).
**Date:** 2026-06-08. **Status:** STEP 0 — context-discovery complete; not yet implemented.
**Type:** Contract + implementation slice. All ADR-006 §8 gates pass (ADR-008 closed (e); (b)/(c) finalized), so the Gold v0 contract and builder are authorable.

This brief is the STEP 0 deliverable: it records what the slice touches and the architectural reconciliation it rests on, established via dev_graph + code discovery before any contract or code is written. It mirrors `REGIME_IMPLEMENTATION_BRIEF.md` and `GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md`.

---

## 1. Objective

Author, contract-first, the **Gold DecisionPacket v0** — the paper-trading planning artifact that turns a Feature Vector (SCHEMA-009) + a Regime Classification (SCHEMA-010, via INT-007) into a deterministic, replay-safe gold stance: a `direction` (the regime→direction policy) + `confidence`/`uncertainty` (the ADR-008 ordinal trust score) + cited features + guard references. It is **paper_only**, instrument = gold/GLD proxy — **not** a live trade signal, order, or broker instruction (ADR-006 §1, Non-Goals). It is a **net-new bounded context** with new canonical_ids, permanently separate from the Supervisor treasury branch (ADR-004).

This realizes the entire gold lineage the audits named as the keystone, now that all five ADR-006 §8 Creation Gates pass.

## 2. Affected modules

| Area | Change |
|------|--------|
| `src/gold/decision_builder/` (NEW, MOD-006) | `models.py` (SCHEMA-011 dataclasses: `GoldDecisionPacket`, `Direction` enum, `FeatureCitation`, `GuardRefs`), `config.py` (`DecisionPolicyConfig` — confidence weights + regime→direction table + `decision_policy_version` + `decision_policy_fingerprint`), `policy.py` (pure helpers: `trust_score`, `direction_for`), `decision_builder.py` (`build_decision(fv, rc, config, as_of) -> GoldDecisionPacket`), `__init__.py` |
| `pyproject.toml` | add `"src/gold"` to hatch wheel packages |
| `tests/gold/` (NEW) | `test_decision_builder.py` (TEST-010), `test_gold_bench.py` (TEST-011) |
| `benchmarks/gold/` (NEW) | `run_gold_bench.py` (BENCH-002) + `artifacts/gold_bench.json` |
| MOD-003/004/005 | **unchanged** — consumed read-only upstream (`FeatureVector`, `RegimeClassification`). No re-derivation of regime/feature logic. |
| MOD-001/002 | **unchanged** — separate bounded contexts (risk, treasury). |

The builder is a **pure, total, stdlib-only, fail-closed** function of `(FeatureVector, RegimeClassification, DecisionPolicyConfig)` — no IO/clock/randomness/history (ADR-003/006 §3). It consumes the `RegimeClassification` (primary) + `FeatureVector` (for coverage/citation); it does **not** call `classify()` itself (the caller composes `consume → build_features → classify → build_decision`).

## 3. Affected schemas

- **NEW SCHEMA-011 `GoldDecisionPacket` v0** — produced by MOD-006. Next-free id (SCHEMA-002/003/006 stay reserved; **never SCHEMA-004**, the treasury packet). Field groups:
  - *decision* — `packet_id` (deterministic composite, no clock/uuid), `packet_schema_version`, `instrument` (= `GLD`), `decision_mode` (= `paper_only`), `regime` (echoed `Regime`), `direction` (enum `LONG`/`FLAT`/`AVOID`/`WATCH`), `confidence` [0,1], `uncertainty` [0,1], `rationale` (deterministic templated string, no free LLM text);
  - *provenance/identity* — `source_snapshot_id`, `source_feature_schema_version`, `regime_taxonomy_version`, `regime_classifier_version`, `regime_classification_trace_version`, `matched_rule_id`, `cited_features` (array<FeatureCitation> — concrete MOD-004 features only, §5), `as_of` (deterministic, never wall-clock);
  - *versions* — `decision_policy_version` (the gold builder's policy axis, ADR-008 §7);
  - *trust trace* — `confidence_inputs` (anchor `rule_margin`, secondary/near counts, max_staleness, revision_risk, unavailable count) for auditability;
  - *guards* — `guard_refs` (the six-guard taxonomy outcomes the packet honored, §6);
  - *safety* — `non_execution_notice` (fixed), `constraints` (invariants asserted).
- **SCHEMA-009 FeatureVector** + **SCHEMA-010 RegimeClassification** — consumed read-only; no shape change. INT-007 `output_schema consumed_by` is wired to MOD-006 at writeback.
- **SCHEMA-004 / SCHEMA-005** (treasury) — untouched; field names kept deliberately distinct (`selected_upgrade_id`/`ranked_options` vs gold `direction`/`confidence`). No reuse.

## 4. Ontology impact

**New nodes (≈8 + file/test nodes at writeback):**
- **SCHEMA-011 Gold DecisionPacket v0 Schema** (artifact_schema) — contract first; `status: planned` / `implementation_status: not-started` until code lands, then bumped.
- **INT-009 Gold Decision API** (interface) — `build_decision(fv, rc, config, as_of) -> GoldDecisionPacket`; `input_schema` (primary) = SCHEMA-010, `### Consumes` lists both SCHEMA-009 + SCHEMA-010; `output_schema` = SCHEMA-011; `stability: experimental`. (INT-008 is earmarked for a future Evaluation API → this takes **INT-009**.)
- **CAP-020 Gold Decision Generation** (capability) under SYS-002 — `### Supersedes → [[Signal Generation]]`; consumes SCHEMA-009/010, produces SCHEMA-011, provides INT-009, realizes [[Pipeline Pattern]] (the successor pipeline stage).
- **MOD-006 Gold Decision Builder** (module) — authored at the implementation step (plan-first body, then code).
- **PRED-006 Duplicate OK**, **PRED-007 Operational OK** (predicates) — the two net-new L3 guards (ADR-004 six-guard taxonomy / ADR-006 §6); **not** MOD-004 features.
- **GATE-002 Gold Decision Gate** (gate) — composes the L3 guards the packet's `guard_refs` cite.
- File nodes (FILE-015…018) + test nodes (TEST-010/011) + **BENCH-002** at writeback.

**CAP-004 "Signal Generation" deprecate-and-supersede (atomic with CAP-020, per ADR-008 §10):**
- CAP-004: `status: active → deprecated`, `implementation_status → deprecated`, deprecation reason recorded in-body, successor `[[Gold Decision Generation]]` named. (Not kept as legacy; not repurposed in place.)
- **Rewire inbound edges so lint check 9 stays clean:**
  - **PAT-004 Pipeline Pattern** — replace `[[Signal Generation]]` with `[[Gold Decision Generation]]` in `instances`, `realized_by_capabilities`, and `### Realized By` (CAP-020 is the successor pipeline stage; PAT-004 keeps ≥2 realizers).
  - **CAP-005 Order Management** `### Depends On [[Signal Generation]]` — annotate: Signal Generation is deprecated and live order routing is deferred (ADR-006 Non-Goals); the gold v0 capability is **paper-only and does not feed Order Management** (so the edge is annotated, not redirected — redirecting would falsely imply a paper packet drives live execution).
  - **SYS-002 Trading Engine** — add `[[Gold Decision Generation]]` to `contains_capabilities` + `### Contains`; annotate the `## Capabilities` prose to mark Signal Generation deprecated→successor.
- Permanent separation from CAP-015 "Decision Making" (treasury, SYS-006) preserved (ADR-004) — untouched.

No new ontology *types* or enum values; the 24-type ontology already covers everything. No `sync_to_neo4j.py` change.

## 5. Replay impact

Extends the determinism chain to the decision layer, honoring ADR-006 §3 as finalized by ADR-008 §8:

- **Packet replay key:** `source_snapshot_id + source_feature_schema_version + regime_taxonomy_version + regime_classifier_version + decision_policy_version + configuration ⇒ identical packet`. (`model_version` is N/A for the rule-based v0; `decision_policy_version` subsumes policy identity.)
- `build_decision()` is pure/total: confidence is the ADR-008 deterministic ordinal trust score; direction is a deterministic table lookup; `packet_id` is a deterministic composite (no uuid/clock); `as_of` is caller-supplied. The regime version-triple composes in unchanged.
- A `decision_policy_fingerprint` (SHA-256 over the confidence weights + direction table, mirroring the regime `decision_fingerprint`) binds `decision_policy_version` to its policy set; a coherence test fails CI on un-versioned drift (ADR-008 §7 risk mitigation).

## 6. Benchmark impact

**BENCH-002 Gold Decision Distribution Benchmark** — `benchmarks/gold/run_gold_bench.py` + committed golden `artifacts/gold_bench.json`, mirroring BENCH-001's structure:
- *determinism* — replay the real snapshot(s) through `consume → build_features → classify → build_decision` twice; assert byte-identical packet `to_dict()`; record the real packet (RESTRICTIVE_RATES → direction `AVOID` under the v0 table; confidence ≈ 0.40).
- *synthetic sweep* (clearly labelled) — over the same fixed regime feature-grid, emit the `direction` distribution, `confidence`/`uncertainty` distributions, and per-regime direction coverage; assert the committed artifact stays in sync.

## 7. Migration risk

**Low–moderate.** Mostly additive: a new `src/gold` package, new tests, new benchmark, new dev_graph nodes, one `pyproject.toml` line. The one cross-cutting, non-additive change is the **CAP-004 deprecation rewiring** (PAT-004 / CAP-005 / SYS-002 edges) — handled per the Deprecation Procedure and lint check 9, mechanically and reviewably. No `wiki/**` or `raw/**` mutation. No existing module/schema/test/canonical_id is changed in a breaking way. The single real snapshot / synthetic-coverage caveat (10/11 regimes synthetic) carries through honestly from the regime layer; direction and confidence are explicitly provisional (calibration deferred to the real corpus, `decision_policy_version` bump).

## 8. Governance impact

- **All five ADR-006 §8 gates pass** → the Gold contract is authorable; this slice authors it contract-first.
- **ADR-006 §1/§2/§5/§6 honored:** net-new bounded context + ids; consumes only SCHEMA-009 + SCHEMA-010 (never raw SCHEMA-001/JSON/external/state/history); cites only the 14 named MOD-004 features (no inventions); `duplicate_ok`/`operational_ok` are L3 guard **predicate nodes**, never MOD-004 features.
- **ADR-008 honored:** confidence = ordinal trust score (anchor = within-rule `rule_margin`; four discounts; NEUTRAL/INDETERMINATE floors; uncertainty = structural-penalty aggregate); not a probability; not the 3-component variant; no SCHEMA-005 calibration bleed; weights under `decision_policy_version` + fingerprint coherence test.
- **ADR-004 separation upheld:** gold ≠ treasury; CAP-015/INT-006/SCHEMA-004/005 untouched; CAP-004 superseded by the gold capability, not merged into treasury.
- **Hygiene** DEBT-01/02/03/04/07 stay in their separate pass (the gold epoch's first trusted Neo4j export wants DEBT-02/03/07 fixed — flagged, not done here).

## 9. Verification summary

- **Tests:** `tests/gold/` unit (field invariants, direction-table totality over all 12 regimes, fail-closed INDETERMINATE → `WATCH`), determinism (build == build, byte-identical `to_dict()`), confidence model (anchor/discounts/floors per ADR-008), `decision_policy_fingerprint` coherence (weights/table edit without a `decision_policy_version` bump fails CI). Target: full suite green (53 prior + 719 regime + new gold).
- **Benchmark:** BENCH-002 golden artifact regenerated deterministically; `all_replays_byte_identical = true`; committed-artifact-in-sync test.
- **Static:** `mypy --strict` clean on `src/gold` + tests; `ruff` clean.
- **dev_graph:** file/test nodes per §7.5 threshold; MOD-006 + CAP-020 `implementation_status` bumped; INT-007/SCHEMA-009/SCHEMA-010 `consumed_by` wired to the gold builder; index.md + log.md updated; **all 11 lint checks** on touched nodes (incl. check 9 deprecated-reference after the CAP-004 flip); **gate-board coherence** (ADR-006 §8 still reads all-pass).

---

## Design decision settled here — the regime → direction mapping

ADR-008 fixed *confidence*; nothing yet specifies how a regime maps to a gold stance. **Decision: treat the regime→direction mapping as versioned decision-policy config under `decision_policy_version` v0 — NOT a companion ADR.**

**Why no companion ADR (per the user's stated test — "a separation/governance hazard comparable to confidence"):** direction carries **no** comparable hazard. (1) No cross-context bleed: unlike confidence (which risked pulling SCHEMA-005 treasury calibration), the direction table is purely gold-internal and touches no other bounded context. (2) No semantic-overclaim risk: `direction` is a plain categorical, paper-only, explicitly non-execution stance — not a probability. (3) It is structurally identical to the regime thresholds (`RegimeConfig`), which live in versioned config, not an ADR. (4) ADR-008 already established `decision_policy_version` as the governing axis for *the gold builder's decision policy*, and direction **is** decision policy — so it is already governed and fingerprinted.

**Governance safeguard (in lieu of an ADR):** the per-regime gold thesis (the table's rationale) is documented in the SCHEMA-011 + MOD-006 nodes and here, flagged **provisional / domain-anchored / calibration-deferred**, and pinned under `decision_policy_version` v0 with its own coherence test (folded into `decision_policy_fingerprint`).

**Direction enum (v0):** `LONG` (regime supports gold) · `FLAT` (no directional edge) · `AVOID` (regime is a gold headwind) · `WATCH` (insufficient/ambiguous basis — fail-closed default).

**Illustrative v0 table (pinned as config in the implementation step; shown here for review — economically provisional):**

| Regime | Direction | Gold thesis (provisional) |
|--------|-----------|---------------------------|
| LIQUIDITY_STRESS | LONG | funding-stress haven bid |
| RISK_OFF | LONG | risk-off haven bid |
| VOLATILE | FLAT | elevated vol, direction unclear |
| RESTRICTIVE_RATES | AVOID | high real yields are a gold headwind |
| REFLATION | LONG | rising inflation expectations + easy real rates |
| DISINFLATION | FLAT | low inflation expectations — real-yield channel offsets the hedge headwind (finalized) |
| CURVE_INVERSION | WATCH | recession signal, mixed for gold |
| STRONG_USD | AVOID | strong USD headwind |
| RISK_ON | FLAT | risk appetite competes with gold |
| LOW_VOL | FLAT | calm, no edge |
| NEUTRAL | FLAT | no signal |
| INDETERMINATE | WATCH | fail-closed — no stance |

The table is total over all 12 `Regime` values (a coherence test asserts this), and INDETERMINATE always maps to `WATCH` (fail-closed).

## Canonical-id re-derivation (at authoring, per ADR-006 §7)

Verified against `index.md` (2026-06-08): SCHEMA → next free **SCHEMA-011** (002/003/006 reserved; never 004); INT → **INT-009** (INT-008 earmarked Evaluation API); CAP → **CAP-020** (last is CAP-019); MOD → **MOD-006**; PRED → **PRED-006/007**; GATE → **GATE-002**; BENCH → **BENCH-002**; FILE → **FILE-015+**; TEST → **TEST-010/011**.

## Execution order (strict contract-first) + checkpoint

1. **Contract layer (no code):** SCHEMA-011 + INT-009 nodes.
2. **Capability + CAP-004 deprecation (atomic):** CAP-020 + flip CAP-004 → deprecated + rewire PAT-004 / CAP-005 / SYS-002; partial writeback (index.md + log.md + lint).
   → **CHECKPOINT: pause for review here — contract + capability frozen, no code.**
3. **Implementation:** MOD-006 builder + `DecisionPolicyConfig` (confidence weights + direction table + fingerprint) + code.
4. **L3 guards:** PRED-006/007 + GATE-002.
5. **Tests + benchmark:** unit + determinism + fail-closed + fingerprint-coherence; BENCH-002 golden.
6. **Writeback:** file/test nodes; bump statuses; wire `consumed_by`; index.md + log.md; 11 lint checks; gate-board coherence.

## Deferred (ADR-006 Non-Goals — not authored)

Live execution, broker integration, order routing, position sizing, fills, P&L, paper-trading runtime, scheduler, learned/history-dependent regimes, secondary stateful layers, real-corpus accumulation. Hygiene DEBT-01/02/03/04/07 stay in their separate pass.
