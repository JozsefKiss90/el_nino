# Architecture / Ontology Stabilization Audit — dev_graph

**Date:** 2026-06-07
**Auditor role:** Chief Architect — final architecture review before the next development epoch
**Mode:** Read-only. No nodes, files, or commits modified during the audit.
**Method:** Multi-agent fan-out — 11 parallel domain finders (Parts 1–11), each material finding subjected to an independent adversarial refutation pass, then synthesis (Parts 12–15). 30 agents, ~2.48M tokens, 632 tool calls. Two highest-stakes findings independently re-verified by hand (`build_features` purity, `consumer` fail-closed gate, publisher `NameError`).

---

## Executive Verdict (BLUF)

> ## 🟢 STABLE WITH MINOR DEBT
> **Architecture Stability Index: 84 / 100** · Digital-Twin Maturity: **Level 4 / 5** (Managed/Integrated)
>
> **0 of 18 debt items block the next development epoch.** The implemented Layer-3 vertical slice is production-credible and replay-safe (53/53 tests pass; `recompute_id()` reproduces the real artifact id `952cc83a…afaef` bit-for-bit; bounded-context separation is grep-clean in source; the 6-ADR chain has zero conflicts). The "minor debt" qualifier is earned by **two *systematic* hygiene defects** (10/10 knowledge assets miss their mandatory ADR back-link; `index.md` statistics are self-contradictory) plus a band of **graph-export-edge defects** and **one upstream producer `NameError`**.
>
> **Recommended next slice: author the Regime Taxonomy** — the single target rated unconditionally READY and the keystone that unblocks the entire gold-decision lineage.

### Stability Index Scoreboard

| Dimension | Score | One-line basis |
|---|---|---|
| Ontology Stability | **82** | 0 duplicates, perfect canonical_id uniqueness/immutability; degraded only by relationship-edge integrity |
| Governance Stability | **87** | 6-ADR chain: 0 conflicts, 0 broken supersession; implementation provably obeys governance |
| Replay Readiness | **86** | L3 chain empirically deterministic & verified; upstream producer leg broken + float-platform caveats |
| Graph-RAG Readiness | **82** | Real Smart Connections/Dataview/Neo4j exporter; gold-frontier needs read-ADR-first; no auto-enforcement |
| Engineering Digital Twin | **82** | Faithful bidirectional code↔graph mirror (22/22 paths resolve); held off L5 by 2 mechanical drifts |
| **Overall Architecture Stability Index** | **84** | Justified aggregate (not a naive mean) — load-bearing dimensions verified, defects non-blocking but systematic |

---

## Part 1 — Ontology Integrity → 82/100

**One concept = one node holds.** 109 unique canonical_ids, **zero reuse or reassignment** (the only `MOD-NNN`/`FILE-NNN` strings are CLAUDE.md template placeholders). **Zero semantic duplications, zero merge candidates, zero forced splits, zero hidden aliases.** Bounded contexts cleanly separated across the 6 systems. The 4 `models.py` file nodes (FILE-003/006/007/009) have distinct ids, paths, and module parents — basename-collision integrity intact.

**Seam verdict (adversarially confirmed as NOT defects):** CAP-002 Feature Engineering (L2 producer) vs MOD-004 Feature Builder (L3 transform), and CAP-003 Snapshot Assembly (L2 producer) vs MOD-003 Snapshot Consumer (L3 ingestion) are **legitimately distinct** opposite sides of a contract — deferral documented in each module's Open Questions and the log.

**Real defect (UPHELD high):** `MOD-003 Snapshot Consumer` declares `provides:` + `### Implements` + `### Consumes` on the *same* interface (INT-001) — a pure consumer cannot "provide" the upstream read contract. Contradicts INT-001's own node and the publisher source.

**Refuted by adversarial pass (excluded from ledger):** "SCHEMA-001↔INT-001 inverted edge" — false positive (`### Consumed By` is a passive reverse-annotation, not a `### Consumes` edge). "Empty `realized_by_modules`" — downgraded; the load-bearing realization machinery is elsewhere.

**Ontology health breakdown:** canonical uniqueness/immutability 100%; semantic duplication 0; bounded-context separation clean; relationship-edge integrity DEGRADED (1 high + edge-modeling inconsistencies).

---

## Part 2 — ADR Consistency → 88/100

**ADR dependency graph (verified):**

