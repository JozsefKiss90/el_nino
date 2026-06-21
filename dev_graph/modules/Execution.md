---
type: module
canonical_id: MOD-008
status: active
implementation_status: tested
canonical: true
created: 2026-06-16
updated: 2026-06-18
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "src/execution/engine.py"
related_files:
  - "[[models.py (execution)]]"
  - "[[config.py (execution)]]"
  - "[[adapters.py]]"
  - "[[alpaca_adapter.py]]"
  - "[[engine.py (execution)]]"
  - "[[runtime.py (execution)]]"
  - "[[run_execution_bench.py]]"
related_tests:
  - "[[test_execution_engine]]"
  - "[[test_execution_determinism]]"
  - "[[test_execution_guards]]"
  - "[[test_execution_bench]]"
  - "[[test_alpaca_adapter]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
  - "[[ADR - Decision Layer Re-grounding]]"
module_name: "execution"
module_path: "src/execution"
responsibility: "Execute an ADMITted paper decision into a (paper) fill + portfolio state; wire GATE-001"
depends_on:
  - "[[Paper-Trading Runtime]]"
provides:
  - "[[Execution API]]"
---

# Execution

## Definition

The first **money-shaped** Layer-3 module (ADR-011): it consumes an **ADMIT** [[Runtime Decision Record
Schema]] (SCHEMA-012) + explicit portfolio state and produces an [[Execution Record Schema]] (SCHEMA-014)
+ a new [[Portfolio State Schema]] (SCHEMA-015). A deterministic, replay-safe **simulated-broker** core
behind the [[Execution API]] (INT-011) port; the non-replayable Alpaca-paper adapter is now built
**default-OFF / dormant** ([[alpaca_adapter.py]] FILE-038, gate f closed 2026-06-18).
Realizes the re-grounded [[Order Management]] (CAP-005) and produces the state of [[Position Tracking]]
(CAP-007).

## Purpose

Turn the deferred execution/portfolio layer (ADR-009/ADR-006 Non-Goals) into a deterministic, replay-safe
paper-execution layer without breaking the determinism / bounded-context discipline of the pure layers
(ADR-011 §2). It is **paper_only** / virtual-money — never a live order; live-money is a Non-Goal.

## Architecture Role

An L3 execution module under [[Trading Engine]] (SYS-002), downstream of [[Paper-Trade Admission]]
(CAP-021): `CAP-020 → MOD-007 ADMIT → execution` (ADR-011 §4). Realizes the [[Pipeline Pattern]] and the
[[Guardrail Pattern]] (it wires [[Trade Validation Gate]] GATE-001). Originates from [[Paper Trading
Validation]] (KA-010). Governed by [[ADR - Execution Layer Planning]] (ADR-011).

## Inputs (or Dependencies)

- An ADMIT `RuntimeDecisionRecord` (SCHEMA-012) from [[Paper-Trading Runtime]] (MOD-007).
- The forwarded `direction` (the ADMIT record omits it) + the re-derived `instrument_price` (ADR-011 D1),
  the prior `PortfolioState`, a captured `GuardrailConfig`, and versioned execution/fill-model config.

## Outputs (or Provides)

- An `ExecutionRecord` (SCHEMA-014) + a new `PortfolioState` (SCHEMA-015), via [[Execution API]] (INT-011).

## Constraints

- **Determinism boundary (ADR-011 §2):** the pure `execute()` core (`engine.py`) is a pure function of
  explicit values; the only IO (portfolio load/persist) + the GATE-001 guard-wiring live in
  `runtime.py` (the composition root). The simulated adapter is replay-safe; the Alpaca adapter (deferred)
  is non-replayable.
- **Bounded-context hygiene (ADR-009 §3):** only the `runtime.py` orchestrator imports `src/risk`; the
  `execute()` core never does — it receives the GATE-001 outcome as a forwarded `GuardResult`.
- **Sizing deferred (ADR-011 D2):** v0 uses a fixed configured `default_size`; the guard validates it.
- **Fail-closed / idempotent:** a blocked guard, a non-LONG stance, or an already-executed snapshot ⇒ a
  no-fill record (portfolio unchanged); idempotent on `source_snapshot_id`. `paper_only` always.

