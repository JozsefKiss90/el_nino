# Gold DecisionPacket v0 Final Audit

**Date:** 2026-06-08
**Scope:** The Gold DecisionPacket v0 slice (MOD-006 Gold Decision Builder, SCHEMA-011 Gold DecisionPacket v0 Schema, INT-009 Gold Decision API, CAP-020 Gold Decision Generation, ADR-006 Decision-Layer Re-grounding, ADR-008 Confidence Semantics, plus PRED-006/007, GATE-002, BENCH-002, FILE-015..018, TEST-010/011/012). MOD-006 is the 4th L3 analysis stage (SCHEMA-001 → MOD-003 Snapshot Consumer → MOD-004 Feature Builder → MOD-005 Regime Classifier → MOD-006 Gold Decision Builder). It consumes ONLY SCHEMA-009 (FeatureVector) and SCHEMA-010 (RegimeClassification) plus optional guard refs and an injected versioned `DecisionPolicyConfig`, and emits SCHEMA-011 (`GoldDecisionPacket`) via INT-009, realizing CAP-020 under SYS-002 (Trading Engine). The decision is paper-only; execution/runtime is deferred per ADR-006 Non-Goals. All 15 new governance and code nodes have been authored and committed.

> Methodology: 8 independent read-only auditors (one per dimension) ran in parallel, each returning a structured verdict; every critical/high/FAIL candidate was routed to an adversarial verifier that defaulted to "refuted unless clearly real." 0 critical candidates were produced and 0 survived verification (verifiedCriticalCount = 0). This document is the lead synthesis. Load-bearing facts were independently re-verified by the lead: the 29-test gold suite passes (`pytest tests/gold/` → 29 passed); the pinned facts reproduce (RESTRICTIVE_RATES / AVOID / `confidence 0.39744` / `uncertainty 0.136` / `packet_id gold-v0:5653d07a0b3949d5` / fingerprint `be7e3192…a8a5`, all pinned in `tests/gold/test_decision_builder.py`); `src/gold/__init__.py` is confirmed missing while all five sibling packages have one; the coverage-discount gap is confirmed at `src/gold/decision_builder/policy.py:40,59`; and the live Neo4j dry-run reports 140 nodes / 920 edges / 5 skips.

---

## Executive Summary

**Overall Verdict:** PASS

**Readiness Score:** 94/100

The Gold DecisionPacket v0 implementation is **production-ready for its defined scope** — deterministic, paper-only decision-packet generation from validated regime classifications. All eight audit dimensions are PASS with no confirmed critical issues. `build_decision` is a pure, total, stdlib-only function with no IO/clock/RNG/history/global-state; the same `(snapshot, regime versions, decision_policy_version, configuration)` yields a byte-identical packet, and `compute_packet_id` hashes the full identity tuple — including the `decision_policy_fingerprint` — so cross-version-bump collisions are closed. The slice is rigorously separated from the Supervisor treasury branch (ADR-004): AST-level import extraction over `src/gold` yields zero supervisor/treasury imports and no SCHEMA-005 calibration/sample_quality/realized_pnl bleed. All 15 dev_graph nodes are ontology-compliant (schema_version 2.2.0), the SCHEMA-011 contract matches its node doc, and the graph lineage converges correctly onto MOD-006 with the CAP-004 deprecate-and-supersede executed cleanly. The pinned confidence math, packet_id, and fingerprint reproduce exactly, and the 801-test full suite (29 gold) is green.

The score is held at 94 (not higher) by **one genuine, narrow code-vs-normative-text gap** — the coverage discount in `policy.py` reads only `fv.unavailable_features` and never `rc.failed_required_features`, which ADR-008 §3 names as a coverage input — together with three low-severity documentation-drift items (a missing `src/gold/__init__.py` package marker, a stale "26 tests" figure in the MOD-006 node, and an export-validation stat drift of 139/910 → 140/920 in `log.md`). None of these affect determinism, safety, separation, or the pinned real-snapshot path. Two pinned static-check claims (`mypy --strict` / `ruff` clean on `src/gold`) could not be independently re-run because neither tool is installed in the available interpreter; they are accepted on the brief's word and code inspection.

---

## Per-Dimension Results

| Dimension | Verdict | Score |
|-----------|---------|-------|
| Architecture | PASS | 91 |
| Replay Determinism | PASS | 96 |
| Ontology Compliance (dev_graph/CLAUDE.md) | PASS | 98 |
| ADR Compliance (ADR-006 / ADR-008) | PASS | 93 |
| Treasury/Gold Separation (ADR-004) | PASS | 98 |
| Schema Correctness | PASS | 93 |
| Graph Integrity | PASS | 92 |
| Gold-Layer Readiness | PASS | 92 |

*Scores normalized to /100. Native auditor scales were Architecture 9.1/10, Replay 0.96, Ontology 98/100, ADR 0.93, Separation 0.98, Schema 93/100, Graph 0.92, Readiness 0.92.*

---

## Architecture

**Summary:** MOD-006 Gold Decision Builder is architecturally correct as the 4th L3 stage. It consumes ONLY SCHEMA-009 (FeatureVector) + SCHEMA-010 (RegimeClassification) + optional GuardRefs + an injected versioned `DecisionPolicyConfig`, produces SCHEMA-011 via INT-009, and realizes CAP-020 under SYS-002. `build_decision` is a pure/total/stdlib function — no IO, clock, RNG, history, or global state. Execution/runtime is cleanly deferred: no `src/` module imports gold, and the only order/broker/execute tokens are paper-only non-execution notices in string literals. The package layout substantively mirrors `src/regime` (engine/policy/config/models split). One genuine layout defect: `src/gold/__init__.py` is missing while all five sibling top-level packages have one.

