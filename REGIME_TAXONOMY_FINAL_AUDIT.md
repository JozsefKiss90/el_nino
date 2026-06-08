# Regime Taxonomy Final Audit

**Date:** 2026-06-08
**Scope:** The Deterministic Regime Taxonomy slice (MOD-005 Market Regime Classifier, SCHEMA-010 Regime Classification Schema, INT-007 Regime Classification API, ADR-007, CAP-019 Market Regime Classification, and associated supporting nodes) is a Gold Layer decision-support module that classifies validated Feature Vectors (from MOD-004) into one of 12 enumerated market regimes. The module sits between the Feature Builder (MOD-004 upstream) and the future Gold DecisionPacket builder (downstream, deferred per ADR-006 §8). All 14 new governance and code nodes have been authored and committed.

> Methodology: 11 independent read-only auditors (one per dimension) ran in parallel, each returning a structured verdict; every critical/FAIL candidate was routed to an adversarial verifier that defaulted to "refuted unless clearly real." 0 critical candidates survived verification. This document is the synthesis.

---

## Executive Summary

**Overall Verdict:** PASS

**Readiness Score:** 97/100

The Deterministic Regime Taxonomy implementation is **production-ready for its defined scope**. All eleven audit dimensions are PASS or WARN with no confirmed critical issues. ADR-006 gate (d) is fully satisfied (regime taxonomy enumerated and grounded). The regime layer is correctly positioned between Feature Builder and the future Gold builder, maintains strict separation from the treasury decision branch (ADR-004), and produces deterministic, auditable classifications across all real and synthetic coverage. Code quality is high (772 tests pass — 719 regime + 53 prior; mypy --strict clean on the regime package; ruff clean; determinism validated byte-identical). The work is transparent about its constraints (synthetic coverage, single real snapshot corpus) and correctly defers the Gold builder per governance.

---

## Per-Dimension Results

| Dimension | Verdict | Score |
|-----------|---------|-------|
| Architecture | PASS | 98 |
| Replay Determinism | PASS | 98 |
| Ontology Compliance | PASS | 100 |
| Population Strategy Compliance | PASS | 98 |
| ADR Compliance | PASS | 98 |
| Feature Grounding | PASS | 98 |
| Schema Correctness | PASS | 97 |
| Graph Integrity | PASS | 99 |
| Gold Layer Readiness | PASS | 100 |
| Benchmark Integration | PASS | 98 |
| Paper Trading Compatibility | PASS | 95 |

---

## Architecture

**Summary:** MOD-005 achieves full architectural conformance. The regime layer sits correctly positioned between MOD-004 Feature Builder (upstream) and the future Gold Decision Builder, consuming FeatureVector (SCHEMA-009) exclusively and never raw snapshots. Complete separation from the Supervisor treasury branch (MOD-002/INT-006) is enforced: zero cross-imports in both directions. Package layout mirrors existing conventions (src/{domain}/{module_name}/), and the public API (INT-007) is cleanly exposed.

**Findings:**
- **PASS:** MOD-005 consumes only FeatureVector from MOD-004, never raw snapshots. The `classify(fv: FeatureVector, ...)` signature enforces the contract at type level; implementation accesses `fv.features`, never Snapshot models.
- **PASS:** Zero imports from the supervisor module tree across `src/regime/*.py`; supervisor code contains no regime imports (complete isolation). The Feature → Regime → Decision ontology is maintained.
- **PASS:** Package layout mirrors MOD-004: `src/regime/regime_classifier/` with `__init__.py`, `regime_classifier.py`, `models.py`, `taxonomy.py`, `config.py`. Public API exports align with INT-007.
- **PASS:** Governance documents (ADR-007, MOD-005, CAP-019, INT-007, SCHEMA-010) are coherent and cross-linked; ADR-006 §8(d) satisfied; ADR-004 permanent-separation invariant respected.

---

## Replay Determinism

**Summary:** `classify()` is a pure, total function producing byte-identical output across replays. No wall-clock, randomness, IO, global state, caches, or history. Margin rounding at serialization (6 dp) neutralizes float-format drift. Benchmark confirms `all_replays_byte_identical=true`.

