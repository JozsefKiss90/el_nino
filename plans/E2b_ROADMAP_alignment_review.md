# Adversarial alignment review — "El Niño · Epoch E2b: Alpaca PAPER Execution Adapter"

Reviewer: project alignment pass against the current `el_nino` state (dev_graph ADR-001..013, the built execution/orchestration/ops code on branch `JARVIS`).
Date: 2026-06-18. Roadmap reviewed: `el nino alpaca paper E2b roadmap.md` (Hungarian; 8 components + A/B verification package).

---

## 1. Summary of findings

**Alignment status: MISALIGNED — usable as a spec, but it must be renumbered, re-cast as a delta, and corrected in two places before it can drive work.**

The roadmap's *constitution* (long-or-flat, paper-only, fail-closed, snapshot-driven determinism, immutable fill records keyed on `snapshot_id`, no margin/short, "La Niña in our evaluator, not broker-side conditional orders") is fully aligned with the project. Several of its design calls (market+day "queue-to-next-open" instead of OPG, cash-cap sizing, GLD-vs-GLD slippage, direction-accuracy-not-slippage as the performance gate) are correct and some are improvements over what exists.

But it is misaligned with the current project in three serious ways:

1. **ADR-number collision (critical).** The roadmap names its governing record **"ADR-010"**. In the actual project **ADR-010 is "JARVIS GraphRAG Integration"** (active). The Alpaca paper adapter is already governed by **ADR-011 "Execution Layer Planning"**, which is **Accepted/active with gate (f) — the Alpaca adapter — already CLOSED**. The roadmap never mentions ADR-011/012/013 and was evidently written from an earlier, isolated snapshot of the project.
2. **Much of the plan is already built (greenfield framing is wrong).** The governing ADR, the env-isolation guard, the execution adapter, the execution record + portfolio state, and the observation/performance gate all already exist. The roadmap reads as net-new work; it must be re-cast as a **delta against the built v0**.
3. **Two proposals would regress or duplicate the codebase.** The Step-7 `"paper-api" not in base_url` substring guard is the *exact* vulnerability the project already fixed (it now uses parsed-hostname equality); adopting it would reintroduce a credential-exfil bypass. The Step-3/Step-6 SQLite `fill_record`/`scorecard` tables duplicate the existing append-only-JSON `SCHEMA-014`/`SCHEMA-015` artefacts and the `MOD-009` labeler — a "second source of truth" that ADR-009/011/013 forbid.

Where the roadmap earns its keep: it specifies a **far more complete adapter than the dormant v0 stub** that's actually in the repo, and it surfaces **real latent defects/gaps** — most importantly a GLD-vs-gold-spot price/slippage bug in the current code and the question of whether the snapshot even carries a GLD price (A8). Those are its genuine value.

Net recommendation: keep the roadmap, but reissue it as **"ADR-014 (or an ADR-011 amendment): Operable Alpaca Paper Execution Adapter v1"**, scoped as the delta from the built v0, with the two regressions removed.

---

## 2. Detailed review

### 2.1 Constitution & assumptions (roadmap "Irányadó alkotmány" / "Feltételezések")
- **Current vs roadmap:** Aligned. Long-or-flat-only, paper-only, fail-closed, deterministic replay, immutable snapshot-keyed records, no margin/short all match ADR-011 §3, ADR-009, KA-010, PRED-005.
- **Issue:** The cash-vs-margin assumption (paper accounts default to ~4x margin) is a **real consideration the current code does not handle at all** — the built `AlpacaPaperAdapter` submits a market buy with no `available_cash` check and no account-type awareness. Legitimately new.
- **Recommended action:** Keep the constitution as-is. Promote the cash-cap from "assumption" to a concrete adapter requirement (it does not exist yet).

### 2.2 Step 1 — "write & accept ADR-010"
- **Current vs roadmap:** The governing ADR already exists as **ADR-011 (Execution Layer Planning)**, Accepted, with the six creation gates (a–f) closed; gate (f) is specifically the Alpaca adapter boundary. ADR-010 is taken (JARVIS).
- **Issue (critical):** Number collision + redundant "write the ADR" step. Following the roadmap literally would create a second ADR-010 and re-decide settled questions.
- **Recommended action:** Renumber to **ADR-014** (next free; ADR-001..013 exist) *or* fold as an **amendment to ADR-011**. Replace "write ADR" with "amend ADR-011 §7(f) / author ADR-014 referencing ADR-011, ADR-012, ADR-013." Import ADR-011's already-closed decisions instead of restating them.

