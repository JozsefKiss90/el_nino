---
type: capability
canonical_id: CAP-005
status: active
implementation_status: in-progress
canonical: true
created: 2026-06-06
updated: 2026-06-16
confidence: confirmed
evidence:
  - design
  - wiki
  - ADR
  - code
source_paths:
  - "wiki/systems/Trading Engine Pipeline.md"
  - "wiki/execution/Position Sizing.md"
related_files: []
related_tests:
  - "[[test_execution_engine]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Execution Layer Planning]]"
capability_id: "order-management"
parent_system: "[[Trading Engine]]"
implemented_by:
  - "[[Execution]]"
interfaces:
  - "[[Execution API]]"
---

# Order Management

## Definition

The capability to **execute an ADMITted paper decision**: take the ADMIT verdict from the runtime
([[Runtime Decision Record Schema]], SCHEMA-012), apply a **fixed configured paper size** (ADR-011 D2 —
adaptive position sizing is deferred), simulate (or, via the deferred Alpaca-paper adapter, place) the
(paper) fill, and manage the order/fill lifecycle. Re-grounded as the **execution layer** of the gold
lineage — `CAP-020 → MOD-007 ADMIT → execution` — and `paper_only` ([[ADR - Execution Layer Planning]]
§3/§4).

## Scope (Execution Layer Re-grounding, ADR-011)

Per [[ADR - Execution Layer Planning]] (ADR-011 §4) and the [[ADR - Decision Layer Re-grounding]] (ADR-004)
precedent, CAP-005 is re-grounded **in place** (not reclassified; canonical_id unchanged) as the execution
layer:

- **Input re-grounded:** the deprecated `Depends On` edge to Signal Generation (CAP-004) is **retired**;
  the decision input is now the ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012) from [[Paper-Trade
  Admission]] (CAP-021).
- **Interface resolved:** the previously node-less `Execution API` placeholder now resolves to the real
  [[Execution API]] (INT-011).
- **Sizing scoped down (D2):** "calculate position sizes" → *apply a fixed/configured v0 paper size;
  adaptive sizing deferred (ADR-009/011 Non-Goal)*. [[Position Size OK]] (PRED-001) still **validates** the
  fixed size — validation is not sizing.
- **Mode:** `paper_only` / virtual-money; live-money order routing is a future epoch under its own ADR.
- Implemented by the execution module (candidate MOD-008) at STEP 2; the simulated-broker adapter is the
  replay-safe core, the Alpaca-paper adapter a deferred, non-replayable plug (ADR-011 §2/§5).

## Purpose

Execute ADMITted paper decisions. Turn an ADMIT verdict into a deterministic (paper) fill at a fixed
configured size — the **simulated-broker adapter** is the canonical replay-safe path; the **Alpaca-paper**
adapter (virtual money, deferred) is a non-replayable plug behind the same [[Execution API]] port (ADR-011
§2). Position **sizing** is deferred (ADR-011 D2); order types / error handling are v0-minimal.

## Architecture Role

The execution capability of [[Trading Engine]] (SYS-002), downstream of [[Paper-Trade Admission]] (CAP-021).
It receives an ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012), is gated by the wired [[Trade
Validation Gate]] (GATE-001) + hard-limit predicates (the guard runs in the orchestrator **before**
execution; the execution core never imports `src/risk`, ADR-009 §3), and produces an [[Execution Record
Schema]] (SCHEMA-014) + an updated [[Portfolio State Schema]] (SCHEMA-015, maintained by [[Position
Tracking]] CAP-007).

## Inputs

- An ADMIT [[Runtime Decision Record Schema]] (SCHEMA-012) from [[Paper-Trade Admission]] (CAP-021) — the
  only decision input (never the deprecated Signal Generation path, never a raw gold packet/snapshot;
  ADR-011 §1/§4).
- The prior [[Portfolio State Schema]] (SCHEMA-015) (explicit state in), the re-derived instrument price
  (ADR-011 D1), and versioned execution / fill-model config.
- The [[Trade Validation Gate]] (GATE-001) APPROVE result (forwarded provenance).

## Outputs

- An [[Execution Record Schema]] (SCHEMA-014) — the (paper) fill + guard provenance — via [[Execution API]]
  (INT-011).
- An updated [[Portfolio State Schema]] (SCHEMA-015) (threaded through CAP-007).
- (Optional, deferred) execution events (candidate EVT-001).

## Constraints

- **paper_only / virtual-money** (ADR-011 §3): never a live-money order; [[Withdrawal Disabled]] (PRED-005)
  enforced; live-money trading is a Non-Goal.
- **Sizing deferred** (ADR-011 D2): v0 uses a fixed configured `default_size`; that fixed size MUST still
  pass [[Trade Validation Gate]] (GATE-001) hard-limit validation before any (paper) fill.
- **Determinism** (ADR-011 §2): the simulated-broker core is pure + replay-safe; the Alpaca-paper adapter is
  explicitly non-replayable (logged, never on the replay / benchmark path).

## Open Questions

- Implemented by [[Execution]] (MOD-008) + the `SimulatedBrokerAdapter` (STEP 2, tested);
  `implementation_status: in-progress` — the Alpaca-paper adapter (gate f) and full chain-orchestrator
  integration remain (ADR-011 §5 / STEP 4–5).

## Relationships

### Depends On
- [[Paper-Trade Admission]]
- [[Risk Control]]

### Consumes
- [[Runtime Decision Record Schema]]

### Produces
- [[Execution Record Schema]]

### Implemented By
- [[Execution]]

### Validated By
- [[test_execution_engine]]

### Provides
- [[Execution API]]
- Order data to [[Trade Logging]]

### Realizes
- [[Pipeline Pattern]]
- [[Guardrail Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Execution Layer Planning]]
