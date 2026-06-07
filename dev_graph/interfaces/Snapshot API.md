---
type: interface
canonical_id: INT-001
status: active
implementation_status: implemented
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
  - "snapshot_sources/query_db.py"
related_files:
  - "[[consumer.py]]"
related_tests:
  - "[[test_consumer]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
interface_id: "snapshot-api"
interface_version: "0.1.0"
parent_capability: "[[Snapshot Assembly]]"
input_schema: null
output_schema: "[[Layer 2 Snapshot Schema]]"
implemented_by:
  - "[[Snapshot Consumer]]"
stability: evolving
---

# Snapshot API

## Definition

The boundary contract by which Layer 3 obtains the Layer-2 truth snapshot. This is the INT-001 interface reserved by Population Strategy §4.6 (Data Pipeline → Trading Engine). Its shape and access rules are taken directly from the Layer-2 publisher (`snapshot_sources/snapshot_publisher.py`) and DB inspector (`snapshot_sources/query_db.py`).

## Purpose

Makes the Layer 2 → Layer 3 boundary an explicit, versioned, read-only contract. It is the *only* sanctioned way Layer 3 sees market truth — Layer 3 never reaches behind it into raw observations.

## Architecture Role

Output interface of the Snapshot Assembly capability (CAP-003), produced by the external Layer-2 publisher. The Layer-3 consumer side is implemented by the Snapshot Consumer (MOD-003). Output schema: Layer 2 Snapshot Schema (SCHEMA-001). It has no request schema — it is a read/pull contract, so `input_schema` is null.

## Contract

Two access modes (publisher docstring):

1. **Latest** — read `latest_snapshot.json` (the most recently published snapshot). Implemented this slice by `consumer.load_snapshot()` / `consumer.consume()`.
2. **By id / point-in-time** — query the `snapshots` (+ `snapshot_values`) table by `snapshot_id` (for replay and counterfactuals). Mirrored by `query_db.py --snapshot-detail`. **Deferred** — not implemented in this slice (no execution/replay path yet).

Hard rules (fail-closed, from the publisher's Layer-3 contract):

- Layer 3 **MUST NOT** read observations directly — only snapshots.
- If **no snapshot exists** or the **quality gate failed** → Layer 3 outputs nothing.
- A snapshot is consumable only when `verdict == "PASS"` **and** `guards.snapshot_ok` **and** not `forced` **and** not `dry_run` (see `consumer.is_consumable`).

## Error Modes

- No snapshot file → `consume()` returns `None` (legitimate "no truth yet").
- Failed gate / forced / dry-run → `consume()` returns `None` (outputs nothing).
- Structurally malformed payload → raises `SnapshotContractError` (loud — an upstream truth-layer fault is never masked as absence).

## Stability

`evolving` / `interface_version: 0.1.0` — the latest-file read mode is implemented and tested against the real artifact; the by-`snapshot_id` DB query mode is specified but deferred, so the contract may extend (not break) when replay lands.

## Open Questions

- The by-`snapshot_id` query path (mode 2) needs the Layer-2 SQLite DB (`layer2_truth.db`) to be reachable from Layer 3, or a query API — out of this slice.
- CAP-003 Snapshot Assembly currently describes the Layer-2 *producer* role; the implemented MOD-003 is the Layer-3 *consumer*. This producer/consumer seam is a re-grounding item (possible CAP split) for the generic→Ripley ADR.

## Relationships

### Produces
- [[Layer 2 Snapshot Schema]]

### Implemented By
- [[Snapshot Consumer]]

### Validated By
- [[test_consumer]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Layer 2 Design Principles]]