```
ADR-001 Bootstrap (root, 2026-05-25)
  └─ justified-by ─ ADR-002 Ontology Redesign (06-06)
        ├─ justified-by ─ ADR-003 Implementation Substrate (06-06) ──→ substrate for MOD-001/002/003/004
        └─ justified-by ─ ADR-004 Decision Layer Re-grounding (06-07)
              ├─ constrains ─ MOD-002 / INT-006 / SCHEMA-004 / SCHEMA-005  (treasury branch)
              └─ justified-by ─ ADR-005 Feature Layer Contract (06-07) ──→ produces SCHEMA-009
                    └─ unblocks ─ ADR-006 Gold DecisionPacket v0 Planning (06-07, draft/proposed)
```

**0 conflicting ADRs · 0 obsolete-but-governing · 0 superseded-still-in-force.** Implementation provably obeys governance (src tree + pyproject match ADR-003; `feature_builder.py` obeys ADR-005 §1–§5 rule-for-rule). The "missing grounding/restructure ADR" finding was **refuted** — ADR-003:44 pre-authorizes the multi-package `src/` layout. Residual: 2 frontmatter-hygiene nits (ADR-002 stale `status:active/in-progress` for a fully-enacted redesign; ADR-001 uses `decision_status: accepted`, outside the declared enum). **The chain is sufficient to support future evolution.**

**ADR conflict / obsolescence matrix:** 0 conflicting, 0 obsolete-but-governing, 0 superseded-still-in-force, 1 (refuted) missing-ADR claim, 2 frontmatter-hygiene deviations.

---

## Part 3 — Layering Validation → 88/100

**No illegal cycles.** The Supervisor-Office→Trading-Engine loop-back and the Trading-Engine↔Risk-Control handshake were both assessed and confirmed as **legitimate evaluation/request-response seams, not cycle violations.**

- **Real defect (UPHELD, high→medium):** `MOD-002 Decision Engine` declares an upward `Depends On` two **capabilities** (module→capability layer inversion), ungrounded in code. Low blast radius (links resolve, conceptual dependency is real — just at the wrong layer/field).
- **Real defect (UPHELD, medium→low):** `FILE-008 consumer.py` uses `owns` to claim an **interface** node — an inverted file→interface ownership shortcut.
- Minor: PAT-002 back-index stale after MOD-001 landed; `Consumes` relationship mistyped on a sibling module; `index.md` still labels MOD-001/002 "(plan only)" despite tested code.

---

## Part 4 — Traceability Audit → 82/100

**Implementation-traceability is faithful and complete for all 4 built modules** (full table under Part 11). Every implemented module traces KA → ADR → SYS → CAP → MOD → FILES → TESTS, *except* the documented L3-consumer seam.

The "MOD-003/MOD-004 have no parent-capability edge" finding was **refuted to INFO**: their would-be parents (CAP-002/CAP-003) are themselves `not-started` L2-producer-framed capabilities — this is the **same deliberate producer/consumer seam**, deferred to a future re-grounding ADR, not a broken chain. **Acceptable, governed debt.**

---

## Part 5 — Contract Audit → 88/100

**Contract-before-implementation honored across all four slices** (verified against log ordering). Implementations match contracts; **no premature frozen contract** — ADR-006 correctly freezes *no* Gold DecisionPacket schema. Reserved-but-uncreated SCHEMA-002/003/006 are correct per §4.6.

**Real defect (UPHELD, low):** SCHEMA-008 documents an `evaluated_at` field the realizing `TradeValidationDecision` dataclass omits — contract drift (and a wall-clock field would anyway violate determinism; `consumed_by` is empty, so nothing is broken today). Minor: INT-003/006 frontmatter `stability` vs body prose; SCHEMA-004/005 empty `validated_by` despite existing tests.

---

## Part 6 — Replay Determinism Audit → 88/100

**The implemented L3 replay chain (Layer-2 Snapshot → MOD-003 → MOD-004) is empirically replay-deterministic.** Independently confirmed: `Snapshot.recompute_id()` reproduces `952cc83a…afaef`; `build_features()` is pure/total/env-invariant (sorted-deterministic ordering, no clock/IO/randomness); the only IO sits at the ingest boundary, not the compute path. **No temporal leakage, no runtime cache, no env-dependence, no randomness in the compute path.**