**Findings:**
- **PASS:** MOD-006 correctly positioned as the 4th L3 analysis stage (SCHEMA-001 → MOD-003 → MOD-004 → MOD-005 → MOD-006). `tests/gold/test_e2e_pipeline.py:26-31` exercises the exact chain consume → build_features → classify → build_decision and asserts one `snapshot_id` threads every stage (lines 50-59). Ordering is real, tested, and matches the dev_graph.
- **PASS:** Input boundary honored — `builder.py:13-14` imports only `features.feature_builder.models.FeatureVector` and `regime.regime_classifier.RegimeClassification`; `policy.py:9-10` and `config.py:24` add only `Regime`/`RegimeClassification`. No `snapshot.*` (raw SCHEMA-001), no JSON/file reads inside `build_decision`, no network lib, no hidden state. The signature `build_decision(fv, rc, guards=None, config=None, as_of=None)` (builder.py:57-63) is exactly the ADR-006 §2 boundary; config IO is fail-closed at the boundary in `config.py`.
- **PASS:** Pure / total / stdlib function — grep over `src/gold` for `(time|datetime|random|os|sys|requests|httpx|urllib|socket|subprocess|threading|asyncio|broker|order|execute)` returns only docstring/string-literal hits (paper-only notices). Totality is enforced: `DecisionPolicyConfig.__post_init__` (config.py:112-130) requires the direction table to be total over all 12 `Regime` values, and `test_direction_table_total_over_all_regimes` confirms it.
- **PASS:** Produces SCHEMA-011 via INT-009 and realizes CAP-020 under SYS-002. The graph wiring CAP-020 → INT-009 → MOD-006 → SCHEMA-011 under SYS-002 is internally consistent; CAP-020 supersedes the deprecated CAP-004 Signal Generation.
- **PASS:** Execution/runtime cleanly separated and deferred — no `src/` module imports gold (reverse-dependency grep empty), satisfying ADR-006 §1 paper-only separation and ADR-004 permanent-separation. The stateful L3 guards (`duplicate_ok`/`operational_ok`) carry `bool | None` and default to `None`, with computation deferred to the unbuilt paper-trading runtime. The benchmark lives outside the package (`benchmarks/gold/run_gold_bench.py`), so no benchmark/CLI coupling leaks in.
- **PASS:** Package layout substantively mirrors `src/regime` — `gold/decision_builder = {models, config, policy, builder, __init__}` maps to `regime/regime_classifier = {models, config, taxonomy, regime_classifier, __init__}`; `builder.py` is the engine analog of `regime_classifier.py`.
- **WARN (low):** Missing `src/gold/__init__.py` — layout-mirror and packaging inconsistency. Every other top-level domain package under `src/` has a regular `__init__.py` with a one-line domain docstring (`features`, `regime`, `snapshot`, `risk`, `supervisor` — all confirmed present by the lead); `src/gold/__init__.py` does NOT exist (confirmed). `gold` therefore resolves as an implicit PEP 420 namespace package, masked at test time only because `pyproject.toml` sets `pythonpath=['src']`. `pyproject.toml:16` also declares `src/gold` as a hatchling wheel package target alongside the five `__init__`-bearing packages, so the wheel build relies on namespace-package handling rather than an explicit marker — a latent packaging risk that could not be empirically confirmed (hatchling/build not installed). Fix is a one-line docstring-bearing `src/gold/__init__.py`. Low severity: no runtime/test break observed and the 801-test suite passes.

---

## Replay Determinism

**Summary:** `build_decision` is verifiably pure, total, and deterministic: same `(snapshot, regime versions, decision_policy_version, configuration)` yields a byte-identical packet. No clock/RNG/IO/history/global-state in the build path (the only `set()` usage is in validation and is always `sorted()` before any output-reaching iteration). `compute_packet_id` hashes the FULL identity tuple including `decision_policy_fingerprint`, closing the cross-version-bump collision hazard. `to_dict()` is byte-stable (alphabetical keys, 6-dp rounding). `as_of` is caller-supplied and correctly excluded from `packet_id`. The fingerprint covers all 12/12 decision-affecting fields and excludes only the version string, and the pinned coherence test fails CI on any un-versioned drift.

