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

---

## [2026-06-06] populate | Phase 1: Architecture Skeleton + Knowledge Foundations

### Nodes Created (14)

**Architecture nodes (4)**:
- Context Map (ARCH-001) — formal bounded context diagram, 6 systems, 8 interfaces
- Runtime Topology (ARCH-002) — runtime event/data flow model, 12 domain events, scheduling
- Layer Model (ARCH-003) — L1 (data) → L2 (analysis) → L3 (execution) with snapshot-as-truth contract
- Infrastructure Diagram (ARCH-004) — migrated from root-level REF-004, retyped reference → architecture

**Knowledge asset nodes (10)**:
- Event Sourcing (KA-001) — immutable event sequences, replay, audit trails
- CQRS (KA-002) — read/write model separation, snapshot layer design
- Supervisor Pattern Methodology (KA-003) — meta-agent governance, treasury constraints, institutional memory
- Office Action Methodology (KA-004) — deterministic state machine interventions, integration checkpoints
- Guardrail Philosophy (KA-005) — hard constraints before autonomy, non-negotiable limits
- Layer 2 Design Principles (KA-006) — snapshot-as-truth-layer, deterministic assembly, schema stability
- Context Engineering (KA-007) — tokens as money, structured retrieval, budget management
- Agent Safety Principles (KA-008) — credential isolation, self-verification, phased autonomy
- Stateless Agent Architecture (KA-009) — Wake-Execute-Sleep, file-based personality, git persistence
- Paper Trading Validation (KA-010) — mandatory simulated validation, quantitative promotion criteria

### Nodes Deprecated (1)

- Infrastructure Diagram (REF-004) at dev_graph root → deprecated, replaced by ARCH-004 in architecture/

### Source Wiki Pages Referenced

Architecture Overview, Trading Engine Pipeline, Three-Layer Trading System, Claude-Assisted Trading Stack, Syndicate Squad Architecture, Guardrail Architecture, Autonomous Trading Risk Model, Agent Memory Architecture, Context Budget Engineering, Office Action Loop, Paper Trading, Stateless Agent Recovery, Agent Self-Verification, Trade Logging, Treasury Policy System, Multi-Agent Orchestration, API Credential Isolation, Walk-Forward Optimization, MCP Architecture

### Phase 1 Metrics

- Total content nodes: 34 (20 from Phase 0 + 14 new)
- Active nodes: 33 (1 deprecated: REF-004)
- Architecture nodes: 4
- Knowledge asset nodes: 10
- Canonical ID coverage: 34/34 (100%)
- Evidence field coverage: 34/34 (100%)
- Wiki pages referenced via source_paths: 19
- Populated directories: 10 / 23
- Empty directories: 15 (awaiting Phase 2+)
- Population roadmap target: 30-32 nodes. Actual: 34 (on track)

---

## [2026-06-06] populate | Phase 2: System Boundaries

### Nodes Created (7)

**System nodes (6)**:
- Data Pipeline (SYS-001) — market data ingestion, feature engineering, snapshot assembly (L1+L2)
- Trading Engine (SYS-002) — signal generation, order management, stop-loss, position tracking (L3)
- Risk Control (SYS-003) — guardrail enforcement, exposure tracking, circuit breaking
- Agent Runtime (SYS-004) — state persistence, context assembly, trade logging
- Evaluation Loop (SYS-005) — performance scoring, promotion validation, lifecycle management
- Supervisor Office (SYS-006) — decision making, treasury management, upgrade evaluation, orchestration

**Workflow nodes (1)**:
- System Lifecycle (WF-001) — 9-state lifecycle: Cold → Initialized → PaperTrading → Validated → Candidate → Production → Paused → Emergency → Archived

### Relationship Summary

All 6 system nodes include:
- `contains_capabilities` forward references to Phase 3 capability nodes
- `upstream_systems` / `downstream_systems` defining inter-system data flow
- `Originates From` edges to knowledge assets established in Phase 1
- `source_paths` referencing wiki pages for domain knowledge context

System dependency graph:
```
Data Pipeline → Trading Engine ↔ Risk Control
                Trading Engine → Agent Runtime
                Agent Runtime → Evaluation Loop → Supervisor Office → Trading Engine
```

### Phase 2 Metrics

