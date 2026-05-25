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
