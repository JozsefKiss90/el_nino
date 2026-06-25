---
type: module
canonical_id: MOD-010
status: active
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-23
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/orchestration/engine.py"
related_files:
  - "[[models.py (orchestration)]]"
  - "[[config.py (orchestration)]]"
  - "[[engine.py (orchestration)]]"
  - "[[runtime.py (orchestration)]]"
  - "[[live_runtime.py]]"
  - "[[operational_feed.py]]"
  - "[[alpaca_clock_feed.py]]"
  - "[[run_chain_bench.py]]"
related_tests:
  - "[[test_chain_engine]]"
  - "[[test_chain_determinism]]"
  - "[[test_chain_bench]]"
  - "[[test_operational_feed]]"
  - "[[test_alpaca_clock_feed]]"
  - "[[test_live_runtime]]"
  - "[[test_operator_halt]]"
  - "[[test_replayable_fence]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
module_name: "orchestration"
module_path: "src/orchestration"
responsibility: "Thread a banked snapshot through the full Layer-3 chain (consume→…→execute→persist); paper-only composition root"
depends_on:
  - "[[Snapshot Consumer]]"
  - "[[Feature Builder]]"
  - "[[Market Regime Classifier]]"
  - "[[Gold Decision Builder]]"
  - "[[Paper-Trading Runtime]]"
  - "[[Execution]]"
  - "[[Guardrail Engine]]"
provides: []
---

# Chain Orchestrator

## Definition

The **end-to-end composition root** for Layer-3: it threads a banked [[Layer 2 Snapshot Schema]]
(SCHEMA-001) through every already-governed stage in one deterministic call —
`consume → build_features → classify → build_decision → evaluate → [GATE-001 guard] → execute → persist`
— producing the full record set ([[Feature Vector Schema]], [[Regime Classification Schema]],
[[Gold DecisionPacket v0 Schema]], [[Runtime Decision Record Schema]], [[Execution Record Schema]]) plus a
new [[Runtime Ledger Schema]] + [[Portfolio State Schema]]. It is the *"full chain-orchestrator
integration"* the STEP-4 execution writeback deferred (forwarding `direction`/`instrument_price` from the
in-hand FeatureVector). **Pure composition**: it changes no layer's logic, no contract, and no `*_version`.

## Purpose

Make the whole Layer-3 lineage runnable as one deterministic, replay-safe call so a banked snapshot can be
admitted and (paper-)executed in a single operational step — without re-deriving anything the chain
already holds. It forwards `packet.direction` and the in-hand `FeatureVector.value("gold_price")` straight
into `execute` (the ADR-011 **D1 in-hand path**; re-derivation is only the execution-only replay fallback)
and runs the GATE-001 guard **in the orchestrator** before `execute` (ADR-009 §3 / ADR-011 gate c).

## Architecture Role

A cross-cutting composition module under [[Trading Engine]] (SYS-002). It does **not** own a new
capability — it *threads* the existing capability chain [[Feature Engineering]] (CAP-002) →
[[Market Regime Classification]] (CAP-019) → [[Gold Decision Generation]] (CAP-020) →
[[Paper-Trade Admission]] (CAP-021) → [[Order Management]] (CAP-005, via [[Execution]] MOD-008), wiring
[[Trade Validation Gate]] (GATE-001) at the trade boundary. It is the executable end-to-end run of the
PaperTrading state of the [[System Lifecycle]] (WF-001). Realizes the [[Pipeline Pattern]] (PAT-004);
originates from [[Paper Trading Validation]] (KA-010). Governed by [[ADR - Paper-Trading Runtime Planning]]
(ADR-009) + [[ADR - Execution Layer Planning]] (ADR-011). It is the **only cross-context importer** (incl.
`src/risk`); the per-layer pure cores stay clean.

## Inputs (or Dependencies)

- A loaded, consumable `Snapshot` (the shell calls `consume()`); the prior `RuntimeLedger` + the prior
  `PortfolioState` (explicit state in).
- A captured `OperationalInput` and a captured `GuardrailConfig` (never read live on the replay path), plus
  the per-layer versioned configs (regime / decision / runtime / execution / fill-model).

## Outputs (or Provides)

- A `ChainResult` bundling the five typed records + the new `RuntimeLedger` + `PortfolioState`. `ChainResult`
  is an in-memory aggregate of already-governed records — **not** a new schema or `*_version`. The persisted
  artifacts are the existing ledger (SCHEMA-013) + portfolio (SCHEMA-015).

## Constraints

- **Pure composition** — changes no layer's logic, no contract, no `*_version`; only threads existing pure
  cores and confines IO to the shell.
- **Determinism** — the full replay key is the union of every composed layer's version axis + the captured
  guard / operational fingerprints + the prior ledger/portfolio state ⇒ identical records + new state.
- **In-hand path (ADR-011 D1)** — forwards `packet.direction` + `fv.value("gold_price")` into `execute`;
  never re-derives them by reloading the snapshot.
- **Execution gated on ADMIT** — `execute()` requires an ADMIT record, so the guard + `execute` run only on
  ADMIT; on HOLD/REJECT there is no `ExecutionRecord` and the portfolio is unchanged. The ledger always
  advances by one entry.
- **Bounded-context hygiene (ADR-009 §3 / ADR-011 gate c)** — only this orchestrator imports `src/risk`
  (the GATE-001 guard seam, via `run_guard`); `evaluate()` and `execute()` stay risk-free.
- **End-to-end idempotency** — re-presenting a processed `source_snapshot_id` cannot double-admit (MOD-007
  `duplicate_ok` once-ever) or double-fill (MOD-008 portfolio `has_execution` once-ever).

## Implementation Notes

