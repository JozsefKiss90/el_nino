---
type: decision_record
canonical_id: ADR-013
status: active
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "OPS_TUI_prompt.md"
  - "OPS_DASHBOARD_prompt.md"
related_files:
  - "[[core.py (ops)]]"
  - "[[app.py (ops)]]"
  - "[[actions.py (ops)]]"
  - "[[gated.py (ops)]]"
  - "[[audit.py (ops)]]"
related_tests:
  - "[[test_ops_core]]"
  - "[[test_ops_audit]]"
  - "[[test_ops_actions]]"
  - "[[test_ops_gated]]"
  - "[[test_ops_app]]"
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - JARVIS GraphRAG Integration]]"
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Empirical Calibration Methodology]]"
  - "[[ADR - Implementation Substrate]]"
decision_id: "ADR-013"
decision_date: 2026-06-18
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Operations Control Plane

## Status

**Accepted** — authored 2026-06-18, **accepted by the operator 2026-06-18** (`status: draft → active`,
`implementation_status: not-started → tested`; `decision_status` stays `active`). It was authored under
the governed `status: draft` stand-in for "Proposed" (the same convention [[ADR - Execution Layer
Planning]] (ADR-011) used before its checkpoint promotion). This is a **governance and
architectural-boundary** record, mirroring [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006),
[[ADR - Paper-Trading Runtime Planning]] (ADR-009), [[ADR - JARVIS GraphRAG Integration]] (ADR-010), and
[[ADR - Execution Layer Planning]] (ADR-011). It **authors no application code**, defines no
schema/module/interface/gate, and **reimplements no safety logic**. It establishes the boundary under
which a **local terminal operator console** (a Textual TUI) may OBSERVE the El Niño Layer-3 runtime and
TRIGGER operator actions in three safety tiers.

The concrete code has since been **built and is green** (Steps 1–4, full suite 1050 tests): the headless
governed read-model ([[core.py (ops)]]), the Textual TUI ([[app.py (ops)]]), the safe-action tier
([[actions.py (ops)]] + [[audit.py (ops)]]), and the gated-live tier ([[gated.py (ops)]]) — all under the
[[Operations Control Plane]] (MOD-011) module + [[Operations Control Plane Console]] (OBS-002), governed by
the invariants recorded here. **Both HARD-PAUSE gates were observed**: this ADR was reviewed and accepted
before console code was written (§10), and the gated-live tier was reviewed before it was wired (§10, the
operator selecting the one-shot live-run model).

## Context

The Layer-3 lineage now runs end-to-end. [[Chain Orchestrator]] (MOD-010) threads
`consume → build_features → classify → build_decision → evaluate → [GATE-001] → execute → persist`
through `orchestration.runtime.run_once`, persisting an append-only runtime ledger ([[Paper-Trading
Runtime]] MOD-007, SCHEMA-012/013) and portfolio state ([[Execution]] MOD-008, SCHEMA-014/015). The
deterministic `SimulatedBrokerAdapter` is the default execution port; the live Alpaca paper plugs
([[alpaca_adapter.py]] FILE-038, [[alpaca_clock_feed.py]] FILE-037) are **default-OFF, fail-closed,
paper-host-only, built-but-dormant** behind their ports (ADR-011 §7 gate (f)). The [[Gold Forward-Return
Labeler]] (MOD-009) measures calibration readiness against the [[ADR - Empirical Calibration Methodology]]
(ADR-012) gate; today's monochromatic corpus (N=5, regimes {RESTRICTIVE_RATES}, directions {AVOID},
0 realized labels) yields **DEFER on all three targets**. Operational scripts (`scripts/daily_chain_run.ps1`,
`scripts/register_daily_chain_task.ps1`) exist; **registering the recurring task and enabling the live
path remain operator HARD-PAUSE actions** (dev_graph log, 2026-06-18).

