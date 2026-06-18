---
type: file
canonical_id: FILE-031
status: implemented
implementation_status: implemented
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "src/orchestration/models.py"
related_files: []
related_tests:
  - "[[test_chain_engine]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Execution Layer Planning]]"
file_path: "src/orchestration/models.py"
language: "python"
module: "[[Chain Orchestrator]]"
owns: []
used_by: []
---

# models.py (orchestration)

## Definition

The chain orchestrator's output model (MOD-010): `ChainResult` (a frozen aggregate of the five typed
records one end-to-end run produces + the two new state artifacts) and `ChainContractError`. **Not** a new
contract / schema / `*_version` — it introduces no persisted format; the persisted artifacts are the
existing [[Runtime Ledger Schema]] (SCHEMA-013) + [[Portfolio State Schema]] (SCHEMA-015).

## Purpose

Give the chain a single typed return value and a deterministic, JSON-stable `to_dict()` projection over all
five records + the two ending state hashes — the byte-identical replay vehicle for BENCH-006 and the
determinism tests. `execution_record` is `None` when the verdict is not ADMIT.

## Architecture Role

The output contract-as-value of [[Chain Orchestrator]] (MOD-010). Aggregates `FeatureVector`,
`RegimeClassification`, `GoldDecisionPacket`, `RuntimeDecisionRecord`, `ExecutionRecord | None`,
`RuntimeLedger`, `PortfolioState` — all already-governed types, never re-derived.

## Constraints

- Frozen dataclass, zero runtime deps (ADR-003); no new persisted `*_version`.
- `to_dict()` rounds feature values at the codebase's 6-dp convention for byte-stability.

## Implementation Notes

`_feature_vector_dict` provides the deterministic projection for `FeatureVector` (which has no `to_dict`);
the other four records expose their own `to_dict` / `state_hash`. `ChainContractError` is raised by the
engine when an ADMIT lacks an in-hand `gold_price`.

## Relationships

### Depends On
- [[Chain Orchestrator]]

### Validated By
- [[test_chain_engine]]
