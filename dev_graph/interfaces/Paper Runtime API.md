---
type: interface
canonical_id: INT-010
status: active
implementation_status: implemented
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
  - "src/gold/paper_runtime/runtime.py"
related_files:
  - "[[engine.py]]"
  - "[[runtime.py]]"
related_tests:
  - "[[test_paper_runtime_engine]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Paper-Trading Runtime Planning]]"
interface_id: "paper-runtime-api"
interface_version: "0.1.0"
parent_capability: "[[Paper-Trade Admission]]"
input_schema: "[[Gold DecisionPacket v0 Schema]]"
output_schema: "[[Runtime Decision Record Schema]]"
implemented_by:
  - "[[Paper-Trading Runtime]]"
stability: experimental
---

# Paper Runtime API

## Definition

The boundary contract by which a caller admits a pure gold packet against explicit runtime state:

```
evaluate(
    packet: GoldDecisionPacket,            # SCHEMA-011 (consumed by reference; never mutated)
    prior_ledger: RuntimeLedger,           # SCHEMA-013 (explicit state in)
    operational_input: OperationalInput,   # versioned operational-readiness artifact
    config: RuntimePolicyConfig = DEFAULT,  # versioned require-flags (+ fingerprint)
) -> tuple[RuntimeDecisionRecord, RuntimeLedger]   # SCHEMA-012 + new SCHEMA-013
```

The pure core is `evaluate()`. The IO boundary shell adds `run_once(packet, ledger_path,
operational_path, config)` (load → evaluate → persist atomically) and `run_sequence(items, config,
ledger)` (thread the ledger in memory over an ordered `(packet, operational_input)` list — the
deterministic replay vehicle, no IO).

## Purpose

Make the packet → admission seam an explicit, versioned contract so a (future) paper-execution or
evaluation layer depends on a stable abstraction. It is the **wrap** seam (ADR-009 §2): it consumes
SCHEMA-011 + runtime state and emits a separate record — it never re-emits or enriches the packet.

## Architecture Role

Output interface of CAP-021 [[Paper-Trade Admission]], implemented by MOD-007 [[Paper-Trading
Runtime]]. `evaluate()` is pure (no IO/clock); IO is confined to `run_once`/the loader shells. It is
the gold-runtime counterpart to INT-009 (the packet builder), one stage downstream.

## Contract

- **Determinism (ADR-009 §4):** same (`packet`, `prior_ledger`, `operational_input`,
  `runtime_policy_version` + fingerprint) ⇒ identical record + identical new ledger; `to_dict()`
  byte-identical.
- **Input boundary (ADR-009 §3):** consumes only SCHEMA-011 + runtime state. The snapshot-derived
  guards + `as_of` arrive **on the packet** (forwarded `snapshot_guards`); the core never reads raw
  SCHEMA-001 and never imports `src/risk` (Context Map / ARCH-001 bounded-context hygiene).
- **Totality:** every `(packet, ledger, op)` yields exactly one record and appends exactly one ledger
  entry; the verdict is fail-closed (WATCH/INDETERMINATE ⇒ HOLD; required-but-failed guard ⇒ REJECT).

## Error Modes

- A malformed ledger file raises `RuntimeContractError` at `load_ledger` (a missing file is the
  legitimate empty state). An absent/malformed operational file resolves **default-closed** (not
  tradeable) at `load_operational`. Both keep the core pure.

## Stability

`experimental` / `interface_version: 0.1.0`. May extend (not break) when computed cooldown, a live
operational feed, or a downstream execution/evaluation layer is authored.

## Relationships

### Consumes
- [[Gold DecisionPacket v0 Schema]]
- [[Runtime Ledger Schema]]

### Produces
- [[Runtime Decision Record Schema]]

### Implemented By
- [[Paper-Trading Runtime]]

### Validated By
- [[test_paper_runtime_engine]]

### Justified By
- [[ADR - Paper-Trading Runtime Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Stateless Agent Architecture]]