**Findings:**
- **PASS:** `classify()` is pure and total — immutable inputs `(FeatureVector, RegimeConfig | None, as_of: str | None)`, no globals modified, no IO; `RULE_TABLE` is a frozen tuple; returns a frozen `RegimeClassification`.
- **PASS:** No wall-clock/`datetime.now()`. `as_of` is optional (defaults None), never auto-set: `classify(fv)` → `as_of=None`; `classify(fv, as_of='…')` passes through unchanged.
- **PASS:** No randomness or global mutable state — no `random`/`uuid`; config frozen; internal accumulators are local.
- **PASS:** `to_dict()` byte-stable — alphabetical keys, margin rounded to 6 dp; golden JSON test confirms byte-identical serialization (internal `0.45999999999999996` → `0.46`).
- **PASS:** Benchmark `all_replays_byte_identical=true` across 3 consumable real snapshots; real PASS fixture → RESTRICTIVE_RATES / `R04_restrictive_rates` / margin 0.46.
- **PASS:** 719 regime tests pass; mypy --strict clean; ruff clean.

---

## Ontology Compliance

**Summary:** All 14 new dev_graph nodes fully conform to `dev_graph/CLAUDE.md`. Universal frontmatter present; enums closed; canonical_ids unique and correctly formatted; type-to-directory bindings verified; all nodes carry `## Relationships` with outbound wikilinks; evidence-confidence coherence maintained.

**Findings:**
- **PASS:** 14 canonical_ids unique and correctly formatted (ADR-007, KA-011, PAT-011, CAP-019, INT-007, SCHEMA-010, MOD-005, FILE-011–014, TEST-008/009, BENCH-001).
- **PASS:** Required universal frontmatter fields present on all 14 nodes; all enum fields within closed sets.
- **PASS:** KA-011 and PAT-011 correctly omit `implementation_status`; all others include it.
- **PASS:** Type-to-directory bindings verified across all 10 affected directories.
- **PASS:** Every node has a `## Relationships` section with ≥1 outbound wikilink; file nodes carry required `module:` inbound link; test nodes carry `covers`.
- **PASS:** No freeform frontmatter keys.

---

## Population Strategy Compliance

**Summary:** The slice followed Population Strategy discipline: contract-first (ADR-007/SCHEMA-010 before code), canonical ownership, no wiki/raw mutation, full writeback checklist (11 lint checks passing). One minor narrative inconsistency in SCHEMA-009 Open Questions does not reflect a governance violation.

**Findings:**
- **PASS:** Contract-first — ADR-007, INT-007, SCHEMA-010 authored same session as code; all new modules have `related_decisions` populated.
- **PASS:** Canonical ownership — 14 unique nodes, substantive content (no TBD); MOD-004/SCHEMA-009 updated with additive downstream links only.
- **PASS:** No `wiki/**` or `raw/**` mutations; only `dev_graph`, `src/regime`, `tests/regime`, `benchmarks/regime`, and root prep docs touched.
- **PASS:** Writeback checklist fully executed — file/test nodes created, MOD-005/CAP-019 status bumped, log.md appended, index.md updated, 11 lint checks passed.
- **WARN:** SCHEMA-009 Open Questions narrative still mentions `consumed_by` as empty though the frontmatter was correctly updated. Non-blocking (governance is frontmatter-driven).

---

## ADR Compliance

**Summary:** Fully satisfies ADR compliance. Code is deterministic, fail-closed (missing features → INDETERMINATE), purely rule-based with domain-anchored thresholds (not learned/fitted), and strictly separated from treasury logic (ADR-004). Forbidden feature classes never used. Config is stdlib-only with fail-closed errors. ADR-006 gate (d) satisfied; Gold builder correctly deferred.

**Findings:**
- **PASS:** ADR-004 separation honored — no supervisor imports, no treasury terminology in regime code.
- **PASS:** ADR-005 forbidden feature classes NOT leaked — `RULE_TABLE` uses only pure level/spread features; no momentum/rolling/z-score/percentile/learned features; no `learned`/`fitted`/`train`/`model` in regime code.
- **PASS:** Rule-based, not learned — thresholds are standard macro bands (VIX 15/25/35, MOVE 125, real-yield +1.5%, 5y5y 2.0/2.5, curve 0, USD 120), versioned by `TAXONOMY_VERSION`; no fitting code.
- **PASS:** ADR-006 gate (d) satisfied and Gold builder NOT built — no SCHEMA-011 / Gold module / guard code.
- **PASS:** ADR-003 stdlib-only + fail-closed — imports restricted to stdlib; `RegimeConfigError` on missing/invalid config.
- **PASS:** Determinism invariant verified; coverage 11/11; real PASS → RESTRICTIVE_RATES (0.46); fingerprint-pinned coherence test.
- **PASS:** Fail-closed on missing required features → INDETERMINATE with reason (never a guessed regime).
- **WARN:** Coverage is honestly labelled synthetic (no real historical corpus — 3 fixtures + 2 source snapshots only).

---

## Feature Grounding