**Real defect (UPHELD high — verified by hand):** `snapshot_sources/snapshot_publisher.py:625` calls `H_get_engine_version()`; the function is defined at line 60 as `_get_engine_version()`. Guaranteed `NameError` — **every `main()` invocation crashes**, breaking snapshot re-publication. (Does *not* touch the replayable L3 chain — the existing artifact replays bit-for-bit — but it gates any "regenerate-and-confirm-stable-id" producer workflow.)

Minor (low): identity hash / feature values depend on platform float behaviour (`.6f` formatting, `repr`-float subtraction); `models.py` docstring wrongly claims `as_of_ts`/`revision_seq` are "not modelled" when they are parsed and identity-determining.

---

## Part 7 — Feature Layer Audit → 96/100 ✅ (cleanest part)

All **14 FEATURE_REGISTRY entries verified as pure snapshot-local transforms** — levels and spreads only. **Zero forbidden classes** (no moving averages, momentum, rolling windows, z-scores, percentiles, smoothing, look-ahead, regimes, or embeddings). Provenance (`inputs`), `revision_risk` (OR over inputs), and `max_staleness_days` (max over inputs) all propagate correctly; missing input → `unavailable_features` with no partial value. ADR-005 prose matches code. **Feature Layer purity confirmed.** (Only a prose nit in ADR-005 §3 and the documented CAP-002 attachment seam; ratio class is admissible but absent from v0.1.0.)

---

## Part 8 — Decision Layer Audit → 96/100 ✅

**Bounded-context separation verified in source code, not merely asserted** (grep-clean). The treasury-upgrade branch (MOD-002/INT-006/SCHEMA-004/005) and the future gold branch are permanently separated; ADR-004 correctly **rejected** the rename/split that would have broken canonical_id immutability (split-only for type changes). ADR-006 freezes no schema and **Creation Gates b–e are correctly still open**. Future Gold DecisionPacket evolution is **safely constrained** (triply-guarded). Only 2 prose-vs-frontmatter nits (ADR-006 `decision_status:active` vs body "Proposed"; a `Depends On SCHEMA-001` edge a naive assembler could misread).

---

## Part 9 — Population Strategy Compliance → 94/100 · Compliance: 96.1% (13.45/14 weighted rules)

**Just-in-time, source-driven, governance-first ordering fully verified** against git history (src/ appeared *after* the MOD nodes; SCHEMA-001 grounded in real `snapshot_sources/*`). **No speculative nodes. Stopping rules respected** (governance 7 ≤ impl 21; under 200-node ceiling). Reserved-id matrix clean: all 8 interface and 6 schema §4.6 reservations are either correctly created in-reservation or correctly uncreated.

The "GOV-005/GOV-006 are orphans" finding was **refuted** — it misquoted CLAUDE.md, which requires ≥1 *outbound* link (not inbound); both nodes satisfy it. Residual (low): strict content-to-content orphan rate 1.8% (under the 5% KPI but worth a one-line inbound link each — e.g. GOV-001→GOV-005, GOV-004→GOV-006); §4.6 reservation-table drift (SCHEMA-007/008/009 created above the 6-schema ceiling); basename-collision latent export hazard.

---

## Part 10 — Graph-RAG Readiness → 82/100

**Infrastructure is real, not paper:** Smart Connections + Dataview installed; `sync_to_neo4j.py` is a working exporter (frontmatter + `### Relationship` parse, `MERGE` on canonical_id); OBS-001 has 21 health queries. **8/11 routing intents are fully assemblable today**; 3 lack substrate only by *documented deferral* (events/benchmarks empty).

The two "HIGH" findings here were **both refuted as false positives**: the ADR-006 "Depends-On traversal trap" (the edge is a build-time dependency, not a runtime consumption) and the "gold branch misfires to treasury" (correct *by design* — gold v0 is deferred, so no entry node exists yet). **Real (UPHELD, low):** mixed bare-vs-path-qualified wikilink forms deterministically drop ≥6 edges at Neo4j export. The validate/enforce layer is manual (no automated admissibility runner) — a precision ceiling, not a defect.

**Simulated retrieval ("implement the Gold DecisionPacket v0 builder"):** Implementation intent routes to a Capability entry point, but no gold-decision capability exists yet — so semantic retrieval surfaces the *treasury* branch (SCHEMA-004/MOD-002/INT-006), which survives Dataview filtering because it is legitimately `active/implemented`. Separation is enforced by **ADR prose, not graph structure**, on the highest-value future task. This is the core conditional weakness — read-ADR-first is mandatory until a gold capability/module entry point exists.

