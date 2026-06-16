# Claude Code prompt — promote ADR-011 to active + author the implementation plan

Paste the block below into a Claude Code session rooted in the `el_nino` repo.

---

Two tasks, in order: **(A)** promote **ADR-011 (Execution Layer Planning)** from `draft`/"Proposed" to `active`/"Accepted" with full writeback; **(B)** author the epoch's **implementation plan** as a STEP-0 brief (a design doc, **not** dev_graph nodes and **not** code). Promotion accepts the boundary record as governing; it does **not** close the §7 Creation Gates — those are closed by the design slice the plan describes. **Stop for my review after both are done; author no contract nodes and no `src/`/`tests/` code.**

## Step 0 — read governance first

1. `dev_graph/CLAUDE.md` — frontmatter schema, writeback checklist, the 11 lint checks, Neo4j re-sync rule.
2. `decisions/ADR - Execution Layer Planning.md` (ADR-011) — the record you are promoting; the §7 Creation Gates and §6 candidate ids drive the plan.
3. The **promotion precedent**: in `dev_graph/log.md`, the 2026-06-08 entry where **ADR-008 promoted ADR-006 `draft → active`** ("Status 'Proposed' → 'Accepted'"). Mirror exactly how that status flip was recorded and logged.
4. `dev_graph/index.md` — to refresh the ADR-011 row/dates (a status change adds no node count) and re-derive ids.
5. The prior epoch **briefs** to match the plan's house style: `GOLD_DECISIONPACKET_V0_BRIEF.md`, the gold STEP-0 brief, and `EPOCH_B_CORPUS_RUNBOOK.md`. The plan is a brief in this idiom — a non-dev_graph design doc at repo root.
6. For the plan's substance, read the implementation precedents it must mirror: `modules/Paper-Trading Runtime.md` (MOD-007) + `files/engine.py.md` / `files/runtime.py.md` (the pure-core vs IO-shell shape), `modules/Guardrail Engine.md` (MOD-001) + `gates/Trade Validation Gate.md` (GATE-001) + PRED-001..005 (the guard wiring), `capabilities/Order Management.md` (CAP-005, the re-grounding target), `decisions/ADR - Implementation Substrate.md` (ADR-003, the `src/` layout + config policy), and `benchmarks/Paper-Trading Runtime Benchmark.md` (BENCH-003, the replay-benchmark idiom).

## Task A — promote ADR-011 to active

In `decisions/ADR - Execution Layer Planning.md`:
- Frontmatter: `status: draft → active`; `updated: 2026-06-16` (keep `decision_status: active`, `created` unchanged).
- `## Status` section: "**Proposed**" → "**Accepted** — 2026-06-16 (promoted at checkpoint review)", preserving the rest.

