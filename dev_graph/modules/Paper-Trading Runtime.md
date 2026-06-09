---
type: module
canonical_id: MOD-007
status: active
implementation_status: tested
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/gold/paper_runtime/engine.py"
related_files:
  - "[[models.py (paper_runtime)]]"
  - "[[config.py (paper_runtime)]]"
  - "[[predicates.py (paper_runtime)]]"
  - "[[engine.py]]"
  - "[[runtime.py]]"
related_tests:
  - "[[test_paper_runtime_guards]]"
  - "[[test_paper_runtime_engine]]"
  - "[[test_paper_runtime_determinism]]"
  - "[[test_paper_runtime_ledger]]"
  - "[[test_paper_runtime_bench]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
module_name: "paper_runtime"
module_path: "src/gold/paper_runtime"
responsibility: "Admit a pure Gold DecisionPacket against explicit runtime state; compute the stateful L3 guards"
depends_on:
  - "[[Gold Decision Builder]]"
provides:
  - "[[Paper Runtime API]]"
---

# Paper-Trading Runtime

## Definition

The first **stateful** Layer-3 component: it consumes a pure [[Gold DecisionPacket v0 Schema]]
(SCHEMA-011) plus explicit runtime state (a self-describing [[Runtime Ledger Schema]] + a versioned
operational input) and emits a [[Runtime Decision Record Schema]] (SCHEMA-012) + a new ledger. It
computes the two stateful L3 guards — [[Duplicate OK]] (PRED-006) and [[Operational OK]] (PRED-007) —
and echoes the snapshot-derived guards. Realizes [[Paper-Trade Admission]] (CAP-021).

## Purpose

Turn the deferred *paper-trading runtime* (ADR-006 Non-Goal) into a deterministic, replay-safe
admission layer without breaking the determinism / bounded-context discipline of the pure layers
(ADR-009). It is **not** live execution, an order, a broker instruction, or the treasury Decision
Engine (MOD-002); permanently separate (ADR-004) and distinct from [[Guardrail Enforcement]] (CAP-008).

## Architecture Role

An L3 admission capability under [[Trading Engine]] (SYS-002), downstream of [[Gold Decision
Generation]] (CAP-020). Realizes the [[Pipeline Pattern]] and originates from [[Stateless Agent
Architecture]] (KA-009 — Wake-Execute-Sleep, file-mediated state). Governed by [[ADR - Paper-Trading
Runtime Planning]] (ADR-009); the record is gated by [[Runtime Admission Gate]] (GATE-003).

## Inputs (or Dependencies)

- A `GoldDecisionPacket` (SCHEMA-011) carrying forwarded `snapshot_guards` + `as_of` (ADR-009 §3).
- The prior `RuntimeLedger` (explicit state in), a versioned `OperationalInput`, and a
  `RuntimePolicyConfig`. Never a raw snapshot, the `src/risk` package, a wall-clock, or env.

## Outputs (or Provides)

- A `RuntimeDecisionRecord` (SCHEMA-012, the ADMIT/HOLD/REJECT verdict + six-guard block) and a new
  `RuntimeLedger` (SCHEMA-013), via [[Paper Runtime API]] (INT-010).

## Constraints

- **Wrap, never enrich-in-place** — the runtime consumes a pre-built packet and never enriches it; its
  chain orchestrator builds the packet with `build_decision(guards=None)`, so the packet stays pure
  (`packet_id` excludes `guard_refs`, so enriching would collide). Guard outcomes live on the record
  (ADR-009 §2).
- **Pure core + IO at the edge** — `evaluate()` is a pure function of explicit values; the only IO
  (ledger load/persist, operational load) is in `runtime.py` (mirrors `consume()` / `load_config`).
- **Stateful determinism** — same (packet, prior ledger, operational input, policy) ⇒ identical record
  + identical new ledger; state is an explicit argument + return value (ADR-009 §4/§5).
- **Fail-closed** — WATCH/INDETERMINATE ⇒ HOLD; a required-but-failed guard ⇒ REJECT naming it;
  default-closed operational input.
- **Bounded-context hygiene** — re-implements the fail-closed verdict pattern; never imports
  `src/risk` (Context Map / ARCH-001).

## Implementation Notes

- `models.py` — SCHEMA-012 `RuntimeDecisionRecord` + `Verdict`/`GuardOutcome`; SCHEMA-013
  `RuntimeLedger`/`LedgerEntry`; `OperationalInput`; `compute_record_id`; `digest_snapshot_guards`.
  Reuses `_GUARD_NAMES` from the gold packet module (single guard ordering).
- `config.py` — `RuntimePolicyConfig` (`require_operational`, `require_snapshot_guards`) +
  `runtime_policy_fingerprint()` (same idiom as `decision_policy_fingerprint`; fingerprint
  `ab798cae…6f32`) + fail-closed `from_mapping`/`load_config`.
- `predicates.py` — `duplicate_ok` (once-ever on a prior ADMIT), `operational_ok`, echo
  `data_ok`/`freshness_ok`/`cooldown_ok` from `packet.snapshot_guards`; `supervisor_ok` is a `None`
  stub. `(passed, reason)` shape mirrors the risk predicates (pattern only — never imported).
- `engine.py` — pure `evaluate()`: full six-guard block + short-circuit conjunction over the required
  guards (first failure names it) → fail-closed verdict → one ledger append.
- `runtime.py` — IO shell `run_once` + the pure `run_sequence` replay driver.
- 50 runtime tests (TEST-013..017) + BENCH-003 (real determinism + a synthetic verdict sweep:
  ADMIT 3 / HOLD 1 / REJECT 3). Full suite green; `mypy --strict`/`ruff` clean on `src/gold/paper_runtime`.

## Open Questions

- A computed cooldown guard, a live operational feed, and a downstream paper-execution/evaluation layer
  are deferred (ADR-009 Non-Goals).
- `supervisor_ok` stays a `None` stub until a supervisor exists (then it flips to computed).

## Relationships

### Implements
- [[Paper Runtime API]]

### Consumes
- [[Gold DecisionPacket v0 Schema]]
- [[Runtime Ledger Schema]]

### Produces
- [[Runtime Decision Record Schema]]
- [[Runtime Ledger Schema]]

### Contains
- [[models.py (paper_runtime)]]
- [[config.py (paper_runtime)]]
- [[predicates.py (paper_runtime)]]
- [[engine.py]]
- [[runtime.py]]

### Validated By
- [[test_paper_runtime_guards]]
- [[test_paper_runtime_engine]]
- [[test_paper_runtime_determinism]]
- [[test_paper_runtime_ledger]]
- [[test_paper_runtime_bench]]

### Depends On
- [[Gold Decision Builder]]

### Realizes
- [[Pipeline Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]

### Originates From
- [[Stateless Agent Architecture]]
