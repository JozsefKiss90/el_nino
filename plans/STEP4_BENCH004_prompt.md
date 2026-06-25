# Claude Code prompt — STEP 4: BENCH-004 (execution-layer byte-identical replay benchmark)

Paste the block below into a fresh Claude Code session rooted in the `el_nino` repo (after the INT-011 `fill()`-port reconciliation has landed).

---

Build **STEP 4** of the execution epoch: the **BENCH-004** byte-identical sequence-replay benchmark — the committed golden artifact + benchmark node that formally **closes ADR-011 §7 gate (d)** and seals the simulator epoch as traceable replay evidence. This is a benchmark/verification slice over the **existing, green** STEP-2 code: **do not change any `src/execution` logic or any contract.** If the benchmark surfaces a determinism defect, **STOP and report it** — never adjust outputs or rounding to force a pass. Pause for my review when the benchmark + writeback are done.

## Step 0 — read governance + precedents; verify the precondition

1. `dev_graph/CLAUDE.md` — the End-of-Coding-Session Writeback Checklist, the 11 lint checks, the §7.5 file-node threshold, the Neo4j re-sync rule.
2. `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` — **§2 gate (d)** and **§6** (the BENCH-004 spec) and **§10** (id re-derivation). This is the authority for what BENCH-004 must prove.
3. `decisions/ADR - Execution Layer Planning.md` — **§2** (the full replay-key invariant) and **§7 gate (d)** (the gate this closes).
4. **The benchmark idiom to mirror**, read all three and copy their shape (deterministic harness → committed golden JSON → artifact-in-sync test): `benchmarks/regime/run_regime_bench.py` + `benchmarks/.../run_gold_bench.py` + the paper-runtime bench; their nodes `benchmarks/` BENCH-001/002/003; and the in-sync tests (`test_regime_bench` / `test_gold_bench` / `test_paper_runtime_bench`, TEST-009/011/017).
5. **The code under test:** `src/execution/runtime.py` (`run_sequence` — the pure replay vehicle; `run_guard` with the captured `guard_config`), `src/execution/models.py` (`PortfolioState.state_hash()`, `to_dict()`, `_PRECISION`), `src/execution/engine.py` (`execute`).
6. **The real corpus:** the consumable real snapshots MOD-007 / BENCH-003 thread (the `952cc83a…` + `05c8369d…` snapshots and the consume→…→evaluate chain). The real sequence must be grounded in these, not invented.
7. **Precondition check:** confirm the INT-011 node now documents **`fill()` as the port method** (the reconciliation from last session). If it still shows `execute()` as the port signature, **stop and tell me** — STEP 4 assumes that drift is fixed.

## Step 1 — author the benchmark + the in-sync test

**`benchmarks/execution/run_execution_bench.py`** — a deterministic, IO-light harness (mirror `run_paper_runtime_bench`):

- **Real sequence.** Build ADMIT `RuntimeDecisionRecord`s by running the real consumable snapshots through the existing chain (`consume → build_features → classify → build_decision → evaluate`), forwarding `direction` + the **D1 re-derived `instrument_price`**; thread them through `run_sequence` **twice** with the same captured `guard_config`. Assert **byte-identical** execution records (`to_dict()`) **and** identical **ending portfolio `state_hash()`** across both runs. Re-present an already-executed `source_snapshot_id` to **evidence idempotency** (once-ever: no double-fill).
- **Synthetic sequence (clearly labelled).** Exercise the full outcome space: APPROVE+LONG ⇒ fill; guard **BLOCK** ⇒ no fill + `blocked_by` attribution; non-LONG stance ⇒ no fill; duplicate snapshot ⇒ idempotent no-fill. Cover `guard_block_attribution` (which predicate blocked) and `fill_distribution`.
- **Determinism discipline:** captured `guard_config` (env-independent, ADR-011 gate c.4), no clock/network/randomness, canonical JSON (sorted keys). 
- **Emit the committed golden artifact** `benchmarks/execution/artifacts/execution_bench.json` (or the path the other benches use) with `measures: [replay_determinism, idempotency, fill_distribution, portfolio_state_hash, guard_block_attribution]`, `all_replays_byte_identical: true`, and the pinned ending `portfolio_state_hash`.

**`tests/execution/test_execution_bench.py`** — the **artifact-in-sync + determinism** test (BENCH-003 idiom): regenerate the benchmark in-memory and assert it equals the committed `execution_bench.json` byte-for-byte (drift ⇒ fail), plus the real-replay byte-identical assertion and the idempotency assertion. Keep the full prior suite green; `mypy --strict` + `ruff` clean on the new files.

## Step 2 — writeback (per the CLAUDE.md checklist)

- **Create `benchmarks/Execution Layer Benchmark.md` (BENCH-004)** — `type: benchmark_result`, re-derived canonical_id **BENCH-004**, `evidence: [code, benchmark]`, `measures: [...]` as above; relationships: `### Validated By` / measures → `[[Execution]]` (MOD-008), `[[Execution Record Schema]]` (SCHEMA-014), `[[Portfolio State Schema]]` (SCHEMA-015); `Justified By → [[ADR - Execution Layer Planning]]`.
- **Create the leaf nodes** (re-derive next-free ids from `index.md`): a file node for `run_execution_bench.py` (**FILE-029+**) and a test node for `test_execution_bench` (**TEST-021+**) per the §7.5 threshold; set `covers`/`module`; add them to MOD-008's `related_tests`/`related_files`.
- **Update node bodies:** MOD-008 / SCHEMA-014 / SCHEMA-015 — record that gate (d) is closed and reference BENCH-004; add the `Validated By → [[Execution Layer Benchmark]]` edges.
- **Reconcile the ADR-011 §7 gate board to actual state** (it still reads "all six OPEN", now stale): mark **gate (d) Closed** (closing artifact = BENCH-004), and reconcile (a)/(b)/(c)/(e) to **Closed** with their actual closing artifacts from STEP 1/2 (INT-011; FillModelConfig; the orchestrator guard-wiring; SCHEMA-015), leaving **(f) deferred** (Alpaca adapter, ADR-011 §5). Bump ADR-011 `updated`. (Body/gate-board edit only — `status` stays `active`, canonical_id unchanged.)
- **`index.md`:** benchmark_result 3→4, file/test/total counts refreshed, coverage line, dated Statistics line, `Last updated`.
- **`log.md`:** append `## [<today>] bench | STEP 4 — BENCH-004 execution-layer replay benchmark (gate d closed)` (Nodes Created / Code / Verification / Metrics / Deferred).
- **Run the 11 lint checks** on touched nodes (report each ✓) and **re-sync Neo4j** (`python dev_graph/sync_to_neo4j.py --clear`); record new node/edge counts.

## Constraints

- **No change to `src/execution` logic or any contract** — this is a benchmark over green code. A determinism failure is a finding to report, not to mask.
- MUST NOT modify `wiki/**` or `raw/**` (CON-001); canonical_id immutable; re-derive all ids from `index.md` (do not assume FILE/TEST/BENCH numbers).
- Keep the Alpaca adapter (STEP 5 / gate f) **out of scope** — deferred.
- When done, summarize the benchmark results (byte-identical replay, idempotency, the pinned state hash, the distributions) and **stop for my review** before STEP 5.
