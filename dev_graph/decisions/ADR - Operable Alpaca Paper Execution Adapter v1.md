---
type: decision_record
canonical_id: ADR-014
status: active
implementation_status: tested
canonical: true
created: 2026-06-21
updated: 2026-06-25
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "el nino alpaca paper E2b roadmap.md"
  - "E2b_ROADMAP_alignment_review.md"
  - "app_audit.md"
related_files:
  - "[[alpaca_adapter.py]]"
  - "[[alpaca_clock_feed.py]]"
  - "[[adapters.py]]"
  - "[[live_adapter.py]]"
  - "[[live_runtime.py]]"
  - "[[price_reference.py]]"
  - "[[operational_feed.py]]"
  - "[[Execution Record Schema]]"
  - "[[Portfolio State Schema]]"
  - "[[Runtime Ledger Schema]]"
related_tests:
  - "[[test_live_runtime]]"
  - "[[test_live_adapter]]"
  - "[[test_price_reference]]"
  - "[[test_guard_day_scope]]"
  - "[[test_reconcile_entry]]"
  - "[[test_operator_halt]]"
  - "[[test_replayable_fence]]"
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Empirical Calibration Methodology]]"
  - "[[ADR - Operations Control Plane]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
decision_id: "ADR-014"
decision_date: 2026-06-21
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Operable Alpaca Paper Execution Adapter v1

## Status

**Draft (v2)** — authored 2026-06-21, **revised in place 2026-06-21** (the governed `status: draft`
stand-in for "Proposed", per the ADR-011 / ADR-013 convention). `canonical_id` stays **ADR-014** and
`decision_status` stays `active`: this is an **in-place revision of an unaccepted draft, not a
supersession** (`supersedes`/`superseded_by` stay empty). The "v1" in the title names the **adapter**
version (the operable adapter built over the dormant v0 stub), not the document version. **HARD PAUSE:
this ADR is reviewed and accepted by the operator before any adapter-v1 code is written.** It authors no
code; the implementation proceeds downstream (`/prd-to-issues` → slices) under its invariants after
acceptance.

> **v2 changelog (what the grilling + audit changed).** v2 folds a **six-round design grilling
> (Q1–Q6 design locks)** and a **full adversarially-verified code audit** (`app_audit.md`, 117 checks,
> 18 re-verifications) into the v1 draft:
> 1. **GLD price reference is re-scoped el_niño-side** — `exec_ref_gld_price` is *source-pluggable*
>    (simulator: a versioned derived proxy `gold_price_proxy × oz_per_share`; live: the real live GLD
>    mark). **A8 is no longer a hard cross-repo blocker** (the audit's "Mr-Ripley must land first" is
>    overruled — §5.1, Step 3).
> 2. **Live operability is a separate non-replayable entrypoint** (`live_runtime.operate_live`,
>    mirroring `run_once`), **not** "behind the same `fill()` port" — `ExecutionPort.fill()` stays the
>    LONG-only replay contract (§6.1).
> 3. **Authority is split** — broker = position truth, local SCHEMA-015 = decision lineage + idempotency;
>    divergence **heals via a new append-only reconcile-entry kind** and any unexplained discrepancy
>    **terminal-refuses execution only** (no auto-flatten), never the decision/labeling chain (§6.2).
> 4. **Cross-snapshot in-flight ownership** is the open-orders-aware reconcile; `client_order_id` 422
>    covers same-order duplicate-submit only (§6.3).
> 5. **Cash-cap binds to the literal settled-cash field** (never any `*_buying_power`); fixed-notional is
>    **live-plug-only** (the sim keeps fixed-qty `default_size`) (§6.4).
> 6. **The simulated portfolio stays accumulate-only**; the sell-fold + realized P&L are **live-only**;
>    the live adapter becomes **side/order-based** (the v0 `fill(direction)` is superseded, not extended)
>    (§6.5).
> 7. The audit's **ungoverned findings** are now each owned: sync-fill raise, mislabeled "daily" guard,
>    uncaught `HTTPError`, 429/`Retry-After`, `GET /v2/account` status gate, operator kill switch, and the
>    broker-traceability fields — scoped **v1** or explicitly **deferred** with a rationale (§6.6,
>    "Enumerated defects").
>
> Still `status: draft` — **operator acceptance is the checkpoint.**

## Context

The Layer-3 lineage runs end-to-end and the execution layer already exists. [[ADR - Execution Layer
Planning]] (ADR-011) is Accepted with creation gates (a)–(f) **closed**; gate (f) — the Alpaca-adapter
boundary — closed 2026-06-18. The chain threads
`consume → build_features → classify → build_decision → evaluate → [GATE-001] → execute → persist` through
`orchestration.runtime.run_once`, persisting an append-only runtime ledger ([[Paper-Trading Runtime]]
MOD-007, [[Runtime Ledger Schema]] SCHEMA-013) and portfolio/execution state ([[Execution]] MOD-008,
[[Execution Record Schema]] SCHEMA-014 + [[Portfolio State Schema]] SCHEMA-015). The deterministic
`SimulatedBrokerAdapter` is the wired default port (`mode=simulated`, `replayable=True`); the live Alpaca
paper plugs ([[alpaca_adapter.py]] FILE-038, [[alpaca_clock_feed.py]] FILE-037) are **default-OFF,
fail-closed, paper-host-only, built-but-dormant** behind their ports. [[Gold Forward-Return Labeler]]
(MOD-009) + [[ADR - Empirical Calibration Methodology]] (ADR-012) are the observation/performance gate
(today **DEFER** on all targets — monochromatic corpus N=5, RESTRICTIVE_RATES/AVOID). [[ADR - Operations
Control Plane]] (ADR-013) is the operator surface whose gated-live tier already exposes a confirmed,
audited, paper-host-precondition Alpaca enable.

