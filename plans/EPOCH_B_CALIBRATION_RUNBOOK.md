# Epoch (b) — Empirical Calibration Runbook

**Status:** methodology + readiness gate only. **No `*_version` bump or value change has occurred.**
**Authority:** [[dev_graph/decisions/ADR - Empirical Calibration Methodology]] (ADR-012, draft).
**Owner repos:** producer = `C:\Code\Mr-Ripley` (Layer-2 Truth corpus); consumer/governance =
`C:\Code\el_nino` (Layer-3 chain + dev_graph).

This runbook is the operational companion to ADR-012. It captures (1) the read-only **corpus
sufficiency assessment** that decides whether calibration may run at all, and (2) the concrete
**recalibrate → validate → re-pin** procedure to follow *only* once a target's readiness gate passes.
It is the calibration sibling of [`EPOCH_B_CORPUS_RUNBOOK.md`](./EPOCH_B_CORPUS_RUNBOOK.md), which
governs corpus *accumulation* (the calendar-bound prerequisite).

> **The cardinal rule.** Do **not** calibrate a target whose gate has not passed. Fitting thresholds,
> weights, or a direction table to a tiny, low-diversity corpus is statistical malpractice that
> silently replaces auditable domain anchoring with noise. When in doubt, defer — the provisional
> values stand.

---

## 1. What can be calibrated, and on which version axis

Three calibration targets, **two** independent version axes. **Never cross them** (ADR-007 §Decision-4,
ADR-008 §7).

| Target | Lives in | Version axis | Fingerprint | Re-pin on bump |
|---|---|---|---|---|
| Regime **thresholds** + margin scales + required gate | `src/regime/regime_classifier/config.py` (`RegimeConfig`, `_DECISION_FIELDS`) | **`taxonomy_version`** | `RegimeConfig.decision_fingerprint()` | BENCH-001 `regime_bench.json` (+ BENCH-002, and BENCH-003/004 if a regime change cascades to direction/admission) |
| Gold **confidence weights** / floors | `src/gold/decision_builder/config.py` (`DecisionPolicyConfig`) | **`decision_policy_version`** | `DecisionPolicyConfig.decision_policy_fingerprint()` | BENCH-002 `gold_bench.json` |
| **Regime→direction table** | `src/gold/decision_builder/config.py` (`DEFAULT_DIRECTION_TABLE`) | **`decision_policy_version`** | `DecisionPolicyConfig.decision_policy_fingerprint()` | BENCH-002 `gold_bench.json` (+ BENCH-003/004 iff a direction change cascades) |

`classifier_version` and `classification_trace_version` are **not** calibration axes (engine /
explainability versions). A calibration bump is a **config amendment, never a rebuild**: no new
ontology object, no `canonical_id` change.

---

## 2. Current pinned baseline (as of 2026-06-17 — unchanged)

| Item | Value |
|---|---|
| `taxonomy_version` | `1.0.0` |
| `classifier_version` | `0.1.0` |
| regime `decision_fingerprint()` | `8ab0be8d506cbb243db68e7e522bf72f5d6327df80cb3bb7777c52fc3a821837` |
| `decision_policy_version` | `0.1.0` |
| gold `decision_policy_fingerprint()` | `be7e3192889ebe5deb100a9510fe2adc0fb676eb2eca199de3ffa1df9369a8a5` |
| Golden artifacts | `benchmarks/regime/artifacts/regime_bench.json`, `benchmarks/gold/artifacts/gold_bench.json` |

The gold fingerprint matches the value pinned in `gold_bench.json` (BENCH-002) — **no config drift**.

Reproduce:
```powershell
cd C:\Code\el_nino; $env:PYTHONPATH='C:\Code\el_nino\src'
& .\.venv\Scripts\python.exe -c "from regime.regime_classifier.config import DEFAULT_REGIME_CONFIG as R; from gold.decision_builder.config import DEFAULT_DECISION_POLICY_CONFIG as G; print(R.taxonomy_version, R.decision_fingerprint()); print(G.decision_policy_version, G.decision_policy_fingerprint())"
```

---

## 3. Step 1 — corpus sufficiency assessment (READ-ONLY; run before any calibration)

Enumerate every honestly-banked PIT snapshot in both sinks and run the real chain
(`consume → build_features → classify → build_decision`) over each. Report N, date span, regime
distribution, direction distribution, confidence range, and coverage gaps.

