---
type: module
canonical_id: MOD-003
status: active
implementation_status: tested
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - layer2
  - code
  - design
source_paths:
  - "snapshot_sources/snapshot_publisher.py"
related_files:
  - "[[models.py (snapshot)]]"
  - "[[consumer.py]]"
related_tests:
  - "[[test_models (snapshot)]]"
  - "[[test_consumer]]"
related_constraints: []
related_decisions:
  - "[[ADR - Implementation Substrate]]"
  - "[[ADR - Ontology Redesign]]"
module_name: "snapshot_consumer"
module_path: "src/snapshot/snapshot_consumer"
responsibility: "Read the Layer-2 truth snapshot and fail-closed gate it for Layer-3 consumption"
depends_on: []
provides:
  - "[[Snapshot API]]"
---

# Snapshot Consumer

## Definition

The Layer-3 ingestion boundary: the module that reads the Layer-2 truth snapshot (SCHEMA-001) via the Snapshot API (INT-001) and decides whether Layer 3 may act on it. It is the first stage of the Layer-3 data path (`Layer 2 Snapshot → [Snapshot Consumer] → features/decision → …`).

## Purpose

Concentrate the Layer 2 → Layer 3 trust boundary in one fail-closed place, so no downstream stage ever has to re-implement "is this snapshot safe to use?". Implements the publisher's hard contract: Layer 3 never reads observations directly; absent snapshot or failed gate ⇒ Layer 3 outputs nothing.

## Architecture Role

Consumer side of the Snapshot API (INT-001). Reads SCHEMA-001. Output is a validated `Snapshot` object (or nothing). Zero runtime dependencies (ADR-003): stdlib `json` + frozen dataclasses.

## Inputs

- `latest_snapshot.json` (mode 1), or a snapshot JSON path. The by-`snapshot_id` DB query (mode 2) is deferred.

## Outputs

- A consumable `Snapshot` (frozen dataclass), or `None` ("output nothing").
- `SnapshotContractError` on a structurally malformed payload.

## Constraints

- **Fail-closed**: consumable only if `verdict == "PASS"` ∧ `guards.snapshot_ok` ∧ ¬`forced` ∧ ¬`dry_run`.
- **No observation access**: the module reads snapshots only — never raw Layer-2 observations.
- **Loud on corruption**: a malformed snapshot raises; it is never silently downgraded to "no snapshot".
- **Integrity check available**: `Snapshot.recompute_id()` re-derives the deterministic id; equality with the published `snapshot_id` detects tampering.

## Implementation Notes

- `models.py` — SCHEMA-001 dataclasses (`Snapshot`, `SeriesValue`, `Guards`, `QualitySummary`) + `from_dict` parsers grounded in `values_by_group` (full fidelity) + `recompute_id()` mirroring the publisher's `compute_snapshot_id`.
- `consumer.py` — `load_snapshot()` (absent→None, malformed→raise), `is_consumable()` (the fail-closed predicate), `consume()` (the single Layer-3 entry point).
- Tests grounded against a verbatim copy of the real artifact plus derived FAIL/FORCED/dry-run fixtures. 16 tests; full suite 43 green.

## Open Questions

- Mode 2 (query by `snapshot_id` from `layer2_truth.db`) is unimplemented — needed for replay/counterfactual; depends on a Layer-2 DB reach or query API.
- Primary capability: this consumer sits behind CAP-003 Snapshot Assembly, but CAP-003 describes the Layer-2 *producer*. Whether to split CAP-003 (produce vs consume) or give ingestion its own capability is deferred to the generic→Ripley re-grounding ADR.

## Relationships

### Implements
- [[Snapshot API]]

### Consumes
- [[Layer 2 Snapshot Schema]]
- [[Snapshot API]]

### Provides
- [[Snapshot API]]

### Validated By
- [[test_models (snapshot)]]
- [[test_consumer]]

### Realizes
- [[CQRS Pattern]]
- [[Pipeline Pattern]]

### Justified By
- [[ADR - Implementation Substrate]]
- [[ADR - Ontology Redesign]]

### Originates From
- [[Layer 2 Design Principles]]