---

## Part 11 — Engineering Digital Twin Readiness → 82/100 · Maturity Level 4/5 (Managed/Integrated)

**Implementation-traceability mirror — zero drift:**

| Module | Source | File nodes | Test nodes | Status |
|---|---|---|---|---|
| MOD-001 Guardrail | `src/risk/guardrail_engine/` | FILE-001/002/003 | TEST-001/002 | ✅ all resolve |
| MOD-002 Decision | `src/supervisor/decision_engine/` | FILE-004/005/006 | TEST-003/004 | ✅ all resolve |
| MOD-003 Snapshot Consumer | `src/snapshot/snapshot_consumer/` | FILE-007/008 | TEST-005/006 | ✅ `recompute_id`==real id |
| MOD-004 Feature Builder | `src/features/feature_builder/` | FILE-009/010 | TEST-007 | ✅ 14-feat registry matches |

22/22 file/test/predicate paths exist on disk (100%).

**Graph-vs-reality drift:** `index.md` headline claims **109** content nodes / **113** files, but the per-type tally *and* disk both show **110** content nodes / **114** files. Root cause: deprecated REF-004 (`Infrastructure Diagram.md`) at the dev_graph root is counted in the per-type tally but omitted from the headline total — an off-by-one propagated into log.md.

Held below L5 by **two mechanical, UPHELD defects**: (a) the self-contradictory `index.md` statistics above; (b) **all 10 knowledge assets carry empty `informs_decisions`** — the KNOWLEDGE→DECISION leg is 100% unwired on the KA side, violating the literal CLAUDE.md "every KA MUST reference ≥1 ADR" rule. (ADR→KA direction *is* wired, so the loop is half-connected, not broken.)

---

## Part 12 — Technical Debt Register (18 items · 0 epoch-blocking)

| # | Class | Sev | Title | Blocks | When |
|---|---|---|---|---|---|
| 01 | implementation | high | Publisher `NameError` (`snapshot_publisher.py:625`) | *producer re-publish workflow only* | near-term |
| 02 | ontology | high | MOD-003 provides+consumes same interface | *first Neo4j export only* | near-term |
| 03 | architectural | med | MOD-002 upward module→capability `Depends On` | *first Neo4j export only* | near-term |
| 04 | governance | med | 10/10 KAs empty `informs_decisions` (KA→ADR) | — | near-term |
| 05 | documentation | med | `index.md` statistics self-contradictory / disk drift | — | near-term |
| 06 | implementation | low | SCHEMA-008 `evaluated_at` contract drift | — | near-term |
| 07 | replay | low | Mixed wikilink forms drop ≥6 export edges | *first Neo4j export only* | near-term |
| 08 | documentation | low | INT-003/006 `stability:evolving` vs body "experimental" | — | deferred |
| 09 | documentation | low | SCHEMA-004/005 empty `validated_by` despite tests | — | deferred |
| 10 | ontology | low | Inconsistent file→schema modeling across 4 `models.py` | — | deferred |
| 11 | ontology | low | `consumer.py` (FILE-008) `owns` the Snapshot API interface | — | deferred |
| 12 | documentation | low | `index.md` Realizes-edge count internally inconsistent | — | deferred |
| 13 | governance | low | `index.md` Modules table still says MOD-001/002 "(plan only)" | — | deferred |
| 14 | ontology | low | `Consumes` relationship mistyped on a sibling module/interface | — | deferred |
| 15 | governance | low | Admissibility Checks 6 & 9 manual, no automated runner | — | deferred |
| 16 | governance | low | `decision_status: accepted` (ADR-001) outside declared enum | — | deferred |
| 17 | documentation | low | ADR-002 stale `status:active/in-progress` for enacted redesign | — | deferred |
| 18 | documentation | low | ADR-006/decision-layer prose-vs-frontmatter hygiene cluster | — | deferred |

**Two step-specific conditional gates** (neither blocks continued L3 development): fix **DEBT-01** before any "regenerate-and-confirm-stable-id" producer run; fix **DEBT-02/03/07** before relying on the **first trusted Neo4j export**.

**Correctly governed deferrals — NOT debt:** CAP-002/MOD-004 & CAP-003/MOD-003 producer/consumer seams; reserved-uncreated INT-002/004/005/007/008 & SCHEMA-002/003/006; empty `events`/`agents`/`skills`/`benchmarks` dirs; ADR-006 not freezing the gold schema; 7 forward-ref wikilinks to reserved ids.