What does **not** exist is a single place to *observe* all of this — the pipeline status, the chain
verdict + six-guard outcomes, the ADR-011/ADR-012 gate boards, calibration readiness, artefacts
(ledger / portfolio / benchmarks), processes (daily job, producer freshness, Neo4j sync), and live-plug
status — and to *trigger* the routine operator actions (run the chain, re-check calibration, re-sync the
graph) and, behind explicit gates, the privileged ones (enable the paper plug, register the schedule).
Today those are scattered across CLI invocations, PowerShell scripts, and runbooks.

There is already a console in this project — the **JARVIS** browser console (ADR-010) — but it is a
**read-only window onto the dev_graph** (Neo4j / `graph.json`), a *knowledge* console. This is a different
artifact: a *runtime operator* console over live artefacts and governed functions. The two are **siblings,
not parent/child**: JARVIS reads the engineering graph; this reads the trading runtime. They may share a
small governed ops-core later, **nothing more** — this console must not depend on, import, or be served by
the JARVIS web stack.

This ADR answers a deliberately narrow question:

> **Under what governance constraints may a local terminal operator console be built over the El Niño
> runtime — observing every status and triggering operator actions up to the gated-live tier — so that it
> adds an operational control plane without becoming a network surface, a second source of truth, a
> live-money path, or a place where the system's fail-closed, paper-only, secrets-isolated discipline is
> re-implemented and therefore weakened?**

It does **not** answer *"what is the console's exact widget tree / core API?"* — that is the implementation
slice, built only under the invariants below.

## Decision

The following governance constraints bind the operations control plane and every slice that implements it.
They are invariants of record; the code authored in later slices must satisfy them.

### 1. Scope & sibling boundary
This ADR governs a **local terminal operator console** — a Textual TUI the operator runs in a terminal
window to observe and interact with the El Niño pipeline's tables, logs, processes, gates, artefacts, and
operations. It is a **net-new, top-level `ops/` package** with new ontology objects and new canonical
identifiers. It is **distinct from** the [[ADR - JARVIS GraphRAG Integration]] (ADR-010) browser/GraphRAG
console: JARVIS reads the **dev_graph**; this reads the **runtime**. They are siblings. The console **may
share a governed, headless ops-core** with no other component, and **must not** import, embed, link to, or
be served by the JARVIS FastAPI/React/voice stack. It is also **not** a producer: the Mr-Ripley Layer-2
producer (separate repo) is READ-ONLY to this console.

### 2. Local-machine only — no network listener
The console is a **terminal application run by the operator on the local machine**. It opens **no network
listener**, exposes **no port**, and ships **no FastAPI/HTTP/web surface**. It reads artefacts on disk and
calls governed functions **directly, in-process**. (Contrast ADR-010, whose read-only bridge is itself a
deliberate, separate concern; this console adds no comparable surface.) There is no remote, no auth layer,
no exposure — because there is nothing listening.

### 3. Three action tiers
Every console capability falls into exactly one of three tiers, and each tier has a fixed safety contract:

- **Tier 1 — Read-only.** Pure reads of existing artefacts via the governed loaders / `to_dict()` /
  `state_hash()` projections. No mutation, no confirm, no audit entry needed (reads are not actions).
- **Tier 2 — Safe (non-destructive).** Key-bound triggers of an existing governed function that is
  deterministic, paper-only, idempotent, and reaches no live broker / live-money path. **No extra confirm
  modal**, but **every invocation writes an append-only audit-log entry** and surfaces its result in the
  log pane.
- **Tier 3 — Gated-live.** Privileged transitions (enabling the live paper plug, registering the OS
  schedule, committing a calibration bump). Each requires, together: an **explicit in-console confirm
  modal** + an **append-only audit-log entry** + **server-side enforcement of its precondition** (gate
  pass / paper creds + paper host / paper host of OS action). The build of this tier is **HARD-PAUSE-gated**
  (§10).

The action assignment is recorded here (the implementation may add read-only views freely, but must not
move an action to a lower tier):

