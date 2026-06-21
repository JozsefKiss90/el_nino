---
type: module
canonical_id: MOD-011
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
  - "ops/core.py"
  - "ops/app.py"
  - "ops/actions.py"
  - "ops/gated.py"
  - "ops/audit.py"
  - "ops/proc.py"
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
  - "[[ADR - Operations Control Plane]]"
module_name: "ops"
module_path: "ops/"
responsibility: "Local terminal operator console (governed read-model + Textual TUI) over the Layer-3 runtime; three action tiers behind confirm/audit/precondition"
depends_on:
  - "[[Chain Orchestrator]]"
  - "[[Paper-Trading Runtime]]"
  - "[[Execution]]"
  - "[[Gold Forward-Return Labeler]]"
provides:
  - "[[Operations Control Plane Console]]"
---

# Operations Control Plane

## Definition

The `ops/` package — a **local terminal operator console** (a Textual TUI over a headless governed
read-model) that observes the El Niño Layer-3 runtime and triggers operator actions in three safety
tiers. Authored under [[ADR - Operations Control Plane]] (ADR-013). It is a **sibling** of the JARVIS
graph console ([[ADR - JARVIS GraphRAG Integration]] ADR-010) — JARVIS reads the dev_graph; this reads
the **runtime** — and is **not** coupled to the JARVIS web stack.

## Purpose

Give the operator one local surface to (a) **observe** pipeline status, the chain verdict + six-guard
block, the ADR-011/ADR-012 gate boards, calibration readiness, artefacts, processes, and live-plug
status; and (b) **trigger** routine and (gated) privileged actions — without reimplementing any safety,
paper-only, or gate logic (every action reuses a governed function unchanged).

## Architecture Role

Sits entirely **on top of** the Layer-3 modules. It imports `src/` governed functions + stdlib (and,
in `app.py` only, Textual/Rich from the optional `ops` dependency group). `src/` keeps its ADR-003
zero-runtime-deps rule; `ops/` is **never imported by** `src/`.

## Inputs (Dependencies)

- [[Chain Orchestrator]] (MOD-010) — `run_once` / `run_sequence` / `find_latest_snapshot` (run + preview).
- [[Paper-Trading Runtime]] (MOD-007) — `load_ledger` / `load_operational`, `Verdict`, the six guards.
- [[Execution]] (MOD-008) — `load_portfolio`, `paper_adapter_from_env` (live-plug status + gated run).
- [[Gold Forward-Return Labeler]] (MOD-009) — the committed golden read for calibration readiness.
- The deterministic `MarketCalendarFeed` / `clock_feed_from_env`; `sync_to_neo4j.py`; the schedule script.

## Outputs (Provides)

- [[Operations Control Plane Console]] (OBS-002) — the observability/control surface.
- An append-only **audit log** (`runtime/ops/audit_log.jsonl`) of every mutating/live console action.

## Constraints

Local-only / no network listener; paper-only / no live-money path; **secrets never displayed** (derived
`dormant`/`creds-present` only, [[Agent Safety Principles]] KA-008); confirm + audit + server-side precondition on
every mutation; reuse-governed-functions; gate-respecting (calibration bump DEFERs unless the ADR-012
gate passes, never bumps a `*_version`); engine stays zero-dep per ADR-003
[[ADR - Implementation Substrate]]. No `wiki/**`/`raw/**` mutation ([[No Wiki Mutation]]).

## Implementation Notes

- **`ops/core.py`** ([[core.py (ops)]]) — the headless read-model: `assemble_dashboard()` bundles
  ledger/portfolio/operational views, a **pure** latest-decision preview (`run_sequence`, no persistence),
  the ADR-011 (a–f) + ADR-012 (G0–G3, advisory) gate boards, calibration readiness (discrete `eligible`
  flag + display string), plug status, processes, policy versions, audit tail. Every loader error is
  caught into an `error` field (never raises).
- **`ops/app.py`** ([[app.py (ops)]]) — the Textual TUI + `ConfirmModal`; tiers wired as key bindings;
  actions run in crash-proof thread workers; `--once` headless dump.
- **`ops/actions.py`** ([[actions.py (ops)]]) — Tier-2 safe actions (run-chain-now on the simulator,
  re-run calibration readiness, re-sync Neo4j); audit-logged, never raise.
- **`ops/gated.py`** ([[gated.py (ops)]]) — Tier-3 gated-live actions (one-shot Alpaca-paper run,
  register/unregister schedule, commit-or-DEFER calibration bump); each enforces a server-side
  precondition and never raises/always audits.
- **`ops/audit.py`** ([[audit.py (ops)]]) — append-only ASCII audit log (`make_entry`/`write_entry`/
  `read_audit`).
- **`ops/proc.py`** — small shared helper (subprocess `default_runner` + secret-`redact` + `tail`) used
  by both action tiers; below the §7.5 file-node threshold (interface-less utility), noted here.
- Tier safety is **structural**: `run_chain_now` hardwires the simulator port; the gated Alpaca run
  fail-closes to REFUSE when `paper_adapter_from_env().client is None`; the bump branches on the discrete
  `eligible` flag and is `executed=False` on every branch.

## Open Questions

- A future shared read-only ops-core with JARVIS (ADR-010) is a possible later amendment — out of scope.
- `proc.py` may warrant its own file node if it grows beyond a thin helper.

## Relationships

### Depends On
- [[Chain Orchestrator]]
- [[Paper-Trading Runtime]]
- [[Execution]]
- [[Gold Forward-Return Labeler]]

### Provides
- [[Operations Control Plane Console]]

### Validated By
- [[test_ops_core]]
- [[test_ops_audit]]
- [[test_ops_actions]]
- [[test_ops_gated]]
- [[test_ops_app]]

### Constrained By
- [[No Wiki Mutation]]
- [[Canonical Ownership]]

### Justified By
- [[ADR - Operations Control Plane]]

### Realizes
- [[patterns/Guardrail Pattern]]

### Originates From
- [[Agent Safety Principles]]
- [[Paper Trading Validation]]
