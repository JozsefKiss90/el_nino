---
type: decision_record
canonical_id: ADR-014
status: draft
implementation_status: not-started
canonical: true
created: 2026-06-21
updated: 2026-06-21
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "el nino alpaca paper E2b roadmap.md"
  - "E2b_ROADMAP_alignment_review.md"
related_files:
  - "[[alpaca_adapter.py]]"
  - "[[alpaca_clock_feed.py]]"
  - "[[adapters.py]]"
  - "[[Execution Record Schema]]"
  - "[[Portfolio State Schema]]"
related_tests: []
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

**Draft** — authored 2026-06-21 (the governed `status: draft` stand-in for "Proposed", per the ADR-011 convention). This is the reissue of the externally-developed "Epoch E2b: Alpaca PAPER Execution Adapter" roadmap, **renumbered from its colliding "ADR-010" to ADR-014** (ADR-010 is [[ADR - JARVIS GraphRAG Integration]]; the Alpaca adapter is governed by [[ADR - Execution Layer Planning]] (ADR-011) gate (f), already closed). It is **scoped as an additive delta over the built v0**, not greenfield work. No code is authored by this record; the implementation slices proceed under its invariants after acceptance. **HARD PAUSE: this ADR is reviewed and accepted before any adapter-v1 code is written.**

## Context

The Layer-3 lineage runs end-to-end and the execution layer already exists. [[ADR - Execution Layer Planning]] (ADR-011) is Accepted with creation gates (a)–(f) **closed**; gate (f) is the Alpaca-adapter boundary. The built v0 comprises: [[Execution]] (MOD-008) — a pure `execute()` core + the `INT-011` `ExecutionPort` (`fill()`), with `SimulatedBrokerAdapter` (canonical, deterministic) and a **default-OFF, paper-host-only, fail-closed `AlpacaPaperAdapter`** (FILE-038) behind the same port; [[Execution Record Schema]] (SCHEMA-014) + [[Portfolio State Schema]] (SCHEMA-015) as append-only, snapshot-keyed JSON with once-ever idempotency; [[Chain Orchestrator]] (MOD-010) threading the chain; [[Gold Forward-Return Labeler]] (MOD-009) + [[ADR - Empirical Calibration Methodology]] (ADR-012) as the observation/performance gate (currently DEFER on all targets — monochromatic corpus); and [[ADR - Operations Control Plane]] (ADR-013) as the operator surface whose gated-live tier already exposes a confirmed, audited, paper-host-precondition Alpaca enable.