| Action | Tier | Reused governed function | Server-side precondition |
|---|---|---|---|
| Render pipeline status / latest chain verdict / six-guard outcomes / direction / fill-or-no-fill / state hashes | 1 | `load_ledger`, `load_portfolio`, `load_operational`, `ChainResult.to_dict`, `_summarize` | none (pure reads) |
| Show latest banked snapshot + consumability | 1 | `find_latest_snapshot`, `consume` | none |
| ADR-011 (a–f) + ADR-012 (G0–G3) gate boards; regime/direction distributions; realized-label count | 1 | `build_report` (MOD-009) / read committed `forward_return_labels.json` | none |
| Active policy versions + fingerprints | 1 | `*.fingerprint()` reads | none |
| Live-plug status badge (dormant / creds-present / enabled) | 1 | `paper_adapter_from_env`, `clock_feed_from_env` → inspect `.client is None` only | none — **secrets never read** |
| Processes (daily task registered? last run? producer freshness? Neo4j last sync?) | 1 | `Get-ScheduledTaskInfo`, `find_latest_snapshot` over the producer dir, log reads | none |
| Run chain now (deterministic simulator + calendar/captured feed, latest snapshot) | 2 | `orchestration.runtime.run_once` (default `SimulatedBrokerAdapter`) | simulator port + non-live feed; paper-only + GATE-001 enforced inside; idempotent on `source_snapshot_id` |
| Re-run calibration readiness check | 2 | `build_report` (MOD-009) | none beyond audit entry; never bumps a `*_version` |
| Re-sync Neo4j read-only projection | 2 | `sync_to_neo4j.py --clear` | none beyond audit entry; idempotent re-projection |
| Enable / disable Alpaca paper execution | 3 | `paper_adapter_from_env` (passed as `port=` to `run_once`) | confirm + audit + **paper creds present AND paper host**; fail-closed to dormant otherwise; never live-money |
| Enable the live Alpaca operational feed | 3 | `clock_feed_from_env` (passed as `operational_feed=` to `run_once`) | confirm + audit + paper creds + paper host; captured, never on the replay path |
| Register / unregister the daily schedule | 3 | `scripts/register_daily_chain_task.ps1` / `Unregister-ScheduledTask` | confirm + audit; reversible; deterministic simulator + calendar feed |
| Commit a calibration bump | 3 | the ADR-012 readiness gate check (G0–G3 derived from `build_report`) | confirm + audit + **returns DEFER unless the ADR-012 gate passes**; the console can NEVER force a bump |

### 4. Reuse governed functions — never reimplement safety, paper-only, or gate logic
Every action calls an **existing governed function unchanged**. The console **never** re-threads the chain,
re-evaluates a guard, re-derives a verdict, re-checks a host, or re-implements persistence. The load-bearing
reuse points are: `orchestration.runtime.run_once` / `run_sequence` / `find_latest_snapshot` (chain);
`run_chain` + `run_guard` (GATE-001 wiring — the single `src/risk` importer); `load_ledger` /
`load_operational` / `load_portfolio` (fail-closed read surfaces); `paper_adapter_from_env` /
`clock_feed_from_env` (the only governed constructors of a live plug — both fail-closed, both refuse a
non-paper host via parsed-hostname equality); `load_config_from_env` (fail-closed GATE-001 limits);
`build_report` (MOD-009 read-only labeler); the `register_daily_chain_task.ps1` script; and
`sync_to_neo4j.py`. Their safety properties — `paper_only` invariants, default-closed operational input,
fail-closed guard verdict, once-ever idempotency, withdrawals-always-disabled (PRED-005), the replay-path
quarantine — live **inside** these functions. The console surfaces them; it must never weaken them.

### 5. Paper-only / no live-money path, ever
No view, action, or tier may open a live-money route. Live actions reuse the **paper** governed functions
only: `paper_adapter_from_env` trades virtual money against the Alpaca **paper** host and fail-closes
otherwise; every `ExecutionRecord` asserts `paper_only`; every `RuntimeDecisionRecord` enforces
`decision_mode == PAPER_ONLY`; [[Withdrawal Disabled]] (PRED-005) stays enforced. This honors
[[Paper Trading Validation]] (KA-010) and extends ADR-011 §3. **Live-money trading is a Non-Goal of this
ADR and of every slice it governs.**

