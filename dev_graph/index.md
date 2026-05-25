# Dev Graph Index

Last updated: 2026-05-25

## Governance

| Node | Type | Summary |
|------|------|---------|
| [[Dev Graph Governance]] | governance | Root governance node for dev_graph |
| [[Context Pack Assembly Rules]] | governance | 8-step context pack assembly sequence |
| [[Admissibility Checks]] | governance | 9 validation checks for context pack inclusion |
| [[MCP Tooling Policy]] | governance | MCP operation safety classifications |
| [[Neo4j Export Mapping]] | governance | Note-to-node, frontmatter-to-property mapping |
| [[Database MCP Mapping]] | governance | Postgres table definitions for future integration |
| [[API Documentation Policy]] | governance | Permitted doc sources, freshness, retrieval rules |
| [[REF - Wiki CLAUDE.md]] | reference | Reference to wiki governance operations manual |
| [[REF - Wiki Metadata Migration Plan]] | reference | Reference to wiki schema design patterns |
| [[REF - Wiki Graph Health Dashboard]] | reference | Reference to wiki Dataview query patterns |

## Observability

| Node | Type | Summary |
|------|------|---------|
| [[Dev Graph Dashboard]] | observability | 12 Dataview queries for dev_graph health |

## Context Packs

| Node | Type | Summary |
|------|------|---------|
| [[Context Pack Template]] | context_pack | Canonical template for context pack creation |

## Decisions

| Node | Type | Summary |
|------|------|---------|
| [[ADR - Dev Graph Bootstrap]] | decision_record | Bootstrap decision — why dev_graph exists |

## Constraints

| Node | Type | Summary |
|------|------|---------|
| [[No Wiki Mutation]] | constraint | MUST NOT modify wiki/** or raw/** |
| [[Frontmatter Required]] | constraint | Every content node must have valid frontmatter |
| [[Canonical Ownership]] | constraint | One implementation concept = one canonical node |

## API Documentation Sources

| Node | Type | Summary |
|------|------|---------|
| [[Alpaca API Docs]] | api_doc_source | Alpaca trading API v2 documentation |
| [[Anthropic API Docs]] | api_doc_source | Anthropic/Claude API and SDK documentation |

## Modules

(Empty — populated when code modules are defined)

## Files

(Empty — populated when source files are tracked)

## Tests

(Empty — populated when test files are tracked)

## Gates

(Empty — populated when CI/CD gates are defined)

## Predicates

(Empty — populated when boolean predicates are defined)

## Schemas

(Empty — populated when artifact schemas are defined)

## Workflows

(Empty — populated when development workflows are defined)

## Agents

(Empty — populated when agent implementations exist)

## Skills

(Empty — populated when agent skills are defined)

## Benchmarks

(Empty — populated when benchmarks are recorded)

---

## Statistics

- **Total content nodes**: 18 (governance: 7, reference: 3, observability: 1, context_pack: 1, decision_record: 1, constraint: 3, api_doc_source: 2)
- **Structural files**: 4 (CLAUDE.md, index.md, log.md, README.md)
- **Total files**: 22
- **Active directories**: 16
- **Empty directories**: 10 (modules, files, tests, gates, predicates, schemas, workflows, agents, skills, benchmarks)
- **Frontmatter coverage**: 18/18 content nodes (100%)
- **Type enum**: 17 values
- **Status enum**: 7 values
- **Implementation status enum**: 7 values
- **Confidence enum**: 4 values
- **Bootstrap date**: 2026-05-25