### 2.3 Step 2 — Execution Adapter (reconcile-then-act, deterministic `client_order_id`)
- **Current vs roadmap:** A `AlpacaPaperAdapter` (`src/execution/alpaca_adapter.py`, FILE-038) exists behind the `INT-011` port, but it is a **one-shot stub**: `fill()` submits a single market BUY, fills only an approved LONG, and relies on the runtime ledger + portfolio once-ever idempotency. It does **not** reconcile (`GET /v2/positions`), has **no FLAT→sell-to-zero path**, **no deterministic `client_order_id`**, and **no Alpaca-side 422 dedup**.
- **Issues:** (a) The roadmap's reconcile-then-act / target-delta / SELL / `client_order_id`-422 model is genuinely missing and is the right design — but it does **not fit behind the current port**, whose contract is `fill(instrument, direction, size, instrument_price, fill_model) -> Fill` (the pure `execute()` core owns portfolio/record logic). (b) `client_order_id` idempotency is stronger than the current ledger-only dedup against broker-side duplicates.
- **Recommended action:** Re-scope Step 2 as **adapter v1 over the existing `INT-011` port** — state explicitly that it either extends `INT-011` (a versioned interface change) or adds a reconcile/SELL capability at the runtime/orchestrator layer, and reconcile the `client_order_id` dedup *with* (not instead of) the existing `source_snapshot_id` once-ever guard.

### 2.4 Step 3 — Fill-record persistence (SQLite `fill_record`)
- **Current vs roadmap:** Execution outcomes are already persisted as **`SCHEMA-014` ExecutionRecord** (frozen dataclass, `to_dict`, byte-stable) carried on the **`SCHEMA-015` PortfolioState** append-only `executions` history (canonical JSON, keyed by `source_snapshot_id`, `INSERT OR IGNORE`-equivalent once-ever). There is **no SQLite execution store**.
- **Issue (duplication / second source of truth):** The proposed `fill_record` SQLite table competes with `SCHEMA-014`/`SCHEMA-015`. Two execution stores violate ADR-009 §2 (wrap-not-enrich), ADR-011, and ADR-013 §11 (no second source of truth).
- **Recommended action:** Drop the new table. Map every `fill_record` column onto `SCHEMA-014`/`SCHEMA-015` and add only the **missing fields** there (e.g. `client_order_id`, `alpaca_order_id`, `exec_ref_gld_price`, `EXECUTION_UNCERTAIN`/`QUEUED` statuses, `raw_payload`) as an additive, versioned schema change. Keep the canonical append-only-JSON artefacts.

### 2.5 Step 4 — Instrument mapping & sizing (fixed-notional + cash-cap)
- **Current vs roadmap:** `ExecutionPolicyConfig` already holds a fixed `default_size` (the ADR-011 D2 "fixed size, sizing deferred" decision) and instrument GLD. There is **no cash-cap** and **no `fractionable` check**.
- **Issues:** (a) The YAML config in the roadmap doesn't match the existing Python `ExecutionPolicyConfig`/`FillModelConfig` (frozen dataclasses + fingerprints, per ADR-003). (b) Cash-cap and `GET /v2/assets/GLD → fractionable` are real, missing, and correct. (c) Moving from `default_size` (size/qty) to `notional`-based sizing changes the execution contract → must bump `execution_policy_version` and re-pin BENCH-004/006.
- **Recommended action:** Express sizing as additive fields on `ExecutionPolicyConfig` (not new YAML), version-bump on the qty→notional change, and keep `cap_to_available_cash` + `fractionable` as the genuinely new logic.

### 2.6 Step 5 — Error handling / fail-closed (queued, partial, EXECUTION_UNCERTAIN, startup reconcile)
- **Current vs roadmap:** The adapter is fail-closed (`AlpacaExecutionError`, no synthetic fill) and the runtime is fail-closed/idempotent — but it is **synchronous one-shot**: no `accepted`/`pending_new` "queued" handling, no partial-fill reconcile, no `EXECUTION_UNCERTAIN`, no startup reconcile.
- **Issue:** These are real gaps and correctly specified. They depend on Step 2's reconcile model existing first.
- **Recommended action:** Keep as written; sequence it strictly after the reconcile/state-machine adapter (2). Add the new statuses to `SCHEMA-014` (per 2.4), not a new table.

### 2.7 Step 6 — Scorecard schema (SQLite `scorecard`, direction accuracy by regime)
- **Current vs roadmap:** Two collisions. (a) **`SCHEMA-005` "Evaluation Scorecard Schema" already exists** — but it is the **Supervisor treasury branch** (Decision API input, kept permanently separate by ADR-004); reusing the name "scorecard" invites exactly the conflation ADR-004 forbids. (b) **`MOD-009` Gold Forward-Return Labeler already computes** per-regime direction-correctness and forward returns — i.e. most of the roadmap's "scorecard" intent, and it feeds the **ADR-012** calibration gate.
- **Issue (naming collision + duplication):** A second "scorecard" SQLite table duplicates MOD-009 and risks being read as the treasury SCHEMA-005.
- **Recommended action:** Do **not** create a `scorecard` table. Define the per-execution P&L/round-trip fields on `SCHEMA-014`/`SCHEMA-015`, and route "direction accuracy by regime" through the existing **MOD-009 / ADR-012** machinery. If a distinct artefact is still wanted, name it to avoid SCHEMA-005 and justify it against canonical ownership (CON-003).

