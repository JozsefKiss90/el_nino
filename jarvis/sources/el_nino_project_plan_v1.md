# El Niño Project — Master Planning Document
## Mr. Ripley Layer 3 Decision Engine

> **Status:** Working specification — not a build order  
> **Last updated:** 2026-06-11 (repo scan + state sync)  
> **Grounded in:** Mr. Ripley canonical docs as of 2026-03-22; el_nino repo as of 2026-06-11; Slice 2 audit (Jun 2026)  
> **Parts:** 0 (current state) + 5 + §5.3 extended look-ahead bias section

---

# Part 0 — Jelenlegi Állapot (2026-06-11)

## Mit épített meg a barát (el_nino repó)

Az el_nino repó (`C:\Code\el_nino`) a Layer 3 önálló kódbázisa — nem a Mr. Ripley repóban van, hanem külön projektként, saját Python package-ekkel, Obsidian dev_graph-fal és ADR-lánccal. Ez a repó tartalmazza az El Niño tényleges kódját.

### Megépített modulok

| Modul | ID | Leírás | Audit |
|-------|----|--------|-------|
| Snapshot Consumer | MOD-003 | Layer 2 snapshot beolvasása, fail-closed | — |
| Feature Builder | MOD-004 | 14 macro feature számítása a snapshotból | — |
| Regime Classifier | MOD-005 | 11 rezsim + NEUTRAL + INDETERMINATE determinisztikus osztályozás | **97/100** |
| Gold Decision Builder | MOD-006 | FeatureVector + Regime → GoldDecisionPacket (direction + confidence) | **94/100** |
| Paper Trading Runtime | MOD-007 | DecisionPacket → ADMIT/HOLD/REJECT (admission gate) | **97/100** |
| Risk Guardrail Engine | MOD-001 | Predikátum-alapú guardrail keret | — |

**Teljes tesztcsomag: 853 teszt, mind zöld.**

### Governance struktúra

A repó ADR-lánccal (Architecture Decision Records) van irányítva: ADR-001–ADR-009. Minden kódváltozást megelőz egy ADR, ami a döntést rögzíti. A dev_graph (Obsidian + Neo4j, ~140 node, ~920 él) az architektúra élő tükre. Ez a governance modell kötelező — minden új komponensnek ebbe kell illeszkednie.

### Corpus státusz

- **DEBT-01 javítva** (2026-06-11): a `snapshot_publisher` NameError-je kijavítva a Mr. Ripley repóban
- **Napi automatikus task**: `MrRipley-Layer2-DailyEOD`, 23:00 helyi időben, `-StartWhenAvailable` kapcsolóval
- **Valós snapshotok száma**: **2** (2026-05-01 és 2026-06-11)
- **Forward accumulation** indul 2026-06-11-től — minden nap +1 snapshot

---

## Hol tartunk az Epoch-terven

| Epoch | Neve | Állapot |
|-------|------|---------|
| **E1** | DEBT-01 Fix | ✅ **KÉSZ** — 2026-06-11 |
| **E2a** | Paper Runtime (admission gate) | ✅ **KÉSZ** — MOD-007, 97/100 |
| **E2b** | Alpaca Execution Adapter (fills + scorecard) | ❌ **NEM KÉSZ** — következő engineering feladat |
| **E3** | Empirikus kalibráció | ⏳ **FOLYAMATBAN** — corpus gyűlik, naptár-korlátozott |
| **E4** | Supervisor Engine (LLM réteg) | ❌ **NEM KÉSZ** |
| **E5** | Policy Evolution | ❌ **NEM KÉSZ** |
| **E6** | La Niña (feltételes) | ❌ **NEM KÉSZ** — E3 gap mérés dönti el |

> **Kritikus belátás:** Az E2 két részre bomlik. Az admission gate (MOD-007) kész — ez dönti el, hogy egy DecisionPacket ADMIT/HOLD/REJECT-et kap. Az E2b a tényleges végrehajtási adapter: Alpaca paper API hívás, fill rögzítés, scorecard generálás. Ez nincs meg. Ez a következő engineering epoch.

---

# Part 1 — Slice 2 Fit Assessment

## Where Slice 2 Sits in the Layer Model

Slice 2 is Layer 3's first stateful component: an admission gate between a ready gold DecisionPacket and the (future) Execution Adapter. It takes a finished gold-packet and decides ADMIT / HOLD / REJECT, then writes to a ledger. In the project's terminology, this is the Trade Validation Gate re-anchored to gold — the generic predicate pattern was mirrored, not imported (confirmed at AST level in audit finding D6).

This is exactly what the re-grounding proposal called for: keep what was right, re-anchor what was generic.

## Where Slice 2 Precisely Confirms the Plan