What the v0 adapter is **not** is *operable*. Grounded against the code: `AlpacaPaperAdapter.fill()`
submits a one-shot `POST /v2/orders` market BUY and then **raises** unless the synchronous response status
is in `_FILLED_STATUSES = {"filled","FILLED"}` (`alpaca_adapter.py:112-113`) — but real Alpaca market
orders return `accepted`/`pending_new` and fill **async**, so the live path would raise on essentially
every real order. There is no startup reconcile, no `GET /v2/positions` / `GET /v2/account` /
`GET /v2/orders` / `GET /v2/assets` read, no `FLAT→exit`, no deterministic `client_order_id`, no cash-cap,
no `try/except` around the order `urlopen` (a 4xx `HTTPError` propagates raw and the Alpaca reject body is
discarded), and no 429/`Retry-After` handling. The port is **LONG-only** (`fill()` raises on any
non-LONG direction) and the simulated portfolio is **buy/accumulate-only** (`_apply_buy` is the sole
position-folding function; `realized_pnl` is propagated but never incremented; there is no `_apply_sell`).

Two further problems exist independent of the broker mechanics:

1. **The env-isolation guard is already hardened.** `_is_paper_base_url` is **parsed-hostname equality**
   (`urlparse(base_url).scheme == "https" and .hostname == "paper-api.alpaca.markets"`,
   `alpaca_adapter.py:55-56`), so the roadmap's `"paper-api" in base_url` **substring** check is a
   *regression to reject* (the exact sub/super-domain + query/fragment exfil bypass it already replaced).
2. **The GLD fill reference is wrong.** `orchestration/engine.py:95` forwards
   `instrument_price = fv.value("gold_price")` into `execute()`. `gold_price` is a pass-through level of
   the SCHEMA-001 series `gold_price_proxy` (`feature_builder.py:68`) = **gold spot, $/oz** (4624.5, source
   `goldapi_com`) — handed to a **GLD share** order (~$300–600/share). Verified: on the live path slippage
   becomes `(GLD_fill − gold_spot)/gold_spot ≈ −9,300 bps` (nonsense), and `_apply_buy` marks
   `avg_cost`/`unrealized_pnl` in $/oz against GLD units on **both** the simulator and the live path. It is
   **latent only because no LONG fires today** (current snapshot → AVOID; ADR-012 DEFER); it misbehaves the
   instant a LONG fills. Note that, today, `gold_price` is a **reserved taxonomy feature**
   (`taxonomy.py:85-90`) — **not** a regime predicate, **not** in `required_features`, **not** cited by the
   decision — so its *only live consumer* is this (wrong) execution price.

This ADR answers a deliberately narrow question:

> **Under what constraints is the v0 stub upgraded to an operable paper adapter — adding reconcile-then-act,
> FLAT→exit, deterministic idempotency, cash-cap, and a queued/partial/uncertain state machine, and fixing
> the GLD price reference — WITHOUT significantly modifying any post-ADR-11 implementation, without a second
> source of truth, and without weakening the determinism, paper-only, fail-closed boundary?**

It does **not** author the adapter, the entrypoint, or the schema-field code — those are the implementation
slices, built only under the invariants below.

## Decision

The decision separates cleanly into **two buckets**, and that split is what makes this a clean `/prd`
slice source:

- **(i) Contained shared changes (versioned)** — §5: the GLD price reference (§5.1), the daily-guard
  `as_of` threading (§5.2), the `assert port.replayable` precondition + the separate ledger/portfolio
  path threading (§5.3), and the additive SCHEMA-014/015 fields (§5.4). Each is additive + versioned;
  old versions stay byte-reproducible; BENCH-004/006 re-pin where a replay key changes.
- **(ii) Live-plug-only additions** — §6: reconcile-then-act, the sell-fold, the state machine, the
  cash-cap, `client_order_id`, the reconcile-heal, and the side-based adapter. All live inside the
  default-OFF, non-replayable plug, reached **only** via the new `operate_live` entrypoint.

### 1. Strategy — additive, simulator-unchanged, broker-realism quarantined
The v1 operability is an **additive delta**. The deterministic spine — the pure `execute()` core,
`SimulatedBrokerAdapter`, MOD-010 orchestrator, MOD-007 runtime, and the BENCH-004/006 replay benchmarks —
stays **structurally unchanged** as the canonical replay path. **All broker-realism (reconcile, SELL,
`client_order_id`, cash-cap, account-state, fractionable, queued/partial/uncertain, reconcile-heal) lives
inside the default-OFF, non-replayable Alpaca plug** (the ADR-011 §2 / gate-(f) quarantine:
logged-not-replayed, never in benchmarks), reached through a **separate non-replayable entrypoint**, not
through the canonical `fill()` port. Shared code changes are **additive + versioned only**, and are
enumerated in §5 — this is what satisfies "introduce the improvements without significant modification of
post-ADR-11 implementations."

