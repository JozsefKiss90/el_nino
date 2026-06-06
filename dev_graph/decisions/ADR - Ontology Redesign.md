---
type: decision_record
canonical_id: ADR-002
status: active
implementation_status: in-progress
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - ADR
source_paths:
  - "audit_plan.md"
  - "audit_plan_addendum.md"
  - "final_strategic_review.md"
  - "population_strategy.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
decision_id: "ADR-002"
decision_date: 2026-06-06
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Ontology Redesign

## Status

Active — Phase 0 (governance foundation) in progress.

## Context

The dev_graph was bootstrapped (ADR-001) with a flat 17-type ontology containing 19 content nodes — governance, constraints, references, and API doc sources. No hierarchy, no system boundaries, no interface contracts, no capabilities, no runtime events. The flat model would collapse at 100+ nodes due to poor Graph-RAG retrieval, no containment structure, and tight wiki coupling.

Four design review documents established the target ontology:

1. **Dev Graph Ontology Redesign** (audit_plan.md) — introduced Architecture → System → Capability → Module → File hierarchy, 5 new types (system, capability, architecture, interface, event), 5 new relationships (Contains, Implements, Emits, Triggered By, Guards). Total: 22 types, 13 relationships.

2. **Architecture Review Addendum** (audit_plan_addendum.md) — introduced knowledge_asset and pattern types, 3 traceability relationships (originates_from, justified_by, realizes), evidence field, experimental confidence value, intent-aware Graph-RAG routing. Total: 24 types, 16 relationships.

3. **Final Strategic Ontology Review** (final_strategic_review.md) — introduced canonical_id universal field, schema_version tracking, Composes relationship, type-aware stale thresholds, 4 new lint checks, merge/split/deprecation procedures, closed-loop engineering continuum, three-layer digital twin architecture. Total: 24 types, 17 relationships.

4. **Population Strategy** (population_strategy.md) — defined population principles, triggers, phased roadmap, wiki migration mapping, code-driven population, maintenance cadences, governance KPIs, stopping rules.

## Decision

Redesign the dev_graph ontology from a flat 17-type model to a hierarchical 24-type Engineering Digital Twin with:

- **24 types** organized into structural (architecture, system, capability), implementation (module, interface, file, test), behavioral (workflow, event), data (artifact_schema), quality (gate, predicate), agent (agent, skill), knowledge (knowledge_asset, pattern), and meta (decision_record, constraint, governance, reference, api_doc_source, context_pack, observability, benchmark_result) categories.
- **17 relationship types** covering structural (Contains, Implements), existing (Depends On, Provides, Validated By, Constrained By, Supersedes, Used By, Produces, Consumes), behavioral (Emits, Triggered By, Guards), traceability (Originates From, Justified By, Realizes), and composition (Composes).
- **canonical_id** as a universal stable identifier surviving renames.
- **evidence** as a universal provenance field.
- **Closed-loop continuum** as the conceptual backbone.
- **Intent-aware routing** with 11-entry routing table.
- **Type-aware stale thresholds** replacing the uniform 30-day check.
- **11 lint checks** (7 existing + 4 new).
- **Schema version 2.2.0** tracked in CLAUDE.md.

## Alternatives Considered

### Alternative 1: Incremental type additions without hierarchy

**Rejected.** Adding types without containment hierarchy creates a wider flat graph, not a navigable one. Graph-RAG precision requires hierarchy for scope filtering.

### Alternative 2: Full Engineering Digital Twin with runtime instances

**Deferred.** Runtime instances (individual trades, evaluations) belong in PostgreSQL, not Obsidian. The ontology defines TYPES that runtime instances conform to; the database stores the instances.

### Alternative 3: Fewer types (merge knowledge_asset into reference, merge pattern into governance)

**Rejected.** Knowledge assets and patterns serve distinct engineering purposes. Knowledge assets answer "why does this architecture exist?" — references answer "where is the external source?" Patterns answer "what reusable structure does this follow?" — governance answers "what rules must be obeyed?" Merging them would create semantic confusion.

## Consequences

### Positive

- Hierarchical navigation from architecture through implementation to verification
- Full traceability from knowledge origins through decisions to code
- Stable identity via canonical_id enables Neo4j export and cross-system reference
- Intent-aware retrieval improves precision for non-implementation tasks
- Type-aware staleness reduces governance noise for stable node types
- Closed-loop continuum enables regression tracing and evolution planning

### Negative

- 24 types and 17 relationships approach the complexity ceiling for a single operations manual
- Existing 19 nodes must be migrated to add canonical_id and evidence fields
- Larger CLAUDE.md requires more context for each session

### Risks

- If the codebase remains small, the ontology may be over-engineered for the actual need
- Maintenance burden increases with node count — mitigated by type-aware thresholds and just-in-time population

## Relationships

### Depends On

### Provides
- Complete ontology schema for all dev_graph operations

### Validated By

### Constrained By
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]

### Supersedes

### Used By
- All future dev_graph content nodes
- All future context pack assembly

### Produces

### Consumes

### Originates From

### Justified By
- [[ADR - Dev Graph Bootstrap]]