### 3.1 Verdict as of 2026-06-17

Truth DB (`C:\Code\Mr-Ripley\layer2_truth.db`, system of record) — **5 PASS snapshots**
(`engine gold-v3.3.0 / config 1.1.0`):

| # | snapshot_id8 | clock_ts | regime | direction | confidence | where it lives |
|---|---|---|---|---|---|---|
| 1 | `952cc83a` | 2026-05-01T22:00Z | RESTRICTIVE_RATES | AVOID | 0.39744 | committed el_nino fixture (`tests/snapshot/fixtures/latest_snapshot_pass.json`) |
| 2 | `05c8369d` | 2026-06-11T22:00Z | RESTRICTIVE_RATES | AVOID | 0.57120 | Mr-Ripley runtime archive |
| 3 | `7d39aa8f` | 2026-06-13T22:00Z | RESTRICTIVE_RATES | AVOID | 0.53856 | Mr-Ripley runtime archive |
| 4 | `e0e44caf` | 2026-06-14T22:00Z | RESTRICTIVE_RATES | AVOID | 0.52734 | Mr-Ripley runtime archive |
| 5 | `c1fe5a02` | 2026-06-15T22:00Z | RESTRICTIVE_RATES | AVOID | 0.56682 | Mr-Ripley runtime archive |

- **N = 5** (1 committed el_nino consumable; 4 producer-only). Forward corpus = **4 trading days**
  (06-11/13/14/15; 06-12 and 06-16 fail-closed; 06-17 not yet run). 2026-05-01 is a backfill anchor.
- **Regime distribution `{RESTRICTIVE_RATES: 5}` — 1/12 regimes.** Never seen: LIQUIDITY_STRESS,
  RISK_OFF, VOLATILE, REFLATION, DISINFLATION, CURVE_INVERSION, STRONG_USD, RISK_ON, LOW_VOL, NEUTRAL,
  INDETERMINATE.
- **Direction distribution `{AVOID: 5}` — 1/4 directions.** Never seen: **LONG, FLAT, WATCH**.
- **Confidence** 0.397–0.571 (mean 0.520); all from `R04_restrictive_rates`; only competitor ever near
  is `R08_strong_usd`. **Zero** staleness / revision / coverage penalty variation across all five.

**Monochromatic corpus ⇒ all three readiness gates FAIL (see §4). No target is calibrated.**

**Re-check 2026-06-18 (no change).** Re-ran the MOD-009 labeler
(`run_forward_return_labels.py --include-external`). The corpus is **unchanged** since 2026-06-17 — no new
day banked after 2026-06-15 (06-16/17/18 not present in `runtime/snapshots`): external N=5, committed N=1,
regimes `{RESTRICTIVE_RATES: 5}`, directions `{AVOID: 5}`, **0 realized labels** (all pending /
no_exit_in_tolerance). The committed golden `benchmarks/calibration/artifacts/forward_return_labels.json`
is **byte-identical** (re-run produced no diff). **Verdict stands: DEFER all three — no `*_version` bump,
no value, no direction-table change.** (Note: the AVOID-objective + FLAT_BAND definitions remain
unsettled in ADR-012 — a further precondition on any future G3 direction-table bump even once G3 data
exists.)

### 3.2 Reproduce the assessment

Run the read-only harness below over both sinks. It writes nothing.

