---
type: file
canonical_id: FILE-046
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-23
updated: 2026-06-23
confidence: confirmed
evidence:
  - code
  - ADR
source_paths:
  - "src/execution/price_reference.py"
related_files:
  - "[[models.py (execution)]]"
related_tests:
  - "[[test_price_reference]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
file_path: "src/execution/price_reference.py"
language: "python"
module: "[[Execution]]"
owns:
  - "resolve_sim_exec_ref"
  - "ExecPriceRef"
  - "OZ_PER_SHARE"
  - "EXEC_PRICE_SOURCE_VERSION"
used_by:
  - "[[Execution]]"
  - "[[Chain Orchestrator]]"
---

# price_reference.py

## Definition

The execution **price-reference seam** (SCHEMA-014 / ADR-014 bucket i): a source-pluggable **GLD share
price** (`exec_ref_gld_price`, $/share), replacing the latent defect of forwarding gold spot ($/oz) into a
GLD share order. One seam, two implementations.

## Purpose

Fix slippage to be GLD-vs-GLD and mark `avg_cost`/`unrealized_pnl` in $/share. `gold_price` (spot, $/oz)
is **severed from execution** and stays a pure decision-context feature.

## Architecture Role

- **Simulator / replay path** → a versioned deterministic derived proxy
  `exec_ref_gld_price = gold_price_proxy × OZ_PER_SHARE` (`resolve_sim_exec_ref`), never a live read (the
  D1 replay discipline).
- **Live Alpaca path** → the real live GLD mark (read non-replayably by [[live_runtime.py]]), plugging into
  the same `ExecPriceRef` shape with a pinned, labelled timestamp.

## Inputs / Dependencies

- The snapshot's `gold_price_proxy` (real XAUUSD spot) + the versioned `OZ_PER_SHARE` constant.

## Outputs / Provides

- `ExecPriceRef(price, ts, basis)` — the resolved GLD-share reference + its provenance basis label
  (`sim_derived_proxy` / `live_submit_mark` / `live_open_mark`).

## Constraints

- The `EXEC_PRICE_SOURCE_VERSION` axis folds into the replay key — a change to the formula / `OZ_PER_SHARE`
  is a documented, versioned re-pin (BENCH-004/006); old goldens stay byte-reproducible under the prior
  version.
- Stdlib frozen dataclass, zero runtime deps (ADR-003).

## Implementation Notes

`OZ_PER_SHARE = 0.0933` is a versioned approximation used **only** by the deterministic proxy; the live
path uses the real broker mark, never this constant. The optional real-GLD-share-price snapshot ingest
(ADR-014 §5.1) plugs into this seam later with zero rework.

## Relationships

### Depends On
- [[Execution]]

### Validated By
- [[test_price_reference]]

### Used By
- [[Execution]]
- [[Chain Orchestrator]]

### Justified By
- [[ADR - Operable Alpaca Paper Execution Adapter v1]]

### Constrained By
- [[Canonical Ownership]]
