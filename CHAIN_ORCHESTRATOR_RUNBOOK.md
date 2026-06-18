# Chain Orchestrator Runbook

**Status:** built 2026-06-18 (MOD-010). **Scope:** the end-to-end Layer-3 composition root — pure
threading of already-governed layers, plus a thin IO shell + CLI. **No** new contract, schema,
interface, gate, or `*_version`; no layer's logic changes. **Owner repos:** consumer/governance =
`C:\Code\el_nino` (this layer); producer = `C:\Code\Mr-Ripley` (Layer-2 Truth, untouched — see
[EPOCH_B_CORPUS_RUNBOOK.md](EPOCH_B_CORPUS_RUNBOOK.md)).

This is the "full chain-orchestrator integration" the STEP-4 execution writeback deferred
(dev_graph/log.md: *"full chain-orchestrator integration (re-deriving price/direction from the
in-hand FeatureVector)"*). It threads a banked Layer-2 snapshot through every Layer-3 stage in one
deterministic call and persists the two pieces of state (the runtime ledger + the portfolio).

---

## 1. What it is (and is not)

The orchestrator is the **composition root** that wires the per-layer pure cores into one chain. It
**changes no layer's logic, no contract, and no `*_version`** — it only *threads* existing pure
functions and confines IO to its shell. Concretely, for one snapshot it runs:

```
consume → build_features → classify → build_decision → evaluate → [GATE-001 guard] → execute → persist
```

forwarding `packet.direction` and the in-hand `FeatureVector.value("gold_price")` straight into
`execute` (the ADR-011 **D1 in-hand path** — never re-deriving them by reloading the snapshot), and
running the GATE-001 guard **in the orchestrator** before `execute` (ADR-009 §3 / ADR-011 gate c —
only the orchestrator imports `src/risk`; the per-layer pure cores stay clean).

It is **not** a scheduler, **not** a live broker, **not** a new decision path. It is `paper_only`.

---

## 2. End-to-end data flow

| Stage | Module | Pure core | In → out |
|---|---|---|---|
| consume | MOD-003 Snapshot Consumer | `consume(path)` | snapshot JSON → `Snapshot` (or `None` if not consumable) |
| features | MOD-004 Feature Builder | `build_features(snap)` | `Snapshot` → `FeatureVector` (SCHEMA-009) |
| regime | MOD-005 Regime Classifier | `classify(fv)` | `FeatureVector` → `RegimeClassification` (SCHEMA-010) |
| decision | MOD-006 Gold Decision Builder | `build_decision(fv, rc, snapshot_guards, as_of)` | → `GoldDecisionPacket` (SCHEMA-011), `guards=None` (wrap-not-enrich) |
| admission | MOD-007 Paper-Trading Runtime | `evaluate(packet, ledger, op_input, cfg)` | → `RuntimeDecisionRecord` (SCHEMA-012) + new `RuntimeLedger` (SCHEMA-013) |
| guard | GATE-001 Trade Validation Gate | `run_guard(direction, portfolio, guard_config)` | portfolio context → `GuardResult` (APPROVE/BLOCK) |
| execute | MOD-008 Execution | `execute(admit, direction, price, portfolio, guard_result, …)` | → `ExecutionRecord` (SCHEMA-014) + new `PortfolioState` (SCHEMA-015) |

**Forwarded provenance** (the orchestrator holds the snapshot + FeatureVector, so it forwards rather
than re-derives):
- `SnapshotGuards` ← `snap.guards.{data_ok,freshness_ok,cooldown_ok}`, and `as_of` ← `snap.clock_ts`,
  copied verbatim onto the packet at build time (ADR-009 §3). The builder never reads the raw snapshot.
- `direction` ← `packet.direction`; `instrument_price` ← `fv.value("gold_price")` — the **in-hand**
  values handed to `execute` (ADR-011 D1). The ADMIT record carries neither; the orchestrator supplies
  both from the lineage it holds.