What the v0 adapter is **not** is *operable*: it is a one-shot market BUY that fills only an approved LONG, with no position reconcile, no FLAT→exit, no deterministic `client_order_id`, no cash-cap, and no queued/partial/uncertain handling. Two further problems exist independent of the adapter: the env-isolation guard is already hardened to **parsed-hostname equality** (so the roadmap's substring guard is a regression to reject), and the execution path currently uses `instrument_price = gold_price` — **gold spot ($/oz, ≈4624 in the real snapshot)** — as the GLD fill reference, making fills and `slippage_bps` compare GLD against gold spot (a latent defect; an ADR-011 D1 interaction).

This ADR answers: **under what constraints is the v0 stub upgraded to an operable paper adapter — adding reconcile-then-act, FLAT-exit, deterministic idempotency, cash-cap, and a queued/partial state machine, and fixing the GLD price reference — WITHOUT significantly modifying any post-ADR-11 implementation, without a second source of truth, and without weakening the determinism, paper-only, fail-closed boundary?**

## Decision

### 1. Strategy — additive, live-plug-quarantined, simulator-unchanged
The v1 operability is introduced as an **additive delta**. The deterministic spine — the pure `execute()` core, `SimulatedBrokerAdapter`, MOD-010 orchestrator, MOD-007 runtime, and the BENCH-004/006 replay benchmarks — stays **structurally unchanged** as the canonical replay path. **All broker-realism (reconcile, SELL, `client_order_id`, cash-cap, account-type, fractionable, queued/partial/uncertain) lives inside the default-OFF, non-replayable `AlpacaPaperAdapter`** (the ADR-011 §2 / gate-(f) quarantine: logged-not-replayed, never in benchmarks). Shared code changes are **additive + versioned only**; there is exactly one contained shared correction (§5). This is what satisfies "introduce the improvements without significant modification of post-ADR-11 implementations."

### 2. Constitution (preserved, binding)
Gold-first, fail-closed, snapshot-driven: same snapshot in → bit-identical decision out. **Long-or-flat only** (LONG/FLAT/AVOID/WATCH); no short, **no margin** — cash-account semantics only; binary size (no confidence-scaled sizing). **Paper only** (`paper-api.alpaca.markets`, virtual money); live money is Phase D, structurally blocked, out of scope. Governance before autonomy: gated, not self-driving; every fill-record references the governing `snapshot_id`; writes are immutable (`INSERT OR IGNORE`-equivalent, never `UPDATE`). La Niña / exits live in **our deterministic evaluator, never broker-side conditional orders**.

### 3. Inherited unchanged — NOT re-decided (respect the built v0)
v1 inherits and must not re-author: ADR-011 gate (f) boundary; the **parsed-hostname env guard** in `alpaca_adapter.py` / `alpaca_clock_feed.py`; the `INT-011` port + pure `execute()` core + `SimulatedBrokerAdapter` as the canonical replay path; SCHEMA-014/015 append-only-JSON + `source_snapshot_id` once-ever idempotency; MOD-010 orchestrator; MOD-007 runtime (incl. PRED-008 computed cooldown); MOD-009 / ADR-012 as the observation + performance gate; ADR-013 ops console as the gated-live enable surface (confirm + audit + paper-host precondition already built); ADR-011 D2 (fixed size, sizing deferred). These are the platform v1 builds on.

### 4. Two regressions removed (explicit)
- **Env isolation is DONE.** The roadmap's `if "paper-api" not in base_url` substring check is **rejected** — it is the exact credential-exfil bypass (sub/super-domain, query-string smuggling) already replaced by parsed-hostname equality. v1 reuses the existing guard and must never reintroduce a substring test.
- **No new SQLite stores.** The proposed `fill_record` / `scorecard` tables are **rejected** as a second source of truth (ADR-009 §2, ADR-011, ADR-013 §11). Execution outcomes stay on SCHEMA-014/015 (additive fields, §6); per-regime direction accuracy stays in **MOD-009 / ADR-012**. The name "scorecard" is avoided ([[Evaluation Scorecard Schema]] SCHEMA-005 is the separate Supervisor treasury branch, ADR-004).

### 5. The one corrected latent defect — GLD price reference (an ADR-011 D1 amendment)
The execution **fill/slippage reference must be the GLD share price** (`exec_ref_gld_price`, $/share), **not** gold spot. `gold_price` (spot, $/oz) remains the **decision-context** reference only (it stays the regime/decision input — unchanged). `slippage_bps` becomes **GLD-vs-GLD**. This is a **contained, additive, versioned** change to the shared price source: add the GLD price as an explicit execution input (re-derived from the snapshot per the D1 discipline — never a live read on the replay path), correct the slippage in `models.py`/`adapters.py`/`alpaca_adapter.py`, bump `execution_policy_version` (or a dedicated `exec_price_source_version`), and re-pin BENCH-004/006; old versions stay byte-reproducible. **Precondition (BLOCKING):** verify the snapshot carries a GLD close (roadmap A8) — **if absent, a minimal Layer-2 ingest extension precedes adapter v1.** This is the only shared modification; everything else in §6 is live-plug-only.

### 6. The v1 adapter delta (all inside the quarantined live Alpaca plug)
- **Reconcile-then-act.** `GET /v2/positions`; compute the delta to target (LONG → full fixed-notional target; FLAT → zero; AVOID/WATCH → **NO_ACTION record, no order**); act on the delta — never a blind buy. **Mandatory startup reconcile** before any new action; a startup discrepancy (broker ≠ local) refuses new action.
- **FLAT → sell-to-zero** on the live path (the exit the v0 lacked), expressed as our deterministic evaluator's decision, not a broker-side conditional order.
- **Deterministic `client_order_id`** = `hash(snapshot_id + asset_id + intended_action)` (shortened per the B1 length flag), giving Alpaca-side **HTTP 422 dedup** — reconciled **with** (not replacing) the existing `source_snapshot_id` once-ever guard.
- **Fixed-notional sizing + cash-cap.** `notional` on market+day; **`notional ≤ available_cash`** (`GET /v2/account`) so margin semantics are structurally excluded even on a margin-default paper account. Realizes ADR-011 D2 concretely; additive fields on `ExecutionPolicyConfig` + version bump.
- **`fractionable` check.** `GET /v2/assets/GLD → fractionable` (B2); else integer-share sizing.
- **Order model.** market + `time_in_force=day` (queue-to-next-open). **Not OPG** (incompatible with fractional notional), **not** broker-side conditional orders.
- **State machine.** `accepted`/`pending_new` = **QUEUED** (not an error, not resent; next reconcile sees the fill); partial fill = `filled_qty` actual, next reconcile corrects (paper simulates ~10% partials); timeout/no-response = **EXECUTION_UNCERTAIN** + halt on that instrument (no blind retry); auth error = halt.
- **SCHEMA-014 additive fields** (not a new table): `client_order_id`, `alpaca_order_id`, `exec_ref_gld_price`, statuses `{QUEUED, PARTIAL, EXECUTION_UNCERTAIN, NO_ACTION}`, `raw_payload`. Additive + versioned; simulator records keep working.

### 7. Determinism & quarantine (binding)
The simulator remains the byte-identical replay/benchmark path (BENCH-004/006 unchanged except the §5 price-source re-pin). The Alpaca plug is **non-replayable** (logged, never replayed, never in benchmarks), **default-OFF**, enabled only via the ADR-013 ops-console gated-live action (confirm + audit + paper-host precondition). No broker state, order id, or live fill ever reaches the deterministic core or a replayed record.

### 8. Pre-code gates & open flags
**Blocking pre-work (parallel to acceptance):** A8 (GLD close in the snapshot) and B6 (GLD-vs-GLD slippage, §5). **Empirical preconditions (no code until confirmed):** B1 (`client_order_id` length/charset), B2 (GLD `fractionable`), B3 (cash vs margin default / `multiplier`). **Sequencing:** the roadmap A-block runs now; adapter v1 only after this ADR is Accepted; gated-live enable stays behind the ADR-013 HARD PAUSE; calibration bumps stay DEFER until the ADR-012 gate passes.

## Current state vs v1 delta (the eight components)

| Component (roadmap step) | Current state | v1 action |
|---|---|---|
| 1 Governing ADR | DONE (ADR-011 gate f) | renumber → this ADR-014; inherit, don't re-decide |
| 2 Execution adapter | PARTIAL (one-shot LONG BUY) | add reconcile-then-act + FLAT-exit + `client_order_id` — live plug only |
| 3 Fill-record persistence | DONE (SCHEMA-014/015 JSON) | additive fields only; **no SQLite** |
| 4 Instrument mapping & sizing | PARTIAL (`default_size`, no cash-cap) | add fixed-notional + cash-cap + `fractionable`; version bump |
| 5 Error handling / fail-closed | PARTIAL (fail-closed, synchronous) | add QUEUED/PARTIAL/EXECUTION_UNCERTAIN + startup reconcile — live plug |
| 6 Scorecard | DONE-VIA MOD-009 / ADR-012 | reuse; **no new `scorecard` table** |
| 7 Env isolation | DONE (hostname-equality guard) | keep; **reject the substring regression** |
| 8 Observation window | DONE (ADR-012 gates + MOD-009) | consume; direction-accuracy gate, slippage live-only |

## Alternatives Considered

- **Author under "ADR-010" / rewrite the execution layer.** Rejected — number collision (ADR-010 = JARVIS); ignores ADR-011; a rewrite is exactly the "significant modification of post-ADR-11 implementations" the constraint forbids.
- **Put reconcile/SELL/`client_order_id` in the pure `execute()` core or the orchestrator.** Rejected — that modifies the deterministic core + benchmarks; broker-realism belongs in the non-replayable plug (ADR-011 §2).
- **New SQLite `fill_record` / `scorecard` stores.** Rejected — second source of truth; duplicates SCHEMA-014/015 + MOD-009; "scorecard" collides with the treasury SCHEMA-005.
- **Substring `paper-api` guard.** Rejected — known credential-exfil bypass; hostname-equality already in place.
- **OPG / market-on-open.** Rejected — incompatible with fractional notional sizing; market+day queue-to-next-open is the path.
- **Keep gold spot as the GLD fill price.** Rejected — meaningless slippage and wrong P&L units; the GLD share price is the correct reference (§5).

## Consequences

### Positive
- Turns the dormant v0 stub into an operable paper adapter (reconcile, FLAT-exit, idempotent, cash-capped, queued/partial-aware) **without disturbing the deterministic spine** — the simulator, core, orchestrator, and benchmarks are untouched but for one versioned re-pin.
- Removes both regressions (the exfil-prone guard, the second-source-of-truth stores) before they enter the codebase.
- Fixes a real latent defect (GLD-vs-gold-spot price/slippage) as a contained, versioned amendment.
- All new non-determinism is quarantined in the default-OFF live plug, behind the ADR-013 gated-live surface.

### Negative / Trade-offs
- One shared, versioned change (the GLD price source) + a BENCH-004/006 re-pin; additive SCHEMA-014 fields + an `execution_policy_version` bump.
- A8 may force a Layer-2 ingest extension before the adapter (if the snapshot lacks a GLD close).
- The live plug grows a genuine broker-realistic surface (reconcile/state-machine) — larger, but quarantined and default-OFF.

### Risks
- **GLD price missing in the snapshot** → ingest pre-work (mitigated: A8 is a blocking gate).
- **`client_order_id` length / GLD fractionable / margin default** → empirical flags B1/B2/B3 close before code.
- **Drift into modifying the deterministic core** → mitigated by §1/§7 (broker-realism is live-plug-only; the simulator stays canonical).
- **Over-trust of the UI enable** → mitigated by the ADR-013 server-side paper-host precondition (the real guarantee), not the modal.

## Pre-launch verification (delta from the roadmap A/B blocks)
A-block (Layer-2 data/snapshot freshness, fail-closed, PIT, replay) runs now; **A8 (GLD close present) is elevated to blocking.** B-block applies to the live plug, with **B6 (GLD-vs-GLD slippage) elevated to blocking** and **B10 rewritten against the parsed-hostname guard** (not the substring check). Baselines refreshed: suite is **1050 tests** (the roadmap's "853" is stale). Every item PASS before paper accumulation goes live.

## Out of scope (Phase D / later, each behind its own evidence gate)
Live-money execution (structurally blocked); short; margin; oil / second instrument; confidence-scaled sizing; broker-side conditional orders; OPG / market-on-open; Zapier; the Alpaca NL MCP server.

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