Housekeeping (the two open loose ends — do both):
- **ADR-008 reciprocal backlink:** ADR-011 lists `[[ADR - Gold Decision Confidence Semantics]]` in `related_decisions`, but ADR-008 has no reciprocal link. Add `[[ADR - Execution Layer Planning]]` to ADR-008's `related_decisions` and bump its `updated` (no body/semantic change), matching the ADR-004/006/009 backlink pattern already applied.
- **`source_paths: ["ultimateplan.md"]`:** verify the file exists at the path the source_paths convention implies. If it exists, leave it; if not, either correct the path or drop the entry (admissibility check #6 requires source_paths to resolve or be explicitly external).

Writeback (governance slice — no code):
- `index.md`: refresh the ADR-011 row if its summary should note "Accepted"; set `Last updated` / dated Statistics line as needed (status flip ⇒ **no** node-count change; coverage stays 160/160).
- `log.md`: append `## [2026-06-16] decision | ADR-011 promoted draft→active (Accepted)` — record the status flip, the ADR-008 backlink, the source_paths resolution, and that Creation Gates remain **open** (acceptance ≠ gate closure).
- Run the **11 lint checks** on touched nodes (ADR-011, ADR-008) and report each ✓.
- **Re-sync Neo4j** (`python dev_graph/sync_to_neo4j.py --clear`) — a status property changed; record new node/edge counts.

## Task B — author the implementation plan (STEP-0 brief, not nodes/code)

Create `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` at repo root (a design doc outside the dev_graph — like the prior epoch briefs; create **no** schema/module/interface/capability/gate/file/test nodes and **no** `src/`/`tests/` code). Organize it as the staged slice that **closes the six §7 Creation Gates, then builds contract-first**, with explicit review checkpoints. It must include:

1. **Gate-closing design (§7 a–f), one section each, each ending in a concrete artifact that flips the gate Open→Closed:**
   - **(a) Execution interface / port (INT-011 candidate).** Specify the signature both adapters implement — consumes an **ADMIT** `[[Runtime Decision Record Schema]]` (SCHEMA-012) + prior portfolio state + execution config + fill model; returns an execution/fill record + new portfolio state. Never consumes a raw gold packet or snapshot.
   - **(b) Fill-simulation model (`fill_model_version`).** A deterministic, seeded fill/slippage policy (in the `RuntimePolicyConfig`/`DecisionPolicyConfig` idiom); define inputs (e.g. instrument price from the snapshot lineage), the slippage function, and fold `fill_model_version` into the replay key.
   - **(c) Guard-wiring.** Exactly how `[[Trade Validation Gate]]` (GATE-001) + PRED-001..005 are invoked in the pipeline — inputs, ordering, fail-closed block attribution on the execution record — **without the execution core importing `src/risk`** (bounded-context hygiene per ADR-009 §3; the orchestrator calls `GuardrailEngine.validate()` before execute()).
   - **(d) Execution-determinism replay requirement.** Pin the full §2 invariant (extended replay key + explicit prior/new portfolio state) and a planned **byte-identical sequence-replay benchmark** (BENCH-004 candidate, BENCH-003 idiom).
   - **(e) Portfolio/position state model (SCHEMA-015 candidate).** Per-instrument quantity / avg_cost / realized & unrealized P&L (mark-to-snapshot), append-only executions history keyed by `source_snapshot_id`, `state_version`; append-only self-describing persistence in the ADR-009 §5 ledger idiom.
   - **(f) Alpaca-adapter boundary.** Credential isolation per KA-008 (keys in env/`.secrets` only, withdrawals disabled, no secret in agent-readable memory) + non-replayable IO quarantine (live runs logged, never replayed, never in benchmarks). Flag this gate as **deferrable** per ADR-011 §5.

2. **Contract-first authoring order** (the future nodes, candidate ids re-derived from index.md, none reserved/created in the plan): INT-011 → SCHEMA-014 (execution/fill) + SCHEMA-015 (portfolio state) → MOD-008 (execution) + MOD-009 (portfolio) → the **deterministic simulated-broker adapter first**, Alpaca paper adapter deferred (MOD-010/MOD-011 or files) → optional EVT-001 (first `events/` occupant) → **re-ground CAP-005** (retire the deprecated `Depends On [[Signal Generation]]`, resolve the node-less `Execution API` placeholder to INT-011) per ADR-011 §4; confirm whether a new execution **capability** under SYS-002 is needed or CAP-005 is re-grounded in place, and state the choice.

3. **Code slices** (per ADR-003): `src/execution/...` mirroring `module_path`, stdlib frozen dataclasses, zero runtime deps, fail-closed config; pure fill-simulator core + thin IO adapter shell (mirroring MOD-007 `engine.py`/`runtime.py`); Alpaca adapter isolated behind the port.

4. **Tests + benchmark:** determinism/idempotency unit tests, guard-wiring fail-closed tests, golden fixtures grounded in the real snapshots, and the BENCH-004 byte-identical sequence-replay benchmark.

5. **Writeback** at each code slice per the CLAUDE.md checklist (file/test nodes, module/capability status bumps, index/log, 11 lint checks, Neo4j re-sync).

6. **Sequencing, dependencies & checkpoints:** simulator-first; Alpaca adapter deferred or parallel to epoch (b) calibration; decoupled from DEBT-01 (closed). Mark explicit **pause-for-review checkpoints** (mirroring the gold/runtime slices that paused at a STEP checkpoint before code). Carry forward the ADR-011 §Consequences risks + mitigations.

## Constraints

- MUST NOT modify `wiki/**` or `raw/**` (CON-001); `canonical_id` immutable; no in-place reclassification.
- Task A changes only ADR-011 + ADR-008 (+ index/log) and re-syncs Neo4j. Task B creates only the root brief — **no dev_graph nodes, no schema freeze, no `src/`/`tests/` code.**
- Re-derive all candidate ids from `index.md`; never assume or reuse a reserved/deprecated id.
- When done, summarize both deliverables and **stop for my review** before any contract authoring or implementation.
