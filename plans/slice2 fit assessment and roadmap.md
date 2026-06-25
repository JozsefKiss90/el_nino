# El Niño / Ripley — Slice 2 Fit Assessment & Forward Roadmap

**Date:** 2026-06-10
**Inputs:** `PAPER_TRADING_RUNTIME_FINAL_AUDIT.md` (2026-06-09, PASS 97/100) · `ultimateplan.md` (evolutionary architecture, critique, dev_graph gap analysis)
**Status:** read-only assessment — no code, node, or plan document was modified.

-----

## Part 1 — How Well the Audited Runtime Fits the Plan

Very well — in fact, this is not merely “fitting”: it is the **first built and audited slice of the plan**, and it visibly incorporates the earlier critiques. Since the May gap analysis the graph has grown from 89 to 158 nodes, and the direction is exactly what the re-grounding recommendation prescribed.

### Where it sits in the layer model

Slice 2 is **Layer 3’s first stateful component**: an admission gate between the DecisionPacket and the (future) Execution Adapter. It decides over a finished gold packet — ADMIT / HOLD / REJECT — and writes the outcome to a ledger. In the plan’s language, this is the **gold-re-anchored, stateful successor of the Trade Validation Gate**: the generic predicate pattern was *mirrored, not imported* (D6 verifies this at the AST level). This is exactly what the “keep / re-anchor / net-new” analysis recommended.

### Where it validates the plan, point by point

1. **The re-grounding happened.** `src/gold/` bounded context, gold-v0 packet, zero treasury/risk imports, CAP-004 (Signal Generation) deprecated, and no typed edge from CAP-021 to the treasury branch. The May “Decision* naming conflict” is resolved.
1. **v0 contract discipline.** The SCHEMA-011 v0.2.0 extension is additive, `packet_id` is unchanged, goldens were re-pinned, and the change is ADR-governed. This is the direct antidote to critique #2 (contract drift) — a formal amendment, not a silent slide.
1. **The v0 guard taxonomy takes shape.** `duplicate_ok` (computed, non-bypassable), `cooldown_ok` (echo, computed version deferred), `supervisor_ok` (explicit stub), and operational input. In the May matrix this taxonomy did not exist in code at all.
1. **Replay determinism as the keystone.** Pure core, zero clock/RNG/IO on the decision path, `as_of` caller-forwarded, and the ledger alone is sufficient replay state. The constitution’s replay guarantee, in code, with 853 green tests.
1. **The minimal-core principle held.** They did not start with the Counterfactual Engine but with the smallest possible stateful slice — the opposite of critique #4 (over-building too early). The Wake-Execute-Sleep model also fits the daily EOD cadence naturally.
1. **Regime / confidence / direction already exist (provisionally).** The upstream policy surface (“regime thresholds, confidence weights, direction table”) implies the Gold v0 builder contains them — in May, Regime Classification was still marked ❌. Additionally, the three-level **INDETERMINATE→WATCH** enforcement is the finest realization of the fail-closed philosophy so far: an uncertain state can never slip through to ADMIT.

### What this is NOT yet — and the document honestly says so

The name can mislead: it is called “Paper-Trading Runtime”, but it is **admission-only** — no fills, no sizing, no P&L, no positions. The actual paper trade (the two-backend Execution Adapter: offline simulator + Alpaca paper) is the next bounded context (§9.1) — **the plan’s largest uncoded piece remains exactly this**.

**DEBT-01 is the critical path:** `snapshot_publisher` (the Truth Layer *producer* side) is broken, so only a single real snapshot exists. Because of this, all empirical work — calibration, backtesting, statistics — is blocked. This echoes the earlier “what is missing from Layer 2” discussion precisely: the consumer is ready; the producer is not.

The Supervisor (the El Niño LLM layer) does not exist yet — the `supervisor_ok` stub awaits it. The learning layer (Supervisor Memory, Policy Evolution, Counterfactual Engine) likewise does not exist — correctly, per the minimal-core principle. The La Niña / intraday layer does not exist either, and that is right (it is a gated “later”) — but there is good news: the runtime’s patterns (caller-forwarded `as_of`, recorded operational state, ledger threading) are **precisely the patterns the IMS / contingency evaluator will need**. The architecture is ready for it.