**Summary:** The classifier and config reference ONLY the 14 real MOD-004 features. All 7 features used in the taxonomy are verified present in `FEATURE_REGISTRY`. No invented indicators. The 7 deliberately unused features are not referenced in code.

**Findings:**
- **PASS:** All 7 used features (breakeven_5y5y_fwd, curve_2s10s, equity_level, rates_vol, real_yield_10y, usd_level, vol_level) present in `feature_builder.py` FEATURE_REGISTRY (lines 55–70).
- **PASS:** Required-feature gate `(vol_level, real_yield_10y, curve_2s10s, usd_level)` is a strict subset of available features.
- **PASS:** No invented indicators — exhaustive grep of `src/regime/` yields only the 7 registry features.
- **WARN:** Seven features deliberately unused (breakeven_10y, breakeven_5y, curve_5s10s, gold_price, gold_flow, policy_spread, real_yield_5y). Rationale is in ADR-007 §1 context but not stated as a single explicit note in `config.py`/`taxonomy.py`.
- **PASS:** mypy --strict clean, ruff clean, 719 tests pass, benchmark determinism true.

---

## Schema Correctness

**Summary:** SCHEMA-010 (RegimeClassification) is comprehensively correct and well-tested. Dataclass definition, field groups, `__post_init__` invariants, and `to_dict()` serialization all align with the schema node and are validated by passing tests. The three independent version fields are correctly separated.

**Findings:**
- **PASS:** Field groups correct — decision / provenance-identity / versions / explainability-trace match the SCHEMA-010 definition exactly.
- **PASS:** `__post_init__` invariants complete — margin ∈ [0,1]; INDETERMINATE ⇒ margin 0.0 + reason; NEUTRAL/INDETERMINATE ⇒ null threshold/scale + empty triggers; non-terminal ⇒ threshold/scale set; `matched_rule_id ∉ secondary_matching_rules`.
- **PASS:** `to_dict()` deterministic/byte-stable (sorted keys, 6-dp margin); golden JSON confirms.
- **PASS:** Three version fields separated — taxonomy (thresholds) / classifier (logic) / classification_trace (explainability); trace-version change does not affect decision fields.
- **PASS:** `Regime` enum has exactly 12 values (10 signal + NEUTRAL + INDETERMINATE); each signal regime appears once in RULE_TABLE.
- **PASS:** SCHEMA-010 node doc matches code; margin reconstructs the deciding value via `threshold + margin*scale`; trigger features sorted; frozen dataclasses enforce immutability.

---

## Graph Integrity

**Summary:** All 14 required nodes created with correct canonical_ids; zero wikilink breakage; upstream nodes updated with reverse links; index.md and log.md current; ADR-006 gate (d) marked satisfied. One minor log.md metric typo (123 vs 124) — index.md is authoritative and correct.

**Findings:**
- **PASS:** All 14 regime nodes exist with unique canonical_ids; global canonical_id uniqueness across 124 content nodes.
- **PASS:** No broken wikilinks in the regime node cluster (60+ links all resolve).
- **PASS:** MOD-004 gained `Used By: [[Market Regime Classifier]]`; SCHEMA-009 gained `consumed_by` (frontmatter + relationship); SYS-002 gained CAP-019 in `contains_capabilities`; ADR-006 gained ADR-007 cross-ref + gate-(d) note + canonical-id shift note.
- **PASS:** index.md updated (124 total content nodes, all 14 new rows, benchmarks section populated); log.md has the full 2026-06-08 session entry; BENCH-001 artifact present.
- **PASS:** All 11 dev_graph lint checks passed on touched nodes.
- **WARN:** log.md metric line states "123 (109 + 14)" but actual is 124; index.md correctly states 124 (authoritative). [Note: corrected during writeback follow-up.]

---

## Gold Layer Readiness

**Summary:** ADR-006 gate (d) is fully satisfied by an enumerated, grounded regime taxonomy (11 signal regimes + INDETERMINATE) with a published, versioned contract (SCHEMA-010) exposed via INT-007. Gates (b)/(c)/(e) are materially advanced but intentionally not fully satisfied. No Gold DecisionPacket schema/module/guard/code created (correctly deferred per ADR-006 §8).