---

## Part 13 — Future Evolution Readiness

| Target | Verdict | Gating reason |
|---|---|---|
| **1. Regime Taxonomy** | 🟢 **READY** | ADR-006 §8(d) is the explicit currently-OPEN gate; grounding (14 tested features) already exists |
| 2. Regime Classifier | 🟡 **CONDITIONALLY READY** | Needs #1 (output domain) + an L3 feature-consuming capability entry point |
| 3. Gold DecisionPacket Schema | 🟡 **CONDITIONALLY READY** | ADR-006 §8 Gates b–e open (feature-coverage, replay finalize, regime taxonomy, confidence semantics) |
| 4. Decision Builder | 🟡 **CONDITIONALLY READY** | Transitively gated on #3; L3 guards (`duplicate_ok`/`operational_ok`) unauthored |
| 5. Execution Layer | 🔴 **NOT READY** | No governing ADR; ADR-006 Non-Goals defer all execution; INT-002/SCHEMA-002 uncreated |
| 6. Paper Trading Loop | 🔴 **NOT READY** | Transitively requires #5; ADR-006 defers backtest/paper runtime; `benchmarks/` empty |
| 7. Replay Engine | 🔴 **NOT READY** | Per-artifact replay proven, but Snapshot API mode-2 (by-id query) deferred; producer leg broken (DEBT-01) |

---

## Part 14 & 15 — Stability Index & Executive Verdict

**Overall Index 84/100** is a *weighted* aggregate (not the ~84.5 naive mean): the verified load-bearing dimensions (faithful traceability, proven L3 replay determinism, sound contract spine, clean bounded-context separation, coherent ADR chain) anchor stability; the deduction reflects that two upheld defects are **systematic** (KNOWLEDGE→DECISION uniformly unwired; observability surface self-contradictory) and the export-edge defects make a first Neo4j export untrustworthy — genuine *minor* debt, broadly distributed but non-blocking.

### → STABLE WITH MINOR DEBT

The ontology, governance model, implementation graph, and architectural layering **have reached a stable fixed point.** No defect touches the replayable L3 chain or any passing test; there is no architectural collapse, no illegal cycle, no canonical_id violation. The graph may enter the next development epoch.

### Single highest-value next slice → Author the Regime Taxonomy

It is the only unconditionally-READY target, it is the **explicit open Creation Gate** ADR-006 §8(d) names, its grounding is already tested (14 deterministic MOD-004 features), it needs no execution/runtime substrate, and it is the **keystone that converts four CONDITIONALLY-READY gold targets toward buildable** (Regime Classifier → Gold DecisionPacket Schema closes Gate d → Decision Builder).

**Recommended ordering** (optional, ~30-min hygiene; none blocks starting the taxonomy):

1. Rename `snapshot_publisher.py:625` → `_get_engine_version` (DEBT-01) — restores the producer leg.
2. Drop MOD-003 `provides`/`### Provides` + MOD-002 capability `Depends On` + normalize wikilink forms (DEBT-02/03/07) — makes the first Neo4j export trustworthy.
3. Batch the KA→ADR back-links + `index.md` stat reconcile (DEBT-04/05) — restores L5 digital-twin self-consistency.

---

## Appendix — Adversarial Verification Ledger

Material findings (severity blocking/high/medium) were each independently re-checked by a separate agent prompted to *refute*. Outcome summary:

- **Upheld (real, kept):** MOD-003 provides/consumes same interface (P1); MOD-002 module→capability inversion (P3); FILE-008 `owns` interface (P3); SCHEMA-008 `evaluated_at` drift (P5); publisher `NameError` (P6); mixed wikilink forms (P10); `index.md` stat drift (P11); 10/10 KA→ADR missing (P11).
- **Refuted (false positives, excluded from ledger):** SCHEMA-001↔INT-001 "inverted edge" (P1); empty `realized_by_modules` (P1); "missing grounding ADR" (P2); MOD-003/004 "broken capability chain" (P4 — it is the documented seam); GOV-005/006 "orphans" (P9 — rule is outbound, not inbound); ADR-006 "Depends-On traversal trap" (P10); "gold branch misfires" (P10 — by design); 4×`models.py` "collision" (P10 — disambiguated).

*Read-only audit — zero nodes/files/commits modified during the audit itself. This report is the architectural baseline for the next major development phase.*