**1. Re-grounding is complete.**  
`src/gold/` bounded context, gold-v0 packet, zero treasury/risk imports. CAP-004 (Signal Generation) deprecated. CAP-021 has no edge to the treasury branch. The May "Decision* naming collision" is resolved.

**2. v0 contract discipline.**  
SCHEMA-011 v0.2.0 extension is additive, `packet_id` unchanged, gold fields re-pinned, ADR-governed. This is precisely the antidote to Problem #2 (contract drift) — a formal amendment, not silent change.

**3. v0 guard taxonomy taking shape.**  
`duplicate_ok` (computed, mandatory), `cooldown_ok` (echo, computed, deferred), `supervisor_ok` (explicit stub), operational input. The May matrix showed this as missing — it now exists.

**4. Replay-determinism as keystone.**  
Pure core, zero clock/RNG/IO, `as_of` caller-forwarded, the ledger alone is sufficient replay state. The constitution's replay guarantee is now in code, with 853 green tests.

**5. Minimal core principle applied.**  
Not starting with the Counterfactual Engine — starting with the smallest possible stateful slice. This is the opposite of Problem #4 (overbuilding too early). The Wake-Execute-Sleep model also fits the EOD cadence.

**6. Regime/confidence/direction exists (provisionally).**  
Upstream policy contains "regime thresholds, confidence weights, direction table" — in May this was ❌ in the matrix. The INDETERMINATE→WATCH three-level enforcement is the cleanest materialization of fail-closed philosophy: uncertain state can never reach ADMIT.

## What Slice 2 is NOT — Honestly Stated

The name "Paper-Trading Runtime" is misleading: this is admission-only. There is no fill, no sizing, no P&L, no position tracking. The actual paper trade (the dual-backend Execution Adapter: offline sim + Alpaca) is the next bounded context — the largest uncoded piece of the plan. This is **E2b**.

~~**DEBT-01 is the critical path.**~~ **DEBT-01 is fixed** (2026-06-11). Corpus accumulation has begun. The next blocker is building the Alpaca Execution Adapter (E2b) so that ADMIT decisions can actually be filled and scorecards generated.

The Supervisor (El Niño LLM layer) is not yet built — `supervisor_ok` is a stub waiting for it. The learning layer (Memory, Policy Evolution, Counterfactual) is correctly absent. La Niña is correctly absent — but good news: the runtime patterns (caller-forwarded `as_of`, fixed operational state, ledger threading) are exactly what the IMS/contingency evaluator will need. The architecture is ready for it.

## One-Line Summary

Small slice, right location, right sequence — plan and implementation are aligned with no drift.

---

# Part 2 — Recommendations (R1–R8)

**R1 — ~~Fix DEBT-01 first, everything else is blocked.~~** ✅ **KÉSZ (2026-06-11)**  
~~The snapshot_publisher must run reliably before any corpus-dependent work begins.~~ DEBT-01 javítva: a `snapshot_publisher` NameError kijavítva, napi automatikus task fut. Corpus accumulation megindult.

**R2 — Keep the v0 contract frozen; amendments must be formal.**  
Any new field in DecisionPacket must go through the SCHEMA-011 amendment process: additive only, ADR-governed, dated, reviewed. No silent field additions. The problem this solves: contract drift that corrupts replay.

**R3 — Do not promote provisional thresholds to "calibrated" until E3.**  
Regime thresholds, confidence weights, direction table — these are placeholders until you have a real corpus. Label them explicitly as provisional in code and docs. Promoting them prematurely creates false confidence.

**R4 — The dual-backend Execution Adapter (E2) must produce identical scorecard format.**  
Offline sim and Alpaca paper must output the same scorecard schema. This is what makes backtest and paper results comparable later. Design the schema before building either backend.

**R5 — Supervisor stub must remain a hard blocker, not a silent pass-through.**  
`supervisor_ok = stub_true` is a placeholder. It should log clearly that it is unvalidated. When the real Supervisor is built (E4), it must replace the stub — not coexist with it.

**R6 — La Niña stays in the drawer until E3 gives you the gap measurement.**  
Do not build any intraday component before knowing whether intraday gaps are material relative to the simple stop. E3 measures this from daily high/low. If the gap is not material, La Niña is unnecessary complexity.

**R7 — Policy Evolution proposals must include their own counterarguments.**  
When the system proposes a policy change (E5), the proposal must explicitly argue against itself: insufficient sample size, regime-specificity, alternative explanations. A proposal without counterarguments is not evidence — it is advocacy.

**R8 — Calendar time is the bottleneck, not engineering time.**  
E1 through E3 are dominated by corpus accumulation (daily snapshots, closed trades). Plan accordingly: DEBT-01 fix buys you calendar time. Starting E2 early (even before E3 calibration is complete) lets paper trading accumulate data while calibration runs.

---

# Part 3 — Six-Epoch Roadmap

## Epoch Overview

