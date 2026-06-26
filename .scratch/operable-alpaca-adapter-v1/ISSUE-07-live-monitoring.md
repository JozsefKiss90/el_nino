<!-- triage: ready-for-agent -->
<!-- source PRD: .scratch/operable-alpaca-adapter-v1/PRD.md -->
<!-- source ADR: dev_graph/decisions/ADR - Operations Control Plane.md (ADR-013) -->
<!-- source ADR: dev_graph/decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md (ADR-014) -->

# Slice 7 — Ops console live read-model (sim-vs-live monitoring + governed adopt)

## Parent

PRD — Operable Alpaca Paper Execution Adapter v1 (`.scratch/operable-alpaca-adapter-v1/PRD.md`).
Governed by **ADR-013** (Operations Control Plane — Tier-1 read-only / Tier-3 gated boundary) and
**ADR-014** (the live `operate_live` path that writes the separate live state).

## What to build

Today `gated.py`'s `run_chain_now_alpaca_paper` → `live_runtime.operate_live` **writes** live state to the
**separate** live files (`*.live.json`), but `core.py`'s read-model reads only the **canonical (sim)**
artefacts — so an operator running live is flying blind. This slice is an **additive, read-only extension
under ADR-013 Tier-1** plus **one governed Tier-3 action** (discrepancy adopt). It touches **no `src/`
decision logic and no determinism/replay path** — the console is not in the replay path.

The safety point that governs the whole slice: the **sim** portfolio is the Q6 **accumulate-only
determinism artifact** (buy-only, never realizes — a *model number, not performance*); the **live**
portfolio is **real paper P&L** (real fills, realized P&L on exits, reconcile observations). The console
must render these as **distinct, clearly-badged panels** and must **never** let the sim portfolio value be
read as a track record (the JARVIS-HUD static-panel hazard).

## Acceptance criteria

- [ ] **Live read-model (core.py, additive, reuses the existing loaders + view dataclasses):**
  - `live_ledger_view` (reads `paths.live_ledger_path`): entry count, latest verdict, verdict
    distribution, `state_hash` — same `LedgerView` shape as the sim ledger.
  - `live_portfolio_view` (reads `paths.live_portfolio_path`): per-instrument qty / avg_cost /
    **realized_pnl** / unrealized_pnl, execution count, `state_hash` — the **real paper P&L**.
  - `reconcile_view`: the `ReconcileEntry` history (observed broker qty / avg / `marker` / seq / as_of),
    **DISCREPANCY markers surfaced prominently**, plus a DERIVED `execution_refused` / `adoptable` /
    `refuse_reason` (advisory; the authoritative refuse is recomputed live by `reconcile_and_act`).
  - `pending_orders_view`: the live-portfolio `PendingOrder` queue (cross-run async-fold state).
  - `live_operational_view` + kill-switch state (`operator_halt_active`).
  - All **pure reads, fail-closed** (missing ⇒ empty; malformed ⇒ `error` field, never crash), **no
    secrets** — same discipline as the existing read-model.
- [ ] **Sim-vs-live badging:** two clearly-separated sections, never interleaved — `SIM · NOT performance`
  (the existing canonical panels) and `LIVE PAPER · real paper P&L` (the new live panels); plus a
  top-of-dashboard **live-state strip** (plug status, kill-switch ENGAGED/clear, and a loud banner on an
  unhealed discrepancy → execution refused).
- [ ] **Wired** into `assemble_dashboard` + `render_text_dashboard` + the Textual TUI; the existing sim
  panels are unchanged.
- [ ] **One governed control (Tier-3, included here):** a gated-live `adopt-broker-position` action
  (confirm modal + append-only audit + server-side precondition) that adopts the observed broker position
  into the live portfolio (**append-only reconcile-adopt, never automatic**, per ADR-014 §6.2), clearing
  the terminal-refuse so live execution can resume.
- [ ] **Tests** (headless, mocked, no network): live views read fixture live files; `reconcile_view`
  surfaces discrepancy markers + the refused/adoptable state; sim and live views are **independent** (live
  empty when no live runs; sim panels unchanged); the badging metadata is correct; **no secret appears** in
  any output; the adopt action is confirm+audit+precondition-gated and append-only.
- [ ] **Determinism untouched:** no `src/` decision logic / replay path change — BENCH-004/006 unaffected
  (regenerate + `git hash-object` to prove zero golden movement); full suite green; `mypy --strict` +
  `ruff` clean.
- [ ] dev_graph writeback: **OBS-002** + the `ops/` file/test nodes; `index.md`; `log.md`; 11 lint checks;
  Neo4j re-sync.

## Constraints

- Read-only observability + the single governed Tier-3 adopt action; **reuse** the existing loaders / view
  dataclasses (no reimplementation); pure / fail-closed / no-secrets.
- **Sim and live must never be confusable** — the sim portfolio value is never shown as performance.
- No `src/` decision-logic, contract, or `*_version` change; no `wiki/**`/`raw/**` mutation; ADR-013
  governs. The adopt action constructs the new live `PortfolioState` from the **existing** immutable value
  type (`append_reconcile` + `dataclasses.replace`) and persists via the existing `persist_portfolio` — it
  adds no `src/` method, no schema, no version bump, and never touches the deterministic replay files.

## Blocked by

None — builds on ISSUE-05 (`operate_live` + reconcile) and ISSUE-06 (operator kill switch), both shipped.
