# REGIME_IMPLEMENTATION_BRIEF

**Slice:** Deterministic Regime Taxonomy layer (MOD-005 / SCHEMA-010 / ADR-007 / INT-007 / CAP-019 / KA-011 / PAT-011 / BENCH-001).
**Date:** 2026-06-08. **Status:** context-discovery complete; implementation executed.

This brief is the STEP 0 deliverable: it records what the slice touches and the architectural reconciliation it rests on, established via dev_graph + code discovery before any code was written.

---

## 1. Objective

Introduce a governance-controlled, deterministic, replayable **Regime Taxonomy** layer that becomes the canonical semantic abstraction between Feature Engineering (MOD-004) and the future Gold Decision Builder. Every Layer-2 snapshot is classified into exactly one market regime using **only snapshot-local feature information** — no future info, no history, no rolling windows, no hidden state, no adaptive learning, no online updates. Replay of the same snapshot always produces an identical classification.

This closes **ADR-006 §8(d)** ("Regime taxonomy exists — `regime_class` values are enumerated and grounded"), the explicit open creation gate for the Gold DecisionPacket v0.

## 2. Affected modules

| Area | Change |
|------|--------|
| `src/regime/regime_classifier/` (NEW, MOD-005) | `models.py`, `config.py`, `taxonomy.py`, `regime_classifier.py`, `__init__.py` |
| `pyproject.toml` | added `"src/regime"` to hatch wheel packages |
| `tests/regime/` (NEW) | `test_regime_classifier.py` (TEST-008), `test_regime_bench.py` (TEST-009) |
| `benchmarks/regime/` (NEW) | `run_regime_bench.py` (BENCH-001) + `artifacts/regime_bench.json` |
| MOD-003 Snapshot Consumer, MOD-004 Feature Builder | **unchanged** (consumed read-only as upstream) |
| MOD-001 Guardrail, MOD-002 Decision Engine | **unchanged** (separate bounded contexts) |

## 3. Affected schemas

- **NEW SCHEMA-010 `RegimeClassification`** — produced by MOD-005, consumed (in future) by the Gold builder. Field groups: decision (`matched_rule_id`, `regime`, `rule_priority`, `rule_margin`, `rule_threshold`, `rule_scale`, `trigger_features`), provenance/identity (`snapshot_id`, `feature_schema_version`, `provenance`, `as_of`), explainability/trace (`evaluated_rule_ids`, `skipped_rule_ids`, `failed_required_features`, `secondary_matching_rules`, `near_matching_rules`), and three independent versions.
- **SCHEMA-009 Feature Vector** — consumed read-only (input contract). No change to its shape.
- **SCHEMA-001 Layer-2 Snapshot** — never consumed directly (boundary respected: MOD-005 takes a FeatureVector, not a snapshot).

## 4. Ontology impact

New nodes: ADR-007, KA-011 (Regime Taxonomy), PAT-011 (Regime Classification Pattern), CAP-019 (Market Regime Classification), INT-007 (Regime Classification API), MOD-005, SCHEMA-010, FILE-011/012/013, TEST-008/009, BENCH-001 (first benchmark_result node). Updated nodes: MOD-004 + SCHEMA-009 (add downstream `Used By` regime classifier), ADR-006 (cross-link ADR-007, gate (d) satisfied), index.md, log.md, Dev Graph Dashboard. No new ontology *types* or enum values — the 24-type ontology and the `benchmark_result`/interface mappings already exist; no `sync_to_neo4j.py` change required.

**Canonical-id note:** ADR-006 §7 named SCHEMA-010 a *non-binding candidate* for the future Gold DecisionPacket. SCHEMA-010 is consumed here for `RegimeClassification`; the Gold DecisionPacket candidate therefore shifts to the next free id (SCHEMA-011), formally assigned only when that node is authored. This is consistent with ADR-006 (ids are reserved only at authoring time).

## 5. Replay impact

Extends the determinism chain to the decision-adjacent layer:
- **Decision replay key:** `(snapshot_id, taxonomy_version, classifier_version)` ⇒ identical decision.
- **Full-serialization key:** `+ classification_trace_version` ⇒ byte-identical `to_dict()`.
`classify()` is a pure, total function (no clock/RNG/IO/history/ML). Evidence: every available real snapshot replayed twice is byte-identical (benchmark `determinism.all_replays_byte_identical = true`), and a golden test pins the real PASS snapshot → RESTRICTIVE_RATES. Thresholds are config-driven and versioned; a `taxonomy_version`↔fingerprint coherence test prevents un-versioned threshold drift.

## 6. Benchmark impact

First population of `dev_graph/benchmarks/` (BENCH-001). `benchmarks/regime/run_regime_bench.py` emits a committed golden artifact with two parts: (1) **determinism evidence** over the real snapshots; (2) a **clearly-labelled synthetic** feature-grid sweep producing distribution, coverage (11/11 regimes reachable), Shannon entropy, classification balance, unclassified %, rule utilization, and regime frequency. The harness is deterministic (fixed grid, no RNG/clock); a test asserts the committed artifact stays in sync.

## 7. Migration risk

**Low.** Purely additive: a new domain package, new tests, new benchmark, new dev_graph nodes. No existing module, schema, test, or canonical_id is modified in a breaking way (MOD-004/SCHEMA-009 get additive downstream links only). No `wiki/**` or `raw/**` mutation. The only cross-cutting edit is one line in `pyproject.toml`. There is **no historical snapshot corpus** in the repo (3 fixtures + 2 source snapshots only) — so replay/coverage evidence is "real determinism + synthetic coverage," reported honestly as such (no fabricated history).

## 8. Governance impact

- Satisfies ADR-006 §8(d); contributes to (b) feature-coverage and (c)/(e) replay/confidence semantics by pinning the regime contract and its determinism key.
- New **ADR-007** governs the layer: rule-selection-engine framing; `rule_margin` is a rule-local activation margin (not epistemic confidence, not globally comparable); config-driven/versioned thresholds; NEUTRAL is the sole catch-all (conflict surfaced via metadata, no MIXED_SIGNAL label); fail-closed INDETERMINATE; independent `classification_trace_version`.
- **ADR-005 reconciliation:** ADR-005 §2 forbids "inferred regimes" *as a feature class*, explicitly deferring such logic to "a later, explicitly stateful node with its own ADR." The regime layer is exactly that node — and it is **rule-based and deterministic, not inferred/learned** — governed by ADR-007. No contradiction: ADR-005 governs the feature layer's purity; ADR-007 governs a separate downstream classification layer that consumes those pure features.

## 9. Verification summary

`pytest` (772 passing incl. 719 regime), `mypy --strict` clean on the regime package + tests (2 pre-existing lambda-inference findings in MOD-004 `feature_builder.py` are out of scope, surfaced only by a newer mypy), `ruff` clean, benchmark artifact regenerated deterministically. Gold builder intentionally **not** implemented (STEP 11): RegimeClassification is exposed via INT-007 as the canonical upstream contract.