### 6. Secrets never displayed
No view ever shows API keys or `.secrets` contents. The console derives live-plug status **only** as
`dormant` / `creds-present` / `enabled` from the boolean `adapter.client is None` (held privately inside
the governed factory), **never** from credential material. Credentials stay in the environment / a
git-ignored `.secrets` per [[Agent Safety Principles]] (KA-008); the console must not read, log, echo,
render, or persist them, and must not write them into any audit entry, dev_graph node, test, or committed
artifact.

### 7. Confirm + audit + server-side precondition on every mutation
Read views (Tier 1) are pure reads. **Every Tier-2 action** writes an **append-only audit-log entry**
(timestamp, action, args-summary, result). **Every Tier-3 action** requires, together: an **in-console
confirm modal**, an **append-only audit-log entry**, and **server-side enforcement of its precondition**
(the precondition is checked by the governed function itself — a gate pass, paper creds, the paper host —
not by the UI). The audit log is append-only and never contains secrets (§6). The UI confirm is a
convenience for the operator; the **real** guarantee is the server-side fail-closed precondition, which
holds even if the UI is bypassed.

### 8. Gate-respecting
The console cannot force a privileged transition. A **calibration-bump** action returns **DEFER** unless the
[[ADR - Empirical Calibration Methodology]] (ADR-012) readiness gate passes for the specific target; with
today's monochromatic corpus that is DEFER for all three targets, and the console presents DEFER and stops —
it never edits a `taxonomy_version` / `decision_policy_version`, re-pins a benchmark, or fits values (a bump
is a human-review-required manual config-version amendment per ADR-012 §6, with **no callable** that
performs it). **Enabling Alpaca** fail-closes to dormant whenever paper creds or the paper host are absent
(`paper_adapter_from_env` / `clock_feed_from_env` return `client=None`). The console may *present* a gate's
state read-only; it may never *override* it.

### 9. The engine stays zero-dependency
[[ADR - Implementation Substrate]] (ADR-003) holds: `src/` keeps `dependencies = []` (zero runtime
dependencies, stdlib-only frozen dataclasses). The console's libraries (Textual, Rich) live in a **separate
optional-dependency group** (`[project.optional-dependencies] ops`, peer to the existing `dev` group),
installed only via the `[ops]` extra. The console lives in its **own top-level `ops/` package**, peer to
`src/`, and is **never imported by `src/`**. `mypy --strict` and `ruff` are extended to cover `ops/` (by
adding `ops` to their file lists — never by relaxing strict mode). This ADR **extends ADR-003 additively**
(a new optional group + a new top-level package); it supersedes nothing and contradicts the zero-runtime-deps
decision in no way.

### 10. Build order is a governance gate (read-only before actions; HARD PAUSE before gated-live)
The console is built in tier order, and two operator HARD PAUSES are invariants of this record:

1. **This ADR is reviewed and accepted before any console code is written.**
2. The **read-only** tier (the governed `ops/core.py` read-model + the Textual read views) is built and
   green (`mypy --strict` + `ruff` clean, `core.py` unit-tested headless) **before** any action is wired.
3. The **safe (Tier-2)** actions are wired next.
4. There is a **HARD PAUSE for operator review before the gated-live (Tier-3) tier is wired.**

This staging is the same phased-autonomy discipline [[Agent Safety Principles]] (KA-008) holds for the
runtime: capability is proven read-only first, and the most privileged surface is gated behind explicit
human review.

### 11. No second source of truth
The persisted ledger / portfolio, the captured operational input, and the committed benchmark goldens are
**canonical**. The console **reads** them and holds **no authoritative corpus of its own** (echoing ADR-010
§Non-Goals and ADR-011 §Non-Goals). The audit log it writes is an **operational journal of console actions**,
not a competing record of pipeline state. The dev_graph markdown remains the single source of truth for the
engineering graph; the runtime artefacts remain the single source of truth for runtime state.

## Candidate ids (non-binding — none reserved or created here)

