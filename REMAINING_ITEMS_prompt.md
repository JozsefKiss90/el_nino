# Claude Code prompt — remaining list: Alpaca live plugs + daily schedule + calibration readiness re-check

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

Three items, in order. They differ in readiness, so the prompt treats them differently — **do not flatten them into "just ship all three."**

- **Part 1 (buildable):** the live **Alpaca clock/calendar feed** (closes the holiday-calendar gap for `operational_ok`) and the deferred **Alpaca paper execution adapter** (ADR-011 gate f), both behind their existing ports.
- **Part 2 (buildable):** **schedule the daily run** of the chain orchestrator over each freshly-banked snapshot — on the **deterministic simulator path**.
- **Part 3 (data-gated):** a **G1/G2/G3 calibration readiness re-check** — run the ADR-012 gate; **execute a bump ONLY if a target's gate passes** (it almost certainly will not — the corpus is monochromatic and far below G0). Otherwise DEFER with no value/version change. **Never calibrate a target whose gate has not passed** — that is the primary failure mode ADR-012 exists to prevent.

## Overriding safety constraints (whole slice)

- **Paper-only, virtual money, ALWAYS.** No live-money path, ever. `Withdrawal Disabled` (PRED-005) stays enforced. The Alpaca **paper** endpoint only.
- **Credential isolation (KA-008):** any Alpaca keys live in **env / a git-ignored `.secrets`** only — never in the repo, a memory file, a dev_graph node, a test, or a committed artifact.
- **Default-off + no auto-enable:** the deterministic simulator stays the canonical execution core for replay/benchmarks; the Alpaca execution adapter ships **disabled by default** and is enabled only by explicit operator opt-in. The scheduled run uses the **simulator**, not the live broker.
- **No real network in tests:** mock/stub the Alpaca client; tests must never hit the real API or place a real (even paper) order.
- **HARD PAUSE before:** (a) enabling any live-broker execution path, and (b) registering the recurring OS scheduled task. Build and validate them; let me throw the switch.

## Step 0 — read

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, §7.5 threshold.
2. `decisions/ADR - Execution Layer Planning.md` — §2 (non-replayable-adapter quarantine), §3 (`paper_only`), **gate f** (the Alpaca adapter boundary this closes), §5 (the adapter is low-information until a LONG exists).
3. `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009) — the operational guard + the live-feed Non-Goal (the Alpaca calendar plug lifts it).
4. `decisions/ADR - Empirical Calibration Methodology.md` (ADR-012) — the G0–G3 gates + the "never calibrate below the gate" rule; `EPOCH_B_CALIBRATION_RUNBOOK.md`.
5. The seams + ports to fill (read; do not change their contracts): `src/orchestration/operational_feed.py` (`OperationalFeed` port + `read_and_capture` quarantine), `src/execution/adapters.py` (`ExecutionPort` / INT-011 + `SimulatedBrokerAdapter`), `src/execution/runtime.py` + `src/orchestration/runtime.py` (`run_once`/`run_sequence`), `benchmarks/calibration/run_forward_return_labels.py` (MOD-009 — the calibration readiness input). The Mr-Ripley `scripts/daily_eod_snapshot.ps1` + `register_daily_task.ps1` (the scheduling pattern to mirror; Mr-Ripley is a separate repo — do not modify it).

## Part 1 — Alpaca live plugs (behind existing ports; non-replayable; default-off)

- **`AlpacaClockFeed`** implementing the `OperationalFeed` port: reads Alpaca's **clock/calendar** (paper base URL) for real venue open / holiday / (where available) halt status → an `OperationalInput`. This **closes the v0 holiday-calendar gap** (Alpaca handles movable feasts / observed dates the fixed-date `MarketCalendarFeed` cannot). **Fail-closed:** missing creds / API error / ambiguous ⇒ `OperationalInput.closed()` (not tradeable). It is read **only on the live path** and **captured** via the existing `read_and_capture` quarantine — replay threads the captured value, never the feed.
- **`AlpacaPaperAdapter`** implementing the `ExecutionPort` (INT-011): its `fill()` submits a **paper** order to Alpaca's paper API and echoes the paper fill; `mode = "alpaca_paper"`, `replayable = False`. **Non-replayable quarantine (ADR-011 §2):** never on the `run_sequence`/benchmark path; live calls logged, not replayed. **Fail-closed** on missing/non-paper creds. **Default-off / built-but-dormant** — note in the node that it cannot fill until calibration produces a LONG (ADR-011 §5), so it ships behind the port unused.
- Tests: a **mocked** Alpaca client only — the calendar feed maps mocked clock/calendar responses to the right `OperationalInput` (incl. a holiday the fixed-date feed missed); the paper adapter maps a mocked order response to a `Fill`; both fail closed without creds; the quarantine (no feed/broker call on replay) holds. No real network.
- Governance: closes **ADR-011 gate f** (update the §7 board: (f) Closed) + an **ADR-009 amendment** for the live calendar plug.

## Part 2 — schedule the daily run (simulator path)

- An el_nino script that, after the Mr-Ripley EOD snapshot banks a snapshot, runs the **chain orchestrator `run_once`** over the latest banked consumable snapshot using the **deterministic simulator** adapter + the operational **calendar feed** (capturing the `OperationalInput`), then persists the ledger + portfolio. Idempotent (re-run ⇒ no double-fill, inherited).
- Mirror the Mr-Ripley `daily_eod_snapshot.ps1` / `register_daily_task.ps1` pattern, but **all changes stay in el_nino**; schedule it to run after the producer's 23:00 job. Validate by a single **manual** invocation; then **PAUSE before registering the recurring task** (I activate it).
- Update `CHAIN_ORCHESTRATOR_RUNBOOK.md` §6 with the live scheduling procedure + disable steps.

## Part 3 — G1/G2/G3 calibration readiness re-check (no bump unless the gate passes)

- Re-run the MOD-009 forward-return labeler + the ADR-012 corpus assessment over the **current** corpus; report N, regime/direction coverage, realized-label count, and the **per-target readiness verdict** (G0/G1/G2/G3).
- **If — and only if — a target's gate passes:** derive the new values by the ADR-012 walk-forward method, bump the correct version (`taxonomy_version` for thresholds; `decision_policy_version` for confidence weights / direction table), re-pin the affected goldens, preserve old-version replay, and **HARD PAUSE before committing the bump**.
- **Otherwise (expected): DEFER** — no value/version/direction-table change; just refresh the runbook + log the current readiness snapshot. Honor the AVOID-objective + FLAT_BAND definitions to be settled in ADR-012 before any direction-table bump.

## Writeback + constraints

- Author the new adapter file/test nodes (re-derive next-free ids); scheduling scripts are ops tooling (node only if it meets the §7.5 threshold — mirror how the Mr-Ripley scripts were handled). Update ADR-011 gate-f board + the ADR-009 amendment + MOD-010/MOD-008/feed nodes; `index.md` + `log.md`; 11 lint checks; **Neo4j re-sync**.
- Determinism unchanged: the simulator + captured operational input remain the replay path; Alpaca (calendar + execution) is the **non-replayable** plug, logged-not-replayed, default-off. No `*_version` bump from Part 1 or 2 (additive adapters); the only possible bump is a Part-3 calibration that passes its gate.
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids; cross-repo discipline (Mr-Ripley untouched).
- When done, summarize: the Alpaca plugs (+ gate-f closure), the validated-but-unregistered schedule, and the Part-3 readiness verdict (almost certainly DEFER), and **stop at the HARD PAUSE points** for my review before enabling live execution or registering the schedule.