### 2. Constitution (preserved, binding)
Gold-first, fail-closed, snapshot-driven: same snapshot in → bit-identical decision out. **Long-or-flat
only** (LONG/FLAT/AVOID/WATCH); no short, **no margin** — cash-account semantics only; binary size (no
confidence-scaled sizing). **Paper only** (`paper-api.alpaca.markets`, virtual money); live money is
Phase D, structurally blocked, out of scope. Governance before autonomy: gated, not self-driving; every
fill-record references the governing `snapshot_id`; writes are immutable (`INSERT OR IGNORE`-equivalent,
never `UPDATE`). La Niña / exits live in **our deterministic evaluator, never broker-side conditional
orders**.

### 3. Inherited unchanged — NOT re-decided (respect the built v0)
v1 inherits and must not re-author: ADR-011 gate (f) boundary; the **parsed-hostname env guard** in
`alpaca_adapter.py` / `alpaca_clock_feed.py`; the `INT-011` `ExecutionPort` Protocol (`fill()` +
`mode`/`replayable` properties) + pure `execute()` core + `SimulatedBrokerAdapter` as the canonical
replay path; SCHEMA-013 runtime ledger; SCHEMA-014/015 append-only-JSON + `source_snapshot_id` once-ever
idempotency (`PortfolioState.has_execution`); MOD-010 orchestrator; MOD-007 runtime (incl. PRED-008
snapshot-`as_of` cooldown); MOD-009 / ADR-012 as the observation + performance gate; ADR-013 ops console
as the gated-live enable surface (confirm + audit + paper-host precondition already built); ADR-011 D2
(fixed size, sizing deferred). *(Note: "ADR-011 D1/D2" is established downstream shorthand — D1 = the
price-is-re-derived-from-the-snapshot replay discipline, ADR-011 §2/§5; D2 = sizing-deferred / fixed
`default_size`, ADR-011 Non-Goals. ADR-011's own body uses §1–§7, not "D1/D2" labels.)*

### 4. Two regressions removed (explicit)
- **Env isolation is DONE.** The roadmap's `if "paper-api" not in base_url` substring check is
  **rejected** — it is the exact credential-exfil bypass (sub/super-domain, query-string smuggling)
  already replaced by parsed-hostname equality (`_is_paper_base_url`). v1 reuses the existing guard and
  must never reintroduce a substring test.
- **No new SQLite stores.** The proposed `fill_record` / `scorecard` tables are **rejected** as a second
  source of truth (ADR-009 §2, ADR-011, ADR-013 §11). Execution outcomes stay on SCHEMA-014/015 (additive
  fields, §5.4); per-regime direction accuracy stays in **MOD-009 / ADR-012**. The name "scorecard" is
  avoided ([[Evaluation Scorecard Schema]] SCHEMA-005 is the separate Supervisor treasury branch, ADR-004).

### 5. Contained shared changes (versioned) — bucket (i)

These four changes touch shared code. Each is **additive + versioned**; old versions stay
byte-reproducible; BENCH-004/006 re-pin where a replay key changes. There is **nothing else** shared —
everything in §6 is live-plug-only.

#### 5.1 GLD price reference — `exec_ref_gld_price`, source-pluggable (Q1; resolves A8)
The execution **fill/slippage reference becomes the GLD share price** (`exec_ref_gld_price`, $/share), via a
**source-pluggable** interface (one seam, two implementations):

- **Simulator / replay path** → a **versioned deterministic derived proxy**:
  `exec_ref_gld_price = gold_price_proxy × oz_per_share`, where `gold_price_proxy` is the existing **real
  XAUUSD spot** series ($/oz) and `oz_per_share` is a **versioned constant** (GLD's approximate gold
  content per share). Derived from the snapshot per the D1 replay discipline — **never a live read** on the
  replay path. The simulator slippage stays a **model number** (the flat `FillModelConfig.slippage_bps`
  applied to the derived ref) and is **labeled** as a synthetic/derived reference.
- **Live Alpaca path** → the **real live GLD mark** (read live, **non-replayable**). The adapter already
  records slippage as **"recorded, not modelled" against the orchestrator's mark** (`alpaca_adapter.py:116`)
  — v1 changes only *which mark*: the GLD mark. The **reference timestamp is pinned + labeled**
  (submit/EOD mark = includes overnight gap; open/routing mark = pure execution slippage), with the
  **paper-account no-liquidity-impact caveat** noted.

`gold_price` (spot, $/oz) is **severed from execution** and remains a pure **decision-context feature**
(today reserved in the taxonomy; if/when it becomes a regime predicate it stays decision-side only). After
this change `slippage_bps` is **GLD-vs-GLD**, and `avg_cost`/`unrealized_pnl` are marked in $/share.

**Versioning.** Introduce a **dedicated `exec_price_source_version`** (the price reference is a distinct
policy axis from the current `_EXEC_FIELDS = (default_size, instrument, paper_equity)` and from
`fill_model_version`'s `slippage_bps`), so each fingerprint keeps clean semantics; equivalently an
`execution_policy_version` bump if the operator prefers one axis. Re-pin **BENCH-004** (Execution Layer
Benchmark) and **BENCH-006** (Chain Orchestrator Benchmark), which today pin `instrument_price = 4624.5`.
Old goldens stay byte-reproducible under the prior version.

**A8 — no hard cross-repo predecessor (overrules `app_audit.md` blocker #1).** The defect is real and
high, but the fix is **el_niño-only**: the derived proxy needs only the *existing* `gold_price_proxy`
series + the new `oz_per_share` constant on the sim path, and the live GLD mark on the Alpaca path —
**no Mr-Ripley (Layer-2) change is required**. The real-GLD-share-price-in-the-snapshot ingest is
**demoted to an optional, separately-tracked simulator-fidelity upgrade**: it would plug into the *same*
`exec_ref_gld_price` seam (replacing the derived proxy with a real GLD close) with **zero rework** when/if
it lands. Every "A8 blocks / Mr-Ripley first" statement is corrected to this. *(Do not mistake the
existing `gld_holdings_flow_confirm` — a holdings-flow magnitude, group `flow` — for a price.)*

#### 5.2 Daily-guard `as_of` threading (the mislabeled-"daily" guard fix) (audit warning #3)
`build_guard_request` (`src/execution/runtime.py:78-101`; the two offending inputs at `:91` and `:99`) feeds GATE-001 two **mislabeled "daily"** inputs:
`daily_pnl = sum(pos.realized_pnl …)` (all-time, and ≈0.0 forever on the buy-only path) and
`trades_today = portfolio.next_seq()` (the **lifetime** fill count — `max_trades_per_day` becomes a
lifetime cap that blocks forever after 10 fills). The GATE-001 predicates themselves are sound; the
**inputs** are wrong. **Fix (contained, versioned):** thread the snapshot `as_of` into
`build_guard_request` and add an **`as_of` field on `ExecutionEntry`** (a SCHEMA-015 change), then
day-scope both inputs — **mirroring the PRED-008 cooldown discipline** (`gold/paper_runtime/predicates.py:79-105`
keys off `packet.as_of`, never wall-clock). This is a **cross-layer mirror of the discipline**, not reuse
(the execution layer does not import the paper_runtime predicates). Re-pin BENCH-004/006 (the SCHEMA-015
field changes the replay key). **Scoped v1.**

#### 5.3 `assert port.replayable` precondition + separate ledger/portfolio paths (Q3 prerequisite)
The `replayable` flag **already exists** (an `ExecutionPort` Protocol `@property`; `True` on
`SimulatedBrokerAdapter`, `False` on `AlpacaPaperAdapter`; stamped onto every `ExecutionRecord`). What is
**net-new** is the *enforcing precondition*: add a **cheap `assert port.replayable`** on the canonical
`orchestration.runtime.run_once` (and `run_sequence`), so a non-replayable broker port is **structurally
barred** from the canonical/replay entrypoint and reachable **only** through `operate_live` (§6.1). This is
load-bearing because `run_once(snapshot_path, ledger_path, portfolio_path, …, port=…)` threads
**caller-chosen** paths regardless of port — so the live path **must** thread a **separate
`(ledger_path, portfolio_path)` pair** (the SCHEMA-013 runtime ledger **and** the SCHEMA-015 portfolio),
**physically distinct** from the canonical replay files. The assert + the live-only entrypoint together
enforce that separation.

#### 5.4 Additive SCHEMA-014 / SCHEMA-015 fields (no new table)
- **SCHEMA-014 (Execution Record)** gains, additively: `exec_ref_gld_price` (+ `exec_ref_gld_price_ts` and an `exec_ref_gld_price_basis` label — the pinned + labeled live reference timestamp of §5.1: submit/EOD vs open/routing), `client_order_id`,
  `alpaca_order_id`, `raw_payload`, and the statuses `{QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION}`.
- **SCHEMA-015 (Portfolio State / `ExecutionEntry`)** gains `as_of` (§5.2), plus a **new append-only
  reconcile-entry kind** (§6.2) — distinct from `ExecutionEntry`, because a reconcile observation has no
  `source_record_id` and no `guard_result` (`source_record_id` required on both `ExecutionEntry` and `ExecutionRecord`; `guard_result` required on `ExecutionRecord` only).

All additive + versioned; simulator records keep working; no SQLite, no second source of truth.

### 6. Live-plug-only additions — bucket (ii)

Everything below lives **inside the default-OFF, non-replayable Alpaca plug**, reached **only** via the
new `operate_live` entrypoint. None of it touches the deterministic core, the simulator, or the
benchmarks.

#### 6.1 Parallel non-replayable live entrypoint — fork-(b) (Q2)
Live operability is a **separate non-replayable entrypoint** — `live_runtime.operate_live`, **mirroring**
`orchestration.runtime.run_once` — **not** "behind the same `fill()` port." `ExecutionPort.fill()` stays
the **LONG-only replay contract, untouched, exercised only by the simulator**. The §1/§6 framing is
therefore "behind the same **module boundary**, a **separate non-replayable entrypoint**", not "behind the
same port." `operate_live` **reuses** the deterministic decision + the GATE-001 guard + the idempotency
layer; **only broker mechanics are new**. (The only pre-existing "live touch" today is the opt-in Alpaca
*clock/calendar feed*, not order execution.)

#### 6.2 Reconcile authority, heal, idempotency bifurcation, discrepancy (Q3)
- **Authority split.** The **broker is authority for position truth**; the **local SCHEMA-015 is authority
  for decision lineage + idempotency**.
- **Reconcile-then-act.** Read `GET /v2/positions` (∪ open orders, §6.3); compute the delta to the
  cash-capped target (§6.4); act on the delta — never a blind buy. **Mandatory startup reconcile** before
  any new action.
- **Heal via a new append-only entry kind.** Divergence heals by recording an **append-only
  reconcile-entry** (observed broker `qty` + `avg_entry_price` + a reconcile marker), **not** an
  `ExecutionRecord`/`ExecutionEntry` (both require `source_record_id`, and the record requires
  `guard_result`, which a reconcile lacks). **Live-path-only.**
- **Idempotency bifurcation (not demotion).** `has_execution(source_snapshot_id)` remains the **sole**
  idempotency on the sim/replay path (crash-consistency depends on it); the **live path** additionally owns
  reconcile-delta + open-orders awareness + `client_order_id` 422 dedup. The once-ever guard is
  **bifurcated by path, not weakened**.
- **Discrepancy → terminal-refuse execution only.** On an unexplained discrepancy (broker ≠ local),
  **terminal-refuse ALL execution** — **no auto-flatten** (auto-flatten imports a real-money instinct and
  destroys evidence). "Refuse" **scopes to execution only**: the decision/observation/labeling chain keeps
  running (calibration runs on **decisions**, not fills), so the corpus does **not** stall. Adopting an
  unexplained non-zero broker position is a **governed adopt** (ADR-013 ops-console-gated), never
  automatic.

#### 6.3 In-flight / queue window ownership (Q4)
The cross-snapshot in-flight/queue window is owned by an **open-orders-aware reconcile**: read
**positions ∪ open orders**; `delta = target − position − Σ(expected-lineage open-order qty)`; a **queued
order nets to zero → NO_ACTION**. **Two windows, two owners:** the open-orders-aware reconcile owns the
**cross-snapshot queue**; `client_order_id` 422 owns **same-order duplicate-submit only**. An
**unexpected** open order (wrong qty/side, or an unknown `client_order_id`) is **not netted** → it is a
§6.2 discrepancy → terminal-refuse → governed adopt. *(Motivation: the weekend case is foreclosed by
`operational_ok`; the real trigger is **>1 ADMITting snapshot between two opens** — catch-up / backfill /
manual multi-run — rare, severe, and closed **structurally**, not by timing.)*

#### 6.4 Sizing + cash-cap (Q5)
- **Cash-cap binds to the literal settled-cash field** from `GET /v2/account` — **never any
  `*_buying_power`** (this makes "no margin" *structural* on any account type, even a margin-default paper
  account).
- **Fixed-notional is live-plug-only.** The **sim keeps fixed-qty `default_size`** (a notional on the sim
  path would change `state_hash` and break BENCH). Accept the **sim(fixed-qty) vs live(fixed-notional)
  asymmetry** — it diverges P&L *magnitude*, not *direction*.
- **Effective reconcile target is cash-capped:** `target = min(configured_notional, settled_cash)` (so
  §6.3's reconcile converges).
- **Fractionable (B2).** `GET /v2/assets/GLD → fractionable`: `true` → `notional` market+day; `false` →
  integer shares = `floor(cash_capped_notional / live_submit_mark)`. **Live-plug-only.**

#### 6.5 Accumulate-only sim, sell-fold, side-based adapter (Q6)
- **The simulated/replay portfolio is a determinism vehicle — buy-only, never realizes — by design**
  (teaching the sim to sell breaks BENCH). `realized_pnl` stays 0.0 on the sim path; its `unrealized_pnl`
  (mark-to-snapshot over accumulate-only buys) is a **plausible-but-wrong artifact** — **labeled
  non-strategic** and **kept out of every performance / ops-console reading**.
- **The sell-fold is live-only**, in `live_runtime`, **never `execute()`**:
  `_apply_sell → realized_pnl += qty × (exit_fill − avg_cost); position → 0`.
- **The live adapter is side/order-based** (`submit_market_buy` / `submit_market_sell`) driven by the
  **reconcile delta** — LONG→buy, FLAT→sell, AVOID/WATCH→NO_ACTION (resolved **before** the adapter). The
  v0 `AlpacaPaperAdapter.fill(direction)` (LONG-only, raises on non-LONG) is **superseded on the live path
  under fork-(b)** — **repurpose/remove it, do not extend it.**

#### 6.6 Order/state machine + typed error handling (the audit's ungoverned findings)
- **Order model.** market + `time_in_force=day` (queue-to-next-open). **Not OPG** (incompatible with
  fractional notional), **not** broker-side conditional orders.
- **State machine.** `accepted`/`pending_new`/`new` = **QUEUED** (not an error, not resent; next reconcile
  sees the fill) — this fixes the v0 **sync-fill raise** (the `_FILLED_STATUSES` gate). Fills resolve via
  `GET /v2/positions` + `GET /v2/orders`, **never the synchronous `POST` echo** (note: there is **no**
  `GET /v2/orders/reconcile` endpoint). `filled_qty < requested` = **PARTIAL** (next reconcile corrects);
  timeout / no-response = **EXECUTION_UNCERTAIN** + halt that instrument (no blind retry); auth error =
  halt.
- **Typed error handling.** Wrap the order `urlopen` in `try/except HTTPError/URLError`, **parse the reject
  body**, route to **EXECUTION_UNCERTAIN/halt**, and **persist `raw_payload`** (the v0 discards it). Add a
  **4xx test** (the suite stubs only terminal *sync* statuses — `filled`/`rejected` — with no async-queued or 4xx-`HTTPError` coverage).
- **429 / `Retry-After`.** Honor `Retry-After`, **no blind resend**; 429 is part of the §6.6 state machine.
- **`GET /v2/account` status gate.** The v1 startup reconcile requires
  `status == "ACTIVE" && !trading_blocked && !account_blocked` (recorded here so it is governed).
- **Operator kill switch.** Add an **audited Tier-2 halt** that writes `halt=True` (the operational feed
  already honors `halt`) as the **governed kill mechanism**; the existing one-shot-enable + unregister
  is a coarse manual disable, **not** a second governed kill mechanism. *(One mechanism chosen, per the Q-lock: the audited Tier-2 halt.)*

### 7. Determinism & quarantine (binding)
The simulator remains the byte-identical replay/benchmark path (BENCH-004/006 unchanged **except** the
§5.1 price-source and §5.2 `as_of` re-pins). The Alpaca plug is **non-replayable** (logged, never replayed,
never in benchmarks), **default-OFF**, enabled only via the ADR-013 ops-console gated-live action
(confirm + audit + paper-host precondition), and reached only through `operate_live` past the
`assert port.replayable` fence (§5.3). No broker state, order id, or live fill ever reaches the
deterministic core or a replayed record. **Threading any live broker read into the shared deterministic
guard input is forbidden** — the audit verified a live account read folded into `build_guard_request`
would contaminate the replay key and break BENCH-004/006.

### 8. Pre-code gates & open flags
**Closed by the audit (no longer blocking):** bare-numeric `qty` accepted by Alpaca (PASS); market orders
return async `accepted`/`pending_new` (confirms the QUEUED reality, §6.6); `GET /v2/calendar` holiday
behavior honored (PASS). **El_niño-side, no cross-repo predecessor:** the §5.1 GLD-price fix (the former
A8/B6 "Mr-Ripley first" is overruled — Step 3). **Empirical preconditions (no live code until confirmed):**
B1 (`client_order_id` length/charset), B2 (GLD `fractionable`), B3 (the **settled-cash field name** /
`multiplier`), and the **live order-lifecycle facts** (`GET /v2/positions ∪ /v2/orders` shapes).

**Empirical verification (2026-06-25, operator paper-account probe `scripts/alpaca_paper_e2e_probe.py`):**
- **B2 — VERIFIED:** GLD `fractionable = true` → the live path uses notional market+day orders.
- **B3 — VERIFIED:** `cash` is present (=100000) on `GET /v2/account`. The account is **`multiplier` = 4**
  (a **margin-default / PDT** account, `buying_power` = 400000 = 4x) — *exactly* the §6.4 case: capping on
  the literal `cash` keeps "no margin" structural and ignores the 4x buying_power. `cash_withdrawable` is
  absent (Broker-API only), confirming `cash` is the field to bind.
- **Live GLD mark (§5.1 / Blocker 1) — VERIFIED:** `data.alpaca.markets/v2/stocks/GLD/trades/latest`
  returned `trade.p` = 370.65 / `trade.t` (RFC-3339). The real mark (370.65) sat ~14% below the sim derived
  proxy (`gold_spot × OZ_PER_SHARE` ≈ 431.5) — empirical proof that slipping against the proxy would be
  wrong; the live path correctly reads the real mark.
- **Doc-verified, no empirical needed:** the order-lifecycle facts (positions exclude un-filled; `status`
  filtering; async fill) and the REST `client_order_id` max (128 — the 48 cap is the FIX limit, self-imposed-safe).
- **B1 — STILL PENDING:** the duplicate-`client_order_id` → 422 dedup contract was not exercised (the probe
  ran read-only). Run `--submit-order` to lock the exact 422 status/body before paper accumulation goes live.

**Sequencing:** adapter v1 only after this ADR is Accepted; gated-live enable stays behind the ADR-013
HARD PAUSE; calibration bumps stay DEFER until the ADR-012 gate passes.

## Enumerated defects (the audit's ungoverned findings, now each owned)

| # | Defect (audit ref) | Severity / face | Scope | Fix + one-line rationale |
|---|---|---|---|---|
| 1 | **Sync-fill raise** — `_FILLED_STATUSES` gate raises on `accepted`/`pending_new` (`alpaca_adapter.py:112`) | high / active-bug face of the QUEUED gap | **v1** | §6.6 state machine; resolve fills via `GET /v2/positions`+`/v2/orders`, never the sync `POST` echo — async fills are the norm |
| 2 | **Mislabeled "daily" guard** — `daily_pnl`=all-time, `trades_today`=lifetime `next_seq()` | medium / dormant | **v1** | §5.2 thread snapshot `as_of` + `ExecutionEntry.as_of` (SCHEMA-015) + BENCH re-pin, mirroring PRED-008 — keep the guard replay-safe and actually day-scoped |
| 3 | **Uncaught `HTTPError` + discarded reject** — no `try/except`, body dropped (`alpaca_adapter.py:141-154`) | medium | **v1** | §6.6 catch `HTTPError/URLError`, parse body → EXECUTION_UNCERTAIN/halt + persist `raw_payload`; add a 4xx test — one root cause covers insufficient-BP and wash/forbidden |
| 4 | **No 429 / `Retry-After`** — genuinely ungoverned | medium | **v1** | §6.6 honor `Retry-After`, no blind resend, 429 in the state machine — rate limits are real even at low volume |
| 5 | **No `GET /v2/account` status gate** | low / ungoverned | **v1** | §6.6 require `status=="ACTIVE" && !trading_blocked && !account_blocked` in startup reconcile; record so it is governed |
| 6 | **No operator kill switch** — `halt` is read-only on the dashboard | low / ungoverned | **v1** | §6.6 audited Tier-2 halt writing `halt=True` (the feed already honors it) — one chosen, governed mechanism |
| 7 | **No broker-traceability fields** — no `alpaca_order_id`/`raw_payload` persisted | low / governed-gap | **v1** | §5.4 additive on SCHEMA-014 — broker lineage for audit |
| 8 | **Early-close / half-days** discarded at session granularity | low / ungoverned | **deferred** | Immaterial at **day** granularity — documented; revisit only if intraday is ever in scope |
| 9 | **Clock-feed TZ normalization** — `_calendar_date` not normalized near 00:00–05:00 UTC | low | **deferred** | Not triggered by this data (US-afternoon UTC) + fail-closed (wrong day → `closed()`); fix needs a near-midnight fixture and **must touch both feeds together** to keep the feed-equivalence test green |
| 10 | **Audit `actor`/`who` field** absent on `AuditEntry` | low / ungoverned | **deferred** | **Single operator** — rationale recorded; add a field only if multi-actor ever applies |
| 11 | **GDPR/CCPA "N-A"** reasoned but unrecorded | doc | **deferred** | Paper-only / virtual-money / single-operator / no custody → genuinely N-A; this one-line governance note records the rationale |
| 12 | **No rate limiter** (~200 req/min) | low / ungoverned | **deferred** | Single-instrument **daily** volume makes it near-moot; the 429 handler (#4) is the real safeguard — documented |

## Current state vs v1 delta (the eight components)

| Component (roadmap step) | Current state (audit-grounded) | v1 action |
|---|---|---|
| 1 Governing ADR | DONE (ADR-011 gate f, closed) | this ADR-014; inherit, don't re-decide |
| 2 Execution adapter | PARTIAL — one-shot LONG BUY; raises on async fill | side-based reconcile-then-act + FLAT→sell + `client_order_id` — **live plug only**, via `operate_live` |
| 3 Fill-record persistence | DONE (SCHEMA-014/015 JSON, once-ever) | additive fields only (§5.4); **no SQLite** |
| 4 Instrument mapping & sizing | PARTIAL — fixed `default_size`, no cash-cap | live fixed-notional + **settled-cash** cap + `fractionable` (§6.4); sim stays fixed-qty |
| 5 Error handling / fail-closed | PARTIAL — fail-closed but synchronous; HTTPError raw; no 429 | QUEUED/PARTIAL/EXECUTION_UNCERTAIN + typed errors + 429 + startup reconcile (§6.6) — live plug |
| 6 Scorecard | DONE-VIA MOD-009 / ADR-012 | reuse; **no new `scorecard` table** |
| 7 Env isolation | DONE (parsed-hostname equality) | keep; **reject the substring regression** |
| 8 Observation window | DONE (ADR-012 gates + MOD-009) | consume; direction-accuracy gate; slippage GLD-vs-GLD, live-recorded |

## Alternatives Considered

- **Author under "ADR-010" / rewrite the execution layer.** Rejected — number collision (ADR-010 =
  JARVIS); a rewrite is exactly the "significant modification of post-ADR-11 implementations" the
  constraint forbids.
- **Put reconcile/SELL/`client_order_id` behind the same `fill()` port (or in the core/orchestrator).**
  Rejected — that either modifies the deterministic core + benchmarks or overloads the LONG-only replay
  contract with broker realism. Broker-realism belongs in the non-replayable plug behind a **separate
  `operate_live` entrypoint** (§6.1).
- **Auto-flatten an unexplained broker position on discrepancy.** Rejected — it imports a real-money
  instinct and **destroys the evidence** needed to diagnose the divergence; the safe response is
  terminal-refuse-execution + governed adopt (§6.2).
- **Cash-cap against `buying_power`.** Rejected — `*_buying_power` can encode margin; binding to the
  **literal settled-cash** field makes "no margin" structural on any account type (§6.4).
- **Teach the simulator to sell / mark a portfolio `value`.** Rejected — realizing on the sim path changes
  `state_hash` and breaks BENCH; the sim is an accumulate-only **determinism vehicle**, and realized P&L /
  exits are **live-only** (§6.5).
- **`client_order_id` as the cross-snapshot in-flight owner.** Rejected — 422 only catches **same-order**
  duplicate submits; the **cross-snapshot queue** needs an open-orders-aware reconcile (two windows, two
  owners — §6.3).
- **A8 blocks on a Mr-Ripley ingest.** Rejected (overrules `app_audit.md` blocker #1) — the GLD-price fix
  is **el_niño-side** (derived proxy on the sim path, live GLD mark on the Alpaca path); the real-GLD
  ingest is an **optional fidelity upgrade** behind the same seam (§5.1).
- **New SQLite `fill_record` / `scorecard` stores.** Rejected — second source of truth; duplicates
  SCHEMA-014/015 + MOD-009; "scorecard" collides with the treasury SCHEMA-005.
- **OPG / market-on-open.** Rejected — incompatible with fractional notional; market+day queue-to-next-open
  is the path.

## Consequences

### Positive
- Turns the dormant v0 stub into an operable paper adapter (reconcile-then-act, FLAT→exit, idempotent,
  cash-capped, queued/partial/uncertain-aware, reconcile-healing) **without disturbing the deterministic
  spine** — the simulator, core, orchestrator, and benchmarks are untouched but for the §5.1/§5.2 versioned
  re-pins.
- Fixes a real latent defect (GLD-vs-gold-spot price/slippage) as a **contained, versioned, el_niño-only**
  amendment — **A8 no longer blocks on a cross-repo ingest**.
- Closes the audit's ungoverned findings (sync-fill raise, mislabeled daily guard, uncaught HTTPError, 429,
  account-status gate, kill switch, broker-traceability) — each now owned, scoped v1 or explicitly deferred
  with a rationale.
- All new non-determinism is quarantined in the default-OFF live plug, behind a `assert port.replayable`
  fence and the ADR-013 gated-live surface; the decision/labeling chain keeps running even when execution
  is refused, so the corpus never stalls.
- The clean **(i) shared-versioned / (ii) live-plug-only** split makes this a tidy `/prd` slice source.

### Negative / Trade-offs
- Four shared changes (the GLD price source, the daily-guard `as_of` threading, the `assert port.replayable`
  precondition, the additive SCHEMA-014/015 fields) + BENCH-004/006 re-pins + a new `exec_price_source_version`
  axis — more than the v1 draft's "exactly one", but all additive and versioned.
- A deliberate **sim(fixed-qty) vs live(fixed-notional)** asymmetry (P&L magnitude, not direction), and a
  sim portfolio whose `unrealized_pnl` is a labeled non-strategic artifact.
- The live plug grows a genuine broker-realistic surface (reconcile / heal / state machine / side-based
  adapter / cash-cap) — larger, but quarantined, default-OFF, and behind a separate entrypoint.

### Risks
- **`client_order_id` length / GLD fractionable / settled-cash field name** → empirical flags B1/B2/B3
  close before live code.
- **Drift into modifying the deterministic core** → mitigated by §1/§5.3/§7 (broker-realism is
  live-plug-only behind `operate_live` + the `assert port.replayable` fence; the simulator stays canonical).
- **A reconcile-heal masking a real divergence** → mitigated by terminal-refuse-execution + governed adopt
  (§6.2): healing is *recorded*, adoption of an unexplained position is *operator-gated*, never automatic.
- **Over-trust of the UI enable** → mitigated by the ADR-013 server-side paper-host precondition (the real
  guarantee), not the modal.

## Pre-launch verification (delta from the roadmap A/B blocks)
A-block (Layer-2 data/snapshot freshness, fail-closed, PIT, replay) runs now. **A8/B6 are re-scoped:** the
GLD-vs-GLD price/slippage fix is el_niño-side (§5.1) and is **no longer gated on a Mr-Ripley ingest** — the
real-GLD-in-snapshot upgrade is optional and separately tracked. **B10 is rewritten against the
parsed-hostname guard** (not the substring check). The live B-block (B1 `client_order_id` length/charset,
B2 `fractionable`, B3 settled-cash field/`multiplier`, plus the live order-lifecycle / positions /
open-orders facts) applies to the live plug and closes before paper accumulation goes live. Baseline: the
suite is **~1050 tests** (the roadmap's "853" is stale; the audit confirms ~1050). Every item PASS before
paper accumulation goes live.

## Out of scope (Phase D / later, each behind its own evidence gate)
Live-money execution (structurally blocked); short; margin; oil / second instrument; confidence-scaled
sizing; broker-side conditional orders; OPG / market-on-open; WebSocket `trade_updates` streaming
(the reconcile poll is the chosen mechanism); the real-GLD-share-price snapshot ingest (optional
fidelity upgrade behind the §5.1 seam); Zapier; the Alpaca NL MCP server; a Phase-D live-money ADR +
canary plan (only after KA-010 paper-validation + the ADR-012 calibration lift + this ADR's acceptance).

## Relationships

### Depends On
- [[Execution]]
- [[Chain Orchestrator]]
- [[Paper-Trading Runtime]]
- [[Gold Forward-Return Labeler]]

### Justified By
- [[ADR - Execution Layer Planning]]
- [[ADR - Empirical Calibration Methodology]]
- [[ADR - Operations Control Plane]]
- [[ADR - Paper-Trading Runtime Planning]]

### Constrained By
- [[No Wiki Mutation]]
- [[Canonical Ownership]]

### Originates From
- [[Paper Trading Validation]]
- [[Agent Safety Principles]]
- [[Guardrail Philosophy]]
