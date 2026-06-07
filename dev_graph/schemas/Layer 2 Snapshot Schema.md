---
type: artifact_schema
canonical_id: SCHEMA-001
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
  - "snapshot_sources/latest_snapshot.json"
related_files:
  - "[[models.py (snapshot)]]"
related_tests:
  - "[[test_models (snapshot)]]"
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
schema_id: "layer2-snapshot"
schema_version: "3.3.0"
schema_path: "src/snapshot/snapshot_consumer/models.py"
validated_by:
  - "[[test_models (snapshot)]]"
consumed_by:
  - "[[Snapshot Consumer]]"
produced_by: []
---

# Layer 2 Snapshot Schema

## Definition

The foundational data contract of the whole system: the deterministic, versioned, self-contained analytical assessment the Layer-2 engine (Mr. Ripley) publishes for Layer-3 consumption. This is the SCHEMA-001 reserved by Population Strategy §4.6, grounded against the **real** published artifact (`snapshot_sources/latest_snapshot.json`) and its publisher (`snapshot_sources/snapshot_publisher.py`), not inferred from architecture prose.

## Purpose

Gives every downstream stage one canonical input shape — the boundary object between Layer 2 (Truth) and Layer 3 (Decision/Execution). Everything downstream (features, regime, decision, risk validation, execution) consumes this snapshot and nothing else. Its `snapshot_id` is a deterministic identity, which is what makes replay and counterfactual evaluation possible.

## Architecture Role

Output of the Layer-2 publisher (external to this repo); input of the Snapshot API (INT-001); consumed by the Snapshot Consumer (MOD-003). Produced by the Snapshot Assembly capability (CAP-003) on the Layer-2 side.

## Schema Definition

Top-level keys of the published JSON payload (21 keys):

| Field | Type | Notes |
|-------|------|-------|
| snapshot_id | string | 64-char SHA-256 deterministic identity hash (see Identity below) |
| engine_version | string | e.g. `gold-v3.3.0` — every snapshot is version-locked |
| config_version | string | series-registry version, e.g. `1.1.0` |
| clock_ts | string (ISO-8601 tz) | point-in-time clock boundary |
| clock_date | string (YYYY-MM-DD) | date form of `clock_ts` |
| verdict | string | `PASS` \| `FAIL` (quality gate result) |
| forced | bool | gate bypassed (testing only) — fail-closed: not consumable |
| dry_run | bool | preview; not normally written to JSON |
| guards | object | gate flags (see below) |
| revision_policy | object | `method`, `revision_writer`, `revision_risk_blocks_snapshot` |
| revision_risk_summary | object | `series_count`, `series[]` |
| tier1_series | map<series_id, obj> | convenience map (no tier/as_of/revision_seq) |
| tier2_series | map<series_id, obj> | convenience map |
| missing_series | array<string> | series excluded from the snapshot |
| layer1_events | array | penalty-only Layer-1 events (empty today; non-directional) |
| run_ts / published_at | string (ISO) | publication wall-clock |
| series_count | int | number of series in `values` |
| quality_summary | object | tier1/tier2 pass/warn/fail counts + revision-risk list |
| values_by_group | map<group, array<SeriesValue>> | **full-fidelity** per-series list |
| values | map<series_id, SeriesValue-lite> | per-series map (no `group`) |

**SeriesValue** (full fidelity, from `values_by_group`): `series_id`, `tier` (1\|2), `group`, `obs_ts`, `value` (number), `staleness_days` (int), `source`, `as_of_ts` (ISO\|null), `revision_seq` (int), `revision_risk` (bool).

**guards**: `snapshot_ok` (binding quality verdict), `data_ok`, `freshness_ok`, `missing_tier1`, `forced`, `revision_risk_present`, `idempotent_ok`, `reason_code`, plus the Layer-3 stubs `cooldown_ok`, `risk_ok`, `supervisor_veto` (defaulted by Layer-2; filled by the Risk Desk / Supervisor downstream).

## Identity (deterministic)

`snapshot_id = SHA-256` over, in order:
```
clock_ts=<iso>
engine_version=<str>
config_version=<str>
<series_id>=<obs_ts>:<value:.6f>:<as_of_ts>:<revision_seq>   # sorted by series_id
```
joined by `\n`, trailing `\n`. **Verified**: `models.py::Snapshot.recompute_id()` reproduces the stored id of the real artifact exactly (`952cc83a…afaef`) — this is the SCHEMA-001 grounding anchor (`test_models (snapshot)`).

## Validation Rules

- Required top-level keys (consumer-enforced): `snapshot_id`, `engine_version`, `config_version`, `clock_ts`, `clock_date`, `verdict`, `guards` (with `snapshot_ok`), `values_by_group`.
- `values_by_group` entries are full-fidelity; the consumer parses these (not the lossy `values`/`tierN_series` maps).
- Temporal independence: a snapshot MUST NOT reference any prior snapshot.
- Assembly is deterministic — identical inputs produce an identical `snapshot_id`.
- Schema changes are breaking and require an ADR.

## Open Questions

- This minimal slice models the consumer-relevant subset (identity, versions, clock, verdict, guards, quality_summary, missing_series, values). `revision_policy`, `revision_risk_summary`, `tier1_series`/`tier2_series`, `values_by_group` raw, `layer1_events`, `run_ts`/`published_at` are carried in the payload but not yet typed — promote them when a downstream stage needs them.
- `schema_version` tracks the engine version (`gold-v3.3.0` → `3.3.0`); confirm the registry/engine versioning policy when the by-`snapshot_id` DB query path (INT-001 mode 2) is implemented.

## Relationships

### Produces

### Consumed By
- [[Snapshot Consumer]]
- [[Snapshot API]]

### Validated By
- [[test_models (snapshot)]]

### Used By
- [[models.py (snapshot)]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Layer 2 Design Principles]]