**Execution is gated on ADMIT.** `execute()` requires an ADMIT record (it raises otherwise), so the
orchestrator calls the guard + `execute` **only** when the runtime verdict is `ADMIT`. On HOLD/REJECT
there is no `ExecutionRecord` (it is `None`) and the portfolio is returned unchanged. The runtime ledger
always grows by exactly one self-describing entry per evaluation (ADMIT, HOLD, or REJECT).

---

## 3. The full replay key & determinism guarantees

The core is a pure function of explicit, versioned inputs — **no IO, clock, randomness, or hidden
state**. The **full replay key** is the union of every composed layer's version axis plus the captured
guard/operational fingerprints:

```
source_snapshot_id
  + feature_schema_version
  + taxonomy_version + classifier_version + classification_trace_version
  + decision_policy_version  (+ decision_policy_fingerprint)
  + runtime_policy_version   (+ runtime_policy_fingerprint)
  + execution_policy_version (+ execution_policy_fingerprint)
  + fill_model_version       (+ fill_model_fingerprint)
  + guard_config_fingerprint           ← captured GuardrailConfig (never read from env on the replay path)
  + operational_input.fingerprint()    ← captured OperationalInput (never a live probe on the replay path)
  + prior RuntimeLedger.state_hash() + prior PortfolioState.state_hash()
  ⇒ identical (FeatureVector, RegimeClassification, GoldDecisionPacket, RuntimeDecisionRecord,
               ExecutionRecord) + identical new RuntimeLedger + new PortfolioState.
```

Guarantees, all inherited (the orchestrator adds no new version, only composes):
- **Byte-identical replay.** `run_sequence` over the same ordered snapshots from the same starting
  ledger + portfolio yields byte-identical records and identical ending `state_hash`es. Proven by
  BENCH-006 (real corpus replayed twice).
- **End-to-end idempotency.** Re-presenting an already-processed `source_snapshot_id` does **not**
  double-admit or double-fill: the MOD-007 ledger's `duplicate_ok` (once-ever on a prior ADMIT) makes
  the re-presentation REJECT → no `execute` call; and the MOD-008 portfolio's `has_execution`
  once-ever guard is a second line that prevents a double-fill even if `execute` were reached.
- **Captured, not live, on the replay path.** Both the `GuardrailConfig` and the `OperationalInput`
  are explicit captured values, fingerprinted into the records/ledger. The orchestrator never reads
  `os.environ`, the wall-clock, or a venue probe on the replay path.

---

## 4. Operational status — an explicit captured input (live feed deferred)

Operational readiness (`tradeable/venue_open/halt/degraded`) is an **explicit captured input**, passed
as a parameter — never hardcoded inside the core and never read live on the replay path. This is the
seam a future live-feed adapter plugs into (ADR-009 Non-Goal: a live operational feed is deferred).