### What this means for the next step

97/100 is 97 for an *admission slice*, not 97% of paper trading — D8 itself frames it that way. The critical path is now unambiguous and matches the earlier “measure first, build later” advice: **(1)** fix DEBT-01 → real corpus accumulates, **(2)** epoch (b) calibration → provisional thresholds become empirical, **(3)** Execution Adapter → actual paper fills. In that order.

**In one sentence:** the slice is small, but it is in exactly the right place, in the right order, and it proves the plan’s values at code level — *there is no drift between plan and implementation here.*

-----

## Part 2 — Recommendation

The sequencing logic below follows one governing observation: **corpus accumulation is calendar-bound.** One EOD snapshot is produced per day; it cannot be parallelized, rushed, or back-filled with the same point-in-time integrity. Every day the publisher stays broken is a day of real corpus permanently lost. Everything else is engineering time; this one is calendar time. Therefore:

**R1 — Fix DEBT-01 first, this week if possible.** It is a producer-side bug, almost certainly small relative to its leverage, and it unblocks epochs (b), the backtest plan, and all statistical work. Until it is fixed, every downstream component is being built against a single snapshot.

**R2 — Start corpus accumulation immediately after R1 and let it run in the background.** It costs nothing once running, and by the time the Execution Adapter exists, weeks of real snapshots will already be banked. This also exercises the Layer 2 gaps identified earlier (freshness stamps, provenance, missing-data handling) against reality instead of theory.

**R3 — Build the Execution Adapter as the next major slice, offline backend first.** This is the plan’s largest uncoded component and the precondition for any closed trade, scorecard, or learning. Build it in two sub-steps that mirror the plan’s two-backend design: (a) the **offline simulator backend** first — deterministic, replayable, testable against the admission ledger today; (b) the **Alpaca paper backend** second — realistic fills, slippage, latency. Give it its own ADR (the audit’s §9.1 already calls for one), and carry the hard gates verbatim: `LIVE_ENABLED=false`, paper base URL only, no order without an ADMIT record.

**R4 — Slot the two small guard epochs (computed cooldown, live operational feed) in parallel or between larger slices.** Both are narrow, well-specified, and low-risk. The operational feed deserves slight priority because its pattern — *record the captured live state to preserve replay* — is the exact rehearsal for the future IMS (La Niña) input. Building it teaches the team the discipline the intraday layer will demand.

**R5 — Supervisor integration only after execution evidence exists.** The Supervisor is the plan’s intelligence layer, and it is tempting to build early. Resist. With no fills and no scorecards, a supervisor has nothing real to supervise, and its policies would be tuned against synthetic data — the exact “confidence theater” the plan forbids. Flip `supervisor_ok` from stub to computed once the adapter produces closed paper trades.

