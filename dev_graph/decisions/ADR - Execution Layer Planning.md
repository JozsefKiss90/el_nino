---
type: decision_record
canonical_id: ADR-011
status: active
implementation_status: not-started
canonical: true
created: 2026-06-16
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "ultimateplan.md"
related_files:
  - "[[alpaca_adapter.py]]"
  - "[[alpaca_clock_feed.py]]"
related_tests:
  - "[[test_alpaca_adapter]]"
  - "[[test_alpaca_clock_feed]]"
related_constraints:
  - "[[Canonical Ownership]]"
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
decision_id: "ADR-011"
decision_date: 2026-06-16
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Execution Layer Planning

## Status

**Accepted** — drafted 2026-06-16, accepted 2026-06-16 (promoted at checkpoint review; `status: draft →
active`, `decision_status` stays `active`). It was authored under the governed `status: draft` stand-in
for "Proposed". This is a **governance and architectural-boundary** record, mirroring [[ADR - Gold
DecisionPacket v0 Planning]] (ADR-006), [[ADR - Paper-Trading Runtime Planning]] (ADR-009), and [[ADR -
JARVIS GraphRAG Integration]] (ADR-010). It authors **no** schema, module, interface, gate, predicate,
event, file, test, or code, and **freezes nothing**.

**Acceptance makes this boundary record governing; it does *not* close the §7 Creation Gates.** Those six
gates govern the *downstream authoring of normative execution contract nodes*, not the acceptance of this
ADR — they remained **Open** at acceptance and are closed by the contract-first design + implementation
slices described in the STEP-0 brief `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md`, not by this promotion.
Acceptance ≠ gate closure. **Current state (2026-06-18): gates (a)–(f) are ALL Closed — see §7.** (Gate
(f), the Alpaca-adapter boundary, was closed 2026-06-18 by the default-OFF live plugs; (a)–(e) closed
2026-06-16.)

It opens the **execution / portfolio layer** epoch — the sanctioned next epoch named in the 2026-06-09
Paper-Trading Runtime audit baseline (dev_graph log, 2026-06-09: *"Paper-Trading Runtime epoch is accepted
as the baseline. Remaining work is future epochs, not gaps: **the execution/portfolio layer**; …"*). It
records the constraints under which an execution/portfolio **contract** may *later* be authored
contract-first in a **separate, post-checkpoint implementation slice**.

## Context

The Layer-3 lineage now runs end-to-end as pure, replay-safe analysis and stateful admission:
`SCHEMA-001 → consume → build_features → classify → build_decision` produces a pure
[[Gold DecisionPacket v0 Schema]] (SCHEMA-011), and [[Paper-Trading Runtime]] (MOD-007) admits that packet
against explicit runtime state, emitting an ADMIT/HOLD/REJECT [[Runtime Decision Record Schema]]
(SCHEMA-012) + an append-only ledger ([[ADR - Paper-Trading Runtime Planning]]). What does **not** yet
exist is anything that *acts* on an ADMIT: there is no position, no portfolio, no fill, no P&L, and no
broker boundary. Every prior epoch deferred exactly this — "live execution, broker integration, order
routing, position sizing, fills, P&L accounting" are Non-Goals in ADR-004, ADR-006, and ADR-009.

Two pieces of dormant machinery already point at this layer and have been waiting for it:

1. **The guardrail machinery is built but unwired.** [[Trade Validation Gate]] (GATE-001) is
   `implementation_status: in-progress`: its logic and the five hard-limit predicates
   ([[Position Size OK]] PRED-001, [[Daily Loss Cap OK]] PRED-002, [[Max Trades OK]] PRED-003,
   [[Max Positions OK]] PRED-004, [[Withdrawal Disabled]] PRED-005) are implemented and tested, but the
   gate's own Open Question records that it is *"not yet wired into a live trade-submission pipeline (no
   order router / execution module exists yet)."* This epoch is where that gate is finally invoked at a
   real trade boundary.