### 2.8 Step 7 — API key / environment isolation (`assert_paper_environment`)
- **Current vs roadmap:** **Already built, and the roadmap's version is a regression.** The repo enforces the paper boundary with **parsed-hostname equality** (`urlparse(base_url).hostname == "paper-api.alpaca.markets" and scheme == "https"`) in both `alpaca_adapter.py` and `alpaca_clock_feed.py`, plus fail-closed `client=None` and credentials in env/`.secrets` (KA-008). This was **specifically hardened after an adversarial review** found a substring check exploitable.
- **Issue (critical regression):** The roadmap's `if "paper-api" not in base_url` substring check is the **exact vulnerable pattern already removed** — it admits `evil.paper-api.alpaca.markets`, `paper-api.alpaca.markets.evil.com`, and `attacker.com?x=paper-api.alpaca.markets` (credential-exfil bypass) and rejects mixed-case legit hosts.
- **Recommended action:** Delete the roadmap's substring snippet. Replace Step 7 with "already satisfied — see the parsed-hostname guard in `alpaca_adapter.py`/`alpaca_clock_feed.py`; do not weaken it." Mark Step 7 DONE.

### 2.9 Step 8 — Observation window (plumbing gate + performance gate)
- **Current vs roadmap:** Strongly aligned conceptually with **ADR-012** (gates G0–G3) + **MOD-009**: direction-accuracy as the performance gate, slippage as live-only, regime diversity + closed round-trips, thresholds fixed before start. The current calibration verdict is **DEFER on all three targets** (corpus N=5, monochromatic RESTRICTIVE_RATES/AVOID, 0 realized labels).
- **Issue:** Framed as new; doesn't reference ADR-012/MOD-009, which already implement the gate and the "never bump below the gate" discipline.
- **Recommended action:** Re-express Step 8 as "consume the existing ADR-012 gate + MOD-009 labeler," and fold the plumbing-gate (orders queue/fill, NO_ACTION rows, partial-fill) into the ADR-012 readiness story rather than a parallel gate.

### 2.10 Verification package (A-block / B-block)
- **Current vs roadmap:** Well-structured and mostly valid. A-block (Layer-2 data/snapshot freshness, fail-closed, PIT, replay) maps to the real Mr-Ripley producer + epoch-(b) corpus. B-block (reconcile delta, `client_order_id` determinism, immutability, NO_ACTION, round-trip, env-guard, queued/partial, timeout/auth, startup-reconcile, E2E) is a sound test plan for adapter v1.
- **Issues:** (a) Stale baselines — it cites "853 green tests" / "high-90s audit"; the current suite is **1050 tests**. (b) **A8 is the load-bearing prerequisite and is probably failing today:** the current execution path fills GLD at `instrument_price = fv.value("gold_price")`, which is **gold spot ($/oz, ≈4624 in the real snapshot)**, not the GLD share price (≈$/share). So both the simulator fill and the `alpaca_adapter` `slippage_bps = (fill_price - instrument_price)/instrument_price` compare GLD against gold spot — a meaningless number. The roadmap's A8 ("is a GLD close price in the snapshot?") and its GLD-vs-GLD slippage correction (B6) are **correct and apply to existing code**. (c) B10 tests the substring guard — update it to assert the hostname-equality guard instead.
- **Recommended action:** Refresh the baselines (1050 tests). **Elevate A8 + B6 to blocking pre-work**: confirm whether the snapshot carries a GLD price; if not, an ingest extension precedes adapter v1, and the GLD-vs-spot price/slippage bug must be fixed in `models.py`/`adapters.py`/`alpaca_adapter.py` first. Rewrite B10 against the parsed-hostname guard.

---

## 3. ADR-011 specific analysis

The user asked specifically whether ADR-011 is correctly reflected. **It is not reflected at all — and that is the core defect.**

