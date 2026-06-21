---
type: file
canonical_id: FILE-026
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-16
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/execution/adapters.py"
related_files:
  - "[[alpaca_adapter.py]]"
related_tests:
  - "[[test_execution_engine]]"
  - "[[test_execution_determinism]]"
related_constraints: []
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/execution/adapters.py"
language: "python"
module: "[[Execution]]"
owns: []
used_by: []
---

# adapters.py

## Definition

The `ExecutionPort` Protocol (the broker boundary — the one `fill()` method that differs between brokers)
and `SimulatedBrokerAdapter` (the deterministic, replay-safe core path — the hard-wired default port).
The non-replayable `AlpacaPaperAdapter` (gate f) now lives in the sibling [[alpaca_adapter.py]] (FILE-038),
**default-OFF** — built behind this same port but never the default, keeping `adapters.py` network-free.

## Purpose

Realize the hexagonal port/adapter split (ADR-011 §2): one deterministic core behind the port, with the
live broker as an interchangeable non-replayable plug. Implements [[Execution API]] (INT-011).

## Implementation Notes

`SimulatedBrokerAdapter` (frozen dataclass, `mode = SIMULATED`, `replayable = True`): a LONG buy fills at
`instrument_price * (1 + slippage_bps/1e4)` — fixed adverse slippage, no clock/network/randomness (the
seeded micro-jitter of gate (b) is a future enhancement). The `ExecutionPort` Protocol exposes read-only
`mode`/`replayable` + `fill()`.

## Relationships

### Depends On
- [[Execution]]

### Implements
- [[Execution API]]

### Validated By
- [[test_execution_engine]]