**R6 — Defer the learning machinery until closed trades exist; then start with the minimal learning core only.** Strategy Registry + Scorecards + Confidence Engine + Replay corpus — nothing more. Counterfactual Engine and Policy Evolution stay deferred until the trade count makes them statistically meaningful (the plan’s own critique #3 and #4).

**R7 — Keep La Niña gated exactly as designed.** During R3, run the cheap measurement from the backtest plan: using daily high/low data, quantify how much damage intraday drawdowns actually cause past the standing market stop. If the gap is immaterial, the contingency layer stays a spec in the drawer. If material, proceed: hourly historical data → contingency replay → alert-only paper → automation. Governance-before-autonomy applies to construction, too.

**R8 — Preserve the contract discipline that Slice 2 demonstrated.** Every schema change as a formal additive amendment with re-pinned goldens; every new component with the same audit method (dimension auditors + adversarial verification + lead reproduction). Slice 2 set the bar; do not let later, bigger slices lower it.

-----

## Part 3 — The Six Future Epochs (§9) Mapped to the Evolutionary Plan

The audit’s §9 lists six future epochs. Below, each is mapped to the evolutionary component(s) it closes in `ultimateplan.md`, with dependencies and gates. The proposed order differs slightly from the §9 listing order — the reasons are in the sequencing notes.

|# |§9 Epoch                                                                                                                                                                                   |Plan component(s) it closes                                                                                                                                                                                  |Depends on                                                  |Gate / exit criterion                                                                                                                                          |
|--|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
|E1|**Real-corpus calibration (epoch b)** — fix DEBT-01, accumulate real snapshots, move regime thresholds / confidence weights / direction table / require-flags from provisional to empirical|Truth Layer producer (Layer 2 gaps: freshness, provenance, missing-data); Regime Classifier maturation; the statistical-thinness remedy (sample gates, walk-forward become possible)                         |DEBT-01 fix only                                            |N real snapshots banked; thresholds re-issued as a governed version bump (not a rebuild)                                                                       |
|E2|**Execution / portfolio layer** — sizing, fills, P&L, position tracking, exits; turning ADMIT into a paper position                                                                        |**Execution Adapter (two backends: offline sim + Alpaca paper)**; DecisionPacket→order mapping; gold→GLD instrument mapping; Trade Logger; the “Alpaca as execution evidence provider” doctrine              |Admission runtime (done); own planning ADR                  |Offline backend replay-deterministic; Alpaca backend paper-only hard gates verified; first closed paper trades logged with `(decision_id, snapshot_id)` anchors|
|E3|**Live operational-status feed** — replace file/caller-supplied `OperationalInput` with a real venue/health probe                                                                          |`operational_ok` becomes real; Layer 2 data-quality discipline; **pattern rehearsal for the IMS (La Niña) input** — record captured live state, preserve replay                                              |None (parallel-safe)                                        |Replay holds with recorded operational state; degraded-feed behavior fail-closed                                                                               |
|E4|**Computed cooldown guard** — `clock_date`-windowed cooldown with its own policy field + fingerprint                                                                                       |Completes the v0 guard taxonomy (`cooldown_ok` from echo to computed); whipsaw/hysteresis protection the contingency design also relies on                                                                   |None (parallel-safe)                                        |Off-by-one tests green; fingerprint bump governed                                                                                                              |
|E5|**Supervisor integration** — flip `supervisor_ok` from stub to computed                                                                                                                    |**El Niño proper**: the L3 Supervisor Decision Engine; desk structure; governance-before-autonomy in the decision path                                                                                       |E1 (calibrated thresholds) + E2 (real evidence to supervise)|Supervisor verdicts reproduce in replay; veto path fail-closed; no LLM on the execution path                                                                   |
|E6|**Scheduler / driver + multi-instrument** — wall-clock-triggered driver over a snapshot stream (TD-2 locking), instruments beyond GLD                                                      |Wake-Execute-Sleep becomes scheduled operation; **Strategy Portfolio Manager prerequisite** (per-strategy paper accounts, P10 isolation); the operational substrate La Niña’s hourly IMS cadence would run on|E2 (something to drive); TD-2 single-writer guarantees      |Driver survives restart with ledger continuity; per-instrument/per-strategy P&L isolated                                                                       |

### Beyond §9 — plan components intentionally not in the epoch list

These remain correctly out of scope for §9 and slot in behind explicit gates:

- **Minimal learning core** (Strategy Registry + Scorecards + Confidence Engine + Replay corpus) — gated on a meaningful count of closed paper trades from E2. The three-component confidence (`performance / calibration / sample_quality`) enters here, as a formal DecisionPacket amendment if and when it touches the contract.
- **Heavy learning machinery** (Counterfactual Engine, Policy Evolution Engine, Calibration History) — gated further out, on trade volume that makes them statistically meaningful. Counterfactuals run on the offline backend only.
- **La Niña (IMS + contingency table + Contingency Evaluator)** — gated on the measured intraday gap study (daily high/low first; hourly data only if the gap is material). Its enabling patterns are deliberately rehearsed earlier by E3 (recorded live state) and E4 (hysteresis/cooldown).
- **Layer 1 Event Intelligence (news, penalty-only)** — last, only after the measurable macro pipeline is stable end-to-end, and never directional.

### Sequenced roadmap (one view)

```
NOW ──► E1 DEBT-01 fix + corpus starts (calendar-bound — every day counts)
         │
         ├─ background: real snapshots accumulate daily
         │
         ├──► E2 Execution Adapter
         │     ├─ E2a offline sim backend (deterministic, replay)
         │     └─ E2b Alpaca paper backend (realistic fills)
         │
         ├──► E3 + E4 in parallel slices (operational feed, computed cooldown)
         │
         ├──► [gate: closed paper trades exist]
         │
         ├──► E5 Supervisor integration (El Niño L3)
         │
         ├──► E6 Scheduler/driver + multi-instrument
         │
         ├──► [gate: N closed trades] ──► Minimal learning core
         │
         └──► [gate: measured intraday gap is material] ──► La Niña
                                  (else: stays a spec in the drawer)
```

**Governing principle across all of it:** data before execution, execution before intelligence, intelligence before learning, and every autonomy increase behind a measured gate. Slice 2 proved the project can hold that discipline at code level; the roadmap above simply keeps holding it.

-----

## Part 4 — La Niña: Intraday Gold Decisions Without Violating Any Principle

The roadmap above gated “La Niña” as a deferred spec. This part fills in that spec: the full problem inventory it must satisfy, the architecture that satisfies it, and an honest account of what it does *not* solve. It is captured here so the design exists in writing before any construction — and the construction gate (R7) still stands.

### 4.1 The complete problem inventory

Every constraint surfaced across the design discussion, grouped:

**A) The cadence gap (the core problem)**

