# Dev Graph Index

Last updated: 2026-06-06

## Architecture

(Empty — populated in Phase 1)

## Systems

(Empty — populated in Phase 2)

## Capabilities

(Empty — populated in Phase 3)

## Knowledge Assets

(Empty — populated in Phase 1)

## Patterns

(Empty — populated in Phase 3)

## Interfaces

(Empty — populated in Phase 4)

## Events

(Empty — populated in Phase 7)

## Governance

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Dev Graph Governance]] | GOV-001 | governance | Root governance node for dev_graph |
| [[Context Pack Assembly Rules]] | GOV-002 | governance | Context pack assembly sequence with intent-aware routing |
| [[Admissibility Checks]] | GOV-003 | governance | 9 validation checks for context pack inclusion |
| [[MCP Tooling Policy]] | GOV-004 | governance | MCP operation safety classifications |
| [[Neo4j Export Mapping]] | GOV-005 | governance | Note-to-node mapping with canonical_id as primary key |
| [[Database MCP Mapping]] | GOV-006 | governance | Postgres table definitions for future integration |
| [[API Documentation Policy]] | GOV-007 | governance | Permitted doc sources, freshness, retrieval rules |
| [[REF - Wiki CLAUDE]] | REF-001 | reference | Reference to wiki governance operations manual |
| [[REF - Wiki Metadata Migration Plan]] | REF-002 | reference | Reference to wiki schema design patterns |
| [[REF - Wiki Graph Health Dashboard]] | REF-003 | reference | Reference to wiki Dataview query patterns |
| [[Infrastructure Diagram]] | REF-004 | reference | Full infrastructure Mermaid diagram (migrates to architecture/ in Phase 1) |

## Observability

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Dev Graph Dashboard]] | OBS-001 | observability | 20 Dataview queries for dev_graph health |

## Context Packs

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Context Pack Template]] | CTX-001 | context_pack | Canonical template for context pack creation |

## Decisions

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[ADR - Dev Graph Bootstrap]] | ADR-001 | decision_record | Bootstrap decision — why dev_graph exists |
| [[ADR - Ontology Redesign]] | ADR-002 | decision_record | Ontology redesign — 24-type hierarchy with canonical_id |

## Constraints

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[No Wiki Mutation]] | CON-001 | constraint | MUST NOT modify wiki/** or raw/** |
| [[Frontmatter Required]] | CON-002 | constraint | Every content node must have valid frontmatter |
| [[Canonical Ownership]] | CON-003 | constraint | One implementation concept = one canonical node |

## API Documentation Sources

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Alpaca API Docs]] | API-001 | api_doc_source | Alpaca trading API v2 documentation |
| [[Anthropic API Docs]] | API-002 | api_doc_source | Anthropic/Claude API and SDK documentation |

## Modules

(Empty — populated in Phase 5 when code modules are defined)

## Files

(Empty — populated in Phase 5 when source files are tracked)

## Tests

(Empty — populated in Phase 5 when test files are tracked)

## Gates

(Empty — populated in Phase 6 when quality gates are defined)

## Predicates

(Empty — populated in Phase 6 when boolean predicates are defined)

## Schemas

(Empty — populated in Phase 4 when artifact schemas are defined)

## Workflows

(Empty — populated in Phase 6 when workflows are defined)

## Agents

(Empty — populated in Phase 5 when agent implementations exist)

## Skills

(Empty — populated in Phase 5 when agent skills are defined)

## Benchmarks

(Empty — populated in Phase 8 when benchmarks are recorded)

---

## Statistics

- **Total content nodes**: 20 (governance: 7, reference: 4, observability: 1, context_pack: 1, decision_record: 2, constraint: 3, api_doc_source: 2)
- **Structural files**: 4 (CLAUDE.md, index.md, log.md, README.md)
- **Total files**: 24
- **Active directories**: 23
- **Empty directories**: 17 (architecture, systems, capabilities, knowledge_assets, patterns, interfaces, events, modules, files, tests, gates, predicates, schemas, workflows, agents, skills, benchmarks)
- **Frontmatter coverage**: 20/20 content nodes (100%)
- **Canonical ID coverage**: 20/20 content nodes (100%)
- **Schema version**: 2.2.0
- **Type enum**: 24 values
- **Relationship types**: 17
- **Status enum**: 7 values
- **Implementation status enum**: 7 values
- **Confidence enum**: 5 values
- **Evidence enum**: 7 values
- **Lint checks**: 11
- **Dashboard queries**: 20
- **Bootstrap date**: 2026-05-25
- **Ontology redesign date**: 2026-06-06
