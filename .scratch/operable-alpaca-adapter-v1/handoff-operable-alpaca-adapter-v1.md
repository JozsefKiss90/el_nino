# Handoff — Operable Alpaca Paper Execution Adapter v1 (ADR-014)

**Date:** 2026-06-23 · **Repo:** `C:\Code\el_nino` · **Branch:** `JARVIS` (PRs target `master`)
**Mode the prior session ran in:** `ultracode` (xhigh + workflow orchestration). Not required to continue, but the prior session used background workflows/subagents for understanding + adversarial review.

## What this work is

Turning the dormant Alpaca **paper** execution adapter into an *operable* one, as **6 vertical slices**. Do not re-derive scope — it is fully specified in:

- **PRD:** `.scratch/operable-alpaca-adapter-v1/PRD.md`
- **Per-slice issues:** `.scratch/operable-alpaca-adapter-v1/ISSUE-01..06-*.md` (each: What to build / Acceptance criteria / Blocked by)
- **Binding ADR:** `dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md` (ADR-014) — **governs; where PRD and ADR differ, ADR-014 wins.**

## State: Slices 1–4 DONE and green; 5, 6, writeback NOT started

- **Test baseline:** started 1050 passing → **now 1091 passing, 0 failures/skips.**
- **Runner:** `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` (full suite ~10–55s). Python 3.13, pytest 9.
- **Everything is UNCOMMITTED** in the working tree (user has not asked to commit). Inspect with `git --no-pager diff`.
- The user explicitly said **"Stop after Slice 4"** — that's why 5/6/writeback are pending. Confirm before resuming.

### Slices delivered (read the diff for specifics — not duplicated here)
- **Slice 1** — `src/execution/price_reference.py` (new `resolve_sim_exec_ref` / `ExecPriceRef` / `OZ_PER_SHARE` / `EXEC_PRICE_SOURCE_VERSION`), SCHEMA-014 `exec_ref_gld_price`(+`_ts`/`_basis`) on `ExecutionRecord`, `run_chain` rewired, both benchmark replay keys gained `exec_price_source_version`. Goldens re-pinned.
- **Slice 2** — `as_of` threaded into `build_guard_request`; `as_of` added to `ExecutionEntry` (SCHEMA-015); `trades_today` day-scoped via `_as_of_date`; **`PORTFOLIO_SCHEMA_VERSION` 0.1.0→0.2.0**. Goldens re-pinned.
- **Slice 3** — `assert port.replayable` fence on `run_once`/`run_sequence` (BOTH `src/orchestration/runtime.py` and `src/execution/runtime.py`); new `src/orchestration/live_runtime.py::operate_live` (currently a **thin run_chain wrapper** — the Slice-3 skeleton) threading **separate** live ledger/portfolio paths; `OpsPaths` gained `live_ledger_path`/`live_portfolio_path`/`live_operational_capture_path` (derived props); `ops/gated.run_chain_now_alpaca_paper` migrated off `run_once` onto `operate_live`. No golden change.
- **Slice 4** — `src/execution/live_adapter.py` (new): widened `LiveBrokerPort` Protocol (buy/sell/positions/open-orders/orders/account/asset), side/order-based `LiveExecutionAdapter` (state machine + typed HTTP/URL/429/auth errors + account gate + cash-cap + fractionable sizing + deterministic `client_order_id` 422 dedup + `resolve_fill` from order reads), `_AlpacaRestLiveBroker` + `live_adapter_from_env`. SCHEMA-014 `ExecutionStatus` enum + `status`/`client_order_id`/`alpaca_order_id`/`raw_payload` fields on `ExecutionRecord`. **Stub-only, not yet wired into any caller.** No golden change (additive, not projected, no schema bump).

New tests added: `tests/execution/test_price_reference.py`, `test_guard_day_scope.py`, `test_live_adapter.py`, `tests/orchestration/test_replayable_fence.py`; edits to `test_chain_engine.py`, `test_chain_bench.py`, `tests/ops/test_gated.py`.

