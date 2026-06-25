# Claude Code prompt — El Niño operations console (terminal TUI)

Paste the block below into a fresh Claude Code session rooted in `el_nino`. (This supersedes the earlier browser/JARVIS dashboard prompt — the operator console is a **terminal interface**, not a web UI and not a copy of the JARVIS console.)

---

Build an interactive **terminal operations console** for the El Niño pipeline — a **Textual** TUI I run in a terminal window to observe and interact with the pipeline's tables, logs, processes, gates, artefacts, and operations. It must monitor every status **and** trigger operator actions in three safety tiers — up to the gated live actions — **behind explicit in-console confirmation, an audit log, and the same fail-closed boundaries the rest of the system enforces.** This adds an **operational control plane**, a new capability, so: author the governing ADR first, build read-only before actions, and **HARD PAUSE before wiring the gated-live tier.**

It is **not** the JARVIS web console (ADR-010, browser/GraphRAG over the dev_graph) and must not depend on it. JARVIS stays the knowledge console; this is a sibling **terminal** operator console over the **runtime**. They may share a governed ops-core, nothing more.

## Overriding safety constraints (whole slice)

- **Local-machine only.** A terminal app run by the operator — no network listener, no exposure. (No FastAPI/web surface; it reads artefacts + calls governed functions directly in-process.)
- **Paper-only, no live-money path, ever.** Live actions reuse the **existing governed functions** (`orchestration.run_once`, the ADR-012 calibration gate check, `paper_adapter_from_env` / `clock_feed_from_env`, the schedule-registration script) — never reimplement safety, paper-only, or gate logic in the console.
- **Secrets never displayed.** No view ever shows API keys / `.secrets`; only derived status (`dormant` / `enabled` / `creds-present`). Credentials stay env/`.secrets` (KA-008).
- **Every mutating or live action:** an explicit in-console confirm modal **+** an append-only **audit-log** entry (timestamp, action, args-summary, result) **+** server-side enforcement of its precondition (gate pass / paper creds / paper host). Read views are pure reads.
- **Gate-respecting.** A calibration-bump action returns DEFER unless the ADR-012 gate passes (the console can never force a bump). Enabling Alpaca fail-closes if paper creds/host are absent.
- **Zero-dep engine preserved.** `src/` keeps its ADR-003 zero-runtime-deps rule. Textual/Rich go in a **separate optional dependency group** (e.g. `[project.optional-dependencies] ops`); the console lives in its own top-level package (e.g. `ops/`), never imported by `src/`.