- **The roadmap's governing ADR is mis-numbered.** It calls it "ADR-010," but the Alpaca paper execution adapter is governed by **ADR-011 "Execution Layer Planning"**, which is **Accepted (active)** with its six creation gates **a–f all closed** — gate (f) being precisely "the Alpaca-adapter boundary (credential isolation + non-replayable IO quarantine)." The roadmap therefore proposes re-deciding, under a colliding number, a boundary that ADR-011 already settled and the code already implements.
- **Consequences of the gap:** (1) the roadmap doesn't inherit ADR-011's determinism boundary (simulator = canonical replay-safe core; Alpaca = non-replayable, logged-not-replayed plug, default-OFF), so its richer adapter must be explicitly bound to that quarantine; (2) it re-specifies env-isolation that ADR-011 gate (f) already closed (and does so with a weaker guard — §2.8); (3) it ignores the **D1/D2 decisions** under ADR-011 — D1 (instrument price re-derived from `source_snapshot_id`, never a live read on the replay path) and D2 (fixed `default_size`, sizing deferred) — which directly govern the roadmap's sizing (Step 4) and slippage (Step 3) sections.
- **The GLD-price issue is an ADR-011 D1 interaction.** D1 forwards `gold_price` as `instrument_price`. The roadmap correctly exposes that for GLD execution this is the wrong series; resolving it is an amendment to the D1 price source (gold spot → GLD close), which is an ADR-011-level decision, not a new ADR-010.
- **Verdict:** The roadmap must be re-anchored to ADR-011 — either as **ADR-014 explicitly referencing ADR-011/012/013** or as an **ADR-011 amendment** — and its overlaps with the already-closed gate (f), D1, and D2 reconciled rather than re-decided.

---

## 4. Final alignment plan (step-by-step, to update the roadmap)

1. **Renumber & re-anchor.** Retitle the doc "ADR-014: Operable Alpaca Paper Execution Adapter v1" (next free id) — or an ADR-011 amendment. Replace every "ADR-010" reference; add a Context paragraph citing ADR-011 (gate f, D1, D2), ADR-012 (the calibration gate), and ADR-013 (the ops control plane). Remove Step 1's "write the ADR" framing.
2. **Re-cast as a delta, not greenfield.** Add a "Current state" column to the eight components marking each: Step 1 DONE (ADR-011), Step 7 DONE (hostname guard — keep, don't weaken), Steps 2/4/5 PARTIAL (v0 one-shot stub exists), Steps 3/6 RECONCILE (map to SCHEMA-014/015 + MOD-009), Step 8 DONE-VIA-ADR-012.
3. **Remove the two regressions/duplications.** Delete the substring `assert_paper_environment` snippet (point to the existing parsed-hostname guard). Delete the SQLite `fill_record` and `scorecard` tables; replace with additive, versioned fields on `SCHEMA-014`/`SCHEMA-015` and reuse `MOD-009`/ADR-012 for direction-accuracy.
4. **Fix the blocking price defect first (A8/B6).** Before adapter v1: confirm whether the snapshot carries a GLD close price; if not, extend Layer-2 ingest. Then correct the GLD-vs-gold-spot fill/slippage in `models.py` / `adapters.py` / `alpaca_adapter.py` (this is an ADR-011 D1 amendment) and re-pin BENCH-004/006.
5. **Keep and prioritize the genuinely new content.** reconcile-then-act + FLAT→sell-to-zero + deterministic `client_order_id` (with Alpaca 422 reconciled against the existing once-ever guard) + cash-cap + `fractionable` check + queued/partial/EXECUTION_UNCERTAIN state machine + startup reconcile. Bind all of it to ADR-011's non-replayable Alpaca quarantine (default-OFF; simulator stays canonical).
6. **Reconcile the adapter shape with INT-011.** Decide explicitly: extend the `INT-011` port (versioned interface change) to carry reconcile/SELL, or place reconcile at the runtime/orchestrator layer. Record the choice; bump `execution_policy_version` for the qty→notional + cash-cap change and re-pin the affected goldens.
7. **Refresh baselines & close the open `[FLAG]`s.** Update "853 tests" → 1050; keep B1 (`client_order_id` length), B2 (GLD `fractionable`), B3 (cash/margin) as empirical pre-work — these are correct and remain genuinely open.
8. **Sequence under the existing discipline.** A-block (Layer-2, esp. A8) runs now in parallel; adapter v1 only after ADR-014/amendment is Accepted; gated-live enablement stays behind the ADR-013 ops-console HARD PAUSE; calibration bumps stay DEFER until the ADR-012 gate passes.

---

## 5. Items that are correct and should be preserved
The constitution; long-or-flat/paper-only/fail-closed/deterministic; market+day "queue-to-next-open" and the explicit rejection of OPG (fractional incompatibility) and broker-side conditional orders; cash-cap as the margin-neutralizer; **GLD-vs-GLD slippage**; **direction-accuracy (not slippage) as the paper performance gate** with slippage marked live-only; reconcile-then-act and deterministic `client_order_id`; the A-before-B verification ordering. These are sound and, in several cases, ahead of the current code.
