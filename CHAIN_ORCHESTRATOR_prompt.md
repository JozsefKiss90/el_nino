# Claude Code prompt — end-to-end chain orchestrator (integration slice)

Paste the block below into a fresh Claude Code session rooted in the `el_nino` repo.

---

Build the **end-to-end chain orchestrator** — the deterministic composition root that threads a banked snapshot all the way through `consume → build_features → classify → build_decision → evaluate (admission) → execute → persist`, forwarding `direction` and the `instrument_price` (the in-hand `gold_price`) from the `FeatureVector`/packet rather than re-deriving them. This is the "full chain-orchestrator integration" that the STEP-4 execution writeback explicitly deferred. **It is pure composition of already-governed layers: it changes no layer's logic, no contract, and no `*_version`.** Write a short brief, build it, prove end-to-end replay determinism with a benchmark, then **stop for my review before wiring any schedule** (scheduling is an operator action).

## Step 0 — read governance + the layers it composes

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, §7.5 file-node threshold, the `workflow` node type.
2. The two ADRs this slice composes (no new contract/ADR is created): `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009 — `evaluate`/`run_once`/`run_sequence`, the append-only ledger, ADR-009 §3 bounded-context hygiene) and `decisions/ADR - Execution Layer Planning.md` (ADR-011 — the port/adapter split, **D1 in-hand-vs-re-derive**, gate c.4 captured guard config). Note ADR-011 D1 explicitly says the full-chain path forwards the in-hand `FeatureVector` `gold_price`; re-derivation is only the execution-*only* replay fallback.
3. The deferred-item note in `dev_graph/log.md` (STEP-4 writeback): "full chain-orchestrator integration (re-deriving price/direction from the in-hand FeatureVector)" — this is what you're implementing.
4. **The per-layer pure cores + IO shells you will compose** (read their real signatures, do not change them): `src/snapshot/snapshot_consumer/` (`consume`), `src/features/feature_builder/` (`build_features`, `gold_price`), `src/regime/regime_classifier/` (`classify`), `src/gold/decision_builder/` (`build_decision`, `SnapshotGuards`), `src/gold/paper_runtime/` (`evaluate`, `RuntimeLedger`, `OperationalInput`, `Verdict`), `src/execution/` (`engine.execute`, `runtime.run_once`/`run_sequence`, `PortfolioState`). The two existing `run_once` shells (MOD-007, MOD-008) are the pattern to extend.
5. The replay-benchmark idiom — `benchmarks/.../run_paper_runtime_bench.py` (BENCH-003) and `benchmarks/execution/run_execution_bench.py` (BENCH-004) — and `workflows/System Lifecycle.md` (WF-001, a candidate home).
6. The downstream + operational context: the MOD-009 forward-return labeler (the consumer of the decision+execution records this produces), `EPOCH_B_CORPUS_RUNBOOK.md`, and the daily-EOD job (producer = Mr-Ripley, a **separate repo**; el_nino consumes — keep all changes in el_nino).

## Step 1 — short integration brief, then build

Write `CHAIN_ORCHESTRATOR_RUNBOOK.md` (repo root, in the `EPOCH_B_CORPUS_RUNBOOK.md` idiom): the end-to-end data flow, the full replay key, the determinism guarantees, how the run is invoked, and how it would be hooked after the daily EOD snapshot (document it — do **not** schedule it here). Then build, under `src/orchestration/` (or the path matching the chosen module node):

- **A pure full-chain core** — given a loaded `Snapshot` + prior `RuntimeLedger` + prior `PortfolioState` + a **captured** `GuardrailConfig` + an **explicit** `OperationalInput` + the layer configs ⇒ the full record set (`FeatureVector`, `RegimeClassification`, `GoldDecisionPacket`, `RuntimeDecisionRecord`, `ExecutionRecord`) + new `RuntimeLedger` + new `PortfolioState`. Pure: no IO/clock/randomness. It forwards `packet.direction` and `fv.value("gold_price")` straight into `execute` (the in-hand path, ADR-011 D1) and runs the GATE-001 guard in the orchestrator before `execute` (ADR-009 §3 / ADR-011 gate c — only the orchestrator imports `src/risk`).
- **A thin IO shell** — `run_once` (load snapshot file + load ledger + load portfolio → core → persist ledger + portfolio atomically, temp-file + `os.replace`) and a pure `run_sequence` (thread ledger+portfolio over an ordered list of snapshots in memory — the benchmark vehicle, no IO). Mirror MOD-007/MOD-008 exactly.
- **Operational status as an explicit captured input** (not hardcoded inside, not read live on the replay path) — so the live-feed adapter can be added later behind that seam. v0 uses a configured default `OperationalInput`, passed as a parameter.
- **End-to-end idempotency** — re-running an already-processed `source_snapshot_id` must not double-admit or double-fill (inherited from the MOD-007 ledger + MOD-008 portfolio once-ever guards); assert it holds through the whole chain.
- A CLI entry that runs the latest banked consumable snapshot through `run_once` and persists.

## Step 2 — full-chain replay benchmark

`benchmarks/orchestration/run_chain_bench.py` + committed golden + an artifact-in-sync test (BENCH-003/004 idiom; re-derive the node id, likely **BENCH-006**):

- **Real sequence:** thread the real consumable snapshots through `run_sequence` **twice** → byte-identical **all** records (feature/regime/packet/runtime/execution) **and** identical ending ledger + portfolio `state_hash`; re-present to evidence end-to-end idempotency.
- Carry forward the honest caveat (as BENCH-004 did): the real corpus is monochromatic RESTRICTIVE_RATES → AVOID, so the end-to-end real path is a deterministic **no-fill**; the fill path is already covered by BENCH-004's synthetic sweep, so this bench proves **end-to-end replay determinism + idempotency**, not a real fill.
- `measures` should include the full replay key (the union of all layer versions: `feature_schema_version`, `taxonomy_version`, `decision_policy_version`, `runtime_policy_version`, `fill_model_version`, `execution_policy_version`, + `guard_config_fingerprint`). `mypy --strict` + `ruff` clean; full prior suite green.

## Step 3 — writeback

- Author the orchestrator node(s) (re-derive next-free ids): a thin chain-orchestrator **module** (likely **MOD-010**) + file/test nodes (FILE-031+, TEST-023+), and the **BENCH-006** node; consider realizing **WF-001 System Lifecycle** (this is the end-to-end run of the lifecycle) and link it. `Justified By → [[ADR - Paper-Trading Runtime Planning]]` + `[[ADR - Execution Layer Planning]]`.
- **No contract / `*_version` / decision-path change.** Record that operational status is an explicit captured input (live feed deferred) and that cooldown remains MOD-007's echo (computed cooldown is a named follow-up, not this slice).
- `index.md` (deltas) + `log.md` entry (the integration, the full replay key, the benchmark result, the named follow-ups) + 11 lint checks on touched nodes + **Neo4j re-sync** (`python dev_graph/sync_to_neo4j.py --clear`).

## Out of scope (named follow-ups — do NOT build here)

- **Live operational-status feed** (the IO adapter behind the explicit `OperationalInput` seam).
- **Computed cooldown guard** (MOD-007's echoed `cooldown_ok` → computed from the ledger; its own slice, since it changes an admission guard's semantics).
- **Scheduling** the daily run (operator action — documented in the runbook, not wired here).
- STEP-5 Alpaca adapter; the calibration bumps (G1/G2/G3 — data-gated).

## Constraints

- **Pure composition** — change no layer's logic, no contract, no `*_version`; the orchestrator only threads existing pure cores and confines IO to its shell.
- **Determinism** — full replay key as above; captured guard config + explicit operational input (never read live on the replay path); `run_sequence` byte-identical on replay; end-to-end idempotency.
- **Bounded-context hygiene** — only the orchestrator imports across contexts (incl. `src/risk` for the guard); the per-layer pure cores stay clean.
- **Cross-repo discipline** — all changes in el_nino; Mr-Ripley is the upstream producer, untouched.
- MUST NOT modify `wiki/**` or `raw/**` (CON-001); canonical_id immutable; re-derive ids from `index.md`.
- When done, summarize the data flow, the replay/idempotency evidence, and the chosen node placement, and **stop for my review** before any scheduling.