1. **EOD blind spot:** the decision is daily, the market is continuous — between two snapshots the decision layer is blind.
1. **Open-position intraday exposure:** today the only protection is the stop placed at entry.
1. **Stop limitations:** gap-open, slippage, and a too-tight stop being shaken out by normal noise.
1. **Market-hours mismatch:** gold trades ~24h, but GLD only during US hours → a gap between decision and execution, with opening-gap risk.
1. **Sudden regime change (war, crisis):** the macro footprint is measurable, but at EOD cadence it reaches the decision with up to a one-day lag.

**B) Inviolable architectural principles (the constraints on any solution)**

1. **Live market data must not leak into the decision as truth** — the plan’s explicit prohibition.
1. **News is penalty-only** — it may never set direction.
1. **Replay determinism:** the same snapshot ⇒ a bit-identical decision; intraday data threatens this.
1. **The LLM never calls a broker and never decides without a snapshot.**
1. **Governance-before-autonomy:** autonomous intervention only after it has been proven.

**C) Statistics and learning**

1. **Sample thinness:** daily EOD + a single instrument ⇒ few decisions; fine-grained regime buckets disintegrate; intraday “decision manufacturing” would add noise, not edge.
1. **Look-ahead bias:** without point-in-time discipline, the backtest cheats.
1. **Untunable triggers:** intraday thresholds can only be guessed without data.
1. **Alpaca fills are non-deterministic:** hence the two-backend design (offline replay vs. paper realism).

**D) Contract, graph, process**

1. **DecisionPacket v0 contract drift:** new fields sliding silently into the frozen schema.
1. **Forward-path and feedback-loop entanglement** + the two-policy-engine ambiguity in the diagram.
1. **dev_graph mis-grounding:** a generic anchor, with the learning layer ~85–90% net-new.
1. **Truth Layer gaps:** snapshot contract, freshness/provenance, missing-data handling, versioning, regime classifier.
1. **Over-building too early:** map > territory — the minimal-core principle.

### 4.2 The design: intraday gold reaction without principle violation

The key insight the whole thing rests on: **the constitution nowhere says the decision must be DAILY.** It says the decision may only be born from a frozen, replayable, governed snapshot. The daily cadence followed from the nature of the macro inputs — it is a consequence, not a principle. Moreover, the plan itself left a door open when it wrote that market data *“may at most be a later Live Market State (a separate governed input, §7 future) — never overwriting the snapshot.”* La Niña fills exactly that reserved slot. Three steps.