## Step 0 — read, then author the governing ADR

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, the `observability` node type, §7.5 threshold; `decisions/ADR - Implementation Substrate.md` (ADR-003) for the dependency-isolation rule.
2. The runtime surfaces the console reads/triggers: `src/orchestration/` (`run_once`, `find_latest_snapshot`, captured `OperationalInput`), `src/gold/paper_runtime/` (ledger + `RuntimeDecisionRecord` + six guards), `src/execution/` (portfolio, `SimulatedBrokerAdapter`, `AlpacaPaperAdapter` + `paper_adapter_from_env`), `src/orchestration/alpaca_clock_feed.py` + `operational_feed.py`, `benchmarks/calibration/run_forward_return_labels.py` (MOD-009 readiness), `decisions/ADR - Execution Layer Planning.md` (§7 gate board) + `decisions/ADR - Empirical Calibration Methodology.md` (G0–G3), the `EPOCH_B_*` + `CHAIN_ORCHESTRATOR_RUNBOOK.md` runbooks, the daily-run / schedule scripts. (For tone/precedent only: how ADR-010's app slices were governed.)

**Author `ADR-013 — Operations Control Plane`** (re-derive the id; governance/boundary record mirroring ADR-009/010/011; `status: draft`). Record: a **local terminal operator console** over the runtime (distinct from the read-only JARVIS graph console); the **three action tiers** (read-only / safe non-destructive / gated-live) and which actions sit in each; the safety boundary (**local-only, paper-only, secrets-never-shown, confirm+audit on every mutation, reuse-governed-functions, gate-respecting, engine stays zero-dep**); Non-Goals (live-money, any network listener, bypassing a HARD-PAUSE gate, a second source of truth, coupling to the JARVIS web stack). **PAUSE for my review of ADR-013 before building.**

## Step 1 — governed ops-core + read-only TUI

- **`ops/core.py`** (headless, testable, **no Textual import**): a governed read-model — functions that assemble pipeline status, the runtime-chain summary, the six-guard outcomes, ADR-011 + ADR-012 gate state, calibration readiness (N/G0, regime + direction distribution, realized-label count), artefacts (ledger / portfolio / benchmark in-sync), processes (daily job, producer freshness, Neo4j sync), live-plug status (dormant/enabled/creds-present — never keys), and recent errors/fail-closed events. Pure reads; reuse the runtime modules + MOD-009.
- **`ops/app.py`** (Textual): the TUI over `core.py`, mirroring the agreed blueprint IA as terminal widgets —
  - a **header/status bar** (pipeline health, paper-only, Neo4j freshness, last run, clock);
  - panes/tabs: **overview** (metric tiles + the chain lane as status cells + latest verdict + guards), **gates** (ADR-011 a–f + ADR-012 G0–G3 as `DataTable`s), **corpus/calibration** (readiness + distributions), **artefacts** (ledger / portfolio / benchmarks `DataTable`s, row-selectable → drill into the full record), **processes**, **plugs**, and a **live log pane** (`RichLog` tailing run logs / fail-closed events + the audit log);
  - **auto-refresh** on an interval (poll `core.py`) + manual refresh; key bindings shown in a footer.
- Read-only only in this step. `mypy --strict` + `ruff` clean; `core.py` unit-tested headless.

## Step 2 — safe (non-destructive) actions

Key-bound, no extra confirm, each calling the governed function + writing an audit-log entry, result surfaced in the log pane: **run chain now** (`orchestration.run_once`, simulator/paper, latest snapshot), **re-run calibration readiness check** (MOD-009 / ADR-012 gate), **re-sync Neo4j** (`sync_to_neo4j.py --clear`).

## Step 3 — gated-live actions (HARD PAUSE before wiring)

**Pause for my review before this step.** Then, each behind a Textual **confirm modal** + audit-log + server-side precondition: **enable/disable Alpaca paper execution** (fail-closed without paper creds/host; paper-only; never live-money), **register/unregister the daily schedule** (existing script; reversible), **commit a calibration bump** (only if the ADR-012 gate passes — else DEFER; never force). These map to the locked controls in the blueprint.

## Step 4 — tests + writeback

- Tests target **`ops/core.py` headless** (mocked — **no real network, no real Alpaca call, no real OS-task registration**, no Textual rendering in tests): read-model shapes from fixture artefacts; secrets never present in any output; a live action fail-closes without paper creds; the calibration-bump path returns DEFER when the gate fails; the audit log is appended on every mutation. Full prior suite green; `mypy --strict` + `ruff` clean on new code.
- Add the `ops` optional-dependency group to `pyproject.toml` (Textual/Rich) — `src/` install stays dep-free.
- Author **ADR-013** + an **observability** node for the console (re-derive, likely `OBS-002`) + the `ops/` file/test nodes per §7.5. `index.md` + `log.md`; 11 lint checks; **Neo4j re-sync**.

## Constraints

- **Local-only; paper-only; secrets never shown; confirm + audit + precondition on every mutation; reuse governed functions; gate-respecting; engine stays zero-dep** (restated — they are the point).
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids; the console changes no `src/` decision logic, contract, or `*_version`; no dependency on the JARVIS web stack.
- When done, summarize the panes/tables/log, the audit/confirm/precondition wiring per action tier, and the ADR-013 boundary, and **stop at the Step-0 and Step-3 pauses** for my review.