Mirroring ADR-011 §6, the nodes the implementation slices will author are named as **non-binding
candidates**, re-derived from `index.md`; none is reserved, none is created in this slice, and formal
assignment happens when each node is authored at writeback:

- an **observability** node for the console — candidate `OBS-002` (next free after `OBS-001`
  [[Dev Graph Dashboard]]);
- **file** nodes for the console at writeback per §7.5 (e.g. `ops/core.py`, `ops/app.py`) — candidate
  `FILE-039`+;
- **test** nodes for the headless core — candidate `TEST-029`+.

No console, ops-core, observability, file, or test **node** is created in this slice.

## Illustrative Information-Architecture Sketch (non-normative)

> **Illustrative, provisional, non-normative — not a contract.** It exists only to give the constraints a
> concrete referent; the implementation slice is the source of truth once authored.

A future console *might* present: a **header/status bar** (pipeline health, `paper-only` badge, Neo4j
freshness, last run, clock); panes/tabs for **overview** (metric tiles + the chain lane as status cells +
latest verdict + six guards), **gates** (ADR-011 a–f + ADR-012 G0–G3 as DataTables), **corpus/calibration**
(readiness + regime/direction distributions), **artefacts** (ledger / portfolio / benchmarks DataTables,
row-selectable → drill into the full record), **processes**, **plugs** (dormant / creds-present / enabled),
and a **live log pane** (a RichLog tailing run logs / fail-closed events + the append-only audit log); with
interval auto-refresh + manual refresh, and key bindings shown in a footer. Gated-live controls render as
**locked** until their confirm + precondition are satisfied.

## Non-Goals (explicitly deferred)

This ADR and the slices it governs explicitly exclude:

- **Live-money trading** (real capital) — paper-only / virtual-money, always (§5);
- **Any network listener / web surface** — no FastAPI, HTTP, socket, or remote exposure; a local terminal
  app only (§2);
- **Coupling to the JARVIS web stack** — no import of, dependency on, or serving by the ADR-010
  FastAPI/React/voice console; siblings, not parent/child (§1);
- **Bypassing a HARD-PAUSE gate** — the console can never force a calibration bump or auto-enable the live
  path; gated transitions fail-closed and require human review (§8, §10);
- **A second source of truth** — the console holds no authoritative pipeline corpus; it reads the canonical
  artefacts and writes only an operational audit journal (§11);
- **Reimplementing safety / paper-only / gate / persistence logic** — every action reuses a governed
  function unchanged (§4);
- **Mutating `src/` decision logic, contracts, or any `*_version`**, and any `wiki/**` or `raw/**` change
  ([[No Wiki Mutation]] CON-001);
- **A scheduler / daemon of its own** — scheduling is delegated to the existing OS-task script (the
  console only registers/observes it).

No console, ops-core, observability, file, or test **nodes** — and no console **code** — are created in
this slice.

## Alternatives Considered

- **Extend JARVIS (ADR-010) into an operator console.** **Rejected** — JARVIS is a read-only *graph*
  console with a browser/web surface; folding runtime *operations* into it would couple the two, add a
  network surface to a local control plane, and blur the knowledge/runtime boundary. They stay siblings
  (§1), optionally sharing a headless ops-core only.
- **Build a web (FastAPI + browser) ops dashboard.** **Rejected** — a web surface is a network listener
  with an auth/exposure problem this control plane does not need; a terminal TUI run by the operator has no
  listener and reads in-process (§2).
- **Let the console call brokers / evaluate guards / write ledgers directly for speed.** **Rejected** —
  that re-implements (and therefore can weaken) the fail-closed, paper-only, gate, and persistence logic.
  The console reuses governed functions unchanged (§4).
- **Make every action a single confirmed tier.** **Rejected** — pure reads need no confirm, and routine
  deterministic re-runs (run chain on the simulator, re-check calibration, re-sync Neo4j) are non-destructive
  and idempotent; collapsing tiers would either over-gate routine work or under-gate the live path. The
  three-tier split (§3) gates exactly the privileged transitions.
