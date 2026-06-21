# Claude Code prompt — El Niño operations dashboard (JARVIS control plane)

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

Build an interactive **operations dashboard** for the El Niño pipeline, extending the existing **JARVIS** FastAPI backend + React HUD (ADR-010). It must let me monitor every process, status, artefact, gate, and error at runtime, **and** trigger operator actions in three safety tiers — up to and including the gated live actions — **behind explicit in-UI confirmation, an audit log, and the same fail-closed boundaries the rest of the system already enforces.** This adds an **operational control plane** to JARVIS, which ADR-010 deliberately scoped as a *read-only* graph consumer — so this is a governed boundary change: author the governing ADR first, build read-only before actions, and **HARD PAUSE before wiring the gated-live tier.**

## Overriding safety constraints (whole slice)

- **localhost-only.** The control plane binds to / is reachable from localhost only — never exposed beyond it (carry ADR-010's localhost Non-Goal forward; it now matters far more).
- **Paper-only, no live-money path, ever.** The dashboard cannot introduce any path the codebase doesn't already have. Live actions reuse the **existing governed functions** (`orchestration.run_once`, the ADR-012 calibration gate check, `paper_adapter_from_env` / `clock_feed_from_env`, the schedule-registration script) — never reimplement safety, paper-only, or gate logic in the web layer.
- **Secrets never leave the process.** No endpoint ever returns API keys or `.secrets` contents — only derived status (`dormant` / `enabled` / `creds-present`). Credentials stay env/`.secrets` (KA-008).
- **Every mutating or live action:** explicit in-UI confirmation **+** an append-only **audit-log** entry (timestamp, action, args-summary, result) **+** server-side enforcement of its precondition (gate pass / paper creds / paper host). Read endpoints are pure reads — no mutation.
- **Gate-respecting.** A calibration-bump action returns DEFER unless the ADR-012 gate actually passes (the UI can never force a bump). Enabling Alpaca fail-closes if paper creds/host are absent. The UI surfaces state; the underlying governed logic decides.
- **No decision-path / contract / `*_version` change** from building the dashboard — it observes and triggers; it changes no layer logic.

## Step 0 — read, then author the governing ADR

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, the `observability` node type, §7.5 threshold.
2. `decisions/ADR - JARVIS GraphRAG Integration.md` (ADR-010) — the read-only-consumer boundary + the localhost/no-write Non-Goals this slice extends; `jarvis/backend/app.py`, `jarvis/hud/` (the React HUD, typed data layer, ThemeContext), and the existing graph/`/ask`/voice routers (the conventions to reuse).
3. The runtime surfaces the dashboard reads/triggers: `src/orchestration/` (`run_once`, `find_latest_snapshot`, the captured `OperationalInput`), `src/gold/paper_runtime/` (ledger + `RuntimeDecisionRecord` + the six guards), `src/execution/` (portfolio, `SimulatedBrokerAdapter`, `AlpacaPaperAdapter` + `paper_adapter_from_env`), `src/orchestration/alpaca_clock_feed.py` + `operational_feed.py`, `benchmarks/calibration/run_forward_return_labels.py` (MOD-009 — calibration readiness), `decisions/ADR - Execution Layer Planning.md` (§7 gate board) + `decisions/ADR - Empirical Calibration Methodology.md` (G0–G3), the `EPOCH_B_*` + `CHAIN_ORCHESTRATOR_RUNBOOK.md` runbooks, and the daily-run / schedule scripts.

**Author `ADR-013 — Operations Control Plane`** (re-derive the id; governance/boundary record mirroring ADR-009/010/011; `status: draft`). Record: the control plane **extends** ADR-010's read-only console with an **operational** surface; the **three action tiers** (read-only / safe non-destructive / gated-live) and exactly which actions sit in each; **localhost-only, paper-only, secrets-never-exposed, confirm+audit on every mutation, reuse-governed-functions, gate-respecting**; Non-Goals (live-money, beyond-localhost exposure, bypassing any HARD-PAUSE gate, a second source of truth). Add an **ADR-010 amendment note** acknowledging the extension. **PAUSE for my review of ADR-013 before building.**

## Step 1 — read-only monitoring (the blueprint IA)

Add ops **read** endpoints to `jarvis/backend/app.py` and an **Ops** view to the HUD mirroring the agreed blueprint panels:

- **Status header:** pipeline health, paper-only badge, Neo4j sync freshness (node count + staleness), last chain-run time.
- **Runtime chain lane:** latest snapshot → consume → features → regime → gold → admission → execution → portfolio, each with status + the latest snapshot id / regime / direction / verdict.
- **Admission guards:** the six-guard outcomes for the latest record + GATE-001 (PRED-001..005) status.
- **Gates:** ADR-011 creation gates (a–f) + ADR-012 calibration gates (G0–G3), read from the gate boards / the calibration check.
- **Calibration readiness:** N vs G0, regime + direction distribution, realized forward-return label count (from MOD-009).
- **Artefacts:** ledger (entries / last verdict), portfolio (positions / P&L), benchmark in-sync status (BENCH-001..006).
- **Processes & schedules:** daily chain run (registered? last/next run), Mr-Ripley producer (DB freshness, DTWEXBGS watch), Neo4j sync.
- **Live plugs:** Alpaca calendar feed + execution adapter status (`dormant`/`enabled`/`creds-present` — never the keys).
- **Errors / fail-closed events:** recent contract errors + fail-closed events parsed from the run logs.

Reuse the HUD's typed data layer + ThemeContext (JARVIS/PIXEL); pure reads only.

## Step 2 — safe (non-destructive) actions

One-click, no extra confirmation, each calling the existing governed function and writing an audit-log entry: **run chain now** (`orchestration.run_once`, simulator/paper, over the latest snapshot), **re-run calibration readiness check** (the MOD-009 / ADR-012 gate), **re-sync Neo4j** (`sync_to_neo4j.py --clear`). Surface the result inline.

## Step 3 — gated-live actions (HARD PAUSE before wiring)

**Pause for my review before implementing this step.** Then, each behind an explicit confirm dialog + audit-log + server-side precondition enforcement: **enable/disable Alpaca paper execution** (fail-closed if paper creds/host absent; paper-only; never live-money), **register/unregister the daily schedule** (the existing script; reversible), and **commit a calibration bump** (only if the ADR-012 gate passes — otherwise return DEFER; never force). Each maps to the locked controls in the blueprint.

## Step 4 — tests + writeback

- Tests (mocked — **no real network, no real Alpaca call, no real OS-task registration**): read endpoints return correct shapes from fixture artefacts; secrets never appear in any response; a live action fail-closes without paper creds; the calibration-bump action returns DEFER when the gate fails; the audit log is appended on every mutation. Full prior suite green; `mypy --strict` + `ruff` clean on new code.
- Author **ADR-013** + an **observability** node for the console (re-derive, likely `OBS-002`) + the app file/test nodes per §7.5; app code under `jarvis/` follows ADR-010's "app slices don't change trading-engine nodes" precedent. Update the ADR-010 amendment note. `index.md` + `log.md`; 11 lint checks; **Neo4j re-sync**.

## Constraints

- **localhost-only; paper-only; secrets never exposed; confirm + audit + precondition on every mutation; reuse governed functions; gate-respecting** (restated because they are the point).
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids; the dashboard changes no `src/` decision logic, contract, or `*_version`.
- When done, summarize the endpoints + view, the audit/confirm/precondition wiring for each action tier, and the ADR-013 boundary, and **stop at the Step-0 and Step-3 pauses** for my review.
