# EXECUTION_LAYER_IMPLEMENTATION_PLAN

**Slice:** Execution / portfolio layer — the first money-shaped layer. Closes the six [[ADR - Execution Layer Planning]] (ADR-011) §7 Creation Gates, then builds contract-first: a deterministic offline fill-simulator core behind a port (INT-011), an execution/fill record (SCHEMA-014) + portfolio/position state (SCHEMA-015), the execution module (MOD-008) + portfolio module (MOD-009), GATE-001 guard-wiring, BENCH-004 replay benchmark, and a deferred Alpaca-paper adapter.
**Date:** 2026-06-16. **Status:** STEP 0 — context-discovery complete; gates Open; nothing implemented.
**Type:** Gate-closing design + contract + implementation plan. ADR-011 is **Accepted** (governing); the §7 gates remain **Open** and are closed by the design in §2 below.

This brief is the STEP-0 deliverable for the execution epoch. It records the gate-closing design, the architectural reconciliation it rests on, and the staged build — established via dev_graph + code discovery **before any contract node or `src/`/`tests/` code is written**. It mirrors `GOLD_DECISIONPACKET_V0_BRIEF.md`, `REGIME_IMPLEMENTATION_BRIEF.md`, and `GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md`, and is a **non-dev_graph design doc at repo root** (like the prior epoch briefs and `EPOCH_B_CORPUS_RUNBOOK.md`) — it creates no schema/module/interface/capability/gate/file/test node and no code.

> **Governing constraint.** ADR-011 §7 forbids authoring any normative execution schema/module/interface until **all six** gates pass. This plan's §2 is the gate-closing design; §3–§8 are the post-gate build. Acceptance of ADR-011 (boundary record) ≠ gate closure — the gates close on review of §2, at the **CONTRACT CHECKPOINT** (§8), not before.

---

## 1. Objective

Build the layer that **acts on an ADMIT**. Today the Layer-3 lineage ends at [[Paper-Trading Runtime]] (MOD-007): `SCHEMA-001 → consume → build_features → classify → build_decision → evaluate` yields an ADMIT/HOLD/REJECT [[Runtime Decision Record Schema]] (SCHEMA-012) + an append-only ledger — but nothing *executes* an ADMIT. This epoch adds the **port/adapter execution layer** (ADR-011 §2): a deterministic offline **fill-simulator** is the canonical replay-safe core (all tests/benchmarks/replay run against it); the **Alpaca Paper** API is an optional, explicitly **non-replayable** live adapter behind the same port, never on the replay path. It is **paper_only / virtual-money** (ADR-011 §3): KA-010 simulated-validation-before-live, [[Withdrawal Disabled]] (PRED-005) enforced, [[Agent Safety Principles]] (KA-008) credential isolation; **live-money trading is a Non-Goal**.

The layer extends MOD-007's proven shape — a **pure `evaluate()`-style core** ([[engine.py]]) confined IO to a **`run_once`/`run_sequence` shell** ([[runtime.py]]) — to execution: a pure `execute()` core, an IO adapter shell, the ledger/state discipline of ADR-009 §5, and a BENCH-003-style byte-identical replay benchmark.

---

## 2. Gate-closing design (ADR-011 §7 a–f)

Each subsection ends in the **concrete artifact** that flips its gate **Open → Closed**. Reviewing §2 *is* the gate-closing act (the CONTRACT CHECKPOINT, §8).

### Gate (a) — Execution interface / port  →  closes when the INT-011 contract is drafted