- Total content nodes: 41 (34 from Phase 1 + 7 new)
- Active nodes: 40 (1 deprecated: REF-004)
- System nodes: 6
- Workflow nodes: 1
- Populated directories: 12 / 23
- Empty directories: 13
- Population roadmap target: 38-40 nodes. Actual: 41 (on track)
- Knowledge-to-system traceability: all 6 systems link to knowledge assets via Originates From

---

## [2026-06-06] populate | Phase 3: Capabilities + Patterns

### Nodes Created (28)

**Capability nodes (18)**:

Data Pipeline (3):
- Market Scanning (CAP-001) — realizes Pipeline Pattern
- Feature Engineering (CAP-002) — realizes Pipeline Pattern
- Snapshot Assembly (CAP-003) — realizes CQRS Pattern; originates from Layer 2 Design Principles

Trading Engine (4):
- Signal Generation (CAP-004) — realizes Pipeline Pattern, Event Sourcing Pattern
- Order Management (CAP-005) — realizes Pipeline Pattern, Guardrail Pattern
- Stop-Loss Management (CAP-006) — realizes Guardrail Pattern
- Position Tracking (CAP-007) — realizes Event Sourcing Pattern

Risk Control (2):
- Guardrail Enforcement (CAP-008) — realizes Guardrail Pattern; originates from Guardrail Philosophy
- Exposure Tracking (CAP-009) — realizes Guardrail Pattern

Agent Runtime (3):
- State Persistence (CAP-010) — realizes Context Assembly Pattern; originates from Stateless Agent Architecture
- Context Assembly (CAP-011) — realizes Context Assembly Pattern; originates from Context Engineering
- Trade Logging (CAP-012) — realizes Event Sourcing Pattern

Evaluation Loop (2):
- Performance Scoring (CAP-013) — realizes Evaluation Loop Pattern
- Promotion Validation (CAP-014) — realizes Promotion Pattern, Guardrail Pattern; originates from Paper Trading Validation

Supervisor Office (4):
- Decision Making (CAP-015) — realizes Supervisor Pattern; originates from Supervisor Pattern Methodology
- Treasury Management (CAP-016) — realizes Treasury Approval Pattern; originates from Supervisor Pattern Methodology
- Upgrade Evaluation (CAP-017) — realizes Evaluation Loop Pattern
- Team Orchestration (CAP-018) — realizes Multi-Agent Coordination Pattern; originates from Supervisor Pattern Methodology

**Pattern nodes (10)**:
- Supervisor Pattern (PAT-001) — coordination; composes Multi-Agent Coordination + Treasury Approval
- Guardrail Pattern (PAT-002) — governance; 4 realizing capabilities
- Evaluation Loop Pattern (PAT-003) — behavioral; 2 realizing capabilities
- Pipeline Pattern (PAT-004) — structural; 4 realizing capabilities
- Event Sourcing Pattern (PAT-005) — behavioral; 2 realizing capabilities
- Context Assembly Pattern (PAT-006) — structural; 2 realizing capabilities
- Treasury Approval Pattern (PAT-007) — governance; 1 realizing capability
- Promotion Pattern (PAT-008) — governance; 1 realizing capability
- CQRS Pattern (PAT-009) — structural; 1 realizing capability
- Multi-Agent Coordination Pattern (PAT-010) — coordination; 1 realizing capability

### Edge Summary

- Realizes edges: 23 (capabilities → patterns)
- Composes edges: 2 (Supervisor Pattern → Multi-Agent Coordination, Treasury Approval)
- Originates From edges: 12 (capabilities/systems → knowledge assets)
- All capabilities reference parent_system
- All patterns reference related_knowledge

### Phase 3 Metrics

- Total content nodes: 69 (41 from Phase 2 + 28 new)
- Active nodes: 68 (1 deprecated: REF-004)
- Capability nodes: 18 (3+4+2+3+2+4 across 6 systems)
- Pattern nodes: 10 (3 structural + 3 governance + 2 behavioral + 2 coordination)
- Pattern realization coverage: 18/18 capabilities have at least one realizes edge (100%)
- Populated directories: 14 / 23
- Empty directories: 11
- Population roadmap target: 68-72 nodes. Actual: 69 (on target)
- Structural skeleton complete: Architecture → Systems → Capabilities fully populated