## Implementation Notes

- `models.py` — SCHEMA-014 `ExecutionRecord` + `Fill` + `GuardResult`; SCHEMA-015 `PortfolioState` /
  `Position` / `ExecutionEntry`; `compute_execution_id`; mark-to-snapshot P&L. Reuses `Direction` and
  `RuntimeDecisionRecord`/`Verdict` from the gold lineage (never re-derived).
- `config.py` — `ExecutionPolicyConfig` (`default_size`, `paper_equity`) + `FillModelConfig`
  (`slippage_bps`, `fill_model_version`) + `fingerprint()`s + fail-closed loaders.
- `adapters.py` — the `ExecutionPort` Protocol + `SimulatedBrokerAdapter` (pure, deterministic fill; the
  hard-wired default port).
- `alpaca_adapter.py` ([[alpaca_adapter.py]] FILE-038, **gate f**) — `AlpacaPaperAdapter` behind the same
  port (`mode=alpaca_paper`, `replayable=False`), an injected paper-broker Protocol + stdlib REST client,
  `AlpacaExecutionError`, and `paper_adapter_from_env` (refuses any non-paper base URL; fail-closed on
  missing creds). **Default-OFF / built-but-dormant** — reached only by an explicit `port=` opt-in, not
  re-exported, and `fill()` runs only for an approved LONG (none until calibration, ADR-011 §5).
- `engine.py` — pure `execute()`: fail-closed fill decision (guard → idempotency → stance) → portfolio
  transition → record. No IO / clock / randomness / `src/risk`.
- `runtime.py` — IO shell (`load_portfolio`/`persist_portfolio`, atomic) + guard-wiring (`run_guard`
  calls `GuardrailEngine.validate` before `execute`) + `run_once` + the pure `run_sequence` replay driver
  (the BENCH-004 vehicle).
- 19 execution tests (TEST-018..020) green; full suite green; `mypy --strict` + `ruff` clean on
  `src/execution`.
- **STEP 4 (gate d closed):** [[Execution Layer Benchmark]] (BENCH-004) — `run_execution_bench.py`
  (FILE-029) + the committed golden `artifacts/execution_bench.json` + the in-sync [[test_execution_bench]]
  (TEST-021) prove the §2 byte-identical sequence-replay invariant over this module. Full suite 887 green.

## Open Questions

- The Alpaca-paper adapter (gate f / STEP 5) is now **built default-OFF** ([[alpaca_adapter.py]]) and
  **dormant** — non-replayable and quarantined off the replay path, it cannot fill until calibration
  produces a LONG (ADR-011 §5). BENCH-004 still grounds replay in the offline simulator core only.
  *Enabling* the live execution path remains an explicit operator HARD-PAUSE action.
- Full chain-orchestrator integration (forwarding `instrument_price`/`direction` from the in-hand
  FeatureVector through the whole chain) is now **implemented** by [[Chain Orchestrator]] (MOD-010) and
  proven end-to-end by [[Chain Orchestrator Benchmark]] (BENCH-006). MOD-008 stays the execution-only
  layer; the orchestrator threads it.

## Relationships

### Implements
- [[Execution API]]

### Consumes
- [[Runtime Decision Record Schema]]

### Produces
- [[Execution Record Schema]]
- [[Portfolio State Schema]]

### Contains
- [[models.py (execution)]]
- [[config.py (execution)]]
- [[adapters.py]]
- [[alpaca_adapter.py]]
- [[engine.py (execution)]]
- [[runtime.py (execution)]]

### Validated By
- [[test_execution_engine]]
- [[test_execution_determinism]]
- [[test_execution_guards]]
- [[test_execution_bench]]
- [[test_alpaca_adapter]]
- [[Execution Layer Benchmark]]

### Depends On
- [[Paper-Trading Runtime]]

### Used By
- [[Chain Orchestrator]]

### Realizes
- [[Pipeline Pattern]]
- [[Guardrail Pattern]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Execution Layer Planning]]

### Originates From
- [[Paper Trading Validation]]
