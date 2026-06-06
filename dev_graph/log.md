# Dev Graph Log

Chronological record of dev_graph operations. Each entry uses format: `## [DATE] operation | details`

---

## [2026-05-25] init | Dev graph bootstrap

### Created

**Directory structure** (16 subdirectories):
modules, files, tests, gates, predicates, schemas, workflows, agents, skills, decisions, constraints, api_docs, benchmarks, context_packs, observability, governance

**Structural files** (4, no frontmatter):
- CLAUDE.md — operations manual (~400 lines)
- index.md — master index
- log.md — this file
- README.md — orientation document

**Constraint nodes** (3):
- No Wiki Mutation — MUST NOT modify wiki/** or raw/**
- Frontmatter Required — every content node needs valid frontmatter
- Canonical Ownership — one concept = one node

**Decision records** (1):
- ADR - Dev Graph Bootstrap — why dev_graph exists, alternatives considered

**Governance documents** (7):
- Dev Graph Governance — root governance node
- Context Pack Assembly Rules — 8-step assembly sequence
- Admissibility Checks — 9 validation checks
- MCP Tooling Policy — operation safety classifications
- Neo4j Export Mapping — graph export schema
- Database MCP Mapping — Postgres table definitions
- API Documentation Policy — doc source governance

**Reference nodes** (3):
- REF - Wiki CLAUDE.md — links to wiki governance source
- REF - Wiki Metadata Migration Plan — links to schema design source
- REF - Wiki Graph Health Dashboard — links to Dataview pattern source

**API doc source nodes** (2):
- Alpaca API Docs — Alpaca trading API v2
- Anthropic API Docs — Anthropic/Claude API and SDK

**Observability** (1):
- Dev Graph Dashboard — 12 Dataview queries

**Context pack templates** (1):
- Context Pack Template — canonical template for context packs

### Architecture Decisions

- Separate type ontology from wiki (17 dev_graph types vs 17 wiki types)
- Universal frontmatter with implementation_status and relationship arrays
- No placeholder module/file/test nodes (create when code exists)
- Reference nodes link to wiki governance for inheritance
- Context pack template ready for first coding session
- Relationship sections on every node for Neo4j export readiness

### Bootstrap Metrics

- Total content nodes: 18
- Structural files: 4
- Total files: 22
- Frontmatter coverage: 18/18 (100%)
- Active directories: 16
- Empty directories awaiting code: 10
- Type enum values: 17
- Status enum values: 7
- Implementation status enum values: 7
- Confidence enum values: 4
- Dataview dashboard queries: 12

---

## [2026-06-06] schema | Phase 0: Ontology Redesign — Governance Foundation

### Schema Changes (v1.0.0 → v2.2.0)

**Type enum**: 17 → 24 values. Added: `architecture`, `system`, `capability`, `interface`, `event`, `knowledge_asset`, `pattern`.

**Confidence enum**: 4 → 5 values. Added: `experimental`.

**Evidence field**: NEW universal field. Allowed values: `wiki`, `layer2`, `code`, `benchmark`, `ADR`, `external`, `design`.

**canonical_id field**: NEW universal field. Stable identifier per node (TYPE_PREFIX-NUMBER). Primary key for Neo4j export. Never changes on rename.

**Relationship types**: 8 → 17. Added: `Contains`, `Implements`, `Emits`, `Triggered By`, `Guards`, `Originates From`, `Justified By`, `Realizes`, `Composes`.

**Lint checks**: 7 → 11. Added: Check 8 (type-content alignment), Check 9 (deprecated reference detection), Check 10 (canonical ID uniqueness), Check 11 (evidence-confidence coherence).

**Stale thresholds**: Uniform 30-day → type-aware (30-180 days).

**Dashboard queries**: 12 → 20. Added: #13-20 (canonical ID coverage, evidence coverage, pattern realization, traceability gaps, population progress, population debt x3).

### New Directories (7)

architecture/, systems/, capabilities/, interfaces/, events/, knowledge_assets/, patterns/

### Nodes Created (1)

- ADR - Ontology Redesign (ADR-002) — documents the redesign decision

### Nodes Updated (19)

All existing content nodes migrated to add `canonical_id` and `evidence` fields:
- CON-001: No Wiki Mutation
- CON-002: Frontmatter Required
- CON-003: Canonical Ownership
- ADR-001: ADR - Dev Graph Bootstrap
- GOV-001: Dev Graph Governance
- GOV-002: Context Pack Assembly Rules
- GOV-003: Admissibility Checks
- GOV-004: MCP Tooling Policy
- GOV-005: Neo4j Export Mapping
- GOV-006: Database MCP Mapping
- GOV-007: API Documentation Policy
- REF-001: REF - Wiki CLAUDE
- REF-002: REF - Wiki Metadata Migration Plan
- REF-003: REF - Wiki Graph Health Dashboard
- REF-004: Infrastructure Diagram
- API-001: Alpaca API Docs
- API-002: Anthropic API Docs
- OBS-001: Dev Graph Dashboard
- CTX-001: Context Pack Template

### Governance Updates

- CLAUDE.md: Complete rewrite (431 → ~580 lines) with v2.2.0 schema
- Neo4j Export Mapping: 7 new labels, 9 new edge types, canonical_id as primary key
- Dev Graph Dashboard: 8 new Dataview queries (#13-20)
- index.md: Updated with canonical_ids, new sections, updated statistics

### Phase 0 Metrics

- Total content nodes: 20 (19 migrated + 1 new ADR)
- Canonical ID coverage: 20/20 (100%)
- Evidence field coverage: 20/20 (100%)
- Schema version: 2.2.0
- Type enum values: 24
- Relationship types: 17
- Directories: 23 (16 existing + 7 new)
- Lint checks: 11
- Dashboard queries: 20

### Design Documents (frozen, not part of dev_graph)

- audit_plan.md — Ontology Redesign
- audit_plan_addendum.md — Architecture Review Addendum
- final_strategic_review.md — Final Strategic Ontology Review
- population_strategy.md — Population Strategy and Execution Roadmap