- `engine.py` — pure `run_chain()`: features → regime → gold decision (`guards=None`, wrap-not-enrich;
  forwarded `snapshot_guards` + `as_of`) → `evaluate` → (on ADMIT) `run_guard` then `execute`. No IO /
  clock / randomness. Fail-closed `ChainContractError` if an ADMIT lacks an in-hand `gold_price` (defensive;
  unreachable for a consumable snapshot — gold is a Tier-1 series, not a regime required-feature).
- `runtime.py` — the IO shell: `run_once` (consume → load ledger + portfolio → `run_chain` → persist
  **portfolio-then-ledger** atomically, temp-file + `os.replace`, for crash-consistency) + the pure
  `run_sequence` replay driver (the BENCH-006 vehicle) + `find_latest_snapshot` + the `python -m
  orchestration.runtime` CLI. Reuses MOD-007 `load_ledger`/`persist_ledger` + MOD-008
  `load_portfolio`/`persist_portfolio`. The CLI gained an **additive** `--operational-feed-source
  {calendar,alpaca}` flag (default `calendar` — behaviour unchanged; `run_once`/`run_sequence` contracts
  untouched) that lazily wires the live [[alpaca_clock_feed.py]] plug on opt-in.
- `alpaca_clock_feed.py` ([[alpaca_clock_feed.py]] FILE-037) — the live Alpaca clock/calendar
  `OperationalFeed` plug, **default-OFF**, closing the v0 holiday-calendar gap; read on the live path only
  and captured/quarantined exactly like the deterministic feed (ADR-009 amendment 2026-06-18).
- **Scheduling scripts** (ops tooling — no file nodes, mirroring how the Mr-Ripley scripts are handled):
  `scripts/daily_chain_run.ps1` runs the latest banked Mr-Ripley snapshot through `run_once` on the
  **deterministic simulator** + the operational calendar feed (captured), persisting the el_nino ledger +
  portfolio (idempotent); `scripts/register_daily_chain_task.ps1` registers the recurring 23:45 task
  (sequenced after the Mr-Ripley 23:00 EOD job). Validated by a single manual `daily_chain_run.ps1`
  invocation; **registering the recurring task is an operator HARD-PAUSE action** (see
  `CHAIN_ORCHESTRATOR_RUNBOOK.md` §6).
- `config.py` — the captured `DEFAULT_OPERATIONAL_INPUT` (v0 configured "venue open" assumption — distinct
  from `load_operational`'s default-closed file fallback) + `DEFAULT_GUARD_CONFIG` (captured GATE-001 limits;
  the operational CLI may instead `--guard-from-env`).
- `models.py` — `ChainResult` (frozen) + `to_dict()` (deterministic projection over all five records + the
  two ending state hashes — the byte-identical replay vehicle) + `ChainContractError`.
- 27 orchestration tests (TEST-023..025) + the live-feed tests (TEST-026/027) green; full suite **986**
  green (after the Alpaca live-plug slice + the adversarial-review hardening of the paper-only host check);
  `ruff` clean; `mypy --strict` clean on `src/orchestration` + the new plug files (the only `mypy` errors
  remain the 2 pre-existing lambda-inference warnings in MOD-004 `feature_builder.py`, unrelated — a named
  follow-up).
- [[Chain Orchestrator Benchmark]] (BENCH-006) — `run_chain_bench.py` (FILE-035) + the committed golden
  `artifacts/chain_bench.json` + the in-sync [[test_chain_bench]] (TEST-025) prove end-to-end byte-identical
  replay + admission idempotency over the real corpus, carrying the full replay key.

## Open Questions

- Operational status is an explicit **captured input** (v0 configured default). The live operational feed
  is **implemented** behind that seam: the deterministic [[operational_feed.py]] (FILE-036
  `MarketCalendarFeed`) **and** the live [[alpaca_clock_feed.py]] (FILE-037 `AlpacaClockFeed`, **default-OFF**,
  env-only creds KA-008) — the latter closes the v0 holiday-calendar gap and is captured/quarantined for
  replay (ADR-009 amendment 2026-06-18). No remaining deferred feed plug.
- `cooldown_ok` remains MOD-007's **echo** of the snapshot flag; a **computed** cooldown guard is its own
  slice (it changes an admission guard's semantics).
- **Scheduling** the daily run after the EOD snapshot: the scripts are now **built + validated**
  (`scripts/daily_chain_run.ps1` ran once manually OK on the simulator path), but **registering** the
  recurring task (`scripts/register_daily_chain_task.ps1`) is an operator **HARD-PAUSE** action — not run
  here (documented in `CHAIN_ORCHESTRATOR_RUNBOOK.md` §6).
- The real corpus is monochromatic `RESTRICTIVE_RATES → AVOID` ⇒ a deterministic ADMIT + no-fill; the fill
  path is covered by BENCH-004's synthetic execution sweep, not reproduced end-to-end here.

## Relationships

### Depends On
- [[Snapshot Consumer]]
- [[Feature Builder]]
- [[Market Regime Classifier]]
- [[Gold Decision Builder]]
- [[Paper-Trading Runtime]]
- [[Execution]]
- [[Guardrail Engine]]

### Contains
- [[models.py (orchestration)]]
- [[config.py (orchestration)]]
- [[engine.py (orchestration)]]
- [[runtime.py (orchestration)]]
- [[operational_feed.py]]
- [[alpaca_clock_feed.py]]

### Validated By
- [[test_chain_engine]]
- [[test_chain_determinism]]
- [[test_chain_bench]]
- [[test_operational_feed]]
- [[test_alpaca_clock_feed]]
- [[Chain Orchestrator Benchmark]]

### Realizes
- [[Pipeline Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
- [[ADR - Execution Layer Planning]]

### Originates From
- [[Paper Trading Validation]]
