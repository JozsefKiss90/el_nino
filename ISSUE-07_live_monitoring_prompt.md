# Claude Code prompt — ISSUE-07: live read-model so the ops console is a real live-monitoring surface

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

Build **ISSUE-07** — the ops console's **live read-model**, so it shows the live ledger/portfolio/reconcile state instead of only the simulator panels. Today `gated.py` *writes* live state (via `operate_live`) to the **separate** live files, but `core.py`'s `ledger_view`/`portfolio_view` read only the **canonical (sim)** paths, so an operator running live would be flying blind. This is an **additive, read-only extension under ADR-013 (Tier-1)** plus **one governed Tier-3 action** (discrepancy adopt). It touches **no `src/` decision logic and no determinism path** — the console isn't in the replay path. Add it to the slice plan as `.scratch/operable-alpaca-adapter-v1/ISSUE-07-live-monitoring.md`.

## The safety point that governs the whole slice
The **sim** portfolio is the Q6 **accumulate-only determinism artifact** — buy-only, never realizes, its value is a *model number, not performance*. The **live** portfolio is **real paper P&L** (real fills, realized P&L on exits, reconcile observations). The console must render these as **distinct, clearly-badged panels** and must **never** let the sim portfolio's value be read as a track record — the same hazard the audit flagged on the JARVIS HUD's hard-coded "VERDICT: ADMIT / 853 TESTS" static panels. If a number could be mistaken for live performance when it isn't, badge it or don't show it.

## Step 0 — read and ground
`decisions/ADR - Operations Control Plane.md` (ADR-013 — Tier-1 read-only / Tier-3 gated boundary); `ops/core.py` (the read-model + `OpsPaths.live_ledger_path`/`live_portfolio_path`/`live_operational_capture_path`/`operator_halt_path`), `ops/app.py` (the Textual panels), `ops/gated.py` (`operate_live` is what writes the live state); `src/execution/models.py` (SCHEMA-015 `PortfolioState` with `reconciles` + any `PendingOrder`; `ReconcileEntry` = observed qty/avg/marker), the SCHEMA-013 `RuntimeLedger`; `src/orchestration/live_runtime.py` (what `operate_live` persists: the live ledger/portfolio, reconcile entries, discrepancy markers, queued/pending orders).

## Step 1 — live read-model (core.py; additive, REUSE the existing loaders/view dataclasses)
Don't reimplement — parameterize `ledger_view`/`portfolio_view` to take a path (or add `live_*` variants) reading the **live** files via the same `load_ledger`/`load_portfolio`, returning the same view shapes:
- **`live_ledger_view`** — `paths.live_ledger_path`: entry count, latest verdict/direction/snapshot, verdict distribution, `state_hash`.
- **`live_portfolio_view`** — `paths.live_portfolio_path`: per-instrument qty / avg_cost / **realized_pnl** / unrealized_pnl, execution count, `state_hash` — the **real paper P&L**.
- **`reconcile_view`** — the `ReconcileEntry` history from the live portfolio: observed broker qty + avg price + `marker` + seq + as_of. **Surface DISCREPANCY markers prominently** (e.g. `discrepancy:unexpected_open_order`, foreign/wrong-side position) and whether live execution is **currently terminal-refused pending a governed adopt**.
- **`pending_orders_view`** (if `PendingOrder` is on the portfolio) — QUEUED orders awaiting fill (the cross-run async-fold state): order id, snapshot lineage, side, qty, status.
- **`live_operational_view` / kill-switch state** — whether the operator halt is engaged (`operator_halt_active(paths.operator_halt_path)`) and the live operational capture.
All **pure reads, fail-closed** (missing ⇒ empty; malformed ⇒ error field, never crash), **no secrets** — same discipline as the existing read-model.

## Step 2 — sim-vs-live badging (render in app.py + render_text_dashboard)
Two clearly separated sections, never interleaved or confusable:
- **`SIM · replay/determinism · NOT performance`** — the existing canonical ledger/portfolio panels, badged so the accumulate-only sim value can't be read as a track record.
- **`LIVE PAPER · real paper P&L`** — the new live ledger, live portfolio (with realized P&L), reconcile/discrepancy panel, pending-orders panel.
Plus a top-of-dashboard **live-state strip**: live-plug status (dormant / creds-present), kill-switch ENGAGED/clear, and a loud banner if there is an **unhealed discrepancy → execution refused**.

## Step 3 — wire into the dashboard
Add the live views to `assemble_dashboard` + `render_text_dashboard` + the Textual TUI (the existing auto-refresh picks them up). Keep all existing sim panels unchanged; add the live section distinctly.

## Step 4 — the one governed control addition (Tier-3; include here or split as ISSUE-08)
A surfaced discrepancy that the operator can't resolve is a half-feature: Q3's terminal-refuse **permanently freezes** live execution until a **governed adopt**. Add a gated-live action **`adopt-broker-position`** (confirm modal + append-only audit + server-side precondition) that adopts the observed broker position into the live portfolio (append-only reconcile-adopt, **never automatic**, per Q3 §6.2), clearing the refuse so execution can resume. *(Discrepancies can't actually occur until the system trades — needs a LONG — so this is needed before/when live trading produces positions; build it now or fast-follow, but don't ship the monitoring surface that shows a discrepancy with no console way out.)*

## Step 5 — tests + writeback
- Tests (headless `core.py`, mocked — **no network**): live views read fixture live files; `reconcile_view` surfaces discrepancy markers + the refused state; sim and live views are **independent** (live empty when no live runs; the sim panels unchanged); the badging metadata is correct; **no secret appears** in any output; the adopt action (if included) is confirm+audit+precondition-gated and append-only.
- **Determinism untouched:** confirm this changes no `src/` decision logic and no replay path — BENCH-004/006 unaffected (regenerate-and-`git hash-object` to prove zero golden movement), full suite green, `mypy --strict` + `ruff` clean.
- dev_graph writeback: update **OBS-002** (the ops console observability node) + the `ops/` file/test nodes; `index.md` + `log.md`; 11 lint checks; **Neo4j re-sync**.

## Constraints
- Read-only observability + the single governed Tier-3 adopt action; **reuse** the existing loaders/view dataclasses (no reimplementation); pure / fail-closed / no-secrets.
- **Sim and live must never be confusable** — the sim portfolio value is never shown as performance.
- No `src/` decision-logic, contract, or `*_version` change; no `wiki/**`/`raw/**` mutation; ADR-013 governs.
- When done, summarize the live panels + badging + the adopt action, and confirm the determinism/secret/fail-closed invariants, and stop for review.