- **Display creds/host so the operator can verify the live plug.** **Rejected** — secrets are never shown;
  a derived `dormant / creds-present / enabled` badge conveys readiness without leaking key material (§6).
- **Wire the gated-live tier in the same slice as the read model.** **Rejected** — read-only is proven
  first and the most privileged surface is HARD-PAUSE-gated (§10), matching KA-008 phased autonomy.

## Consequences

### Positive
- A single, local, fail-closed operator surface for observing the whole Layer-3 pipeline and triggering its
  routine and (gated) privileged actions — without inventing any new safety logic.
- The console inherits the runtime's discipline by construction: paper-only, secrets-isolated, fail-closed,
  gate-respecting, zero-dep engine — because it **reuses** the governed functions rather than reimplementing
  them.
- Establishes the operational control plane's boundary **before** any console code is written, eliminating
  the drift risk of an ad-hoc tool that grows a network surface or a second source of truth.
- Keeps JARVIS (knowledge) and this console (runtime) cleanly separated, the engine zero-dependency, and the
  live path gated and reversible.

### Negative / Trade-offs
- A terminal TUI is local-only by design: no remote observation, no shared dashboard (acceptable — the
  control plane is deliberately not a network surface).
- Textual/Rich add an **optional** dependency group; operators must install the `[ops]` extra. The engine
  stays dep-free, but the console is a separate install step.
- The console's value is bounded by what the governed functions already expose; richer telemetry requires
  enriching the runtime artefacts, not the console.

### Risks
- **Scope creep into a network surface** — a future "just add a small web view" would violate §2 (mitigated
  by recording local-only / no-listener as an invariant and a Non-Goal).
- **Re-implementation drift** — a contributor re-deriving a guard/host/verdict in the console for convenience
  (mitigated by §4: reuse-only, and by tests that assert the console calls the governed functions and never
  re-checks host/gate).
- **Secret leakage** — a status view or audit entry inadvertently rendering a credential (mitigated by §6
  and a test that asserts no secret value appears in any read-model output or audit entry).
- **Over-trust of a UI confirm** — treating the modal as the guarantee (mitigated by §7: the server-side
  fail-closed precondition is the real guarantee, enforced by the governed function even if the UI is
  bypassed).

## Future Work

When this ADR is accepted, the slices proceed in tier order under §10: (1) the headless governed read-model
`ops/core.py` + the Textual read-only TUI `ops/app.py` (read-only, `mypy --strict` + `ruff` clean,
`core.py` unit-tested headless); (2) the safe (Tier-2) actions — run chain now (simulator), re-run
calibration readiness, re-sync Neo4j — each audit-logged; **(HARD PAUSE)**; (3) the gated-live (Tier-3)
tier — enable/disable Alpaca paper execution, register/unregister the daily schedule, commit-or-DEFER a
calibration bump — each behind confirm + audit + a server-side precondition; (4) tests (headless, mocked —
no real network / Alpaca / OS-task registration) + the `[project.optional-dependencies] ops` group + the
dev_graph writeback (the `OBS-002` observability node + the `ops/` file/test nodes per §7.5, `index.md`,
`log.md`, the 11 lint checks, and the Neo4j re-sync). Later epochs may add richer telemetry or a shared
read-only ops-core with JARVIS — each under its own amendment, never widening the safety boundary recorded
here.

## Relationships

### Depends On
- [[Chain Orchestrator]]
- [[Paper-Trading Runtime]]
- [[Execution]]
- [[Gold Forward-Return Labeler]]

### Justified By
- [[ADR - JARVIS GraphRAG Integration]]
- [[ADR - Execution Layer Planning]]
- [[ADR - Paper-Trading Runtime Planning]]
- [[ADR - Empirical Calibration Methodology]]
- [[ADR - Implementation Substrate]]

### Constrained By
- [[No Wiki Mutation]]
- [[Canonical Ownership]]

### Originates From
- [[Agent Safety Principles]]
- [[Paper Trading Validation]]
- [[Guardrail Philosophy]]