v0 uses a **configured default** — `DEFAULT_OPERATIONAL_INPUT` (`src/orchestration/config.py`): GLD,
`tradeable=True, venue_open=True` with `as_of=None`. This is a *configured assumption* ("for paper
v0, assume the venue is open"), **distinct from** `load_operational`'s default-**closed** fallback for
an *absent/malformed file* (unknown status → fail closed, ADR-009 §3). The configured default is
explicit, fingerprinted into the ledger (auditable), and replaced — not bypassed — when the live feed
lands. Safety is preserved independently: paper-only / virtual-money, GATE-001 hard limits still
enforced, `withdrawal_disabled` (PRED-005) always on.

`cooldown_ok` remains MOD-007's **echo** of the snapshot's `cooldown_ok` (a **computed** cooldown is a
named follow-up, not this slice — it changes an admission guard's semantics).

---

## 5. How to invoke

```powershell
cd C:\Code\el_nino; $env:PYTHONPATH='C:\Code\el_nino\src'

# Run the latest banked consumable snapshot through the whole chain and persist state.
& .\.venv\Scripts\python.exe -m orchestration.runtime

# Explicit paths (snapshot file / ledger / portfolio), and optional real env hard-limits for the guard:
& .\.venv\Scripts\python.exe -m orchestration.runtime `
    --snapshot snapshot_sources\latest_snapshot.json `
    --ledger runtime\chain\runtime_ledger.json `
    --portfolio runtime\chain\portfolio_state.json `
    [--snapshot-dir <archive dir>] [--guard-from-env]

# Re-pin the BENCH-006 golden after an intentional, version-bumped change:
& .\.venv\Scripts\python.exe benchmarks\orchestration\run_chain_bench.py
```

- `--snapshot PATH` (default `snapshot_sources/latest_snapshot.json`) — the consumable snapshot to run.
- `--snapshot-dir DIR` — if given, selects the lexicographically-latest `snapshot_*.json` in `DIR`
  (clock_date sorts lexicographically) — the "latest banked" discovery for an archive directory.
- `--ledger` / `--portfolio` — state files (default under `runtime/chain/`). Created on first run.
- `--guard-from-env` — load the GATE-001 hard limits from env (`MAX_TRADE_SIZE`, … fail-closed) instead
  of the captured `DEFAULT_GUARD_CONFIG`. Recommended for any non-demonstration run.

**Fail-closed CLI behavior:** a non-consumable snapshot (absent, failed gate, forced, dry-run) prints
"nothing to do" and exits 0 (the MOD-003 *"Layer-3 outputs nothing"* contract). A structurally
malformed snapshot raises loudly (`SnapshotContractError`). A corrupt ledger/portfolio raises loudly.

**Crash-consistent persistence.** The shell persists the **portfolio first, then the ledger** (each via
temp-file + `os.replace`). A crash between the two leaves a "redo" state — the ledger lacks the ADMIT,
so a re-run re-admits, but the portfolio's `has_execution` once-ever guard prevents a double-fill. (The
reverse order could strand an admitted-but-never-filled snapshot, since `duplicate_ok` would then skip
it forever.)

---

## 6. How it would be hooked after the daily EOD snapshot (documented — NOT scheduled here)

Scheduling is an **operator action**; this slice wires nothing. The intended hook, once an operator
chooses to enable it:

1. The Mr-Ripley `MrRipley-Layer2-DailyEOD` task banks one immutable consumable snapshot per day
   (EPOCH_B_CORPUS_RUNBOOK.md §3) and archives it under
   `C:\Code\Mr-Ripley\runtime\snapshots\snapshot_<clock_date>__<id8>.json`.
2. A **separate, later** el_nino scheduled task would run **after** the EOD job, e.g.
   `python -m orchestration.runtime --snapshot-dir C:\Code\Mr-Ripley\runtime\snapshots
   --guard-from-env`, threading that day's snapshot through the chain and appending to the el_nino
   runtime ledger + portfolio. Because `consume()` fail-closes and the chain is idempotent on
   `source_snapshot_id`, a missed/duplicate run is safe (no double-admit / double-fill).
3. The banked decision + execution records are what the **MOD-009 Gold Forward-Return Labeler**
   consumes downstream for the ADR-012 G3 calibration measurement.

Do not register the task as part of this slice. When an operator wants it, register it in the idiom of
`register_daily_task.ps1`, sequenced after the EOD job, and verify with `Get-ScheduledTaskInfo`.

---

## 7. Out of scope (named follow-ups — not built here)

- **Live operational-status feed** — the IO adapter behind the explicit `OperationalInput` seam (§4).
- **Computed cooldown guard** — MOD-007's echoed `cooldown_ok` → computed from the ledger; its own
  slice (it changes an admission guard's semantics).
- **Scheduling the daily run** — operator action (§6).
- **STEP-5 Alpaca paper adapter**; the **G1/G2/G3 calibration bumps** (data-gated, ADR-012).

---

## 8. Provenance — what the real corpus proves today

The real consumable corpus is monochromatic **RESTRICTIVE_RATES → AVOID** (a non-LONG stance), so the
end-to-end real path is a deterministic **ADMIT + no-fill** (the execution engine fills only an approved
LONG on a fresh snapshot). BENCH-006 therefore proves **end-to-end replay determinism + admission
idempotency** (re-presentation REJECTs on `duplicate_ok`; the portfolio never double-fills), **not** a
real fill. The fill path is covered by BENCH-004's synthetic execution sweep. This is the same honest
caveat BENCH-004 carries forward — the orchestrator changes none of it.