**Step 1 — Two-tier Truth: an IMS alongside the macro snapshot.**

The daily EOD macro snapshot stays, untouched. Beside it comes a second, separate snapshot family: the **Intraday Market-State Snapshot (IMS)**.

The IMS is produced by the **Truth Layer** (not ad-hoc by the execution adapter — this is the decisive difference from “leakage”): hourly, with a frozen schema, its own `ims_id`, a parent reference to the day’s EOD snapshot, freshness and provenance stamps, archived. Its content is strictly what actually updates intraday: gold spot/futures price, realized volatility, VIX, DXY, possibly yield. It contains no macro fields and never overwrites the EOD snapshot — the letter and spirit of the plan’s prohibition.

And the iron rule that protects principles 6 and 7: **direction (entry) may be set only by the macro truth. The IMS may be read only by the protective logic.** The IMS is not a “second opinion” — it is sentinel data.

**Step 2 — Pre-authorized contingency plan: the “standing orders” model.**

Here is the trick that dissolves the “who decides intraday?” paradox: **no one decides intraday — every intraday action was decided the night before.**

The EOD decision (El Niño, L3) now emits not just an action, but a **contingency table** in the DecisionPacket for the next 24 hours: condition → pre-authorized action. For example:

```
if intraday drawdown > X%      → reduce 50%
if realized vol > Y threshold  → full exit
if IMS stale (> 2 hours)       → freeze + alert (stop remains)
if price reaches Z limit       → execute the EOD-authorized entry
                                 (timing, not new direction)
```

Intraday, a **Contingency Evaluator** runs — deterministic code, *not* an LLM — which hourly evaluates the current IMS against the table and executes only pre-authorized transitions. Military analogy: command (the Supervisor) issues the order in the evening *together with its conditional branches*; the field unit executes but does not improvise.

Look at what this solves at once: the authority hierarchy is intact (every intraday action was also decided by the Supervisor — just in advance); the LLM is not in the intraday loop (principle 9, plus cost and latency); replay determinism holds (archived IMSs + pure code = bit-identically replayable — problem 8 solved, with non-determinism remaining only at the fill, as before); and every action gets an auditable anchor: `(eod_decision_id, ims_id, contingency_rule_id, idempotency_key)`.

**Step 3 — Asymmetric authority: the one-way valve.**

The statistical problem (11) and the Riddick trap are both excluded by a single rule: **intraday, authority exists only in the risk-reducing direction.** Reduce, exit, tighten, freeze — yes. Taking on new direction, increasing size beyond the EOD envelope, regime re-classification — only at EOD. The single “entry-like” intraday operation is the *timing* of an already-EOD-authorized, bounded entry (limit / scale-in within that envelope) — that is tactics, not a decision.

This one-way valve guarantees that the intraday layer can never blow up the account, only protect it — and that it manufactures no noisy “decisions” that would wash out the learning statistics.

**The whole thing in one picture:**

```
   [EOD macro snapshot]               [IMS — hourly]
            │                              │
            ▼                              │
     El Niño (L3, LLM)                     │
            │                              │
   DecisionPacket v0.1                     ▼
   ├─ action (direction: macro only)  Contingency Evaluator
   └─ contingency table ───────────►  (deterministic code)
            │                              │
            ▼                              ▼
        Execution Adapter ◄── pre-authorized transitions only
            │
   defense line 0: broker-side stop (system-independent)
```

Three lines of defense in depth: the broker stop (alive even if your system crashes), the contingency evaluator (hourly, from the IMS), and the EOD re-evaluation (full regime). The regime-change question closes elegantly this way: **protection intraday, direction daily** — the IMS catches the crisis vol signal the same day and the protective branch fires; the new direction comes from the next EOD snapshot’s full regime classification.

### 4.3 Governance: this is a formal v0.1, not a silent drift

