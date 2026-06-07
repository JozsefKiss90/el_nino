---
type: decision_record
canonical_id: ADR-005
status: active
implementation_status: implemented
canonical: true
created: 2026-06-07
updated: 2026-06-07
confidence: confirmed
evidence:
  - design
  - code
  - layer2
source_paths:
  - "snapshot_sources/latest_snapshot.json"
  - "ultimateplan.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Implementation Substrate]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
decision_id: "ADR-005"
decision_date: 2026-06-07
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Feature Layer Contract

## Status

Active — enacted 2026-06-07 alongside the MOD-004 Feature Builder implementation slice.

## Context

The data path is `SCHEMA-001 → MOD-003 Snapshot Consumer → (features) → future Gold DecisionPacket v0`. [[ADR - Decision Layer Re-grounding]] (ADR-004) established that the gold decision branch must depend **only** on deterministic features derived from SCHEMA-001 and explicitly versioned upstream artifacts — never raw payloads or implicit state — so that replay and counterfactual evaluation are exact. Before any gold decision contract can be authored, that feature layer must exist and its determinism rules must be governed of record. This ADR is that governance.

## Decision

The **Feature Layer** is introduced as a deterministic, snapshot-local transform. The [[Feature Builder]] (MOD-004) realizes it under the following binding rules.

### 1. Deterministic feature eligibility
A feature is admissible only if it is a **pure function of a single Layer-2 snapshot's series values** (and the versioned feature-schema definition). Allowed classes:
- **levels** — a direct series read (`DFII10`)
- **spreads** — `a − b` (`DGS10 − DGS2`)
- **ratios** — `a / b`
- **arithmetic combinations** of the above
- **direct transforms** (sign, abs, clip to declared bounds)

### 2. Forbidden feature classes (hard)
Moving averages, momentum / rate-of-change, rolling windows, z-scores, percentiles, temporal smoothing (EWMA), look-ahead / future-bar features, inferred regimes, and learned embeddings. **Rationale:** a Layer-2 snapshot is *temporally independent* (no reference to any prior snapshot), so any feature requiring history or cross-snapshot state cannot be computed deterministically here. Such features belong to a later, explicitly stateful node with its own ADR.

### 3. Provenance requirements
Every emitted feature MUST carry: its input `series_ids`, `max_staleness_days` (the max over its inputs), and `revision_risk` (the OR over its inputs). Both are read directly from SCHEMA-001 per-series fields — no inference. This keeps stale/revisable inputs (e.g. Tier-2 monthly inflation series) honestly flagged downstream.

### 4. Replay / counterfactual determinism rule
**Same `snapshot_id` + same `schema_version` ⇒ byte-identical feature output.** The feature registry and `schema_version` are fixed in code; the output is a total pure function of `snapshot.values`. No clock, no randomness, no environment reads.

### 5. Input boundary
The Feature Builder consumes **only validated `Snapshot` objects produced by MOD-003 Snapshot Consumer** — never raw JSON, never a file path, never raw Layer-2 observations, never an external API. Ingestion + the fail-closed quality gate are MOD-003's responsibility; MOD-004 assumes an already-consumed (PASS) snapshot and only transforms it.

### 6. Relationship to ADR-004
This ADR operationalizes ADR-004's determinism invariant for the feature layer. The feature vector (SCHEMA-009) is the "deterministic SCHEMA-001-derived features" that ADR-004 requires before a Gold DecisionPacket v0 may be authored.

## Alternatives Considered

- **Stateful/normalized features now** (z-scores, momentum). **Rejected** — needs history a snapshot does not carry; would break replay determinism.
- **Feature Builder reads `latest_snapshot.json` itself.** **Rejected** — duplicates MOD-003 and bypasses its fail-closed gate; violates the single-ingestion-boundary design.
- **Hard-fail on any missing series.** **Softened** — a missing input marks that single feature *unavailable* (recorded in `unavailable_features`) rather than aborting the whole vector; the snapshot itself is already gated upstream.

## Consequences

### Positive
- Replay-safe, counterfactual-safe feature layer; exact-arithmetic testable against the real fixture.
- Clean separation: MOD-003 ingests/gates, MOD-004 transforms.
- Provenance flags surface stale/revisable inputs to any future consumer.

### Negative / Trade-offs
- The feature set is intentionally minimal (levels/spreads only); richer signals wait for a governed stateful layer.

### Risks
- Temptation to add history-dependent features into MOD-004 — guarded by the forbidden-classes list and this ADR.

## Relationships

### Constrains
- [[Feature Builder]]
- [[Feature Vector Schema]]

### Depends On
- [[Layer 2 Snapshot Schema]]
- [[Snapshot Consumer]]

### Constrained By
- [[Canonical Ownership]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]

### Originates From
- [[Layer 2 Design Principles]]
