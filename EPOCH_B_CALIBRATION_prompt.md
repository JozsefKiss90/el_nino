# Claude Code prompt — epoch (b): empirical recalibration

Paste the block below into a fresh Claude Code session rooted in the `el_nino` repo.

---

Run **epoch (b) — empirical recalibration**: convert the provisional, **domain-anchored** regime thresholds, confidence weights, and regime→direction table into **empirically calibrated** ones, driven by the real snapshot corpus that has been accumulating since 2026-06-11. This is a **versioned config bump, never a rebuild** (no canonical_id changes, no new ontology objects beyond a governing ADR). **The first and most important task is to decide whether the corpus is large enough to calibrate at all — if it is not, you must NOT bump any version or change any value; you produce the methodology + readiness gate and stop.** Do not overfit a handful of snapshots. Pause for my review before any `*_version` bump or value change.

## Step 0 — read governance and the version-axis rules

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, the Schema/Config Evolution procedures.
2. **The version-axis authorities (do not cross them):**
   - `decisions/ADR - Deterministic Regime Taxonomy.md` (ADR-007) — `RegimeConfig` thresholds are versioned by **`taxonomy_version`**.
   - `decisions/ADR - Gold Decision Confidence Semantics.md` (ADR-008) — the confidence form/weights **and** the regime→direction table are governed by **`decision_policy_version`**; §7/§9 explicitly call empirical recalibration "an expected v1 amendment" and say **bump `decision_policy_version`, never `taxonomy_version`** for confidence/direction.
   - `decisions/ADR - Gold DecisionPacket v0 Planning.md` (ADR-006 §3) + `ADR - Feature Layer Contract.md` (ADR-005) — the replay invariant: `snapshot_id + version tuple ⇒ identical output`. A bump changes outputs; **old versions must stay reproducible** (the version is part of the replay key).
3. **The epoch-(b) operational context:** the 2026-06-11 `log.md` entry ("Epoch (b) operationalized") + `EPOCH_B_CORPUS_RUNBOOK.md` — the corpus sinks (`layer2_truth.db` `snapshots`/`snapshot_values`; `Mr-Ripley/runtime/snapshots/snapshot_*.json`), the daily EOD schedule, and the DTWEXBGS staleness watch.
4. **Methodology sources (read-only):** `knowledge_assets/Paper Trading Validation.md` (KA-010 — quantitative criteria), `knowledge_assets/Regime Taxonomy.md` (KA-011), and the wiki `Walk-Forward Optimization` page (out-of-sample discipline). Calibration stays **rule-based and deterministic** — no learned/ML models (ADR-005/007 forbid history-dependent/learned logic).
5. **The config + evidence under calibration:** `src/regime/regime_classifier/config.py` (`RegimeConfig` thresholds + `taxonomy_version` + fingerprint), `src/gold/decision_builder/config.py` (`DecisionPolicyConfig` — confidence weights + regime→direction table + `decision_policy_version` + fingerprint), `src/gold/decision_builder/policy.py` (`trust_score`), and the golden benchmarks `benchmarks/regime/` (BENCH-001) + `benchmarks/.../gold` (BENCH-002) that will need re-pinning **iff** a version bumps.

## Step 1 — corpus sufficiency assessment (READ-ONLY; change nothing)

Enumerate the **real, honestly-banked PIT snapshots** (both corpus sinks; the producer is Mr-Ripley, el_nino consumes). For each, run the existing chain (`consume → build_features → classify → build_decision`) and report:

- **N** (count) and the **date span**; how many are committed el_nino consumables vs. truth-DB-only.
- The **regime distribution** (which of the 12 regimes actually appear), the **direction distribution** (LONG/FLAT/AVOID/WATCH), and the **confidence range**.
- **Coverage gaps:** which regimes / directions have **zero or near-zero** observations (e.g., today every banked snapshot is RESTRICTIVE_RATES → AVOID — so a fill has never occurred).

Then state the **empirical-readiness verdict** honestly, per target — the three have very different data appetites:
1. **regime thresholds** (`taxonomy_version`),
2. **confidence weights** (`decision_policy_version`),
3. **regime→direction table** (`decision_policy_version`).

