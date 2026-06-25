# Claude Code prompt — pre-live-run readiness: check, verify, clear the remaining blockers

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

Drive the **pre-live-run readiness pass** for the ADR-014 Alpaca paper adapter: check, verify, and clear the remaining blockers, then produce a GO/NO-GO readiness report. **Two hard rules up front:**

- **You do NOT place any order — paper or otherwise.** You do the static/doc verification, the code fixes, the stub tests, and you *ready* the live probe; the **operator runs anything that touches the real Alpaca API** (with their own paper creds) and pastes the results back. Pause for that.
- **Clearing these blockers ARMS the adapter; it does not start trading.** The decision layer still emits only AVOID (monochromatic corpus, ADR-012 DEFER), so a full-pipeline live run today produces AVOID → NO_ACTION → no order. Say so in the report. A real *fill* still waits on calibration producing a LONG — that is a separate, data-gated epoch.

Also: **paper-only always** (never the live host), credentials in env/`.secrets` only (KA-008, never committed/logged), and **enabling live execution stays behind the ADR-013 ops-console gated-live HARD PAUSE** — the kill switch is the governed stop. Nothing here auto-enables live.

## Step 0 — ground the checklist
Read: `dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md` (ADR-014 v2 — the binding constraints), the six issues under `.scratch/operable-alpaca-adapter-v1/`, `app_audit.md` (esp. Part 5, the e2e probe), and the live code: `src/orchestration/live_runtime.py`, `src/execution/live_adapter.py` + `models.py`, `src/orchestration/price_reference.py`.

## Blocker 1 — live slippage submit-mark (Q2 correctness gate; verify-and-fix)
**Inspect** whether the live path computes `slippage_bps` / the execution reference against the **real broker GLD mark** or falls back to the **derived proxy**. Per ADR-014 §5.1 / the Q2 lock, the **live path must use the real broker mark** (a live quote at the pinned reference time), with `exec_ref_gld_price_ts` + `exec_ref_gld_price_basis` set (submit/EOD vs open/routing); the **derived proxy is sim-path-only**. If the live path uses the proxy, that is the "plausible-but-wrong slippage" defect we explicitly killed — **fix it** (live-plug-only), add/confirm a stub test that proves live slippage = fill-vs-real-mark (not proxy), and confirm the fix touches **no** sim path (goldens unchanged). If it already uses the real mark, record it verified.

## Blocker 2 — cross-run async-fill fold (Q4 lifecycle completion; verify, implement if missing)
**Verify** the QUEUED→fill lifecycle *across runs*: an order submitted in run N (status `accepted`/`pending_new` = QUEUED, no fill yet) that fills before run N+1 must be **folded by the next startup reconcile** — positions ∪ open-orders read detects the now-filled order, the fill is booked, and `client_order_id`/open-orders netting prevents a double-submit. If this cross-run fold is incomplete/deferred, **implement it** inside `live_runtime` (stub-tested, no network): a queued order from a prior run, then a stub showing it filled, then the next `operate_live` reconcile folds it exactly once. This is the last piece of the order lifecycle before a real queued order is safe.

## Blocker 3 — empirical B-flags + lifecycle facts (doc-verify, then operator-run probe)
For each, first verify what you can from **docs.alpaca.markets**, then mark what needs an empirical paper call:
- **B1** `client_order_id` max length/charset; **B2** GLD `fractionable` value; **B3** the **settled-cash field name** (+ `multiplier`) on `GET /v2/account` (the cash-cap must bind to *settled cash*, never `*_buying_power`).
- **Lifecycle:** `GET /v2/positions` excludes `accepted`/`pending_new`; open orders queryable by status with qty/side/`client_order_id`; day-order queue-to-next-open + cancel-at-close; async fill via `trade_updates`.
- **Ready the probe** (the audit's `alpaca_paper_e2e_probe.py`, or adapt it) so the operator can run it against their **paper** account to capture the real values. **Then PAUSE** — hand the operator the exact command (paper creds in env), have them run it and paste the output. When they do, **replace the stub's documented-assumption values with the verified ones**, and update the issue/ADR notes from "assumed" → "verified (value)".

## Blocker 4 — regression + determinism gate
After the fixes: full `pytest` green; `mypy --strict` + `ruff` clean on touched files; and **BENCH-004/006 byte-identical** — `git hash-object` the golden artifacts and confirm the live-only fixes moved **zero** sim goldens (Blockers 1–2 are live-path-only; any golden movement is a determinism leak to investigate). Confirm `operate_live` is still unreachable from `run_once`/`run_sequence` (the `assert port.replayable` fence holds).

## Step F — readiness report + checkpoint
Produce a **GO/NO-GO readiness report**: each blocker with status (cleared / verified / operator-action-pending / blocked), the verified B-flag values, the determinism confirmation (golden hashes), and the fence/quarantine confirmation. State explicitly: **(a)** the adapter is/ isn't verified-operable; **(b)** even when GO, the live pipeline produces no order until a LONG exists (calibration, ADR-012); **(c)** enabling live execution is the operator's ADR-013 gated-live action, with the kill switch as the stop.

Then the housekeeping (not live-run blockers, but do them): **commit** the ADR-014 epoch as a clean staged checkpoint (it's a large uncommitted surface — back it up before any arming); run the **Neo4j `--clear` re-sync** when the DB is up; and per-touched-node dev_graph writeback for any code you changed (file/test nodes, index/log, lint).

## Constraints
- **You place no orders** — operator runs every real-API call; you ready and verify. **Paper-only**, creds in env/`.secrets`, never committed/logged.
- Live-path fixes must not touch the deterministic sim/core/benchmarks (goldens stay byte-identical); reuse the governed functions; no `wiki/**`/`raw/**` mutation.
- Stop at the operator-probe pause and at any point a blocker can't be cleared without a decision — report and wait.
