---
type: interface
canonical_id: INT-011
status: active
implementation_status: implemented
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
  - "src/execution/runtime.py"
related_files:
  - "[[engine.py (execution)]]"
  - "[[runtime.py (execution)]]"
  - "[[adapters.py]]"
  - "[[alpaca_adapter.py]]"
related_tests:
  - "[[test_execution_engine]]"
  - "[[test_execution_determinism]]"
  - "[[test_execution_guards]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
interface_id: "execution-api"
interface_version: "0.1.0"
parent_capability: "[[Order Management]]"
input_schema: "[[Runtime Decision Record Schema]]"
output_schema: "[[Execution Record Schema]]"
implemented_by:
  - "[[Execution]]"
stability: experimental
---

# Execution API

## Definition

The execution layer's boundary contract (ADR-011 §2). It has **two seams** — the layer entry point and
the broker (port) seam the adapters implement — and they are distinct (the code reconciliation):

**(1) Layer entry point — `execute()` ([[Execution]] / MOD-008's pure core, NOT the adapter seam).**
Consumes an **ADMIT** `RuntimeDecisionRecord` + the forwarded `direction` (the ADMIT record omits it) +
the re-derived `instrument_price` (ADR-011 D1) + explicit portfolio state + the GATE-001 `guard_result` +
an **injected** `ExecutionPort`; returns a (paper) `ExecutionRecord` + a new `PortfolioState`:

```
execute(
    admit: RuntimeDecisionRecord,        # SCHEMA-012, verdict == ADMIT only (asserted)
    direction: Direction,                # forwarded from the gold packet (the ADMIT record omits it)
    instrument_price: float,             # re-derived from admit.source_snapshot_id (ADR-011 D1)
    prior_portfolio: PortfolioState,     # SCHEMA-015 (explicit state IN)
    guard_result: GuardResult,           # the GATE-001 outcome, forwarded as provenance — NOT recomputed
    port: ExecutionPort = SimulatedBrokerAdapter(),  # the injected broker adapter (seam 2 below)
    fill_model: FillModelConfig = ...,   # versioned (fill_model_version + fingerprint)
    config: ExecutionPolicyConfig = ..., # versioned (carries the fixed default_size — sizing deferred, D2)
) -> tuple[ExecutionRecord, PortfolioState]   # SCHEMA-014 + the new SCHEMA-015
```

**(2) Broker seam — `ExecutionPort.fill()` (what each adapter implements).** The hexagonal port (ADR-011
§2) is the one broker-specific method `execute()` dispatches to. The deterministic `SimulatedBrokerAdapter`
(the replay-safe core path, `replayable = True`) and the now-built, **default-OFF** non-replayable
`AlpacaPaperAdapter` ([[alpaca_adapter.py]] FILE-038, `replayable = False`, gate f closed 2026-06-18) each
implement it:

```
ExecutionPort.fill(
    instrument: str, direction: Direction, size: float,
    instrument_price: float, fill_model: FillModelConfig,
) -> Fill
```

`execute()` is pure; the IO boundary shell adds `run_once(...)` (load portfolio → guard → execute → persist
atomically) and `run_sequence(...)` (thread the portfolio over an ordered ADMIT sequence — the deterministic
BENCH-004 replay vehicle, no IO), mirroring [[Paper Runtime API]] (INT-010)
`evaluate`/`run_once`/`run_sequence`.

## Purpose

Make the **ADMIT → (paper) execution** seam an explicit, versioned contract behind which a deterministic
fill-simulator and an optional live broker adapter are interchangeable (the hexagonal port/adapter split,
ADR-011 §2). The deterministic adapter is canonical for tests/benchmarks/replay; the Alpaca adapter is
quarantined off the replay path (ADR-011 §2/§6, gate f).

## Architecture Role

Output interface of the re-grounded [[Order Management]] (CAP-005), one stage downstream of [[Paper
Runtime API]] (INT-010): it consumes the ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012), **never** a
raw gold packet or snapshot (ADR-011 §1). `execute()` is pure (no IO/clock/randomness, never imports
`src/risk`, ADR-009 §3); IO is confined to the `run_once` shell. This node resolves the node-less
`Execution API` placeholder CAP-005 previously named (ADR-011 §4).

## Contract

- **Determinism (ADR-011 §2):** same (`admit`, `direction`, `instrument_price`, `prior_portfolio`,
  `guard_result`, `fill_model_version` + fingerprint, `execution_policy_version`, the simulated `port`) ⇒
  identical execution record + identical new portfolio state; `to_dict()` byte-identical. The Alpaca path is
  `replayable: false` and never on this invariant.
- **Input boundary (ADR-011 §1 / D1):** consumes only SCHEMA-012 + explicit re-derived inputs + prior
  portfolio. `instrument_price` is re-derived from `admit.source_snapshot_id` (immutable, content-addressed
  snapshot) at the orchestrator — never read live on the replay path; the core never reads SCHEMA-001.
- **Guard provenance (ADR-011 §4 / gate c):** `execute()` is called only on a GATE-001 **APPROVE**; the
  `guard_result` is forwarded and recorded, never recomputed. A BLOCK prevents `execute()` — the
  orchestrator records the first failing predicate, no fill.
- **Totality / fail-closed:** every admitted call yields exactly one execution record + one new portfolio
  state; a non-ADMIT input is a caller error (asserted). Size is the fixed `config.default_size` (ADR-011
  D2 — sizing deferred, not computed here).

## Error Modes

- A malformed portfolio file raises a contract error at `load_portfolio` (a missing file is the legitimate
  empty state). Missing/non-paper Alpaca credentials **fail closed** (no live call) on the live path. Both
  keep the core pure.

## Stability

`experimental` / `interface_version: 0.1.0`. May extend (not break) when the Alpaca adapter, a computed
fill model, or multi-instrument support is authored.

## Open Questions

- Implemented by [[Execution]] (MOD-008) + the `SimulatedBrokerAdapter` (STEP 2, tested) and now the
  **default-OFF** `AlpacaPaperAdapter` ([[alpaca_adapter.py]], gate f closed 2026-06-18 — non-replayable,
  fail-closed, paper-only; validated by [[test_alpaca_adapter]]). BENCH-004 and the chain-orchestrator
  integration (MOD-010) are done. The live adapter is **built-but-dormant** (no LONG until calibration,
  ADR-011 §5) and *enabling* the live execution path is an operator HARD-PAUSE action.

## Relationships

### Consumes
- [[Runtime Decision Record Schema]]
- [[Portfolio State Schema]]

### Produces
- [[Execution Record Schema]]

### Implemented By
- [[Execution]]

### Validated By
- [[test_execution_engine]]
- [[test_execution_determinism]]
- [[test_execution_guards]]

### Justified By
- [[ADR - Execution Layer Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Paper Trading Validation]]