| Epoch | Name | Key Deliverable | Gate Condition | Státusz |
|-------|------|-----------------|----------------|---------|
| E1 | DEBT-01 Fix | Snapshot publisher runs daily, unattended | N consecutive clean publications | ✅ KÉSZ |
| E2a | Paper Runtime (admission gate) | MOD-007: ADMIT/HOLD/REJECT admission layer | 853 teszt zöld, 97/100 audit | ✅ KÉSZ |
| E2b | Execution Adapter | Alpaca paper fills + offline sim, unified scorecard | N closed trades with complete scorecards | ❌ következő |
| E3 | Empirical Calibration | Thresholds frozen from corpus; gap measured | Walk-forward out-of-sample passes; La Niña decision made | ⏳ corpus gyűlik |
| E4 | Supervisor Engine | El Niño LLM layer live; supervisor_ok populated | Supervisor tested in paper; stub removed | ❌ |
| E5 | Policy Evolution | Human-approved learning pipeline | First full proposal→gate→decision cycle complete | ❌ |
| E6 | La Niña (conditional) | IMS + Contingency Evaluator, alert-only first | Material gap confirmed in E3; paper evidence on alerts | ❌ |

## Epoch Detail

### E1 — DEBT-01 Fix ✅ KÉSZ (2026-06-11)

**What:** Repair the snapshot_publisher so it runs reliably daily without manual intervention.  
**Delivered:** `snapshot_publisher.py` NameError javítva (`H_get_engine_version` → `_get_engine_version`). Napi PowerShell wrapper (`daily_eod_snapshot.ps1`) + Windows Scheduled Task (`MrRipley-Layer2-DailyEOD`, 23:00, `-StartWhenAvailable`). Valós snapshotok: 2026-05-01 és 2026-06-11 (PASS, 16/16 Tier-1, 21 series).  
**Corpus forward accumulation:** Indul 2026-06-11-től.

### E2a — Paper Runtime (Admission Gate) ✅ KÉSZ (2026-06-09, audit 97/100)

**What:** MOD-007 Paper Trading Runtime — determinisztikus admission layer.  
**Delivered:** `src/gold/paper_runtime/` — `evaluate(packet, prior_ledger, operational_input, config) → (RuntimeDecisionRecord, new_ledger)`. Pure core, zero clock/RNG/IO a döntési úton. `run_sequence` byte-identikus replay. Verdiktek: ADMIT / HOLD / REJECT. Ledger `state_hash` alapú dedup (once-ever ADMIT per packet_id). ADR-009 által irányítva.  
**Eredmény a valós snapshotokon:** RESTRICTIVE_RATES → ADMIT. Duplicate presentationnél REJECT.

### E2b — Execution Adapter (Dual Backend)

**What:** Build the two-backend Execution Adapter — offline simulation backend (deterministic, historical data) and Alpaca paper backend (live prices, real fills, virtual money).  
**Why dual backend:** The offline sim validates decision logic quickly on historical data. The Alpaca paper backend captures realistic execution friction (slippage, timing, fill delays). They must use the same decision chain and produce the same scorecard schema.  
**Előfeltétel:** E2a kész (✅). Az ADMIT verdikt már él — most kell a tényleges fill (GLD order Alpaca papíron) + scorecard rögzítés.  
**Unified Scorecard Schema (required fields):**
```
decision_id       — anchors to DecisionPacket
snapshot_id       — anchors to Layer 2 truth
regime_class      — what regime drove the decision
confidence        — at time of decision
preferred_action  — what was decided
fill_price        — actual fill (paper or sim)
expected_price    — mid-price at decision time
slippage          — fill_price - expected_price
outcome_pnl       — realized P&L at close
max_drawdown      — intraday low from entry
hold_duration     — time from entry to close
close_reason      — EOD decision / monitor trigger / stop / manual
backend           — "offline_sim" or "alpaca_paper"
```
**Gate:** N closed trades (suggested: 30) with complete scorecards across both backends.  
**Governance:** ADR-first — új ADR kell a fill-adapter határhoz, mielőtt kód születik (a dev_graph ADR-lánc kötelező).  
**Fontos:** Az Alpaca paper API-t csak a GLD ETF-en, csak paper base URL-en, csak DecisionPacket alapján szabad hívni (LIVE_ENABLED=false).

### E3 — Empirical Calibration