2. **The live order path is mis-grounded.** [[Order Management]] (CAP-005) still carries a `Depends On`
   the now-deprecated Signal Generation (CAP-004), and names a placeholder `Execution API` interface for
   which **no node exists**. Its successor, [[Gold Decision Generation]] (CAP-020), is explicitly
   **paper-only and does not feed Order Management** (CAP-005/CAP-020 both record this). So the live path
   from a gold decision to an executed (paper) order is undefined and must be re-grounded — exactly the
   kind of name-vs-semantics drift [[ADR - Decision Layer Re-grounding]] (ADR-004) was created to prevent.

This ADR answers a deliberately narrow question:

> **Under what governance constraints may an execution / portfolio contract be created — and where is the
> boundary drawn between a deterministic, replay-safe core and an optional live broker adapter — so that
> the first money-shaped layer is built without breaking the determinism and bounded-context discipline
> the pure layers established?**

It does **not** answer *"what is the execution contract?"* — that is a future, dedicated set of normative
nodes authored only when the Creation Gates (§7) are met.

## Decision

The following governance constraints bind any future execution / portfolio layer. They are invariants of
record; the contract and code authored in a later slice must satisfy them.

### 1. Scope & epoch boundary
This ADR governs the **execution / portfolio layer** — the component that consumes an **ADMIT** verdict
from MOD-007 and produces a (paper) fill and an updated portfolio/position state. It answers *"under what
constraints may an execution/portfolio contract be created?"*; **it is not that contract**. The execution
layer is a **net-new, permanently separate** bounded context implemented with **new ontology objects and
new canonical identifiers**. It is **not** the Supervisor Office **treasury-upgrade** decision branch
([[Decision Engine]] MOD-002 / [[Decision API]] INT-006 / [[Decision Packet Schema]] SCHEMA-004 — ADR-004),
which remains permanently separate and untouched by this ADR. It is also distinct from, and complementary
to, MOD-007 admission and [[Guardrail Enforcement]] (CAP-008): admission decides *whether* to act; risk
control decides *whether the action is within hard limits*; execution *performs* the (paper) action and
updates portfolio state. A complete trade passes all three.

### 2. The determinism boundary is the load-bearing invariant (port/adapter split)
This is the central decision. The execution layer is split on the **hexagonal (port/adapter)** seam, not
on "Alpaca vs offline":

- **The deterministic offline fill-simulator is the canonical, replay-safe core.** All tests, all
  benchmarks, and all replay run against it. It is a pure function of explicit, versioned inputs — exactly
  as MOD-007's `evaluate()` / `run_sequence` are pure and confine IO to the `run_once` shell
  ([[engine.py]] / [[runtime.py]]). It extends the existing replay key — `source_snapshot_id` + the
  upstream version tuple (`feature_schema_version` + `model_version` + `decision_policy_version`) +
  `runtime_policy_version` + `configuration` (ADR-006 §3, ADR-009 §4) — to cover **execution
  determinism**, by adding a versioned **fill-model** (a `fill_model_version` + an explicit, seeded
  fill/slippage policy) and the **prior portfolio/position state** as explicit inputs. The binding
  invariant is:

  > Same `source_snapshot_id` + same upstream version tuple + same `runtime_policy_version` + same
  > `fill_model_version` + same execution config + same fill seed/policy + same prior portfolio/ledger
  > state ⇒ **identical execution record and identical new portfolio/ledger state.**

- **The Alpaca Paper API is an optional, explicitly non-replayable live adapter.** It is quarantined
  behind the **same execution interface (port)** at an **IO boundary shell**, mirroring MOD-007's pure
  core vs `run_once` IO shell. Alpaca is **never on the replay path** and **never in benchmarks**; live
  runs are **logged, not replayed**. No clock, network, broker response, order id, or live fill may
  influence the deterministic core or any replayed record.

This determinism boundary is a **non-negotiable invariant**: the offline simulator is the source of truth
for correctness and replay; the live adapter is an interchangeable, non-replayable plug behind the port,
honest about its non-determinism.