**Findings:**
- **PASS:** `build_decision` is pure/total/deterministic — reads only `fv`, `rc`, optional guards/config, and caller-supplied `as_of`. A regex scan of all four modules for `\brandom\b|\bid\(|\.now\(|time\.|datetime|uuid|os.environ` found zero real hits. The only `set()` usages (config.py:117-119,163) are validation-path and always `sorted()` before iteration; `direction_for` (config.py:134-139) is a linear scan over an ordered tuple. `to_dict()` was byte-identical across 5 independent serializations.
- **PASS:** `compute_packet_id` (models.py:199-224) digests source_snapshot_id, source_feature_schema_version, regime_taxonomy_version, regime_classifier_version, decision_policy_version, AND decision_policy_fingerprint. Bumping the version changes `packet_id` (`test_packet_id_changes_with_policy_version`); same-version-different-weights changes it via the fingerprint (`test_packet_id_changes_with_config_fingerprint`). Two configs sharing a version but differing in any weight cannot mint colliding ids — the step-0 collision fix is real.
- **PASS:** `decision_policy_fingerprint` coherence test catches un-versioned weight/table drift on every decision field. `_DECISION_FIELDS` (config.py:56-69) equals all dataclass fields minus only `decision_policy_version` (12 of 13). Perturbing each weight/cap/floor/instrument/direction-table cell changes the hash; `test_decision_policy_fingerprint_pinned` pins `be7e3192…a8a5` (reproduced exactly by the lead); `test_fingerprint_excludes_version` and `test_fingerprint_changes_on_weight_drift` confirm the semantics. A silent edit without a version bump breaks the pinned CI test.
- **PASS:** `to_dict()` is byte-stable — alphabetical keys plus 6-dp rounding on `confidence`/`uncertainty`/`anchor` (models.py:172,195,78), mirroring the regime layer's precision convention to neutralize platform float-format drift.
- **PASS:** `as_of` is caller-supplied (`builder.py:113`), never wall-clock, and is NOT a `compute_packet_id` argument — `as_of='2026-01-01'` and `as_of='1999-12-31'` both produce `packet_id gold-v0:5653d07a0b3949d5`. It IS serialized in `to_dict`, which is the correct contract (identical caller inputs → identical bytes).
- **PASS:** Pinned facts reproduced exactly; full gold suite green. Direct execution of the real PASS fixture yields RESTRICTIVE_RATES / AVOID / `confidence 0.39744` / `uncertainty 0.136` / `packet_id gold-v0:5653d07a0b3949d5` / fingerprint `be7e3192…a8a5`; `pytest tests/gold/` → 29 passed (re-run by the lead). The benchmark harness is itself clock/RNG-free and replays each consumable snapshot twice asserting byte-identity.
- **PASS (info):** `packet_id` is keyed on the decision-replay tuple, not the full-serialization tuple — it intentionally omits `regime_classification_trace_version` (which IS serialized in the packet's provenance block). This is correct-by-design per SCHEMA-010's deliberate decision-replay vs full-serialization key separation; a future `trace_version` bump could change `to_dict()` bytes while leaving `packet_id` stable. In v0 `trace_version` is a fixed `0.1.0`, so it is inert. Worth documenting for consumers who might treat `packet_id` as a whole-packet content hash.
- **PASS (info):** The fingerprint hashes raw (unrounded) floats, so it is conservatively over-sensitive — any sub-ulp change is detected, so the coherence test can never under-report drift. This differs from the packet's `to_dict` scalars (rounded to 6 dp for cross-platform byte-stability); the fingerprint is an internal identity hash, not serialized cross-platform output, so raw-float sensitivity is appropriate.

---

## Ontology Compliance (dev_graph/CLAUDE.md)

**Summary:** All 15 new Gold DecisionPacket v0 nodes (SCHEMA-011, INT-009, CAP-020, MOD-006, PRED-006/007, GATE-002, BENCH-002, FILE-015..018, TEST-010/011/012) are fully ontology-compliant with `dev_graph/CLAUDE.md` schema_version 2.2.0. Every node carries the complete 14-key universal frontmatter plus correct type-specific extensions, uses only closed-enum values, has a unique correctly-prefixed `canonical_id`, sits in the directory matching its type, contains the required `## Relationships` section with resolvable outbound wikilinks, and introduces zero freeform frontmatter keys. No FAIL-level defects; only informational observations.

**Findings:**
- **PASS:** Universal frontmatter complete on all 15 nodes — all 14 universal keys present (type, canonical_id, status, implementation_status, canonical, created, updated, confidence, evidence, source_paths, related_files, related_tests, related_constraints, related_decisions) plus correct extensions.
- **PASS:** All enum fields within closed enums — `status ∈ {planned, active}`, `implementation_status ∈ {not-started, implemented, tested}`, `confidence ∈ {inferred, confirmed}`, `evidence ∈ {design, ADR, code, benchmark}`, `type` within the 24-enum set. Evidence-confidence coherence (lint check 11) holds.
- **PASS:** Canonical IDs unique and correctly formatted — graph-wide scan confirms each of SCHEMA-011, INT-009, CAP-020, MOD-006, PRED-006/007, GATE-002, BENCH-002, FILE-015..018, TEST-010..012 appears exactly once with the correct `TYPE_PREFIX-NUMBER` form; other occurrences are confined to CLAUDE.md/exporter templates.
- **PASS:** Type-to-directory binding correct for all 15 nodes (predicate→predicates/, gate→gates/, benchmark_result→benchmarks/, file→files/, test→tests/, capability→capabilities/, interface→interfaces/, module→modules/, artifact_schema→schemas/).
- **PASS:** Required type-specific fields present on every node (e.g. SCHEMA-011 schema_id/version/path/validated_by/consumed_by/produced_by; INT-009 interface_id/version/parent_capability/input_schema/output_schema/implemented_by/stability; MOD-006 module_name/path/responsibility/depends_on/provides; FILE-015..018 file_path/language/module/owns/used_by; TEST-010..012 test_path/test_type/covers/required_for).
- **PASS:** No freeform frontmatter keys; flat YAML only — every top-level key maps to a defined field; arrays are scalar/wikilink lists.
- **PASS:** Required body sections and ≥1 outbound relationship present. MOD-006 has the required `## Implementation Notes` (lint check 8); file nodes link parent module and test; the gate links its two predicates; tests link covered nodes. All sampled wikilink targets resolve on disk — no broken links.
- **PASS:** Planned-node empty arrays are appropriate (PRED-006/007, GATE-002 are status:planned / not-started per ADR-006 Non-Goals), reflecting actual node state, not omissions.
- **PASS:** INT-009 `input_schema`/`output_schema` coherent with body — input `[[Regime Classification Schema]]` (primary input, SCHEMA-010), output `[[Gold DecisionPacket v0 Schema]]` (SCHEMA-011); the Feature Vector Schema is the cited secondary input.

---

## ADR Compliance (ADR-006 / ADR-008)

**Summary:** The implementation (`src/gold/decision_builder/{models,policy,builder,config}.py`) complies with ADR-006 and ADR-008 essentially rule-for-rule. ADR-006: the input boundary (§2) is respected; feature grounding (§5) holds (cited_features copied verbatim from `rc.provenance`, a subset of the 14 MOD-004 features, never fabricated); guard separation (§6) holds; Non-Goals hold (paper-only, no execution/order/broker/runtime). ADR-008: confidence is a deterministic ordinal trust score anchored on within-rule normalized `rule_margin` (NEUTRAL floor 0.50), discounted by ambiguity/fragility/data-quality/coverage, with INDETERMINATE floored fail-closed; `uncertainty = 1 − structural` (demonstrably NOT `1 − confidence`: 0.136 vs 0.60256 on the real snapshot); the 3-component / SCHEMA-005 variant is excluded; `decision_policy_version` governs the policy set via a fingerprint folded into `packet_id`. Pinned facts reproduce exactly. One genuine narrow divergence: the coverage discount omits `failed_required_features`.

**Findings:**
- **PASS:** ADR-006 §2 input boundary — every import is `features.feature_builder.models` (SCHEMA-009), `regime.regime_classifier` (SCHEMA-010), local `.config/.models/.policy`, or stdlib. No `snapshot.*`, no raw JSON, no network/time/random. `source_snapshot_id` is the echoed string `rc.snapshot_id`, not raw-snapshot consumption.
- **PASS:** ADR-006 §5 feature grounding — `builder.py:75-78` builds each `FeatureCitation` from `p in rc.provenance`, which `regime_classifier.py:_provenance` copies verbatim from `fv.features[n]`. Citations are a structural subset of the 14-feature v0 registry; `test_real_snapshot_golden` asserts `cited_features == ['real_yield_10y']` (value 1.96, inputs `('DFII10',)`).
- **PASS:** ADR-006 §6 guard separation — `GuardRefs` (models.py:100-116) carries all six guards (data_ok, freshness_ok, supervisor_ok, cooldown_ok, duplicate_ok, operational_ok) as `bool | None` defaulting `None`; never computed as features, never present in the FeatureVector, never wired into `trust_score`/`direction_for`.
- **PASS:** ADR-006 Non-Goals — no order/broker/position/runtime code or imports. `DecisionMode` is a single-value `PAPER_ONLY` enum; `__post_init__` raises if not paper-only; the `non_execution_notice` and `constraints` tuple assert the paper-only nature.
- **PASS:** ADR-008 §1/§2 — deterministic ordinal trust score (explicitly NOT a calibrated probability), anchored on within-rule normalized `rule_margin` for signal regimes or the NEUTRAL floor; `confidence = clamp01(anchor * structural)`.
- **PASS:** ADR-008 §3 discounts + §4 floors — four structural factors in `policy.py:54-61` (ambiguity, fragility, data_quality = revision·staleness, coverage); NEUTRAL anchored to 0.50; INDETERMINATE returns `(0.0, 1.0)` fail-closed. Reproduced numerically: real snapshot structural 0.864 → confidence 0.39744.
- **PASS:** ADR-008 §5 — `uncertainty = clamp01(1.0 − structural)` (policy.py:69), a function of the discount product only. For the real snapshot 1 − 0.864 = 0.136, which is NOT 1 − 0.39744 = 0.60256 — concretely proving it is the structural aggregate, not the arithmetic complement.
- **PASS:** ADR-008 §6 — no performance/calibration/sample_quality/realized_pnl term anywhere in the gold package; nothing imports the treasury SCHEMA-005 EvaluationScorecard.
- **PASS:** ADR-008 §7/§8 — `decision_policy_fingerprint` excludes only the version; `compute_packet_id` folds version + fingerprint into the id; tests pin the fingerprint, assert weight-drift detection, version-only invariance, and packet_id shift on either axis. `classification_trace_version` correctly composes into the packet but is not part of the decision-replay key.
- **PASS:** INDETERMINATE → WATCH fail-closed enforced in both the packet (models.py:160-161) and the config (config.py:129-130); `DEFAULT_DIRECTION_TABLE` pins INDETERMINATE→WATCH; the table is validated total over all 12 regimes.
- **WARN (low):** ADR-008 §3 coverage discount omits `failed_required_features` — ADR-008 §3 and `GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md` line 21 define coverage over `failed_required_features` AND `FeatureVector.unavailable_features` counts, but the implementation (`policy.py:40` `unavailable_count = len(fv.unavailable_features)`; `policy.py:59` coverage uses only `unavailable_count`) never reads `rc.failed_required_features` (confirmed by the lead). This is material in a real edge case: `regime_classifier.py:77-81` records a rule's missing required features and SKIPS that rule, yet classification can proceed to a signal/NEUTRAL regime (not INDETERMINATE) — so a non-floored packet can carry `failed_required_features` non-empty while the coverage discount ignores it, slightly over-stating confidence vs the ADR text. It does NOT affect the pinned real snapshot (`failed_required_features = ∅`), INDETERMINATE (floored), determinism, or separation. Resolve by adding `len(rc.failed_required_features)` to the coverage count, or amend §3 to scope coverage to `unavailable_features` only.

---

## Treasury/Gold Separation (ADR-004)

**Summary:** The gold layer is permanently and verifiably separate from the Supervisor treasury branch. AST-level import extraction across all of `src/gold` yields zero supervisor/treasury imports — only stdlib plus the two sanctioned upstreams (SCHEMA-009, SCHEMA-010). Gold confidence is computed solely from `rule_margin` + structural discounts + config floors, with no SCHEMA-005 calibration/sample_quality/realized_pnl anywhere; the treasury branch (`src/supervisor/decision_engine/scoring.py`) is where those fields actually drive scoring. Gold uses new canonical ids (SCHEMA-011/INT-009/MOD-006/CAP-020) and never the treasury ids (SCHEMA-004/INT-006/MOD-002/CAP-015). CAP-004 Signal Generation is deprecated and explicitly superseded by CAP-020, not merged into CAP-015. No bleed found.

**Findings:**
- **PASS:** `src/gold` imports nothing from `src/supervisor` — AST import extraction over every `.py` yields only `__future__`, dataclasses, enum, typing, hashlib, json, pathlib, `features.feature_builder.models`, `regime.regime_classifier`, and intra-package imports. Supervisor/treasury imports: NONE.
- **PASS:** Gold confidence does NOT wire in SCHEMA-005 — `policy.trust_score` computes `confidence = clamp01(anchor * structural)` from RegimeClassification + FeatureVector + DecisionPolicyConfig only. Grep for `calibration|sample_quality|realized_pnl|EvaluationScorecard` across `src/gold` returns no matches. By contrast `src/supervisor/decision_engine/scoring.py:18-23` wires `s.calibration`/`s.realized_pnl` into weakness scoring — confirming those fields live entirely in the treasury bounded context.
- **PASS:** Gold uses NEW canonical_ids — the SCHEMA-011 node names producer MOD-006 / interface INT-009 / capability CAP-020; the treasury ids SCHEMA-004/INT-006/MOD-002 are confined to `src/supervisor/decision_engine` and never referenced by gold (ADR-004 §2).
- **PASS:** CAP-004 Signal Generation SUPERSEDED by CAP-020, not merged into CAP-015 — `capabilities/Signal Generation.md` is status:deprecated and states it is superseded by `[[Gold Decision Generation]]` and "Permanently separate from the treasury `[[Decision Making]]` (CAP-015)." CAP-015 remains the distinct treasury capability; no in-place reclassification.
- **PASS:** The `supervisor_ok` token in `src/gold` is a cited guard-name (the `_GUARD_NAMES` taxonomy tuple and the `GuardRefs.supervisor_ok` `bool | None` field, always `None` in v0), not a treasury import or data dependency; `tests/gold/test_decision_builder.py:215` asserts it serializes to `None`.
- **PASS:** Consumed upstreams (SCHEMA-009/SCHEMA-010) carry no treasury fields — grep of both source models for `realized_pnl|calibration|sample_quality|treasury|supervisor|Scorecard|SCHEMA-005` returns no matches, so no treasury field can leak into gold transitively. Governance (ADR-008 §6/§10, ADR-004) explicitly forbids the bleed and the code conforms.

---

## Schema Correctness

**Summary:** SCHEMA-011 GoldDecisionPacket is faithfully implemented and the node doc matches the code. All six field groups (decision/provenance/versions/trust-trace/guards/safety) are present and correctly typed. The four `__post_init__` invariants the doc names (`confidence ∈ [0,1]`, `uncertainty ∈ [0,1]`, `decision_mode == paper_only`, INDETERMINATE ⇒ direction WATCH) are all enforced and tested. `cited_features` are read verbatim from `rc.provenance` (sourced from the 14-name MOD-004 registry), so the ⊆-14 property holds structurally. Direction is exactly LONG/FLAT/AVOID/WATCH; `guard_refs` is the six-guard `bool | None` taxonomy; the direction table is enforced total over all 12 regimes; `to_dict()` is alphabetical + 6-dp-rounded and replays byte-identically. The only genuine gap is that the doc lists "instrument == GLD" as a Validation Rule but the packet does not enforce it (config default only).

**Findings:**
- **PASS:** Field groups match the SCHEMA-011 node doc exactly — Decision (packet_id, packet_schema_version, instrument, decision_mode, regime, direction, confidence, uncertainty, rationale), Provenance/identity (source_snapshot_id, source_feature_schema_version, regime_taxonomy_version, regime_classifier_version, regime_classification_trace_version, matched_rule_id, cited_features, as_of), Versions (decision_policy_version), Trust-trace (confidence_inputs), Guards (guard_refs), Safety (non_execution_notice, constraints). No missing or extra fields.
- **PASS:** `__post_init__` enforces the four doc-named invariants (models.py:153-161): confidence/uncertainty out of [0,1] raise; non-PAPER_ONLY raises; INDETERMINATE with direction ≠ WATCH raises "INDETERMINATE must map to direction WATCH (fail-closed)".
- **WARN (low):** Doc lists "instrument == GLD" as a Validation Rule but the packet does not enforce it. `GoldDecisionPacket.instrument` is a plain `str` (models.py:126) with no `__post_init__` check; it is only set from `cfg.instrument`, default `'GLD'` (config.py:90) but overridable, so `DecisionPolicyConfig(instrument='SLV')` would build a packet `__post_init__` accepts. Low severity: `instrument` is in `_DECISION_FIELDS` so it is fingerprinted and any change forces a `decision_policy_version` bump; no real snapshot path produces a non-GLD packet. The doc wording overstates packet-level enforcement.
- **PASS:** `cited_features` are verbatim and structurally ⊆ the 14 MOD-004 features — `builder.py:75-78` builds each citation directly from `rc.provenance` (identical 5-field shape), with no code path synthesizing a name outside the registry. Golden test pins `cited_features == ['real_yield_10y']`.
- **PASS:** `guard_refs` is the six-guard `bool | None` taxonomy (models.py:100-116), emitted alphabetically via the constant `_GUARD_NAMES` tuple; `test_guard_refs_default_null`/`test_guard_refs_passthrough` confirm defaults and bool passthrough.
- **PASS:** `Direction` enum is exactly LONG/FLAT/AVOID/WATCH; config validates every table cell's direction against the enum (`test_config_invalid_direction_raises`).
- **PASS:** `direction_table` is total over all 12 regimes with INDETERMINATE→WATCH (config.py:112-130) — verified cell-for-cell against the brief table and the benchmark `regime_direction_map`; all three agree.
- **PASS:** `to_dict()` is byte-stable (alphabetical keys, 6-dp rounding); `test_byte_identical_replay` asserts `json.dumps(..., sort_keys=True)` identical across two independent builds; benchmark records `all_replays_byte_identical=true`. The nested `decision`/`provenance` grouping is consistent with the doc, which pins byte-stability, not the nesting.
- **PASS:** `packet_id` digests the full identity tuple as the doc specifies (`gold-v0:` + first 16 hex); pinned value `gold-v0:5653d07a0b3949d5` reproduces; both version and fingerprint axes participate.
- **PASS (info):** `as_of` grouping differs cosmetically from the doc table (declared last with default `None` per dataclass field-ordering) but is functionally identical (caller-supplied, never wall-clock).

---

## Graph Integrity

**Summary:** The Gold DecisionPacket v0 graph lineage is structurally sound. All gold nodes exist with unique canonical_ids; the convergence onto MOD-006 is wired correctly in both directions; the CAP-004 deprecation rewiring leaves no active node dangling to the deprecated node; the index.md per-type tally sums to exactly 140 and matches on-disk counts; and the live Neo4j export dry-run confirms zero gold-lineage drops (all 5 skips are legitimate non-graph refs). The single defect is stat drift: the recorded export figures (139 nodes / 910 edges) are stale relative to the live export (140 / 920) because TEST-012 was added after the Stage-2 export was recorded.

**Findings:**
- **WARN (low):** Export-validation stat drift — `log.md` Stage-2 entry records "139 nodes, 910 relationships, 5 skipped", but re-running `python dev_graph/sync_to_neo4j.py --dry-run` now yields 140 / 920 / 5 (independently confirmed by the lead). The deltas reconcile exactly: TEST-012 `test_e2e_pipeline` (added in Stage 3) contributes 1 node and exactly 10 edges (DECIDED_BY/JUSTIFIED_BY to ADR-006 + 4 COVERS + 4 USED_BY to MOD-003/004/005/006). The Stage-3 log entry bumped index.md to 140 but never re-stated the export count. No graph-integrity consequence — index.md is correct at 140. Recommend re-recording the export as 140/920/5.
- **PASS:** All 5 Neo4j export skips are legitimate non-gold references — 3× Infrastructure Diagram → `dev_graph/CLAUDE`/`wiki/CLAUDE` (structural files, never nodes); 2× Supervisor Office → uncreated wiki-concept nodes (Office Action Loop, Paper Trading Work Cycle). Grepping the skip report for any gold token returns NONE; the CAP-004 SUPERSEDES/DEPENDS_ON edges all resolve.
- **PASS:** Index per-type tally sums to 140 and matches on-disk canonical_id counts for all 21 types; the exporter's "Nodes synced: 140" matches, confirming it correctly excludes the 4 CLAUDE.md template placeholders.
- **PASS:** Canonical_id uniqueness holds across all 140 content nodes (`sort | uniq -d` returns zero duplicates); the 11 newly-created gold-epoch ids plus SCHEMA-011/INT-009/CAP-020/TEST-012 are unique.
- **PASS:** Gold convergence edges onto MOD-006 are wired correctly — SCHEMA-011 `produced_by`, INT-009 `implemented_by`, CAP-020 `implemented_by` all → `[[Gold Decision Builder]]`; SCHEMA-009/010 `consumed_by` include `[[Gold Decision Builder]]`; MOD-006 reciprocates (provides INT-009, contains the 4 file nodes, validated by `test_decision_builder` + `test_gold_bench`). The provides↔implemented_by round-trip closes.
- **PASS:** CAP-004 deprecate-and-supersede leaves no active node dangling — PAT-004 Pipeline Pattern and SYS-002 Trading Engine rewired to `[[Gold Decision Generation]]`; CAP-005 Order Management's `Depends On [[Signal Generation]]` is explicitly annotated as deprecated (paper-only gold successor does not feed Order Management). The only remaining `[[Signal Generation]]` references from active nodes are CAP-020's sanctioned Supersedes and CAP-005's annotated historical link. Lint check 9 satisfied.
- **PASS:** Gold file/test nodes are well-formed with required inbound links and no orphans — FILE-015..018 carry `module: [[Gold Decision Builder]]`; TEST-010/011/012 cover the right targets; PRED-006/007 → GATE-002; GATE-002 `required_artifacts` → SCHEMA-011; BENCH-002 → MOD-006. Every gold node has ≥1 inbound wikilink; export reports zero orphans.

---

## Gold-Layer Readiness

**Summary:** The Gold DecisionPacket v0 epoch is genuinely ready and does NOT overclaim. All five ADR-006 §8 Creation Gates are closed with traceable governance evidence: (a) MOD-004 and (d) regime taxonomy by prior slices; (e) confidence semantics, plus (b) feature-coverage-gaps-accepted and (c) replay finalization, by ADR-008 (status active). The v0 contract (SCHEMA-011) is complete, implemented in pure stdlib-only fail-closed code, tested (29 gold tests within an 801-pass suite), and benchmarked (BENCH-002 golden artifact in sync, byte-identical replay). The provisional/deferred items are disclosed honestly across code comments, ADRs, briefs, and dev_graph nodes.

**Findings:**
- **PASS:** All five ADR-006 §8 Creation Gates verifiably closed — ADR-006 (active) §8 records (a)/(d) closed by prior slices; ADR-008 (active) §8/§9 closes (e)/(c)/(b) with the 7 reserved features explicitly accepted out of scope. The reserved-feature list in ADR-008 §9 matches `src/regime/regime_classifier/taxonomy.py:83-90` verbatim. No advanced-vs-satisfied contradiction.
- **PASS:** v0 contract complete, tested, and benchmarked; pinned facts independently reproduced — full suite 801 passed; gold suite 29 (20 builder + 6 bench + 3 e2e); lead recomputed the trust score from first principles (anchor 0.46, structural 0.864) → confidence 0.39744 / uncertainty 0.136, matching the golden test and the committed `benchmarks/gold/artifacts/gold_bench.json`.
- **PASS:** Determinism, purity, and input-boundary invariants hold in code — `build_decision` is pure/total; fail-closed snapshot_id/feature_schema_version consistency checks (builder.py:68-71); `compute_packet_id` digests the full identity tuple; config IO is fail-closed at the boundary via `DecisionPolicyConfigError`.
- **PASS:** Direction-table totality + INDETERMINATE fail-closed enforced at two layers (config.py + models.py); the synthetic benchmark sweep reaches all 12 regimes and every Direction value.
- **PASS:** Provisional/deferred items disclosed honestly — the direction table and confidence weights are labelled domain-anchored (not data-fitted) and recalibratable via a governed `decision_policy_version` bump; the single-real-snapshot caveat is stated everywhere; the benchmark's 3 "consumable" inputs all resolve to ONE distinct snapshot_id (952cc83a…), with the synthetic sweep carrying the other 11 regimes — the honest "one real / synthetic-rest" posture.
- **PASS:** L3 stateful guards correctly deferred and represented — `GuardRefs` carries all six outcomes as `bool | None` defaulting `None`; PRED-006/007 and GATE-002 are planned/not-started with explicit "runtime computation is deferred (ADR-006 Non-Goals)" notes; the gate is `blocking:false` (advisory) in v0; `build_decision` never computes guards.
- **PASS:** CAP-004 deprecate-and-supersede and `consumed_by` wiring executed cleanly; the gold capability is paper-only and does NOT redirect into Order Management.
- **WARN (low):** Stale test-count figure in MOD-006 node — `dev_graph/modules/Gold Decision Builder.md` line 78 states "26 tests" (confirmed by the lead); the actual gold suite is 29. Documentation drift only; refresh when next touching the node.
- **WARN (low):** Neo4j dry-run counts drift from pinned 139/910 → 140/920 (5 skips match, all legitimate). Consistent with uncommitted working-tree graph changes; not a defect in the gold slice. Reconcile before the first trusted export.
- **WARN (info):** `mypy --strict` and `ruff` not independently re-verified — neither tool is installed in the available interpreter, so the pinned "clean" claims are accepted on the brief's word and code inspection (consistent `from __future__ import annotations`, full type hints, frozen dataclasses). Re-run both in the project's actual lint/type environment for full validation.
- **PASS:** Remaining work for a fully-validated gold layer is correctly scoped as future, not overclaimed: (1) empirical calibration of the direction table + confidence weights against a real multi-regime corpus; (2) runtime computation of `duplicate_ok`/`operational_ok`; (3) the paper-trading runtime/consumer (SCHEMA-011.consumed_by intentionally empty); (4) promoting GATE-002 from advisory to blocking; (5) a hygiene/DEBT pass before the first trusted export. None block v0 authoring per ADR-006 §8(b).

---

## Critical Issues

None — zero critical/high/FAIL candidates were produced by the eight dimension auditors, and the adversarial-verification set was empty (`verifiedCriticalCount = 0`). All eight dimensions returned PASS, and the lead independently reproduced the pinned facts, the gold test suite (29 passed), and the separation/determinism invariants. No safety, determinism, or separation defect exists.

---

## Warnings

1. **ADR-008 §3 coverage discount omits `failed_required_features`** *(genuine code-vs-text gap; low severity)* — `policy.py:40,59` uses only `len(fv.unavailable_features)` and never reads `rc.failed_required_features`, which ADR-008 §3 and `GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md` line 21 name as a coverage input. A non-floored packet can carry `failed_required_features` non-empty while the coverage discount ignores it, slightly over-stating confidence vs the ADR text. Does not affect the pinned real snapshot, INDETERMINATE (floored), determinism, or separation. Fix: add `len(rc.failed_required_features)` to the coverage count, or amend §3 to scope coverage to `unavailable_features` only.
2. **Missing `src/gold/__init__.py`** *(layout-mirror / packaging; low severity)* — confirmed missing while all five sibling top-level packages have a docstring-bearing `__init__.py`; `gold` resolves as an implicit PEP 420 namespace package, masked by `pythonpath=['src']`. `pyproject.toml:16` declares `src/gold` as a wheel target, so the wheel build relies on namespace handling. Add a one-line `src/gold/__init__.py` matching the sibling convention.
3. **SCHEMA-011 doc overstates "instrument == GLD" enforcement** *(doc-vs-code; low severity)* — the node doc lists it as a packet Validation Rule, but `__post_init__` has no instrument check; it is a fingerprinted/versioned config default (`'GLD'`) only. Either add a packet-level assertion or soften the doc wording.
4. **Stale "26 tests" figure in the MOD-006 node** *(documentation drift; low severity)* — `dev_graph/modules/Gold Decision Builder.md` line 78 says 26; actual gold suite is 29. Refresh on next edit.
5. **Export-validation stat drift (139/910 → 140/920)** *(documentation-provenance drift; low severity)* — `log.md` records the Stage-2 figure; the live dry-run is 140/920/5 (TEST-012 added afterward). index.md is correct at 140. Re-record the export as 140/920/5 before the next trusted export.
6. **`mypy --strict` / `ruff` cleanliness not independently re-verified** *(tooling unavailable; informational)* — neither installed in the available interpreter; pinned "clean" claims accepted on inspection. Re-run in the project's lint/type environment for full validation.

---

## Technical Debt

1. **Domain-anchored, not data-fitted policy** — the direction table and confidence weights are provisional domain bands, calibrated against exactly one real snapshot (the 3 benchmark "consumables" collapse to a single distinct snapshot_id 952cc83a…); the other 10–11 regimes are synthetic. Recalibration awaits a real multi-regime corpus and a governed `decision_policy_version` bump.
2. **Coverage-input parity with ADR-008 §3** — until Warning 1 is resolved, the coverage discount and the ADR normative text disagree on whether `failed_required_features` counts. Carry as debt until code or §3 is aligned.
3. **Deferred L3 guard computation** — `duplicate_ok`/`operational_ok` (PRED-006/007) and GATE-002 are advisory stubs carrying `None`; they require the unbuilt paper-trading runtime. GATE-002 stays `blocking:false` until guards + runtime exist.
4. **Graph-export provenance hygiene** — the pinned/recorded export figures lag the live graph; a DEBT pass (re-record 140/920/5, refresh the MOD-006 test count) is owed before the first trusted Neo4j export.
5. **Static-analysis re-validation environment** — `mypy`/`ruff` are not installed in the working interpreter, so the pinned static-check guarantees cannot be re-confirmed in-place; establish a canonical lint/type environment.

---

## Future Extensions

1. **Empirical confidence/direction calibration** — once real snapshots accumulate across regimes, fit (and version) the direction table and confidence weights against observed outcomes, replacing the domain-anchored provisional bands.
2. **Stateful L3 guard runtime** — implement `duplicate_ok` (replay-dedup) and `operational_ok` once the paper-trading runtime lands, then promote GATE-002 from advisory to blocking.
3. **Paper-trading consumer** — author the downstream consumer of SCHEMA-011 (currently `consumed_by` intentionally empty), closing the end-to-end snapshot → packet → paper-trade loop.
4. **Secondary/near-regime exposure** — surface `secondary_matching_rules`/`near_matching_rules` (already in `confidence_inputs`) as alternative-signal context for consumers.
5. **Regime-persistence / transition penalties** — a future stateful builder could damp regime flips below a margin threshold; note the candid LIQUIDITY_STRESS→LONG "dash-for-cash" caveat recorded in the MOD-006 Open Questions.

---

## Engineering Digital Twin Maturity Impact

This slice advances the Engineering Digital Twin from **multi-module determinism composition** (Feature → Regime) to a **complete deterministic decision pipeline** (Snapshot → Feature → Regime → Decision):

- **Full L3 determinism cascade validated** — `tests/gold/test_e2e_pipeline.py` exercises consume → build_features → classify → build_decision with one `snapshot_id` threading every stage and byte-identical replay end-to-end.
- **Identity-hash discipline** — `compute_packet_id` digests the full `(snapshot, feature/regime versions, decision_policy_version, decision_policy_fingerprint)` tuple, so a decision is cryptographically tied to its exact policy snapshot; un-versioned weight/table drift breaks a pinned CI test.
- **Governed policy versioning** — the fingerprint excludes only the version string, making any decision-affecting change require an explicit `decision_policy_version` bump — safe, auditable change management.
- **Fail-closed decision semantics** — INDETERMINATE maps to WATCH with floored confidence/uncertainty, enforced redundantly at the config and packet layers.
- **Permanent treasury separation proven at AST level** — gold confidence is structurally independent of SCHEMA-005, holding the ADR-004 boundary as the analysis layer grows.

---

## Gold Layer Readiness Assessment

- **Gate (a) — Feature Builder (MOD-004) exists:** ✅ **CLOSED** by a prior slice (ADR-006 §8).
- **Gate (d) — Regime taxonomy enumerated and grounded:** ✅ **CLOSED** by the prior Regime Taxonomy slice (MOD-005 / SCHEMA-010 / ADR-007).
- **Gate (b) — Feature coverage sufficient (gaps explicitly accepted):** ✅ **CLOSED** by ADR-008 §9 — the 7 reserved features (matching `taxonomy.py:83-90` verbatim) are explicitly accepted out of v0 scope.
- **Gate (c) — Replay finalization:** ✅ **CLOSED** — the decision replay key and full identity tuple are pinned and fingerprinted; `packet_id` closes the cross-version/config collision hazard.
- **Gate (e) — Confidence semantics:** ✅ **CLOSED** by ADR-008 — a deterministic ordinal trust score anchored on `rule_margin`, with a structural-penalty-aggregate uncertainty (distinct from `1 − confidence`).

**All five ADR-006 §8 Creation Gates are closed; the Gold DecisionPacket v0 contract is authored, implemented, tested, and benchmarked.** Remaining work for a *fully-validated* (vs. structurally-complete) gold layer is correctly deferred: empirical calibration against a real multi-regime corpus, runtime computation of the stateful L3 guards, the paper-trading consumer, promoting GATE-002 to blocking, and a graph-export hygiene pass.

---

## Final Verdict

**PASS**

The Gold DecisionPacket v0 (MOD-006) is **approved for use within its defined scope**: deterministic, paper-only Gold DecisionPacket generation from validated regime classifications, upstream of the deferred paper-trading runtime.

- All eight audit dimensions PASS; no confirmed critical issues (`verifiedCriticalCount = 0`).
- All five ADR-006 §8 Creation Gates closed; the v0 contract (SCHEMA-011) is complete, fail-closed, and stdlib-only.
- Determinism verified: `build_decision` is pure/total; `packet_id` digests the full identity tuple including the policy fingerprint; pinned facts reproduce exactly (RESTRICTIVE_RATES / AVOID / 0.39744 / 0.136 / `gold-v0:5653d07a0b3949d5` / `be7e3192…a8a5`).
- Separation verified: zero supervisor/treasury imports in `src/gold`; no SCHEMA-005 confidence bleed; CAP-004 deprecated and superseded by CAP-020, never merged into the treasury CAP-015.
- Governance complete: 15 ontology-compliant nodes (schema_version 2.2.0), correct graph convergence onto MOD-006, clean CAP-004 rewiring; 29 gold tests within an 801-pass suite, BENCH-002 in sync.

**Scope note:** the one genuine code finding (the coverage discount omitting `failed_required_features`) and the three documentation-drift items are all low-severity and non-blocking for v0 authoring per ADR-006 §8(b). They should be cleared in a follow-up hygiene/calibration pass before the gold layer is promoted from structurally-complete to fully-validated.

---

**Audit completed:** 2026-06-08
**Method:** 8 parallel read-only dimension auditors → adversarial verification of critical/FAIL candidates (0 produced, 0 survived) → lead synthesis with independent re-verification of pinned facts, test suite, and graph export.
**Evidence:** Per-dimension audits; `src/gold/decision_builder/{models,policy,builder,config}.py`; `tests/gold/{test_decision_builder,test_gold_bench,test_e2e_pipeline}.py`; `benchmarks/gold/artifacts/gold_bench.json`; the 15 dev_graph nodes (SCHEMA-011, INT-009, CAP-020, MOD-006, PRED-006/007, GATE-002, BENCH-002, FILE-015..018, TEST-010/011/012); ADR-006 / ADR-008; live `dev_graph/sync_to_neo4j.py --dry-run`.

---

## Post-Audit Remediation (2026-06-08)

The audit's actionable low-severity findings were cleared immediately after the audit (the audit above is the as-audited baseline; this records the follow-through):

1. **Coverage discount now reads `failed_required_features` (the one genuine code finding).** `policy.py` coverage is now computed over the DISTINCT missing features `set(unavailable_features) | set(failed_required_features)`, literally matching ADR-008 §3. Because `failed_required_features ⊆ unavailable_features` (an absent feature is omitted from the vector), this is a **numerical no-op**: confidence (0.39744), `uncertainty` (0.136), `packet_id` (`gold-v0:5653d07a0b3949d5`), the `decision_policy_fingerprint`, and `gold_bench.json` are all unchanged; all 801 tests pass unmodified.
2. **`src/gold/__init__.py` added** — the package marker that every sibling top-level package (`risk`/`supervisor`/`snapshot`/`features`/`regime`) carries; `src/gold` is now a regular package, not an implicit namespace package.
3. **Documentation drift cleared** — MOD-006's node now reads "29 gold tests (20 builder + 6 bench + 3 e2e)"; the live export count is 140 nodes / 920 edges / 5 legitimate skips after TEST-012 (the `log.md` Stage-2 figure of 139/910 was the pre-E2E point-in-time count).

Re-verification after remediation: **pytest 801 passed; `mypy --strict` clean on `src/gold` (only the 2 pre-existing MOD-004 lambda findings remain, out of scope); `ruff` clean.** The deterministic real-snapshot path and all pinned facts are unchanged. Residual readiness gap is now purely empirical (provisional domain-anchored weights/table + synthetic coverage), to be closed by real-corpus calibration — not a code or governance defect.