**What:** Replace provisional thresholds with values derived from the actual corpus. Run walk-forward optimization. Measure intraday gap magnitude vs. simple stop.  
**Critical sub-task — gap measurement:**  
Using daily high/low from the corpus, compute: for each closed trade, what was the maximum intraday drawdown? How much did the gap cost beyond the simple stop? If the gap is not material (e.g., stop captured >90% of protection), La Niña is unnecessary. If material, proceed to E6.  
**Calibration rules:**
- Never use future data to set thresholds (point-in-time discipline, see §5.3)
- Out-of-sample period must not overlap training period
- Report confidence intervals on threshold estimates, not point estimates
- Regime-specific thresholds only if sample size supports them (see Problem #11)

**Gate:** Thresholds frozen, documented with sample size and confidence bounds. La Niña decision made (build vs. defer).

### E4 — Supervisor Engine (El Niño LLM Layer)

**What:** Build the actual Supervisor: reads snapshot + feature outputs + regime classification → emits `supervisor_ok` verdict, soft-shrink (reduce position budget), hard-veto (block action), UnknownMode (fallback).  
**LLM role:** Analyst and auditor only. The LLM reads the DecisionPacket candidate and the snapshot context, then emits a structured verdict. It does not generate the decision — it reviews the deterministic system's output.  
**Hard constraints:**
- Supervisor verdict must be machine-readable (no free text at the execution boundary)
- Hard-veto overrides all other signals — no guard can override a veto
- UnknownMode forces NO_TRADE regardless of other guards
- Every supervisor verdict is logged with its reasoning

**Gate:** supervisor_ok field live (stub removed), tested across at least 20 paper trade scenarios including forced veto cases.

### E5 — Policy Evolution (Human-Approved Learning)

**What:** Build the observation and proposal pipeline. The system collects patterns from the scorecard corpus, generates Policy Proposals, and submits them through a human-approval gate.  
**Policy Proposal required structure:**
1. What to change (specific field, threshold, weight — not vague)
2. Evidence base (how many trades, which regime, expected vs actual with delta)
3. Expected impact if adopted
4. Counterarguments (why this might be wrong — required, not optional)
5. Minimum sample size assessment (is the evidence statistically adequate?)

**Three-state gate:**
- **Accept** → versioned policy change, ADR entry, dated with your sign-off
- **Reject** → archived in Failure Library with your stated reason (system does not re-propose same change)
- **Return for refinement** → specific question sent back (e.g., "collect 20 more trades in high-vol regime first")

**What this is NOT:** automatic self-modification. The system never changes a live threshold without your approval.

**Gate:** First complete proposal→gate→decision cycle logged. Failure Library initialized.

### E6 — La Niña (Conditional on E3 Gap Measurement)

**What:** Intraday protection layer. Only built if E3 confirmed material intraday gap vs. simple stop.  
**Architecture (three steps):**

*Step 1 — Dual-Level Truth:*  
Daily EOD macro-snapshot (unchanged) + Intraday Market-State Snapshot (IMS). IMS produced by the Truth Layer (not ad-hoc in the execution adapter), hourly, frozen schema, `ims_id`, `parent_snapshot_id` reference, freshness/provenance stamp, archived. IMS contains only fast-refreshing fields: gold spot/futures, realized vol, VIX, DXY, yields. Never overwrites EOD snapshot.

*Step 2 — Standing Orders / Contingency Table:*  
The EOD DecisionPacket includes a pre-authorized contingency table for the next 24 hours:
```
if intraday_drawdown > X%       → reduce 50%
if realized_vol > Y threshold   → full exit
if IMS stale (> 2 hours)        → freeze + alert (stop remains)
if price reaches Z limit        → execute EOD-authorized entry (timing, not new direction)
```
The Contingency Evaluator (deterministic code, NOT LLM) runs hourly, reads current IMS against the table, executes only pre-authorized transitions. Every action logged with `(eod_decision_id, ims_id, contingency_rule_id, idempotency_key)`.

*Step 3 — Asymmetric One-Way Valve:*  
Intraday authority exists only in risk-reducing direction: reduce, exit, tighten, freeze. New direction, size increases above EOD budget, regime reclassification → EOD only.

**Three guard fields added to DecisionPacket (formal §16.1 amendment):**
- `ims_freshness_ok` — IMS not stale
- `action_budget_ok` — max N contingency actions per day not exceeded
- `cooldown_ok` — hysteresis against whipsaw

**Deployment order:** Alert-only mode first (monitor detects, logs, notifies — does not touch position). Only after alert-only paper evidence shows trigger quality, enable automatic reflex.

**Gate:** N alert-only paper days with trigger quality assessed. Then: N automatic-reflex days with kill switch tested fail-closed.

## Sequenced Roadmap Diagram

```
[E1: DEBT-01] ✅ KÉSZ (2026-06-11)
    │
    ▼ 
[E2a: Paper Runtime / Admission Gate] ✅ KÉSZ (2026-06-09, 97/100)
    │
    ▼ (MOD-007 live, ADMIT/HOLD/REJECT működik)
[E2b: Execution Adapter]  ◄── KÖVETKEZŐ ENGINEERING FELADAT ──────────────────────┐
    │                                                                               │
    ▼ (N closed trades with scorecards)                                            │
[E3: Calibration + Gap Measurement]  ⏳ corpus gyűlik (2 snapshot, napi +1)        │
    │                        │                                                     │
    │                        └─── gap NOT material ──► La Niña: DEFER             │
    ▼ (thresholds frozen)    │                                                     │
[E4: Supervisor]             └─── gap IS material ──► E6 planned                  │
    │                                                                              │
    ▼ (supervisor_ok live)                                                        │
[E5: Policy Evolution]                                                            │
    │                                                                              │
    ▼ (first proposal cycle complete)                                             │
[E6: La Niña] ◄───────────────────────────────────────────────────────────────────┘
    │           (only if gap material from E3)
    ▼
[Phase D: Live Execution Gate]
  (kill switch tested, paper complete, thresholds frozen, schema frozen)
```

**Critical principle:** Calendar time (corpus accumulation) dominates engineering time. Starting E2 paper trading while E3 calibration runs in parallel reduces total elapsed time without violating sequencing.

---

# Part 4 — La Niña Architecture

## The 19-Point Problem Inventory

### Group A — Cadence Gap (the core problem)

1. **EOD blind spot:** Decision is daily, market is continuous — between two snapshots the decision layer is blind.
2. **Open position intraday vulnerability:** Today the only protection is the stop placed at entry.
3. **Stop limitations:** Gap opens, slippage, stop too tight knocks out on normal noise.
4. **Market hours misalignment:** Gold trades ~24 hours, GLD only US hours → gap between decision and execution, opening gap risk.
5. **Sudden regime change (war, crisis):** Macro signal is measurable but may reach the daily decision layer with up to one day's lag.

### Group B — Inviolable Architecture Constraints

6. **No live market data in truth:** Live prices may not flow into the snapshot as truth — explicit prohibition.
7. **News is penalty-only:** Event Risk Stream may never generate direction.
8. **Replay determinism:** Same snapshot → bit-identical decision. Intraday data threatens this.
9. **LLM never calls broker:** LLM never makes execution decisions without a snapshot anchor.
10. **Governance-before-autonomy:** Autonomous intervention only after evidence.

### Group C — Statistics and Learning

11. **Sample thinness:** Daily EOD + one instrument = few decisions; fine regime buckets collapse; intraday "decision manufacturing" adds noise, not edge.
12. **Look-ahead bias:** Without point-in-time discipline, backtest cheats.
13. **Untunable triggers:** Intraday thresholds can only be guessed without data — must be measured first.
14. **Non-deterministic Alpaca fill:** Reason for the dual backend (offline replay vs. paper realism).

### Group D — Contract, Graph, Process

15. **DecisionPacket v0 contract drift:** New fields silently entering the frozen schema.
16. **Forward-path and feedback-loop conflation + two policy-engine ambiguity in diagrams.**
17. **Dev_graph mis-grounding:** Generic anchor; the learning layer is ~85–90% net-new.
18. **Truth Layer gaps:** Snapshot contract, freshness/provenance, missing-data handling, versioning, regime classifier.
19. **Overbuilding too early:** Map > territory — minimal core principle.

## The Key Architectural Insight

The constitution nowhere says the decision must be **daily**. It says the decision must come from a frozen, replayable, governed snapshot. The daily cadence followed from the nature of macro inputs — it was a consequence, not a principle. The architecture document explicitly reserved a slot: "Live Market State (separate governed input, §7 future) — never overwrites the snapshot." La Niña fills that reserved slot.

## Three-Step Architecture

### Step 1 — Dual-Level Truth: Macro Snapshot + IMS

The daily EOD macro-snapshot is unchanged and untouched. Alongside it, a second snapshot family: the **Intraday Market-State Snapshot (IMS)**.

The IMS is produced by the Truth Layer (not ad-hoc in the execution adapter — this is the decisive difference from "leaking" live data). It is:
- Generated hourly
- Frozen schema with its own `ims_id`
- Contains a `parent_snapshot_id` reference to the governing daily EOD snapshot
- Freshness and provenance stamped
- Archived immutably

IMS contents: only fast-refreshing fields — gold spot/futures price, realized volatility, VIX, DXY, yields. No macro fields. It never overwrites the EOD snapshot.

**The iron rule protecting principles #6 and #7:** Direction (entry) can only come from macro truth. The IMS is readable only by the protection logic. The IMS is not a "second opinion" — it is watchman data.

### Step 2 — Standing Orders: Pre-Authorized Contingency Table

The paradox "who decides intraday?" resolves this way: **nobody decides intraday — every intraday decision was made the previous evening**.

The EOD DecisionPacket now includes a contingency table valid for the next 24 hours:
```
if intraday_drawdown > X%       → reduce 50%
if realized_vol > Y threshold   → full exit
if IMS stale (> 2 hours)        → freeze + alert
if price reaches Z limit        → execute EOD-authorized entry (timing only, not new direction)
```

The **Contingency Evaluator** — deterministic code, not LLM — runs hourly, reads the current IMS against the table, and executes only pre-authorized transitions. Military analogy: command issues the order with conditional branches the night before; the field unit executes but does not improvise.

What this solves simultaneously:
- Authority hierarchy intact (all intraday actions were decided by Supervisor — just in advance)
- LLM not in the intraday loop (principle #9, plus cost and latency)
- Replay determinism preserved (archived IMS + clean code = bit-identical replay; non-determinism remains only at fill level, as before)
- Every action has an audit anchor: `(eod_decision_id, ims_id, contingency_rule_id, idempotency_key)`

### Step 3 — Asymmetric One-Way Valve

Statistical problem (#11) and the Riddick trap are eliminated by a single rule: **intraday authority exists only in risk-reducing direction**.

Allowed intraday: reduce, exit, tighten, freeze.  
EOD only: new direction, size increase above EOD budget, regime reclassification.  
The one "entry-like" intraday operation allowed: executing an EOD-authorized entry with limit/scale-in timing — this is tactics, not decision.

The one-way valve guarantees the intraday layer can never blow up the account, only protect it — and produces no noisy "decisions" that would contaminate learning statistics.

## Full Architecture Diagram

```
   [EOD macro-snapshot]                    [IMS — hourly]
            │                                      │
            ▼                                      │
     El Niño (L3, LLM)                             │
            │                                      │
   DecisionPacket v0.1                             ▼
   ├─ action (direction: macro only)    Contingency Evaluator
   └─ contingency table ────────────►   (deterministic code)
            │                                      │
            ▼                                      ▼
        Execution Adapter ◄── only pre-authorized transitions
            │
   Defense line 0: broker-side stop (system-independent)
```

**Three layers of defense:**
1. Broker stop (survives system crash)
2. Contingency Evaluator (hourly, from IMS)
3. EOD re-evaluation (full regime)

The regime-change question closes elegantly: the vol signal in the IMS triggers the protection branch the same day; the new direction comes from the next EOD snapshot's full regime classification.

## Governance: Formal v0.1 Amendment

Three new guard fields must be added to DecisionPacket as a formal §16.1 amendment (not silent drift):
- `ims_freshness_ok` — IMS not stale
- `action_budget_ok` — daily max N contingency actions not exceeded (prevents faulty data stream from emptying account)
- `cooldown_ok` — hysteresis against whipsaw

## What La Niña Does NOT Solve — Honestly

- **Gap risk on GLD at open:** reduced (first IMS triggers contingency immediately at open) but not zero — a weekend shock's first minutes are only protected by position sizing.
- **Whipsaw cost:** protection pays in knock-outs. Thresholds must be tuned on intraday historical data (hourly bars) — this is Problem #13, unavoidable.
- **This is still a specification, not a build order.** The gate: first measure from daily high/low whether the gap vs. simple stop is material. If not, La Niña is unnecessary complexity.

## A Name, as a Gift

If the slow, warm, directional layer is **El Niño**, then this fast, cold, protective counter-phase is naturally **La Niña** — the two phases of the same ENSO phenomenon. The metaphor is precise: La Niña never gives direction, it only cools. Direction daily, protection continuously, discretion intraday never.

---

# Part 5 — Backtesting, Paper Trading, and Learning Data Collection

## 5.1 Collecting vs. Automatic Learning — A Critical Distinction

What you are asking for when you say "build it in so we can study it together later" is **collection and preservation** — not automated learning. These are different things:

- **Collection:** Every decision, every outcome, every parameter stored with its original snapshot anchor so we can retrieve and analyze it later. This is cheap and necessary.
- **Automatic learning:** The system modifies its own thresholds or weights based on observed patterns. This is expensive, risky, and explicitly deferred (see §5.5).

Build collection now. Defer learning until E5. This is consistent with the minimal-core principle and with your explicit governance-before-autonomy requirement.

The practical implication: when the Execution Adapter (E2) is built, every closed trade must log a complete structured record. Not a human-readable note — a machine-readable scorecard that both the offline sim and the Alpaca paper backend produce in identical format.

## 5.2 The Unified Scorecard — Foundation of All Future Evidence

The scorecard is the single most important structural decision in E2. If the schema is well-designed now, every future analysis — calibration, policy proposal, La Niña threshold study, backtesting comparison — draws from the same source. If the schema is weak, every future study hits the same wall.

**Required scorecard fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `decision_id` | string | Anchors to the DecisionPacket |
| `snapshot_id` | string | Anchors to the Layer 2 truth used |
| `snapshot_clock_ts` | datetime | Point-in-time of the governing snapshot |
| `regime_class` | enum | What regime classification drove this |
| `confidence` | float | Confidence at decision time |
| `uncertainty_class` | enum | Uncertainty classification at decision time |
| `preferred_action` | enum | What was decided (BUY/SELL/NO_TRADE/REDUCE) |
| `no_trade_reason` | string/null | Populated when preferred_action = NO_TRADE |
| `fill_price` | float/null | Actual fill price (null if NO_TRADE) |
| `expected_price` | float/null | Mid-price at decision time |
| `slippage` | float/null | fill_price - expected_price |
| `outcome_pnl` | float/null | Realized P&L at close (in %) |
| `max_drawdown_intraday` | float/null | Worst intraday drawdown from entry |
| `hold_duration_hours` | float/null | Time from entry to close |
| `close_reason` | enum | eod_decision / contingency_trigger / stop / manual |
| `backend` | enum | "offline_sim" or "alpaca_paper" |
| `supervisor_verdict` | enum | PASS / SOFT_SHRINK / HARD_VETO / STUB |
| `guard_flags` | object | All guard field values at decision time |

The key property: **offline_sim and alpaca_paper must populate every field identically**. The only difference is the `backend` field and the `fill_price` / `slippage` values (which reflect real vs. simulated execution). This enables direct comparison: "did the sim predict what paper actually produced?"

## 5.3 Backtesting — Point-in-Time Discipline and Look-Ahead Bias

The backtest runs the same decision logic as the live system (El Niño + guards), but on historical snapshots, in sequence from 2014 forward. For each historical day it "pretends" today is that day, using only data known as of that day.

**This point-in-time constraint (Problem #12, look-ahead bias) is explicitly required — and has two subtle failure modes beyond the obvious one:**

### Obvious failure: decision date ≠ knowledge date

If an inflation (CPI) print is released on January 15th and covers January's data, it must not appear in a January 1st snapshot. Many data sources attach values to their reference date rather than their release date. If used carelessly, the backtest "knows" CPI three weeks early — and shows unrealistically good results.

### Subtle failure 1: publication date vs. reference date

Many macro series have a gap between what they measure and when they are published:
- GDP for Q1 (Jan–Mar) is typically published in late April
- Initial jobless claims for week ending Friday are published the following Thursday
- FRED often stores data by the period it covers, not by the publication date

**The correct discipline:** use only the `obs_ts` (observation/publication date) to determine what was "known" on any given backtest day — never the `as_of` date alone. The Mr. Ripley Layer 2 system already enforces `obs_ts <= clock_date` for point-in-time alignment. This discipline must carry through into the backtest runner.

### Subtle failure 2: revised vs. vintage data

Most macro data is revised after initial publication. GDP, employment, inflation — the number published in real time is often materially different from the "final" number seen in current data sources.

If a backtest uses today's revised values to simulate 2020 decisions, it is cheating: the system in 2020 did not know those revisions. This is called **vintage data discipline**.

**Practical implication for Mr. Ripley:** FRED provides point-in-time vintage data via their `vintage_date` parameter. When building the backtest runner, queries must retrieve the value as it was first published (or as published before the decision date), not as it appears today after revisions. The observation table's `revision_seq` field is the mechanism for this — prioritize `revision_seq = 0` observations for historical backtest runs.

**Before building the backtest runner, validate it cannot cheat:** run the same test on two windows where you know the outcome, once with correct point-in-time discipline and once deliberately with look-ahead, and confirm the results differ. If they produce the same result, the discipline check is not working.

**The practical starting point:** before acquiring intraday data for La Niña testing, use daily high/low to assess whether the gap problem is real at all (see §3 E3). Daily high/low is available point-in-time and is enough to answer: "does the intraday gap cost meaningfully more than the stop catches?" If no, La Niña stays in the drawer.

## 5.4 Extracting the Essence — Joint Manual Work

"Extracting the essence" from backtesting and paper trading data is joint, manual work — not a system function. This is by design.

The essence refers to answers to questions like:
- In which regime did the strategy work and in which did it fail?
- What does the gap between expected and actual outcome reveal (was the system overconfident)?
- How much did slippage cost?
- Are there recurring failure patterns?
- Did the offline sim predict what paper actually produced?

This analysis requires well-structured, searchable data — which §5.2 provides. It does not require an AI engine. We do this together when there is enough data. The analysis informs Policy Proposals (§5.5) — which then go through the approval gate.

## 5.5 Human-Approved Policy Evolution

The principle: **the system may observe and propose automatically; only you may activate changes**.

This is not a new requirement — it is the precise formulation of the "governance-before-autonomy" principle already embedded in the architecture. But it needs to be made concrete for the learning layer.

### Policy Proposal Required Content

Every proposal the system generates must contain:

1. **What to change** — specific, not vague. "Reduce the `HIGH_STRESS` regime confidence weight from 0.84 to 0.60" — not "adjust risk parameters."
2. **Evidence base** — how many closed trades, in which regime(s), what was the expected vs. actual outcome delta, and the statistical adequacy assessment (is N large enough?).
3. **Expected impact** — what changes if this is adopted, quantified where possible.
4. **Counterarguments (mandatory)** — why this might be wrong. Insufficient sample. Regime-specificity (only valid in one unusual period). Alternative explanations for the observed pattern. If the system cannot generate counterarguments, the proposal is not ready.

A proposal without counterarguments is advocacy, not evidence.

### Three-State Approval Gate

| State | Action | What happens |
|-------|--------|--------------|
| **Accept** | You approve | Versioned policy change, ADR entry, your name + date logged |
| **Reject** | You decline | Archived in Failure Library with your stated reason; system will not re-propose the same change |
| **Return** | You send back | Specific question attached (e.g., "collect 20 more trades in high-vol regime first") |

Every gate decision — accept, reject, return, and the reasoning — is logged. This makes the approval history itself auditable: you can look back and see what you approved and whether you were right.

### What This Is Not

This is not the Policy Evolution Engine (E5) — that is the code that generates and submits proposals. This section defines the governance model that code must implement. The governance model is decided now; the code is built in E5.

## 5.6 Now vs. Later Split

| Component | Now | Later |
|-----------|-----|-------|
| Scorecard schema design | ✅ Design it now | — |
| Scorecard collection in Execution Adapter | ✅ Build in E2 | — |
| Point-in-time backtest discipline | ✅ Enforce from day 1 | — |
| Vintage data handling | ✅ Enforce from day 1 | — |
| Essence extraction (analysis) | — | Joint manual work when corpus exists |
| Policy Proposal generation | — | E5 |
| Human-approval gate code | — | E5 |
| Failure Library | — | E5 (first entry) |
| Automatic learning (any kind) | — | Never without gate |

## 5.7 On Zapier — Honest Assessment

Zapier is an automation glue tool for connecting applications: "when X happens in one app, do Y in another." It is designed for simple event-driven chains between consumer and business apps — not for structured data pipelines.

**Why Zapier is the wrong tool for the core pipeline:**
- It is not deterministic and not replayable in the sense required by the system (principle #8)
- It cannot enforce point-in-time discipline in a backtest
- It does not understand financial data — it moves fields between services
- It would make your most valuable asset (the evidence log) dependent on a black-box third-party service, contradicting the internal auditability that is the entire system's foundation

**Where Zapier could be useful (periphery only):**
- Sending a push notification when La Niña monitor triggers
- Writing a one-line summary row to a Google Sheet for quick human review
- Triggering a scheduled task from an external event

These are convenience features at the system's edge — never the collection layer, never the analysis layer, never anything that touches the scorecard or decision log.

## 5.8 Summary

The single most important structural choice in the learning and data collection design:

> Collection is built now (cheap, necessary). Learning is deferred (expensive, risky, gated). Analysis is done together manually. Policy changes require your explicit approval. The scorecard schema must be designed before the Execution Adapter is built, because it is the foundation all future evidence draws from.

---

# Appendix — Key Terminology

| Term | Meaning |
|------|---------|
| El Niño | Layer 3 decision engine (slow, directional, EOD cadence) |
| La Niña | Intraday protection layer (fast, risk-reducing only, gated) |
| IMS | Intraday Market-State Snapshot — hourly, produced by Truth Layer |
| Contingency Evaluator | Deterministic code that runs hourly against IMS + contingency table |
| Standing Orders | Pre-authorized contingency table emitted with each EOD DecisionPacket |
| DEBT-01 | ~~Critical blocker~~ — **JAVÍTVA 2026-06-11**: snapshot_publisher NameError kijavítva |
| Scorecard | Structured per-trade record, identical schema across offline_sim and alpaca_paper |
| Vintage data | Data as first published, before revisions — required for backtest integrity |
| Policy Proposal | Structured system-generated change proposal, requires human gate before activation |
| Failure Library | Archive of rejected Policy Proposals with rejection reasons |
| One-way valve | Intraday authority only in risk-reducing direction — never new direction intraday |
| dev_graph | Obsidian + Neo4j knowledge graph — az el_nino architektúra élő tükre (~140 node, ~920 él) |
| ADR | Architecture Decision Record — minden architekturális döntés írott nyoma, kötelező az el_nino governance-ban |
| MOD-xxx | Module node ID a dev_graph-ban (pl. MOD-007 = Paper Trading Runtime) |
| SCHEMA-xxx | Schema node ID (pl. SCHEMA-011 = GoldDecisionPacket v0) |
| epoch (a/b/c) | A barát saját epoch-jelölése: (a) = Paper Runtime build, (b) = corpus accumulation, (c) = calibration |
| admission gate | MOD-007 — ADMIT/HOLD/REJECT verdikt a GoldDecisionPacket-re, mielőtt fill történik |
| forward accumulation | 2026-06-11-től induló napi snapshotok — az egyetlen tiszta corpus; korábbi napok nem backfill-elhetők PIT integritással |