### 3. `paper_only` / virtual-money safety posture
The execution layer honors [[Paper Trading Validation]] (KA-010) — **mandatory** simulated validation
with real market data **before** any live capital — and the pervasive `non_execution_notice` discipline
the gold lineage carries. Concretely: every execution record asserts a **`paper_only`** invariant
(mirroring the runtime record's `paper_only` invariant); [[Withdrawal Disabled]] (PRED-005) remains
enforced (withdrawals **ALWAYS** disabled, fail-closed) per [[Agent Safety Principles]] (KA-008)
credential isolation; and the **Alpaca Paper** adapter trades **virtual money only**, which respects this
posture rather than violating it. **Live-money trading is an explicit Non-Goal at this epoch** (§Non-Goals).
The gold packet's "this is a paper-trading plan, not an order" notice carries forward as the execution
record's standing `paper_only` / virtual-money assertion — the layer never moves real funds.

### 4. Re-grounding the live path (ADR-004 as precedent)
Following [[ADR - Decision Layer Re-grounding]] (ADR-004), this epoch re-wires the live trade path away
from the deprecated Signal Generation lineage. The sanctioned wiring is:

> **CAP-020 Gold Decision Generation → MOD-007 runtime admission (an ADMIT verdict) → execution layer.**

The execution layer consumes an **ADMIT** [[Runtime Decision Record Schema]] (SCHEMA-012) — never a raw
gold packet, never a snapshot, never the deprecated signal path — and only then performs a (paper) fill.
The dormant guardrail machinery is **activated here**: [[Trade Validation Gate]] (GATE-001) +
PRED-001..005 are wired into the **actual trade pipeline** at the Risk Control ↔ Trading Engine boundary,
so no (paper) order is placed without passing hard-limit validation ([[Guardrail Philosophy]] KA-005:
"every trade attempt MUST pass through the Trade Validation Gate before reaching the broker"). The precise
contract edits to [[Order Management]] (CAP-005) — retiring the deprecated `Depends On` and resolving the
placeholder `Execution API` name to a real interface node — are **deferred to the implementation slice**,
exactly as ADR-004 deferred the treasury-branch clarifications; this ADR only records that the re-grounding
must happen and how the path is drawn. No CAP-005 edit is made in this slice.

### 5. Decouple from DEBT-01 and epoch (b) calibration
The execution epoch is **independent of DEBT-01** and of real-corpus calibration. DEBT-01 was **resolved
on 2026-06-11** — both legs (the producer `NameError` and the operational corpus gap) are closed
(dev_graph log, 2026-06-11) — so it is no longer a blocker for anything, including this epoch. Epoch **(b)**
(real-corpus accumulation, to convert the provisional, **domain-anchored** regime thresholds + confidence
weights + regime→direction table into **empirically calibrated** ones; operationalized 2026-06-11) is a
**separate, parallel epoch**. The execution layer does not wait on it. The **sequencing caveat** of record:
build the **deterministic offline-simulation core first** — it is fully replay-testable today against
synthetic and the existing real snapshots. The **Alpaca Paper adapter yields low-information results until
the decision logic is calibrated** (the regime thresholds, confidence weights, and direction table are
still provisional per ADR-008 §9 and the 2026-06-11 epoch-(b) note), so the Alpaca adapter **may be
deferred, or run in parallel with epoch (b)** — its value rises as calibration lands. Correctness of the
core never depends on calibration; only the *information content* of live paper runs does.

### 6. No schema freeze — candidate objects named, none reserved or created
This ADR does **not** define or freeze any execution contract. The normative artifacts are future,
dedicated nodes with **new canonical_ids**, authored contract-first in a later slice. The likely-next-free
ids below are **re-derived from index.md** and named as **non-binding candidates only** — none is reserved,
none is created here, and formal assignment happens at the moment each node is authored. None reuses a
deprecated id, and none reuses a reserved id (INT-002/004/005/008; SCHEMA-002/003/006):

- an **execution interface** — candidate `INT-011` (next free; CAP-005 today only gestures at an
  `Execution API` placeholder with no backing node);
- **execution / portfolio schema(s)** — candidate `SCHEMA-014` (execution / fill record) and `SCHEMA-015`
  (portfolio / position state);
- an **execution module** — candidate `MOD-008` — and a **portfolio / position-tracking module** —
  candidate `MOD-009`;
- the **simulated-broker adapter** and the **Alpaca paper adapter** — candidate `MOD-010` / `MOD-011`, or
  files under the execution module (the two plugs behind the §2 port);
- **position / portfolio state** (the explicit prior-state input + return value of the §2 invariant);
- the **fill model** (a versioned `fill_model_version` + seeded fill/slippage config, in the idiom of
  `DecisionPolicyConfig` / `RuntimePolicyConfig`);
- any **execution events** — candidate `EVT-001` (e.g. an order-submitted / fill-simulated event; the
  `events/` directory's first occupant).

### 7. Creation Gates
A normative execution **schema / module / interface** node may be authored **only after ALL** of the
following hold. They opened the epoch at its start; the contract-first design + implementation slices then
closed them. **Gate-board reconciliation (2026-06-18):** gates **(a)–(f) are ALL CLOSED** — (a)–(e) at
STEP 1/2/4 (2026-06-16); **(f) closed 2026-06-18** by the default-OFF, non-replayable live plugs (STEP 5).
Each gate's current state + closing artifact:

- **a. Execution interface contract defined** — the port (`INT-011`) is specified: what an
  ADMIT-consuming execution call takes and returns, both fill-simulator and live-adapter implementing it.
  **Closed** — closing artifact: the [[Execution API]] (INT-011) interface node (STEP 1; `fill()` is the
  port/broker seam, `execute()` the layer entry point).
- **b. Fill-simulation model specified and replay-keyed** — the deterministic fill/slippage model and its
  `fill_model_version` are defined and folded into the §2 replay key. **Closed** — closing artifact:
  `FillModelConfig` (`fill_model_version` + `fingerprint()`, `src/execution/config.py`, STEP 2).
- **c. Guard-wiring specified** — exactly how GATE-001 + PRED-001..005 are invoked in the trade pipeline
  (inputs, ordering, fail-closed block attribution), without the execution core importing `src/risk`
  (bounded-context hygiene, per ADR-009 §3). **Closed** — closing artifact: the orchestrator guard-wiring
  (`run_guard` → `GuardrailEngine.validate()` before `execute()`, captured `guard_config`,
  `src/execution/runtime.py`, STEP 2); [[Trade Validation Gate]] (GATE-001) advanced `in-progress →
  implemented`.
- **d. Execution-determinism replay requirement finalized** — the full §2 invariant (the extended replay
  key, the explicit prior/new portfolio state) is pinned, with a byte-identical sequence-replay benchmark
  (in the BENCH-003 idiom). **Closed** — closing artifact: the [[Execution Layer Benchmark]] (BENCH-004)
  byte-identical sequence-replay benchmark + committed golden artifact + in-sync test (STEP 4).
- **e. Portfolio / position state model agreed** — the position/portfolio state representation
  (`SCHEMA-015`) and its append-only / self-describing persistence (in the ledger idiom,
  ADR-009 §5) are agreed. **Closed** — closing artifact: the [[Portfolio State Schema]] (SCHEMA-015) state
  model (STEP 1/2).
- **f. Alpaca-adapter boundary specified** — credential/auth isolation per KA-008 (keys in env only,
  withdrawals disabled, no secret in agent-readable memory) and the non-replayable IO quarantine (live
  runs logged, never replayed, never in benchmarks) are specified. **Closed (2026-06-18)** — closing
  artifacts: [[alpaca_adapter.py]] (FILE-038, `AlpacaPaperAdapter` behind the INT-011 `ExecutionPort`,
  `mode=alpaca_paper` / `replayable=False`) + [[alpaca_clock_feed.py]] (FILE-037, `AlpacaClockFeed` behind
  the `OperationalFeed` port — the live-calendar plug that also closes ADR-009's holiday-calendar gap),
  both **default-OFF** (explicit operator opt-in only; not re-exported, not the default port/feed) and
  **fail-closed** — `*_from_env` factories refuse any non-paper base URL and fail-closed on missing creds
  (keys in env / git-ignored `.secrets` only; PRED-005 [[Withdrawal Disabled]] enforced). Validated by
  [[test_alpaca_adapter]] (TEST-028) + [[test_alpaca_clock_feed]] (TEST-027) — STEP 5. **Built-but-dormant
  per §5:** `execute()` calls `fill()` only for an approved LONG, which the provisional decision logic
  does not yet emit, so the adapter ships behind the port unused until calibration (ADR-012) lands. The
  recurring scheduled run + any *enabling* of the live execution path remain operator HARD-PAUSE actions.

## Illustrative Field Sketch (non-normative)

> **Illustrative, provisional, non-normative — not a schema.** It exists only to give the constraints a
> concrete referent; the normative SCHEMA nodes (a later slice) are the single source of truth once
> authored. Names, types, and presence are all subject to change.

A future execution record *might* carry: `execution_id` (deterministic, binding the ADMIT
`record_id` + `fill_model_version` + execution config fingerprint + prior portfolio state hash),
`source_record_id` (the admitting SCHEMA-012 record), `source_snapshot_id`, `instrument` (gold / GLD
proxy), `intended_direction`, a `fill` block (simulated price / quantity / slippage, or the adapter's
paper fill echoed for logging only), `guard_result` (the GATE-001 outcome + first failing predicate, if
any), `portfolio_state_before` / `portfolio_state_after` hashes, `execution_mode`
(`simulated` | `alpaca_paper`), `replayable` (true for `simulated`, false for `alpaca_paper`),
`fill_model_version`, `paper_only` (always true), and a `non_execution_notice` carried forward. A
portfolio / position state *might* carry: per-instrument `quantity`, `avg_cost`, `realized_pnl`,
`unrealized_pnl` (mark-to-snapshot), an append-only `executions` history keyed by `source_snapshot_id`,
and a `state_version`.

## Non-Goals (explicitly deferred)

Extending the ADR-009 Non-Goals list, this ADR and the epoch it plans explicitly defer:

- **live-money trading** (real capital) — the layer is `paper_only` / virtual-money only;
- **real broker order routing beyond Alpaca Paper** — no live broker, no production order management;
- the **wall-clock scheduler / cron / long-running daemon** (carried from ADR-009);
- **multi-instrument** support — gold / GLD only;
- **learned or history-dependent** execution logic (momentum/rolling-window sizing, adaptive slippage from
  history) — the fill model stays deterministic and versioned;
- a **second source of truth** — no execution-side corpus competes with the canonical ledger/portfolio
  state;
- **persistence beyond the local ledger pattern** — append-only, deterministically-serialized JSON in the
  ADR-009 §5 idiom; no external store, DB backend, or service;
- the **normative SCHEMA nodes, execution/portfolio modules, the execution interface, the adapters, the
  fill model, any execution events, the gate-wiring, and all implementation code** (a later slice).

No execution, order, broker, position, fill, P&L, portfolio, or adapter **nodes** are created in this
slice.

## Alternatives Considered

- **Frame the split as "Alpaca vs offline" (broker choice first).** **Rejected** — that makes the broker
  the organizing axis and lets live, non-deterministic IO leak into the core. The load-bearing seam is the
  **port/adapter / determinism boundary** (§2): one deterministic core, interchangeable adapters behind a
  port. Alpaca is then just a non-replayable plug, not the design center.
- **Build the live Alpaca adapter first (fastest "real" feedback).** **Rejected** — premature: the
  decision logic is still provisional/domain-anchored pending epoch (b), so live paper runs are
  low-information (§5); and a live-first build risks baking non-determinism into the core. Build the
  replay-safe simulator first; add the adapter when (and if) calibration makes it informative.
- **Fold execution onto Order Management (CAP-005) in place / reuse its placeholder `Execution API`.**
  **Rejected** — CAP-005 still depends on the deprecated signal path and names a node-less placeholder;
  reusing it in place would repeat the exact mis-grounding ADR-004 forbids. The path is re-grounded
  (CAP-020 → MOD-007 ADMIT → execution) with new ids; CAP-005's edits are a deferred, just-in-time slice.
- **Enrich the runtime record in place with fill data.** **Rejected** — mirrors ADR-009 §2: the SCHEMA-012
  record is the admission verdict and must stay pure; execution outcomes live on a **new** wrapping record,
  never by mutating the admission record (the same "wrap, never enrich-in-place" discipline).
- **Author the execution contract inside this ADR (one combined epoch).** **Rejected** — keeps this a
  boundary record; the contract/code is a separate reviewable slice after the checkpoint, preserving the
  ADR-006 → SCHEMA-011 and ADR-009 → MOD-007 rhythm.
- **Make the Alpaca adapter replayable (record/replay its responses).** **Rejected for v0** — a recorded
  broker transcript is a second source of truth and a determinism trap; live runs are **logged, not
  replayed** (§2). Deterministic replay is the simulator's job alone.

## Consequences

### Positive
- Establishes the execution layer's boundary, the determinism seam, and the re-grounded live path
  **before** any contract is frozen — extending the determinism discipline to the first money-shaped layer
  and eliminating the prose-only drift risk ADR-004 flagged.
- Finally **activates** the dormant guardrail machinery: GATE-001 + PRED-001..005 move from
  built-and-tested-but-unwired to wired into a real (paper) trade pipeline.
- Keeps the Supervisor treasury branch permanently separate, the gold packet and runtime record pure, and
  Risk Control vs admission vs execution distinct-but-complementary.
- Decouples execution from DEBT-01 (closed) and epoch (b) calibration, with an explicit "simulator-first,
  adapter-when-calibrated" sequencing that lets work start immediately.

### Negative / Trade-offs
- The concrete execution contract remains unwritten until the Creation Gates pass; downstream design waits
  on them.
- Re-grounding CAP-005's live path (retiring the deprecated dependency, resolving the `Execution API`
  placeholder) is incurred as a later just-in-time edit — a small, deferred wikilink/contract churn.
- A live Alpaca Paper adapter, if/when built, adds a genuinely non-replayable surface that must be held
  rigorously off the replay/benchmark path.

### Risks
- **Determinism leak** — wall-clock, network, or broker state leaking into the core (mitigated by §2: the
  pure simulator core + IO-only adapter shell + the extended replay key + a planned byte-identical
  sequence-replay benchmark, mirroring MOD-007).
- **Re-grounding drift** — execution wired onto the deprecated signal/placeholder path (mitigated by §4 and
  ADR-004 precedent: new ids, CAP-020 → MOD-007 ADMIT → execution only).
- **Premature live trading** — any drift toward live-money or withdrawals (mitigated by §3: `paper_only`
  invariant, PRED-005 enforced, KA-008 credential isolation, live-money a Non-Goal).
- **Low-information live runs** — running Alpaca before calibration (mitigated by §5: simulator-first; the
  adapter is deferred or parallel to epoch (b)).

## Future Work

When this ADR is accepted at the checkpoint and the Creation Gates (§7) are closed, a later slice authors —
contract-first, with new canonical_ids — the execution interface, the execution/fill and portfolio/position
schemas, the execution and portfolio modules, the deterministic fill-simulator, the (optional, deferred)
Alpaca Paper adapter, and any execution events; **wires** GATE-001 + PRED-001..005 into the trade pipeline;
**re-grounds** CAP-005's live path (CAP-020 → MOD-007 ADMIT → execution); and adds the
determinism/idempotency tests + a byte-identical sequence-replay benchmark. Later epochs may add live-money
trading (under its own safety ADR), multi-instrument support, a scheduler/daemon, and richer P&L/portfolio
analytics — each under its own amendment.

## Relationships

### Depends On
- [[Paper-Trading Runtime]]
- [[Gold Decision Generation]]
- [[Trade Validation Gate]]

### Constrains
- [[Order Management]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Decision Layer Re-grounding]]

### Constrained By
- [[Canonical Ownership]]
- [[No Wiki Mutation]]

### Originates From
- [[Paper Trading Validation]]
- [[Guardrail Philosophy]]
- [[Agent Safety Principles]]