## Determinism discipline (MANDATORY — this is the whole game)

The deterministic sim/replay spine + benchmark goldens must stay byte-identical **except** for documented versioned key changes. Verified empirically each slice via: **change code → regenerate goldens → `git diff` the artifacts to confirm only intended keys moved → run full suite.**

Regenerate goldens:
```
.venv/Scripts/python.exe benchmarks/execution/run_execution_bench.py
.venv/Scripts/python.exe benchmarks/orchestration/run_chain_bench.py
```
Then `git --no-pager diff benchmarks/*/artifacts/*.json` and confirm the diff is explainable. Only `ExecutionRecord` is **not** hashed; `PortfolioState.state_hash` (over `to_dict`) is the binding surface, and `compute_execution_id` folds in `instrument_price` + `prior_portfolio_state_hash`.

## Remaining work + the non-obvious decisions for it

### Slice 5 — `operate_live` reconcile-then-act (the integration centerpiece; large)
Enrich `operate_live` (today a thin `run_chain` wrapper) to a reconcile-driven live path using the Slice-4 `LiveExecutionAdapter`. **Key decisions already settled by PRD/ADR-014 §6:**
- **Do NOT use `execute()`/`port.fill()` for the live order** — that LONG-only path stays the simulator's. Reuse the *decision + GATE-001 guard + once-ever idempotency* by re-threading the same pure cores `operate_live` already imports (mirror `run_chain`'s decision composition: `build_features → classify → build_decision → evaluate → run_guard`), then do reconcile-act instead of sim execute. Keep `run_chain` and the simulator **structurally unchanged.**
- **ReconcileEntry (new SCHEMA-015 kind):** add to `PortfolioState`, but **OMIT it from `to_dict()` when empty** so sim/replay portfolios stay byte-identical → no `PORTFOLIO_SCHEMA_VERSION` bump, no golden re-pin. This is the critical determinism trick (sim never has reconcile entries). Distinct from `ExecutionEntry` (no `source_record_id`, no `guard_result`). Update `from_dict`/`append`/`empty` (note `append` constructs `PortfolioState` positionally — add the field carefully).
- **SELL-fold lives in `live_runtime`, NOT the pure core:** `realized_pnl += qty*(exit_fill − avg_cost); position → 0`. Sim stays accumulate-only (`realized_pnl == 0.0`).
- **Reconcile delta:** `target − broker_position − Σ(expected open-order qty)`; nets to **NO_ACTION**. Target: LONG → cash-capped qty (`resolve_order_qty`, `min(notional, settled_cash)`); FLAT → 0; AVOID/WATCH → NO_ACTION resolved before the adapter.
- **Discrepancy** (unexpected open order = unknown `client_order_id`/wrong side/qty; or unexplained broker-vs-local position divergence) → **terminal-refuse execution only** (no auto-flatten) while the decision/observation/labeling chain keeps advancing (ledger still persists) → append a **reconcile-heal entry** (observed broker qty + avg entry + marker). **Governed adopt** (ops-console-gated) is the only way to adopt a non-zero broker position — never automatic.
- **Idempotency bifurcation:** `has_execution(snapshot_id)` on the *live* portfolio + reconcile-delta + open-orders awareness + `client_order_id` 422 dedup.
- **Default-OFF:** `ops/gated.run_chain_now_alpaca_paper` already calls `operate_live`; wire the reconcile + new adapter into `operate_live` so that action drives it. No new SQLite (PRD Out-of-Scope).
- **Carry-over caveat from the Slice-4 review:** `resolve_fill(requested_qty)` compares share counts — for **fractionable notional** orders the share qty isn't known at submit time; define the FILLED/PARTIAL contract for notional orders when wiring.
- The v0 `AlpacaPaperAdapter.fill()` (LONG-only) is **superseded on the live path** — `operate_live` should stop routing through `run_chain→execute→fill`. Decide whether to retire `AlpacaPaperAdapter` or leave it dormant (its tests in `tests/execution/test_alpaca_adapter.py` still pass today).