```python
# epoch-(b) corpus sufficiency assessment — READ-ONLY. Run from C:\Code\el_nino with
#   $env:PYTHONPATH='C:\Code\el_nino\src'; .\.venv\Scripts\python.exe this_file.py
import sqlite3
from collections import Counter
from pathlib import Path
from features.feature_builder import build_features
from gold.decision_builder import SnapshotGuards, build_decision
from regime.regime_classifier import classify
from snapshot.snapshot_consumer import consume

TRUTH_DB = Path(r"C:\Code\Mr-Ripley\layer2_truth.db")
ARCHIVES = Path(r"C:\Code\Mr-Ripley\runtime\snapshots")
FIXTURE  = Path(r"C:\Code\el_nino\tests\snapshot\fixtures\latest_snapshot_pass.json")

con = sqlite3.connect(str(TRUTH_DB)); con.row_factory = sqlite3.Row
banked = list(con.execute("SELECT snapshot_id, clock_ts, verdict FROM snapshots ORDER BY clock_ts"))
con.close()
print("banked PASS snapshots:", sum(r["verdict"] == "PASS" for r in banked))

paths = [FIXTURE, *sorted(ARCHIVES.glob("snapshot_*.json"))]
regimes, directions, confs = Counter(), Counter(), []
for p in paths:
    snap = consume(p)
    if snap is None:                      # fail-closed snapshots are skipped
        print(p.name, "NOT CONSUMABLE"); continue
    fv = build_features(snap); rc = classify(fv)
    sg = SnapshotGuards(snap.guards.data_ok, snap.guards.freshness_ok, snap.guards.cooldown_ok)
    pkt = build_decision(fv, rc, snapshot_guards=sg, as_of=snap.clock_ts)
    regimes[rc.regime.value] += 1; directions[pkt.direction.value] += 1; confs.append(pkt.confidence)
    print(p.name, rc.regime.value, pkt.direction.value, round(pkt.confidence, 5))

print("N=", sum(regimes.values()), "regimes=", dict(regimes), "directions=", dict(directions))
print("regimes_unseen=", [r for r in
      "LIQUIDITY_STRESS RISK_OFF VOLATILE RESTRICTIVE_RATES REFLATION DISINFLATION CURVE_INVERSION "
      "STRONG_USD RISK_ON LOW_VOL NEUTRAL INDETERMINATE".split() if r not in regimes])
if confs: print("confidence", min(confs), max(confs), sum(confs)/len(confs))
```

> The truth DB stores normalized `snapshots`/`snapshot_values` rows, not consumable JSON. The runnable
> consumables are the el_nino fixture (2026-05-01) + the Mr-Ripley `runtime/snapshots/*.json` archives
> (forward days). Every banked PASS snapshot has a matching runnable JSON today, so the assessment
> covers the whole corpus.

---

## 4. Step 2 — the empirical-readiness gate (authority: ADR-012 §3)

No target is recalibrated until **its** gate passes. The gates differ because the targets have
different data appetites. Numbers are floors, anchored on KA-010 (5 days ⇒ "not significant") and
walk-forward discipline; revisable under governance.

| Gate | Target | Must hold before calibrating |
|---|---|---|
| **G0** | any | `N ≥ 60` distinct, forward-accumulated, PASS PIT snapshots (≈ a quarter). **Today N=5 → FAIL.** |
| **G1** | regime thresholds (`taxonomy_version`) | per moved boundary: both bordering regimes each ≥ 20 snapshots **with real boundary-straddling obs**; ≥ 3 distinct regimes overall; temporally-disjoint walk-forward validation. **Today 1/12 regimes → FAIL.** |
| **G2** | confidence weights (`decision_policy_version`) | each penalty dimension shows **real variation** across ≥ 30 snapshots / ≥ 3 regimes (ambiguity, fragility, staleness, revision, coverage all exercised); ordinal-monotonicity validation on a holdout; **no** PnL/outcome fit, **no** SCHEMA-005 bleed. **Today zero staleness/revision/coverage variation → FAIL.** |
| **G3** | regime→direction table (`decision_policy_version`) | per revised cell: that regime ≥ 20 snapshots **and** a forward gold-return evaluation harness shows the revised cell beats the provisional one out-of-sample (KA-010: ≥3 metrics improved, no regressions, ≥12% avg rel. improvement). The harness now exists — the **Gold Forward-Return Labeler** (MOD-009 / BENCH-005, `benchmarks/calibration/run_forward_return_labels.py`, built 2026-06-17). **Today 11/12 cells unexercised; the labeler emits all-pending/no-exit labels (0 realized) → FAIL.** |

A gate passing for one target does **not** authorize another. A threshold/regime/cell that fails its
gate keeps its domain-anchored default.

---

## 5. Step 3 — recalibrate → validate → re-pin (ONLY when a gate passes)

Do this **per target whose gate passes**, on the **single** correct version axis. Each is
**human-review-required**; **HARD PAUSE for operator review before any `*_version` bump or value
change.**

1. **Derive deterministically.** Compute candidate values from the corpus by a documented, rule-based
   rule (no learned/ML/online/history-dependent logic — ADR-005/007). Examples: boundary at an
   economically-motivated separation of the observed feature distribution (thresholds); penalty
   magnitude from observed frequency/spread of each structural condition (weights); per-regime
   out-of-sample directional accuracy (direction table).