The port (candidate **INT-011**, the real node behind CAP-005's today-dangling `Execution API` placeholder) is the single signature **both adapters implement**. Illustrative shape (design sketch, not code):

```
# INT-011 "Execution API" — the port; SimulatedBrokerAdapter and AlpacaPaperAdapter both implement it
class ExecutionPort(Protocol):
    def execute(
        self,
        admit: RuntimeDecisionRecord,     # SCHEMA-012, verdict == ADMIT only (asserted; non-ADMIT is a caller bug)
        instrument_price: Decimal,        # re-derived from admit.source_snapshot_id at the orchestrator (D1) — explicit value to the pure core
        prior_portfolio: PortfolioState,  # SCHEMA-015 — explicit state IN
        guard_result: GuardResult,        # the GATE-001 outcome, forwarded as provenance (see (c)) — NOT recomputed here
        fill_model: FillModelConfig,      # versioned, fill_model_version (see (b))
        config: ExecutionPolicyConfig,    # versioned, execution_policy_version
    ) -> tuple[ExecutionRecord, PortfolioState]:   # SCHEMA-014 + the new SCHEMA-015
        ...
```

**Input boundary (ADR-011 §1/§2, mirroring ADR-009 §3):** the port consumes **only** the ADMIT `RuntimeDecisionRecord` (SCHEMA-012) + explicit re-derived inputs + prior portfolio state. It **never** consumes a raw [[Gold DecisionPacket v0 Schema]] (SCHEMA-011) or a raw [[Layer 2 Snapshot Schema]] (SCHEMA-001) — the ADMIT record already carries `source_snapshot_id`, `as_of`, and instrument identity; the **instrument price is re-derived deterministically from `admit.source_snapshot_id`** at the orchestrator (**D1** below) — **no field is added to the frozen SCHEMA-011/012 contracts**. State is **explicit in / explicit out** (ADR-009 §4), never ambient.

> **Closing artifact:** the **INT-011 interface node** (`build`-time stability `experimental`; `input_schema` = SCHEMA-012, `output_schema` = SCHEMA-014; parent capability = re-grounded CAP-005), authored contract-first at the CONTRACT CHECKPOINT. → gate (a) **Closed**.

### Gate (b) — Fill-simulation model (`fill_model_version`)  →  closes when the fill model + version are pinned

A deterministic, **seeded** fill/slippage policy in the `RuntimePolicyConfig`/`DecisionPolicyConfig` idiom (a frozen `FillModelConfig` carrying a `fill_model_version` + a `fill_model_fingerprint()` SHA-256 over the policy-defining fields, version excluded — exactly `runtime_policy_fingerprint`'s shape, MOD-007 `config.py`). Design:

- **Inputs:** the **re-derived** `instrument_price` (the snapshot's gold/GLD price, recovered from `admit.source_snapshot_id` per **D1** — never a live feed on the replay path), the ADMIT record's `direction`, the **fixed configured `default_size`** (**D2** — sizing is deferred), and the seeded policy.
- **Slippage function:** deterministic `fill_price = f(instrument_price, direction, slippage_bps, seed)` — e.g. a fixed or size-tiered slippage in bps plus an optional deterministic micro-jitter derived from a seed folded from `(source_snapshot_id, fill_model_version)` (no `Math.random`/clock — seed is content-derived, replay-stable). v0 may be as simple as fixed-bps slippage at the forwarded price; the point is **determinism + versioning**, not market realism.
- **Replay key:** `fill_model_version` (and the `fill_model_fingerprint`) **fold into the §2 replay key** (gate (d)); an unversioned edit changes the fingerprint and fails a CI coherence test (the `decision_policy_fingerprint` pattern).

> **Closing artifact:** the **`FillModelConfig` spec** (fields, `fill_model_version` v0, fingerprint, the slippage function) pinned in the SCHEMA-014 + MOD-008 node bodies and folded into the replay key. → gate (b) **Closed**.

### Gate (c) — Guard-wiring (GATE-001 + PRED-001..005)  →  closes when the wiring is drawn

The dormant guardrail machinery activates here (ADR-011 §4; GATE-001 today is `in-progress`, "not yet wired into a live trade-submission pipeline — no order router yet"). Wiring, grounded in [[Guardrail Engine]] (MOD-001) `GuardrailEngine.validate()` (short-circuit conjunction over `ALL_PREDICATES`, first failure → BLOCK with that predicate's reason):

1. **Composition root, not the core.** The **chain orchestrator** (the composition layer that already runs `consume → … → evaluate`) — not the execution core — builds a [[Trade Validation Request Schema]] (SCHEMA-007) from the ADMIT record's intended trade + `prior_portfolio` (`size`, `current_equity`, `daily_pnl`, `trades_today`, `open_positions`) and calls `GuardrailEngine.validate(request)` **before** `port.execute()`.
2. **Ordering & fail-closed attribution.** Predicate order is MOD-001's: [[Position Size OK]] (PRED-001) → [[Daily Loss Cap OK]] (PRED-002) → [[Max Trades OK]] (PRED-003) → [[Max Positions OK]] (PRED-004) → [[Withdrawal Disabled]] (PRED-005). On **BLOCK**, `execute()` is **not** called; the orchestrator records a non-executed [[Order Management]] outcome naming the **first failing predicate** on the execution record's `guard_result` (`blocked_by`), mirroring MOD-007's "non-ADMIT names its triggering guard". On **APPROVE**, the `GuardResult` is forwarded into `execute()` as **provenance** (so the record carries proof it passed) — the execution core records it, never recomputes it.
3. **Bounded-context hygiene (ADR-009 §3).** The execution **core** (`src/execution/...`) **never imports `src/risk`** — it receives `guard_result` as an explicit input. Only the **orchestrator** (the composition root, which legitimately sees both bounded contexts across the Risk Control ↔ Trading Engine boundary, [[Context Map]] ARCH-001) imports `GuardrailEngine`. This re-uses MOD-007's "re-implement the fail-closed verdict pattern, never import the other context" discipline.
4. **Replay determinism of the guard (important).** On the replay/simulator path the guardrail **limits are an explicit, fingerprinted input** (a captured `guard_config` snapshot), **not** read fresh from `os.environ` at replay time — otherwise an ambient env change would silently alter a replayed BLOCK/APPROVE. The `guard_config_fingerprint` folds into the §2 replay key. (The live path may read env; the replay path uses the captured snapshot.)

> **Closing artifact:** the **guard-wiring spec** (orchestrator builds SCHEMA-007 → `validate()` → APPROVE gates `execute()`; BLOCK records first-failing predicate; core never imports `src/risk`; captured fingerprinted `guard_config` on the replay path) recorded in the orchestrator + MOD-008 node bodies; GATE-001 advances `in-progress → implemented` at writeback when it is invoked at the real trade boundary. → gate (c) **Closed**.

### Gate (d) — Execution-determinism replay requirement  →  closes when the key + benchmark are finalized

Pin the full ADR-011 §2 invariant and the benchmark that proves it:

> Same `source_snapshot_id` + same upstream version tuple (`feature_schema_version` + `model_version` + `decision_policy_version`) + same `runtime_policy_version` + same `fill_model_version` + same `execution_policy_version` + same `guard_config_fingerprint` + same fill seed + **same prior portfolio/ledger state** ⇒ **identical execution record AND identical new portfolio/ledger state.**

State is an **explicit argument + return value** (the prior portfolio in, the new portfolio out; ADR-009 §4/§5) — never ambient. The pure `execute()` core has **no clock/network/randomness/hidden state**; the Alpaca path is held entirely off this invariant (gate (f)). The benchmark is candidate **BENCH-004** (BENCH-003 idiom): a **real sequence** (thread ADMIT records from the real consumable snapshots through `run_sequence` twice → assert byte-identical execution records **and** ending portfolio state; re-present to evidence idempotency) + a clearly-labelled **synthetic sequence** exercising the fill/guard-block outcome space, pinned by a committed golden artifact a test asserts stays in sync. `measures: [replay_determinism, idempotency, fill_distribution, portfolio_state_hash, guard_block_attribution]`.

> **Closing artifact:** the **replay-key definition + BENCH-004 plan** (real + synthetic sequence, golden artifact, in-sync test) recorded in the SCHEMA-014/015 + MOD-008 bodies. → gate (d) **Closed**.

### Gate (e) — Portfolio / position state model (SCHEMA-015)  →  closes when the state model is agreed

A **portfolio/position state** (candidate **SCHEMA-015**) realizing the **existing** [[Position Tracking]] (CAP-007) capability ("track open positions, monitor P&L, maintain current portfolio state"). Design, in the ADR-009 §5 self-describing append-only ledger idiom:

- **Per-instrument position:** `instrument` (GLD), `quantity`, `avg_cost`, `realized_pnl`, `unrealized_pnl` (**mark-to-snapshot** — marked at the re-derived snapshot instrument price (D1), never a live mark on the replay path), `state_version`.
- **Append-only `executions` history** keyed by `source_snapshot_id` (the same dedup/replay key MOD-007's ledger uses), `seq = len(prior.executions)` so it continues across reload; no entry mutated or deleted.
- **Self-describing & replay-sufficient:** each entry persists everything needed to reproduce its own portfolio transition (the execution record digest, fill price, `fill_model_version`, prior-state hash). Replaying the same ADMIT sequence from the same starting state yields a **byte-identical** ending state (the gate (d) invariant). Persistence is canonical-JSON, atomic temp-+-`os.replace`, mirroring MOD-007 `runtime.py` `persist_ledger`.

> **Closing artifact:** the **SCHEMA-015 state model** (fields, key, append-only persistence, mark-to-snapshot rule) agreed and recorded; CAP-007 named as its realizing capability. → gate (e) **Closed**.

### Gate (f) — Alpaca-adapter boundary (deferrable)  →  closes when the boundary is drawn

The **AlpacaPaperAdapter** implements the same INT-011 port but lives **entirely in the IO shell**:

- **Credential isolation (KA-008):** Alpaca keys in **env / a git-ignored `.secrets`** only — **never** in an agent-readable memory file, a dev_graph node, or the repo. **Withdrawals disabled** (PRED-005 holds at the credential level); Alpaca **Paper** = virtual money. Missing/!paper credentials **fail closed** (no live call).
- **Non-replayable IO quarantine (ADR-011 §2):** live Alpaca runs are **logged, not replayed**, **never** in BENCH-004, **never** on the `run_sequence` path. The execution record stamps `execution_mode: alpaca_paper` + `replayable: false`; the simulator stamps `execution_mode: simulated` + `replayable: true`. No broker order id, fill, or response ever enters the deterministic core or a replayed record.
- **Deferrable (ADR-011 §5):** this gate **may be deferred** — the simulator-first core is fully replay-testable today; the Alpaca adapter yields low-information results until the decision logic is calibrated (epoch (b)). Closing (f) is required only when the live adapter is actually built; it does **not** block (a)–(e) or the simulator slice.

> **Closing artifact:** the **adapter boundary spec** (credential isolation, fail-closed, non-replayable stamping/quarantine) recorded in the MOD-010/adapter node body **when the adapter is authored** (deferrable). → gate (f) **Closed** (or explicitly deferred).

---

## Design decisions settled at the CONTRACT CHECKPOINT

Two items §2 must pin before STEP 1 (raised at checkpoint review) — decided here, not left to ride.

### D1. `instrument_price` sourcing — deterministic re-derivation, NOT a schema field

**Decision: the orchestrator re-derives `instrument_price` from `admit.source_snapshot_id`; no field is added to SCHEMA-011 / SCHEMA-012.** `source_snapshot_id` is already on the ADMIT record, and the Layer-2 corpus is **content-addressed and immutable** (the snapshot_id *is* a content hash). So the orchestrator (the IO / composition layer that already runs `consume()`) resolves that one immutable snapshot and reads `gold_price` (a SCHEMA-001 series, already surfaced as the `gold_price` MOD-004 feature, ADR-006 §5) **replay-stably**: same `source_snapshot_id` ⇒ same price, forever. In a full-chain run the value is already in hand (the `FeatureVector` the decision was built from carries `gold_price`); in execution-only replay (BENCH-004 / `run_sequence`) it is re-resolved from the id. Either way the **pure `execute()` core receives `instrument_price` as an explicit argument and never reads the snapshot itself** — ADR-006 §2 / ADR-009 §3 bind the *core* (which stays pure), not the orchestrator. Price provenance is persisted on the **new SCHEMA-014** execution record (`instrument_price` + `source_snapshot_id`), so the record is self-describing for its own replay (ADR-009 §5) **without** touching the frozen contracts.

**Alternative rejected — forward the price as an additive field on SCHEMA-011/012** (the ADR-009 §3 `snapshot_guards` pattern). Rejected for v0: it mutates the **frozen pure-chain contracts** (additive field + `packet_schema_version`/record-schema bump + re-pinned goldens + re-run BENCH-002/003) purely to serve a downstream consumer, when the price is already deterministically recoverable from the immutable, content-addressed snapshot the ADMIT record names. Re-derivation keeps the pure chain frozen and confines the new provenance to the new SCHEMA-014 record. (If a future epoch needs the price *on* the pure packet for an unrelated reason, that is its own additive-change ADR — not incurred here.)

### D2. CAP-005 v0 sizing scope — sizing is deferred; v0 uses a fixed configured size

**Decision: re-grounded CAP-005 v0 does NOT calculate position sizes.** CAP-005's wiki-derived definition lists "calculate position sizes," but **position sizing is an ADR-009 / ADR-011 Non-Goal**. v0 executes an ADMITted decision at a **fixed, versioned paper size** — `config.default_size` (a notional/unit in `ExecutionPolicyConfig`, folded into `execution_policy_fingerprint`) — **not** a sizing algorithm and **not** a decision-driven quantity (the gold packet carries `direction`/`confidence`, the runtime record carries the verdict; **neither carries a size**). Adaptive / decision-driven sizing is **deferred** to a future epoch under its own ADR.

**Scope-down at re-grounding:** the CAP-005 node's "calculate position sizes" responsibility is narrowed to *"apply a fixed/configured v0 paper size; adaptive position sizing deferred (ADR-009/011 Non-Goal)"* so the capability does not over-claim what the epoch delivers. **Validation ≠ sizing:** [[Position Size OK]] (PRED-001) still *validates* the fixed size against the hard cap (`size ≤ min(equity·pct, MAX_TRADE_SIZE)`) — guard-wiring (gate c) stays honest; it checks the size, it does not compute it.

---

## 3. Contract-first authoring order (candidate ids — none reserved/created here)

Strict contract-first, mirroring the gold/runtime epochs. Candidate ids **re-derived from `index.md` (2026-06-16, 160 nodes)** — named as non-binding candidates only; formal assignment at authoring; never reuse a reserved/deprecated id.

1. **INT-011** "Execution API" (interface) — the port (gate a). `input_schema` SCHEMA-012, `output_schema` SCHEMA-014; `stability: experimental`.
2. **SCHEMA-014** Execution / Fill Record (artifact_schema) + **SCHEMA-015** Portfolio / Position State (artifact_schema) — produced/threaded by the execution layer (gates b, d, e).
3. **MOD-008** Execution (module) realizing the re-grounded **CAP-005** + **MOD-009** Portfolio (module) realizing the existing **CAP-007** (see §4).
4. **Simulated-broker adapter first** (the deterministic core path), **Alpaca paper adapter deferred** — candidate **MOD-010** (sim-broker) / **MOD-011** (Alpaca paper), or files under MOD-008 if they stay small (decide at authoring per the §7.5 file-node threshold).
5. **EVT-001** (optional) — the first `events/` occupant (e.g. `FillSimulated` / `OrderSubmitted`); author only if a real consumer exists (avoid emitting into a vacuum, per the ADR-004 "Guard Mapper" lesson).
6. **Re-ground CAP-005** (ADR-011 §4) — retire `### Depends On [[Signal Generation]]` (deprecated), set the live path to consume an ADMIT SCHEMA-012 record (CAP-020 → MOD-007 ADMIT → execution), and **resolve the node-less `Execution API` placeholder → INT-011**; set `implemented_by → [[MOD-008]]`, narrow to `paper_only`.

Next-free leaf ids (assigned at writeback): **FILE-024+**, **TEST-018+**, **BENCH-004**. Reserved/earmarked not reused: INT-002/004/005/008; SCHEMA-002/003/006. No new ontology **type** or enum value is needed (the 24-type ontology covers everything); no `sync_to_neo4j.py` change.

---

## 4. Capability decision — re-ground CAP-005 in place; realize the existing CAP-007 (no new capability)

**Confirmed: no new execution capability is needed.** Both halves map to **existing** Trading Engine (SYS-002) capabilities:

- **Execution → re-ground [[Order Management]] (CAP-005) in place.** CAP-005's semantics ("route orders, calculate position sizes, manage order lifecycle, handle fills/rejections") **are** the execution layer's responsibility — they are not obsolete. Re-grounding: retire the deprecated `### Depends On [[Signal Generation]]`; wire the real live path (CAP-020 → MOD-007 ADMIT → execution); resolve CAP-005's `interfaces: [[Execution API]]` placeholder to the real **INT-011**; set `implemented_by → [[MOD-008]]`; narrow the mode to **paper_only** (Alpaca Paper virtual money; live-money a future epoch under its own ADR); and **scope down "calculate position sizes" → "apply a fixed/configured v0 paper size; adaptive sizing deferred"** (D2). This is **not** a type reclassification (CAP-005 stays a capability, keeps its canonical_id), so ADR-004's no-in-place-reclassify rule (about *type* changes + id reassignment) is not triggered; it is a dependency/interface re-grounding exactly as ADR-011 §4 frames it.
- **Portfolio/position → realize the existing [[Position Tracking]] (CAP-007).** CAP-007 ("track open positions, monitor P&L, maintain portfolio state"; `not-started`) is precisely SCHEMA-015's concept and **already `### Depends On [[Order Management]]`** for fill data — the execution→portfolio edge is pre-anticipated. MOD-009 realizes CAP-007; bump CAP-007 `implementation_status → in-progress` at writeback.

**Alternative rejected — a new capability (e.g. CAP-022) under SYS-002.** Rejected: it would **duplicate** the execution concept CAP-005 already owns (violates [[Canonical Ownership]], CON-003) and orphan the existing CAP-005/CAP-007 wiring. CAP-005's semantics aren't obsolete (unlike CAP-004 Signal Generation, which *was* deprecated-and-superseded by CAP-020) — so deprecation/replacement is unwarranted.

> **Flag for the CONTRACT CHECKPOINT:** narrowing CAP-005 to `paper_only` touches its semantics (in-place re-grounding) — surface it for explicit sign-off, since it edits an existing capability node rather than creating a new one.

---

## 5. Code slices (per [[ADR - Implementation Substrate]], ADR-003)

- **Layout:** `src/execution/...` mirroring the dev_graph `module_path` (MOD-008 `module_path: src/execution/engine`-style; MOD-009 portfolio analogously), tests mirrored under `tests/execution/`. One `pyproject.toml` line adds `"src/execution"` to the wheel packages (the gold-epoch precedent).
- **Substrate:** Python ≥3.10, **stdlib frozen `dataclasses`** (SCHEMA-014/015 models), **zero runtime dependencies** for the simulator slice (Alpaca SDK enters only with the deferred adapter, isolated behind the port), `from __future__ import annotations`, `mypy --strict` + `ruff` clean, `pytest` via `pythonpath=["src"]`.
- **Pure core + IO shell (mirror MOD-007 `engine.py`/`runtime.py`):**
  - `engine.py` — pure `execute(admit, instrument_price, prior_portfolio, guard_result, fill_model, config) -> (ExecutionRecord, PortfolioState)`: deterministic fill (gate b), one append to the portfolio `executions` history, fail-closed; **no IO/clock/randomness/`src/risk` import**.
  - `runtime.py` — IO shell: `load_portfolio`/`persist_portfolio` (absent ⇒ `PortfolioState.empty()`, malformed ⇒ contract error; atomic write), `load_operational`/price forwarding, `run_once` (load → guard (orchestrator) → execute → persist atomically) and the pure **`run_sequence`** in-memory replay driver (the BENCH-004 vehicle).
  - `config.py` — `ExecutionPolicyConfig` + `FillModelConfig` with versions + fingerprints + fail-closed `load_config` (missing required value ⇒ raise, never silently relax — ADR-003 config policy).
  - `adapters/` — `SimulatedBrokerAdapter` (pure, the core path) **first**; `AlpacaPaperAdapter` (IO, deferred) isolated behind INT-011.
- **Orchestrator** — the composition root that runs `… → evaluate → validate (GATE-001) → execute`; the only place importing both `src/risk` and `src/execution`.

---

## 6. Tests + benchmark

- **Unit (determinism/idempotency):** `execute()` is total + deterministic (build == build, byte-identical `to_dict()`); portfolio transitions are correct (quantity/avg_cost/realized+unrealized P&L mark-to-snapshot); re-presenting an already-executed `source_snapshot_id` is idempotent (no double-fill — the MOD-007 once-ever discipline).
- **Guard-wiring fail-closed:** each PRED-001..005 BLOCK path prevents `execute()` and records the first-failing predicate on `guard_result`; APPROVE forwards the guard provenance; a captured-vs-env `guard_config` test proves replay independence from ambient env.
- **Golden fixtures grounded in the real snapshots** (the consumable corpus MOD-007/BENCH-003 use), plus a clearly-labelled synthetic sweep for the fill/guard-block outcome space.
- **BENCH-004** byte-identical sequence-replay benchmark — `benchmarks/execution/run_execution_bench.py` + committed `artifacts/execution_bench.json` + an in-sync test (BENCH-003 idiom); `all_replays_byte_identical = true`, ending portfolio-state hash pinned.
- **Static:** `mypy --strict` + `ruff` clean on `src/execution` + tests; full prior suite stays green.

---

## 7. Writeback per code slice (CLAUDE.md End-of-Coding-Session Checklist)

At **each** code slice: create file nodes (FILE-024+) per the §7.5 threshold + test nodes (TEST-018+) with `covers`; author **MOD-008**/**MOD-009** (plan-first body, then bump `implementation_status` not-started→in-progress→tested, `status: active`, add `code` evidence); bump **CAP-005** (re-grounded) + **CAP-007** `implementation_status → in-progress`; wire INT-011/SCHEMA-014/015 `consumed_by`/`produced_by`; advance **GATE-001** `in-progress → implemented` once invoked at the real trade boundary; author **BENCH-004**; update `index.md` (rows + Statistics) + `log.md`; run **all 11 lint checks** on touched nodes (incl. check 9 after the CAP-005 re-grounding — no dangling deprecated refs); **re-sync Neo4j** (`python sync_to_neo4j.py --clear`, repo-root script).

---

## 8. Sequencing, dependencies & checkpoints

```
STEP 0  THIS BRIEF (gate-closing design §2)               ← you are here
        → CONTRACT CHECKPOINT: review §2 ⇒ gates (a)–(e) Closed [(f) deferrable]; PAUSE FOR REVIEW
STEP 1  Contract nodes (no code): INT-011 + SCHEMA-014 + SCHEMA-015; re-ground CAP-005; CAP-007 realized
        → CONTRACT CHECKPOINT: contract + capability frozen, no code; PAUSE FOR REVIEW
STEP 2  Simulator core: MOD-008 engine/runtime/config + SimulatedBrokerAdapter + guard-wiring (GATE-001)
STEP 3  Portfolio: MOD-009 + SCHEMA-015 persistence
STEP 4  Tests + BENCH-004 (byte-identical replay)
        → CHECKPOINT: simulator epoch green; PAUSE FOR REVIEW
STEP 5  (deferrable) AlpacaPaperAdapter behind INT-011 — gate (f); off the replay/benchmark path
STEP 6  Writeback (§7) at each step
```

- **Simulator-first** (ADR-011 §5): STEP 2–4 deliver a fully replay-testable epoch with **zero runtime deps**; the Alpaca adapter (STEP 5) is **deferred or run parallel to epoch (b)** calibration — it yields low-information results until the regime thresholds / confidence weights / direction table are calibrated.
- **Decoupled from DEBT-01** (closed 2026-06-11, both legs) and from epoch (b) (ADR-011 §5).
- **Explicit pause-for-review checkpoints** mirror the gold/runtime slices (which paused at the STEP-2 contract checkpoint before code). Author **no contract node and no code** past STEP 0 until the CONTRACT CHECKPOINT is approved.

---

## 9. Risks & mitigations (carried from ADR-011 §Consequences)

- **Determinism leak** (wall-clock/network/broker state into the core) → pure `execute()` core + IO-only adapter shell + the extended replay key (incl. `fill_model_version`, `guard_config_fingerprint`, explicit prior/new portfolio state) + BENCH-004 byte-identical replay; the live mark/price never reaches the replay path (mark-to-snapshot).
- **Re-grounding drift** (execution wired onto the deprecated signal/placeholder path) → §4 + ADR-004 precedent: new ids, CAP-020 → MOD-007 ADMIT → execution only; lint check 9 after the CAP-005 re-grounding.
- **Premature live trading** (drift toward live-money/withdrawals) → §3/gate (f): `paper_only` record invariant, PRED-005 enforced, KA-008 credential isolation, live-money a Non-Goal.
- **Low-information live runs** (Alpaca before calibration) → simulator-first; adapter deferred/parallel to epoch (b).
- **Guard non-determinism on replay** (env-read limits) → captured fingerprinted `guard_config` on the replay path (gate c.4).

---

## 10. Canonical-id re-derivation (from `index.md`, 2026-06-16)

INT → next free **INT-011** (INT-002/004/005/008 reserved/earmarked). SCHEMA → **SCHEMA-014** + **SCHEMA-015** (002/003/006 reserved; never a deprecated id). MOD → **MOD-008** (execution) + **MOD-009** (portfolio); adapters **MOD-010**/**MOD-011** or files. CAP → **none new** (re-ground CAP-005; realize existing CAP-007). EVT → **EVT-001** (events/ empty; optional). BENCH → **BENCH-004**. GATE → **none new** (wire existing GATE-001; a blocking execution gate `GATE-004` is an open question, deferred — only if the execution record warrants its own gate like GATE-003 does the runtime record). FILE → **FILE-024+**, TEST → **TEST-018+** (at writeback). Re-derive again at authoring per ADR-011 §6 — do not assume.

---

## 11. Deferred (ADR-011 Non-Goals — not authored)

Live-money trading; real broker order routing beyond Alpaca Paper; the wall-clock scheduler/daemon; multi-instrument (GLD only); learned/history-dependent execution logic; a second source of truth; persistence beyond the local ledger pattern; **the normative SCHEMA/module/interface/adapter/event nodes and all `src/`/`tests/` code** (authored only after the CONTRACT CHECKPOINT closes the gates). The Alpaca adapter (gate f / STEP 5) is deferrable. No `wiki/**` or `raw/**` mutation (CON-001).