Problem 15 must not be re-created: the contingency-table field, the IMS schema, and the new guards (`ims_freshness_ok`; `action_budget_ok` — a daily max of N contingency actions; `cooldown_ok` — hysteresis against whipsaw) are to be raised into v0.1 as a **formal §16.1 amendment**, dated, with an ADR. This is exactly what the plan’s critique demanded — and exactly the discipline Slice 2 already demonstrated with its additive SCHEMA-011 v0.2.0 change.

### 4.4 What this does NOT solve — honestly

The opening gap on GLD is reduced (at the open, the contingency runs immediately on the first IMS) but not zero — against the first minutes of a weekend shock, only position size protects. The whipsaw cost is real: protection pays in shake-outs, and the thresholds can be tuned only on intraday historical data (hourly bars) — this is problem 13, which no clever architecture circumvents, only measurement does. And the main caution stands: **this remains a specification, not a build order.** The gate: first measure from the daily high/low how big the gap is past the plain stop; if material, then hourly data and contingency replay; then alert-only paper; then automatic reflex. Governance-before-autonomy — for construction, too.

### 4.5 Naming

If the slow, warm, direction-setting layer is **El Niño**, then this fast, cold, defensive counter-phase is naturally **La Niña**. Two phases of the same phenomenon (ENSO) — as here, two cadences of the same Truth. The metaphor is exact: La Niña never sets direction, it only cools.

**In one sentence:** direction daily, protection continuous, discretion intraday never — this is how you get intraday reaction while violating none of the 19 problems, and in fact reinforcing three or four of them (5, 8, 11, 15).

### 4.6 Where La Niña sits in the roadmap (refinement of Part 3)

La Niña is not a single epoch; it is a small bounded context gated behind a measurement, with its enabling patterns deliberately rehearsed by earlier epochs. Its dependency chain:

- **Rehearsed by E3** (live operational feed): the discipline of *recording captured live state to preserve replay* is the exact pattern the IMS requires.
- **Rehearsed by E4** (computed cooldown): the hysteresis/cooldown mechanism La Niña’s `cooldown_ok` whipsaw-guard relies on.
- **Depends on E2** (Execution Adapter): there must be a position to protect before protection means anything.
- **Gated by the intraday-gap measurement** (the daily high/low study in R7): if the gap past the standing stop is immaterial, La Niña stays a spec in the drawer.

Construction order, once gated open: IMS schema + producer (formal v0.1 amendment) → Contingency Evaluator (deterministic, replay-tested against archived IMSs) → alert-only paper validation → automatic reflex with `action_budget_ok` cap. Each step behind its own gate, mirroring the Slice 2 method.

-----

## Part 5 — Evidence Collection, Backtesting & Human-Approved Learning

This part consolidates the data-collection design: how paper-trading and backtest results should be captured and studied, how learning should be gated behind human approval, and why a workflow-glue tool (Zapier) is the wrong fit for the core of it. Like Part 4, this is design captured in writing ahead of construction — the actual learning layer remains gated behind a meaningful count of closed trades (Part 3).

### 5.1 The governing distinction: collecting data ≠ building a learning machine

There is a critical conceptual line between **collecting and preserving evidence** and **building an automatic learning system**, and the two must not be conflated.

What we want now is collection and preservation: paper-trade and backtest results stored such that they can later be reviewed **by hand, together** to extract the lesson. This is *not* the Policy Evolution Engine or the Counterfactual Engine — those mean the *system itself* learns automatically, and the plan correctly defers them until enough closed trades exist.

So the answer is a clear **yes, build it in — but only at the collection/preservation level, not the automatic-learning level.** And the good news: this largely **already exists** in the system. The audit document shows the **ledger** and the **scorecard** concept, and every decision carries a `(decision_id, snapshot_id)` anchor. That is exactly the “building in” being asked for: every decision, every outcome, every reason-parameter stored, retrievable, bound to the originating snapshot.

**The principle:** build the *collection* now (it is cheap and needed regardless), but do not automate the *learning* — that we do by hand, together, while the data is thin. This is fully consistent with the minimal-learning-core principle.

### 5.2 The unified scorecard — the keystone of evidence collection