**Findings:**
- **PASS:** Gate (d) satisfied — 12 enumerated regimes; domain-anchored thresholds; all 11 signal regimes reachable (benchmark `all_reachable=true`).
- **PASS:** SCHEMA-010 published with correct canonical_id; decision/provenance/explainability field groups.
- **PASS:** INT-007 exposes the contract, marked experimental; sole downstream consumer (Gold builder) deferred (`consumed_by` empty).
- **PASS:** Gate (b) advanced — 14 features exercised, 7 used in decision logic.
- **PASS:** Gate (c) advanced — replay key `(snapshot_id, taxonomy_version, classifier_version)` pinned; fingerprint coherence test.
- **PASS:** Gate (e) advanced — `rule_margin` scalar fixed as a rule-local [0,1] activation margin (not the 3-component variant).
- **PASS:** No Gold schema/module/guard/code created; canonical-id reassignment (SCHEMA-010 for regime; Gold candidate → next free id) coherent and documented.

---

## Benchmark Integration (BENCH-001)

**Summary:** BENCH-001 exists with proper frontmatter and relationships. The harness is deterministic and replayable, emitting a committed golden artifact with real-replay determinism evidence and a clearly-labelled synthetic sweep. All seven measures present; coverage 11/11; artifact stays in sync with fresh builds.

**Findings:**
- **PASS:** BENCH-001 node active/implemented/confirmed; harness implements `run_determinism`, `run_synthetic_sweep`, `build_report`, `main`; repeated runs produce identical content.
- **PASS:** Real-replay determinism — `all_replays_byte_identical=true`, `consumable_count=3`; golden PASS → RESTRICTIVE_RATES (0.46).
- **PASS:** Synthetic sweep clearly labelled (`synthetic=true`); coverage `regimes_hit=11`, `all_reachable=true`.
- **PASS:** All seven measures present — distribution_pct, coverage, entropy_bits (3.010131), classification_balance (0.870123), unclassified_pct (0.3448), rule_utilization, regime_frequency.
- **PASS:** `test_committed_artifact_in_sync` passes; edge cells exercise LOW_VOL (equity dropped) and INDETERMINATE (required dropped).
- **PASS:** Decision fingerprint pinned (`8ab0be8d…821837`); versions recorded (classifier 0.1.0 / taxonomy 1.0.0 / trace 0.1.0); BENCH-001 → TEST-009 → MOD-005 wired.
- **WARN:** Pretty-printed artifact byte size can vary slightly between fresh runs; the guaranteed invariant (`json.dumps(sort_keys=True)` equality) holds and the in-sync test passes.

---

## Paper Trading Compatibility

**Summary:** MOD-005 supports replay-first, regime-stratified paper trading: deterministic output, snapshot_id-anchored classification, one label per snapshot, full provenance, and honest documentation of synthetic vs real coverage.

**Findings:**
- **PASS:** Deterministic byte-identical replay across all consumable real snapshots.
- **PASS:** snapshot_id-anchored classification (required schema field; golden test pins it).
- **PASS:** One label per snapshot — NEUTRAL sole catch-all; conflict surfaced as trace metadata (secondary/near), never a separate label; first-match-wins guarantees a single match.
- **PASS:** Full provenance — snapshot_id, rule_id, margin, threshold, scale, trigger features, version triple.
- **PASS:** Decision replay key + full-serialization key (adds `classification_trace_version`) both honored.
- **PASS:** Fail-closed → INDETERMINATE on missing required feature; `as_of` caller-supplied, never wall-clock.
- **PASS:** Honest about corpus — brief states no historical corpus; synthetic sweep labelled; all 11 regimes reachable for stratification.
- **INFO:** All consumable real snapshots share one snapshot_id (the same real snapshot at different paths), so real-data validation rests on one snapshot — explicitly acknowledged in the brief.

---

## Critical Issues

None — all critical candidates were refuted on verification. No adversarial verification produced `isReal=true` for any critical claim (verifiedCriticalCount = 0).

---

## Warnings

1. **SCHEMA-009 narrative inconsistency** — Open Questions mentions `consumed_by` empty though frontmatter was updated. Refresh on next edit (non-blocking; frontmatter-driven).
2. **Deliberate feature non-use not centrally documented** — 7 reserved features (breakeven_10y/5y, curve_5s10s, gold_price, gold_flow, policy_spread, real_yield_5y); rationale is in ADR-007 context but not a single note in `config.py`/`taxonomy.py`. Recommend adding a "reserved for future expansion" comment.
3. **Synthetic-only coverage for 10 of 11 regimes** — only one real snapshot is consumable (the three real inputs are the same snapshot). Honestly documented; recommended next step is to accumulate real snapshots over time.
4. **Paper trading end-to-end test gap** — no snapshot→FeatureVector→RegimeClassification→Gold E2E test (appropriate while Gold is deferred; add when INT-007 is consumed).
5. **log.md node-count typo** — said 123, actual 124; index.md authoritative. (Corrected in writeback follow-up.)

---

## Technical Debt