2. **Walk-forward validate.** Fit on an earlier window; validate on a strictly later, held-out window.
   Report in-sample **and** out-of-sample behavior. Reject if it does not generalize.
3. **Edit the one config + bump the one version.** Change values in `RegimeConfig` **xor**
   `DecisionPolicyConfig`; increment the matching `*_version`; the fingerprint changes automatically.
   Never touch the other axis.
4. **Re-pin goldens under the NEW version, retain the old ones.**
   - `taxonomy_version` bump → regenerate `benchmarks/regime/artifacts/regime_bench.json` (BENCH-001);
     re-run `benchmarks/gold/artifacts/gold_bench.json` (BENCH-002) and, if the regime change cascades
     into direction/admission/fills, `paper_runtime_bench.json` (BENCH-003) /
     `benchmarks/execution/artifacts/execution_bench.json` (BENCH-004).
   - `decision_policy_version` bump → regenerate `gold_bench.json` (BENCH-002); re-pin BENCH-003/004
     **iff** a direction change cascades.
   - Keep the prior golden for the prior version. Goldens are version-labelled, append-only.
   ```powershell
   cd C:\Code\el_nino; $env:PYTHONPATH='C:\Code\el_nino\src'
   & .\.venv\Scripts\python.exe benchmarks\regime\run_regime_bench.py   # taxonomy bump
   & .\.venv\Scripts\python.exe benchmarks\gold\run_gold_bench.py       # policy bump (or cascade)
   ```
5. **Assert determinism both ways.** Byte-identical replay at the **new** version; **unchanged** replay
   at every **prior** version. Run the pinned suite:
   ```powershell
   & .\.venv\Scripts\python.exe -m pytest tests/ -q
   ```
6. **Writeback (dev_graph).** Bump `updated` + `implementation_status`/`evidence` on the affected config
   file nodes (FILE-013 / FILE-016) and benchmark nodes (BENCH-001/002[/003/004]); record the bump in
   `dev_graph/log.md` per the Config Evolution procedure; update this runbook's §2 baseline; update
   ADR-012 (or author a successor ADR if the *method* changes); run the 11 lint checks on touched
   nodes; re-sync Neo4j (`python dev_graph/sync_to_neo4j.py --clear`).

---

## 6. PIT honesty & invariants (do not violate)

- **Calibrate only on honestly-banked, forward-accumulated snapshots.** Never back-fabricate history;
  data fetched now for a past date is not what was known then (`EPOCH_B_CORPUS_RUNBOOK.md` §6). The
  ~40 producer-outage days (2026-05-02…06-10) are **not** reconstructed.
- **Old versions stay byte-reproducible** — the version is part of the replay key (ADR-006 §3); a bump
  adds a new version, never edits an old one's meaning.
- **Rule-based / deterministic only** — no learned/ML/online/history-dependent logic at runtime or in
  the shipped derivation (ADR-005, ADR-007).
- **Never cross version axes; never change a `canonical_id`; never modify `wiki/**` or `raw/**`**
  (CON-001).
- **Confidence is an ordinal trust score, not a probability** — no outcome/PnL fit; no treasury
  SCHEMA-005 bleed (ADR-008 §1/§6, ADR-004 separation).

---

## 7. Current status

| Target | Gate | Verdict 2026-06-17 |
|---|---|---|
| Regime thresholds (`taxonomy_version`) | G0 + G1 | **DEFER** — N=5, 1/12 regimes. No bump. |
| Confidence weights (`decision_policy_version`) | G0 + G2 | **DEFER** — no penalty-dimension variation. No bump. |
| Regime→direction table (`decision_policy_version`) | G0 + G3 | **DEFER** — 11/12 cells unexercised. The forward-return labeling harness (MOD-009/BENCH-005) is **built** (2026-06-17); it emits 0 realized labels today (corpus monochromatic + clustered). No bump. |

**Re-checked 2026-06-18 — unchanged (DEFER all three; committed golden byte-identical; corpus still N=5
monochromatic, no day banked after 2026-06-15).**

Re-run §3 as the corpus grows (watch the regime distribution diversify away from RESTRICTIVE_RATES).
The first gate likely to come into reach is G0; G1/G2/G3 additionally need regime/penalty diversity the
macro tape must actually supply.