The corpus only began accumulating 2026-06-11, so **expect a small N that is insufficient for credible calibration.** If a target lacks the N/coverage to calibrate without overfitting noise, say so plainly and **do not calibrate it.** Calibrating thresholds/weights from a few same-regime snapshots would be statistical malpractice — the correct output in that case is the methodology + the gate (Step 2), not a bump.

## Step 2 — author the calibration governance (always valid, regardless of N)

Author **ADR-012 — Empirical Calibration Methodology** (`decisions/ADR - Empirical Calibration Methodology.md`, re-derive the next-free id from index.md; governance/boundary record mirroring ADR-006/009 style; `status: draft` until accepted). It must record:

- **Version-axis mapping:** regime thresholds → `taxonomy_version` (ADR-007); confidence weights + regime→direction table → `decision_policy_version` (ADR-008); never cross them; canonical_ids unchanged (a bump is a config amendment, not a rebuild).
- **The empirical-readiness gate:** the explicit minimum **N + per-regime/per-direction coverage + out-of-sample holdout** required before each target may be recalibrated (quantify it; cite KA-010). Until the gate passes for a target, its provisional domain-anchored values stand.
- **The methodology:** walk-forward / out-of-sample validation, no in-sample overfit, how thresholds/weights are derived from the corpus, how the direction table is validated; deterministic and rule-based only (no ML).
- **Determinism / replay preservation:** old versions stay byte-reproducible (version in the replay key); on any bump, re-pin the affected golden artifacts (BENCH-001/002, and BENCH-003/004 if a direction change cascades) **under the new version**, retaining the old goldens; PIT honesty (calibrate only on honestly-banked snapshots — never back-fabricate).
- **Non-Goals:** learned/ML/ history-dependent models; live-money trading; changing schemas or canonical_ids; recalibrating a target whose gate has not passed.

Also write/refresh a non-dev_graph **calibration runbook** (`EPOCH_B_CALIBRATION_RUNBOOK.md` at repo root, in the `EPOCH_B_CORPUS_RUNBOOK.md` idiom) capturing the Step-1 corpus assessment and the concrete recalibration + validation + re-pin procedure.

## Step 3 — execute calibration ONLY IF the Step-1 gate passes (else defer)

For **each** target whose readiness gate passes (only those):

- Derive the new `RegimeConfig` thresholds and/or `DecisionPolicyConfig` weights/direction-table values from the corpus via the Step-2 walk-forward method (hold out a validation slice; report in-sample vs out-of-sample behavior).
- **Bump the correct version** (`taxonomy_version` and/or `decision_policy_version`) and update the fingerprint; **re-run and re-pin** the affected golden benchmark artifacts under the new version; assert determinism still holds (byte-identical replay at the new version) and that **old-version replay is unchanged**.
- **HARD PAUSE for my review before committing any `*_version` bump or value change.**

If no target's gate passes (the likely outcome today), make **no** value or version change: ADR-012 + the runbook + the corpus assessment are the deliverable, and the bumps wait for the corpus to mature.

## Step 4 — writeback

- ADR-012 node (+ the runbook). If a version bumped: update the affected config file nodes (FILE-013 regime config / FILE-016 gold config), record the bump in `log.md` per the Config Evolution procedure, and update the affected benchmark nodes (BENCH-001/002[/003/004]) with the re-pinned artifacts.
- `index.md` (decision_record 11→12; any other deltas) + `log.md` epoch-(b) calibration entry (corpus assessment + the readiness verdict + what was/ wasn't bumped + why).
- Run the 11 lint checks on touched nodes; **re-sync Neo4j** (`python dev_graph/sync_to_neo4j.py --clear`).

## Constraints

- A bump is a **config-version amendment**, never a canonical_id change or a rebuild; preserve replay determinism for all prior versions.
- **Rule-based / deterministic only** — no learned/ML/history-dependent logic (ADR-005/007).
- MUST NOT modify `wiki/**` or `raw/**` (CON-001); re-derive ids from index.md.
- **Never calibrate a target whose readiness gate has not passed** — overfitting a tiny corpus is the primary failure mode this epoch must avoid.
- When done, summarize the corpus assessment, the readiness verdict per target, and exactly what was (or deliberately was not) changed, and **stop for my review**.