The single most important design decision here: **backtest and paper trading must use the same scorecard format.** This is what makes the two comparable and jointly analyzable later.

When the Execution Adapter (E2) is built, what gets added is not a learning engine but a **rich, structured record of every closed trade.** For each trade, store at minimum:

- which snapshot it was born from (`snapshot_id`);
- the regime classification at decision time;
- the expected outcome (what the decision anticipated);
- the actual outcome — profit/loss, maximum adverse excursion (the worst drawdown during the trade), how long it lasted;
- the execution friction (slippage — the gap between intended and filled price);
- which fill backend produced it (offline sim vs. Alpaca paper).

This is the “scorecard” — and it is exactly what we will later review together.

### 5.3 How backtesting fits and how to run it

Backtest and paper trading must emit the **same scorecard format** — this is the key to later comparability. How to run the backtest, step by step:

The backtest runs the *same decision logic* as the live system (El Niño + the guards), only over historical snapshots, in sequence from 2014. For each historical day it “pretends” it is that day — using strictly the data known up to that day. This is **point-in-time discipline**, the defense against look-ahead bias (problem #12): if a CPI figure was *published* on January 15th, it must not appear in a January 1st snapshot, or the system would “know” something it could not have known, and the backtest would show unrealistically good results. For each decision it computes a scorecard in **exactly the same format** the paper trading produces. Results are aggregated per regime.

Why this matters for “building in”: if backtest and paper trading emit identically-formatted scorecards, then later we can review both in one place, uniformly, and compare — *“what the backtest showed on 2014–2024, does paper trading confirm in the present, or does it diverge?”* That comparability is the essence being sought.

The plan is already built for this: the two-backend Execution Adapter (offline sim + Alpaca paper) does exactly this — the same decision chain, two fill backends, with the scorecard marking which produced it. The backtest is essentially the offline backend, run over long historical data. Two further cautions carry over from the plan’s own critique:

- **Out-of-sample / walk-forward:** do not tune parameters until they are perfect on 2014–2024 — that is fitting the past, not predicting the future (overfitting). Develop on one slice (e.g. 2014–2020), validate on an unseen slice (2021–2024); walk-forward is the rolling version of this.
- **Sample thinness (problem #11):** a single daily-EOD instrument yields few decisions; coarse regimes (3–4 classes) and minimum-sample gates per bucket keep the statistics honest.

### 5.4 Extracting the essence — joint, manual work

“Extracting the essence” is **joint, manual work, not an automation.** The essence is concretely the answer to questions like: which regime did the strategy work in and which not? What does the gap between expected and actual outcome reveal (was the system overconfident)? How much did slippage eat from the profit? Are there recurring failure patterns? This needs no AI engine — it needs the data to be *well-structured and searchable*, which 5.2 and 5.3 provide.

### 5.5 Human-Approved Learning — the system argues before it learns

A core requirement: **if the system learns, it must first propose with our approval, and argue its case before anything takes effect.** This is not a new requirement — it is a precise statement of a cornerstone the plan already holds: **governance-before-autonomy** (problem #10), and the Policy Evolution Engine’s existing “proposal-only” property (“does not modify the LLM; produces a new policy version”; the `final_strategic_review` explicitly forbids silently mutating the live policy).

**The key distinction: to learn ≠ to put into effect.**

- The system **may observe and propose** automatically — *“in the high-real-yield regime, strategy X consistently underperforms expectation; I propose lowering its confidence weight.”* This is the *thinking* half of learning, and it may run on its own.
- The system **may not put anything into effect** without approval. The proposal stays a proposal until a human (and the validation gates) let it through. This is the *acting* half, and it is **gated.**

The danger of learning is not in the observation but in the *silently executed* self-modification — exactly the Riddick “I let the agent develop its own strategy” trap. This model structurally excludes it: the output of learning is never direct action, always an *argued proposal in front of a human gate.*

**The Policy Proposal as a document.** So the system can “argue what it concluded,” the output of learning must be a structured proposal, not a silent parameter change. It must contain:

- what it proposes to change, concretely (e.g. “strategy X confidence weight in High Real Yield from 0.84 to 0.60”);
- the evidence — how many closed trades, in which regime, the expected-vs-actual gap, statistical grounding (is the sample sufficient?);
- the expected effect if adopted;
- crucially, **what argues against it** — the risk of the change, what could make the conclusion wrong (e.g. “based on only 12 trades, which may be noise given sample-thinness #11”).

The last point is vital: a good argument presents the counter-arguments too, or it is self-justification, not reasoning. This can be enforced — the proposal *must* contain its own weaknesses. The audit document did exactly this when it honestly listed its own limitations (§9) — the same spirit.

**The approval process: a three-state gate.** Approval is not binary, but three-state, to leave room for genuine joint work:

- **Accept** → the proposal becomes a formal, versioned policy change (like the additive, ADR-governed schema change in the audit), dated and with the human approval in the log.
- **Reject** → the proposal is archived in the **Failure Library** (already in the Supervisor Memory plan), with the reasoning — so the system does not repeat the same proposal, and there is a record of why it did not pass.
- **Return for refinement** → “interesting, but too little data, gather more” or “consider this angle too” — the proposal waits or recomputes.

Every decision — acceptance, rejection, reasoning — is logged. So not only the system learns; the *approval history itself* is auditable.

### 5.6 What to build now vs. later

This approval mechanism belongs to the **learning layer**, which is far back on the roadmap (the minimal learning core in Part 3, gated behind closed trades, after E5/E6). Therefore:

- **Now:** record this as a binding design principle — *“the output of learning is always an argued, human-approved proposal, never a silent self-modification.”* Worth writing into the constitution if not already explicit.
- **Later:** when building the learning layer (after many closed trades), concretize the Policy Proposal schema and the approval flow into code.

But one thing must be done **now, not later:** for the system to argue well later, the *evidence* must already accumulate well-structured now. Hence the unified scorecard (5.2) — the Policy Proposal will draw its arguments precisely from it. If the scorecard is well-designed now (expected vs. actual, which regime, sample size), the later reasoning will be rich and grounded; if it accumulates incompletely now, the later proposals will be weak.

### 5.7 On Zapier — the wrong tool for the core

**No, Zapier is not suitable for this, and likely would not do what is intended.**

Zapier is **automation glue between apps**: “if X happens in one app, do Y in another” (e.g. “if an email arrives, save the attachment to Drive”). It is for simple, event-based chains, for non-developers. What is described here — collecting structured trade data, point-in-time backtesting, scorecard analysis, essence-extraction — is **data processing and analysis, not app-connection.** The system already does this in its own code (the ledger, the scorecard, the Execution Adapter), far more precisely and auditably than any Zapier chain could.

Concretely why it is a poor fit:

- Zapier is not deterministic and not replayable in the project’s sense — this alone violates the system’s core principle (#8).
- It cannot maintain point-in-time discipline on a backtest.
- It does not “understand” financial data; it only moves fields.
- It would entrust the system’s most valuable part (the evidence ledger) to an external black-box service, while the whole architecture’s point is internal auditability.

**What Zapier *would* be good for, if anything:** purely at the periphery, for notifications. For example, “if the La Niña monitor alerts, send a push to my phone,” or “when a trade closes, append a row to a Google Sheet for a quick glance.” This is a convenience layer at the *edge* of the system — never the data-collection or analysis core. That is the code’s job.

### 5.8 Summary

Yes — build in the *collection and preservation* of paper-trade and backtest data, but this is collection, not automatic learning; the learning we do by hand while data is thin. The key is that backtest and paper trading emit an **identically-formatted scorecard**, because that makes them comparable and jointly analyzable. “Extracting the essence” is joint, manual work needing only well-structured, searchable data — not an AI engine. Learning, when it comes, must **argue before it acts**: every effective change is an argued proposal that also exposes its own weaknesses, stopped in front of a human gate (accept / reject / return-for-refinement, all logged) — the governance-before-autonomy principle made concrete. And Zapier is not for this: it is app-connecting glue, not a data analyzer; at most use it at the system’s edge, for notifications.