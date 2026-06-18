# Claude Code prompt — forward-return labeling harness (epoch (b), ADR-012 gate G3 prerequisite)

Paste the block below into a fresh Claude Code session rooted in the `el_nino` repo.

---

Build the **forward-return labeling harness** — the deterministic evaluation tool that labels each banked decision with the gold return realized *after* it, producing the per-regime outcome data that **ADR-012 gate G3** (regime→direction table calibration) requires. G3 is the hardest calibration gate precisely because no such harness exists yet; this is the highest-leverage thing buildable today, and it's tractable independent of corpus size. **This is a measurement tool only: it changes no decision logic, no config, and no `*_version`; it never calibrates the direction table (G3 stays deferred — the corpus is still monochromatic). Its job is to produce the labels G3 will eventually consume.** Pause for my review when built and validated.

## The one non-negotiable: look-ahead containment

Forward returns are computed from data **after** the decision's timestamp — that is legitimate for an **outcome label**, but it is poison if it ever touches the decision path. Hard wall: this harness is **strictly downstream** of the decision chain. It reads the immutable corpus and the already-produced decisions and emits labels for *analysis*. It MUST NOT import into, modify, or feed back into `consume → build_features → classify → build_decision → evaluate → execute`. No future price, return, or label may influence any decision. Build the chain read-only; if labeling would require reaching into the decision path, stop and flag it.

## Step 0 — read governance and the data

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, the §7.5 file-node threshold.
2. `decisions/ADR - Empirical Calibration Methodology.md` (ADR-012) — especially **G3** (the gate this serves), the **PIT / no-back-fabrication** rule (§5), and the walk-forward / out-of-sample discipline. This harness is the implementation of G3's stated prerequisite; ADR-012 governs it. No new ADR is needed.
3. `EPOCH_B_CALIBRATION_RUNBOOK.md` + the 2026-06-11 `log.md` epoch-(b) entry + `EPOCH_B_CORPUS_RUNBOOK.md` — the corpus sinks (`layer2_truth.db` `snapshots`/`snapshot_values`; `Mr-Ripley/runtime/snapshots/snapshot_*.json`; the one committed el_nino consumable fixture) and the daily-EOD accumulation. The producer is Mr-Ripley; el_nino consumes.
4. **The decision chain + price series (read-only, do not modify):** `src/snapshot/snapshot_consumer/` (`consume`), `src/features/feature_builder/` (the `gold_price` feature — the series the gold thesis is about), `src/regime/regime_classifier/` (`classify` → regime + matched_rule), `src/gold/decision_builder/` (`build_decision` → direction; the regime→direction table in `config.py` — read-only). Use the snapshot's `gold_price` as the return series (it is what the regime thesis predicts; GLD-ETF returns are a possible future alternative — leave the price series pluggable).
5. **The natural home + idiom:** `systems/Evaluation Loop.md` (SYS-005) + `capabilities/Performance Scoring.md` (CAP-013, `not-started`) — assess whether this harness is the first realization of CAP-013, or is better placed as a standalone calibration tool under ADR-012. Pick one, justify it, and do **not** create a duplicate concept (CON-003). Mirror the benchmark-harness shape for determinism: deterministic harness → committed golden artifact → artifact-in-sync test (`run_*_bench.py` / `test_*_bench`, BENCH-001/002/003).

## Step 1 — build the harness (deterministic, read-only over the corpus)

- **Enumerate** the real banked PIT snapshots (both sinks), and for each derive `(source_snapshot_id, clock_ts, gold_price, regime, matched_rule, direction)` by running the existing chain — exactly as the ADR-012 corpus assessment did.
- **Define holding horizons** (the key design decision — document it): medium-term horizons suited to a macro/regime thesis (e.g. 5 / 20 / 60 trading-day-equivalents). The corpus is **non-contiguous** (fail-closed days, gaps), so specify the exit-selection rule explicitly — nearest banked snapshot at or after `clock_ts + H`, with a stated max-gap tolerance — and mark a label **`pending`** (not zero, not dropped) when the horizon extends beyond the latest banked snapshot. Gap handling is the main correctness risk; make it explicit and tested.
- **Label** each `(snapshot × horizon)`: entry `gold_price`, exit `gold_price` + `exit_snapshot_id`, realized forward return `(exit − entry)/entry`, and a **direction-correctness** field (did `LONG` capture an up-move, did `AVOID`/`FLAT` correctly dodge a down-move, etc.), plus the `realized | pending` status.
- **Aggregate per regime** (the G3 input): per regime × horizon, the count, mean/median forward return, hit-rate, and per-direction correctness. This is the data G3 consumes — the harness **reports** it; it does **not** change the direction table.
- **Determinism + PIT:** pure computation over the immutable, content-addressed corpus; sorted-key canonical JSON; no clock/network/randomness; only honestly-banked snapshots, never back-fabricated prices.

## Step 2 — validate (the corpus is monochromatic, so prove correctness synthetically)

- **Synthetic price/regime series** proving the return math, the horizon/gap/nearest-exit logic, the `pending` marking, and per-direction correctness across **all four directions and multiple regimes** (up-move ⇒ LONG correct / AVOID wrong; down-move ⇒ AVOID correct / LONG wrong; etc.). The real corpus cannot exercise any of this (it is 1/12 regimes, 1/4 directions, no fill), so correctness must be established synthetically.
- **Real-corpus run:** show it produces the correct sparse labels + `pending` markers today (≈ all RESTRICTIVE_RATES / AVOID, longer horizons pending) — demonstrating it is ready to accumulate labels as the corpus grows, not that it has enough yet.
- **Committed golden artifact + artifact-in-sync test** (BENCH idiom); `mypy --strict` + `ruff` clean on new files; full prior suite green.

## Step 3 — writeback

- Author the chosen node(s) (re-derive next-free ids from `index.md`): if it realizes **CAP-013 Performance Scoring**, create the module (next-free MOD) + file/test nodes and bump CAP-013 `not-started → in-progress`; otherwise a calibration-tool file/test (+ optional `benchmark_result`) node set. Either way: `Justified By → [[ADR - Empirical Calibration Methodology]]`; link the labeled-output artifact.
- **No config / `*_version` / direction-table change** — record explicitly that this is the G3 *prerequisite* (the measurement), and that G3 itself stays deferred until per-regime coverage accrues (ADR-012).
- `index.md` (deltas) + `log.md` epoch-(b) entry (what the harness measures, the horizon definition, the synthetic-validation result, today's sparse real output) + 11 lint checks on touched nodes + **Neo4j re-sync** (`python dev_graph/sync_to_neo4j.py --clear`).

## Constraints

- **Strictly downstream / read-only** w.r.t. the decision chain and config — no decision-path edit, no `*_version` bump, no direction-table change.
- **Rule-based / deterministic only** — no learned/ML logic (ADR-005/007); the harness measures, it does not predict.
- **PIT honesty / look-ahead containment** as above — labels never reach a decision.
- MUST NOT modify `wiki/**` or `raw/**` (CON-001); canonical_id immutable; re-derive ids from `index.md`.
- When done, summarize the horizon design, the synthetic-validation evidence, today's real-corpus label output, and the chosen node placement, and **stop for my review**.