1. **Single hardcoded `TAXONOMY_VERSION`** — module constant, not loaded from config; sufficient and coherent for determinism, but limits smooth multi-version/A-B threshold testing.
2. **Synthetic sweep ignores feature correlation** — flat Cartesian grid (290 cells + 2 edges); realistic joint distributions await real history. Sufficient for gate (d) + determinism.
3. **No staleness enforcement in classifier** — provenance carries `max_staleness_days`/`revision_risk`, but `classify()` does not gate on them (decoupled; staleness policy deferred to the downstream consumer).
4. **`rule_margin` is rule-local, not globally comparable** — correct by design; recommend an explicit note in INT-007 for downstream consumers.

---

## Future Extensions

1. **Secondary-regime signals** — expose `secondary_matching_rules` downstream as alternative signals.
2. **Feature-impact scoring** — extend triggers with impact weights ("how robust is this regime to a 2% DFII10 move?").
3. **Regime persistence / transition penalties** — a future stateful Gold builder could penalize regime flips below a margin threshold (explicitly deferred per ADR-006).
4. **Historical frequency & duration analysis** — once real snapshots accumulate, compute observed frequencies, durations, and transition probabilities.
5. **Additional macro drivers** — new signal regimes from the reserved features (gold flow/price, policy spread, 5y real/breakevens).

---

## Engineering Digital Twin Maturity Impact

This slice advances the Engineering Digital Twin from single-module determinism (Snapshot/Feature modules) to **multi-module determinism composition** (Feature → Regime decision pipeline):

- **Determinism cascade validated** — MOD-004 + MOD-005 form a pure, stateless pipeline with byte-identical replay verified end-to-end.
- **Contract-first governance proven** — ADR-007/SCHEMA-010/INT-007 authored before/with code; reduces friction when the Gold builder lands.
- **Fail-closed architecture** — missing features yield explicit INDETERMINATE, never a guess.
- **Versioning + fingerprinting** — ties decisions to their config snapshot, enabling safe change and coherence audit.
- **Snapshot-anchored paper-trading foundation** — `snapshot_id` enables deterministic replay from real snapshots.

---

## Gold Layer Readiness Assessment

- **Gate (d) — Regime taxonomy exists (enumerated and grounded):** ✅ **CLOSED.** ADR-007 published; 11 signal regimes + INDETERMINATE; thresholds domain-grounded; SCHEMA-010 + INT-007 published; all regimes reachable.
- **Gate (b) — Feature coverage sufficient:** ✅ **MATERIALLY ADVANCED.** 14 features exercised; 7 in decision rules. Fully advanced when synthetic coverage is replaced by real traces.
- **Gate (c) — Replay finalization:** ✅ **MATERIALLY ADVANCED.** Regime replay key pinned + fingerprinted. Fully advanced when the Gold builder's replay key integrates.
- **Gate (e) — Confidence semantics:** ✅ **MATERIALLY ADVANCED.** `rule_margin` fixed as a rule-local [0,1] margin. Fully advanced when the Gold builder's confidence semantic is defined against it.

**Remaining work for full Gold readiness (all deferred per ADR-006 §8):** author the Gold DecisionPacket schema (next free SCHEMA id), the Gold Decision Builder module, the Gold Decision API, and the L3 guards; integrate Supervisor context while preserving ADR-004 separation.

---

## Final Verdict

**PASS**

The Deterministic Regime Taxonomy (MOD-005) is **approved for use within its defined scope**: regime classification for validated Feature Vectors upstream of the future Gold Decision Builder.

- All eleven audit dimensions PASS or WARN (no confirmed critical issues; verifiedCriticalCount = 0).
- ADR-006 gate (d) satisfied; gates (b)/(c)/(e) materially advanced.
- Code quality verified: 772 tests pass, mypy --strict clean (regime package), ruff clean, determinism validated.
- Governance complete: 14 nodes authored with full frontmatter, zero wikilink breakage, writeback checklist executed, 11 lint checks passed.
- ADR compliance verified: deterministic, fail-closed, rule-based, stdlib-only, feature-grounded, separated from treasury logic.
- Paper trading support confirmed: snapshot-anchored, multi-regime coverage, honest about synthetic vs real corpus.

**Scope note:** MOD-005 is production-ready *as a regime classification layer*. The downstream Gold DecisionPacket builder remains deferred per ADR-006 §8 and should be authored when institutional risk context is finalized.

---

**Audit completed:** 2026-06-08
**Method:** 11 parallel read-only dimension auditors → adversarial verification of critical/FAIL candidates (0 survived) → lead synthesis.
**Evidence:** Per-dimension audits, benchmark artifact, code inspection, governance audit.