### Slice 6 — operator kill switch (audited Tier-2 halt)
Add a gated action that writes `halt=True`; the operational feed **already honors** `halt` (read path exists — see `src/orchestration/operational_feed.py` `OperationalInput.halt` and `cooldown`/`operational_ok` predicate usage). Mirror the audit pattern in `ops/gated.py` (`_finish`/`audit.make_entry`). No new read path, no standalone rate limiter. See `ISSUE-06`.

### dev_graph writeback (per `dev_graph/CLAUDE.md` — currently STALE w.r.t. slices 1–4)
Run the end-of-session checklist: create file/test nodes for the new modules (`price_reference.py`, `live_runtime.py`, `live_adapter.py` + their tests), update SCHEMA-014 (`dev_graph/schemas/Execution Record Schema.md`) and SCHEMA-015 (`dev_graph/schemas/Portfolio State Schema.md`), `FILE-038` (alpaca adapter), `MOD-010`, `BENCH-004/006`; bump `implementation_status`; run lint checks 1–11 on touched nodes; append to `dev_graph/log.md`; update `dev_graph/index.md`; re-sync Neo4j: `python sync_to_neo4j.py --clear` from **repo root** (needs `NEO4J_PASSWORD` env; use `127.0.0.1` not `localhost` per the IPv6 stall memory). Next free canonical IDs + exact node paths are in the saved understanding-workflow output (below).

## Useful artifacts from the prior session
- **Deep structural map (8 readers, incl. dev_graph node IDs + next free MOD-/FILE-/TEST- numbers + exact determinism notes):** `C:\Users\jozse\.claude\projects\C--Code-el-nino\0a509fa1-3e6c-49ec-9fa7-266f748fe1fa\tasks\w0nrgxqtq.output` (large JSON; read selectively).
- Adversarial reviews of Slice 1 and Slice 4 both returned **no blocking issues** (their two non-blocking notes are folded into the Slice-5 section above).
- Empirical preconditions **B1/B2/B3** (PRD "Empirical preconditions") are encoded as documented assumptions in `live_adapter.py`: `_COID_MAXLEN=48`, `_SETTLED_CASH_FIELD="cash"`, GLD `fractionable` read live. **Confirm against Alpaca docs before any live run** (use context7).

## Suggested skills for the next session
- **`tdd`** — Slice 5/6 are best driven red→green with integration tests at the seam (stub broker + temp separate paths), mirroring `tests/orchestration/test_chain_engine.py` and `tests/execution/test_live_adapter.py`.
- **`context7-mcp`** (or `/context7`) — fetch current Alpaca Trading API docs to close B1/B2/B3 (client_order_id charset/length, account settled-cash field name + `multiplier`, GLD `fractionable`, positions/orders response shapes for queued/partial/filled) before trusting the stub assumptions.
- **`code-review`** (consider `ultra`) and **`security-review`** — the live path (Slice 5) is the credential/real-broker boundary; review fail-closed, paper-only host guard, no-double-order, and determinism non-contamination.
- **`to-prd` / `to-issues`** are already done for this work — don't re-run.
- After coding: perform the **dev_graph writeback** per `dev_graph/CLAUDE.md` (this is a hard project requirement, not optional).

## First moves for the continuing agent
1. Confirm scope/stop-point with the user (they paused after Slice 4) — and whether to commit slices 1–4 first.
2. `git status` / `git --no-pager diff --stat` to load the working-tree state; run the suite to confirm 1091 green.
3. If resuming Slice 5: re-read `ISSUE-05`, ADR-014 §6, and `src/orchestration/live_runtime.py` + `src/execution/live_adapter.py`, then implement reconcile-then-act per the decisions above, regenerating + diffing goldens to prove the sim spine stayed byte-identical.
