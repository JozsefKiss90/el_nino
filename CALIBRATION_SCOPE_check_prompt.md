# Claude Code prompt — diagnose the `calibration_readiness` scope (does the gate count the accumulating corpus?)

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

**Investigate, don't fix yet.** The ops console shows `CALIBRATION: DEFER (N=1)` "committed scope" while the producer is banking a fresh snapshot daily (`producer-freshness: ok, latest=snapshot_2026-06-25`). That mismatch suggests the calibration **readiness gate** may be counting only the committed el_niño snapshot(s) and **not** the accumulating Mr-Ripley corpus — which would mean the gate can never approach `G0 ≥ 60` from daily accumulation, quietly invalidating "let the corpus mature." Diagnose exactly what scope the gate reads, report the finding + options, and **PAUSE** — the scope policy is an ADR-012 methodology decision for the operator, not a mechanical edit.

## Step 1 — trace the scope (read-only)
Read and follow the data path that produces the console's calibration numbers:
- `ops/core.py` → `calibration_readiness(...)` (what it calls, and the `N` / G1 / G2 / G3 / "realized=0 of 3" it returns).
- `benchmarks/calibration/run_forward_return_labels.py` (MOD-009) — note `_COMMITTED_INPUTS` (the committed fixtures that dedup to `952cc83a` → N=1), `_EXTERNAL_ARCHIVE_DIR` (the Mr-Ripley `runtime/snapshots` archives), and the `--include-external` / committed-vs-external distinction; and which scope `build_report()` uses by default.
- The `producer-freshness` reader in `ops/core.py` (it already locates the Mr-Ripley archive dir and found `snapshot_2026-06-25` — so the console *can* see the growing corpus; the question is whether the *gate* counts it).
- `decisions/ADR - Empirical Calibration Methodology.md` (ADR-012) + `EPOCH_B_CORPUS_RUNBOOK.md` / `EPOCH_B_CALIBRATION_RUNBOOK.md` — the documented intent for committed-vs-external scope and why the committed scope exists (reproducibility / PIT honesty / the committed golden BENCH-005).

Determine precisely: (a) which snapshot set the gate's `N` and coverage are computed over; (b) why `N=1` today; (c) where the daily-banked snapshots actually live and whether the gate reads them; (d) the "realized=0 of 3" — what 3, and over which scope.

## Step 2 — report the finding + the scope tension, then PAUSE
State plainly whether the gate is **committed-scope-only** (and therefore static / won't move with daily accumulation) or already counts the full corpus. If committed-only, lay out the genuine tension and the options — and stop for the operator to choose:

- The **committed scope** (el_niño fixtures, N=1) is reproducible-in-CI and is correctly what the **golden benchmark (BENCH-005)** uses — that should *not* change (determinism).
- The **readiness gate** is an *operational* question ("do we have enough real data yet?"), which is inherently about the **growing** corpus — so it arguably *should* count the accumulating Mr-Ripley archives, even though they're external.

Options to present (recommend, but let the operator pick — it changes what the gate *means*):
1. **Gate reads the full accumulating corpus** (the archive dir `producer-freshness` already reads), while the golden/benchmark stays committed-scope. *(Likely right: the gate reflects real accumulation; the benchmark stays reproducible.)*
2. **Promote daily forward snapshots into the committed/reproducible scope** so they're both counted and CI-reproducible (heavier — repo growth).
3. **Leave committed-only** and document that the gate is intentionally static — in which case "wait for the corpus" needs a *different* trigger, and you should say so.

## Step 3 — implement ONLY the chosen option (after the operator decides)
If the operator picks (1) (or 2): make the **readiness gate** count the chosen corpus, **fail-closed and PIT-honest** (only honestly-banked, content-addressed snapshots; never back-fabricate), and **preserve the committed-scope reproducibility of the golden** (do not move BENCH-005 / the committed artifact — bifurcate: gate = real corpus, golden = committed). Crucially, **change only WHAT is counted, not the anti-overfitting thresholds** — the gate must still DEFER until `N ≥ 60` + coverage; this fix lets the gate *move with real data*, it does not loosen it. Update ADR-012 + the runbook to document the gate's scope explicitly (gate vs golden), add tests for the new counting (mocked archive dir; fail-closed on missing), and do the dev_graph writeback (ADR-012 / OBS-002 / MOD-009 nodes as touched, index/log, lint, Neo4j re-sync) if nodes change.

## Constraints
- Step 1–2 are **read-only + report + PAUSE**; no fix until the operator chooses the scope policy.
- Never force calibration or change the DEFER thresholds — only what the gate counts.
- Preserve the golden benchmark's committed-scope reproducibility and determinism; PIT honesty throughout; no `wiki/**`/`raw/**` mutation.
- When done with Step 1–2, summarize: the exact scope the gate reads, why N=1, where the daily corpus lives, and the option recommendation — then stop.
