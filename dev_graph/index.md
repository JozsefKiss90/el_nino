# Dev Graph Index

Last updated: 2026-06-06

## Architecture

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[architecture/Context Map]] | ARCH-001 | architecture | Formal bounded context diagram — 6 systems and interactions |
| [[architecture/Runtime Topology]] | ARCH-002 | architecture | Runtime component interaction model — events, data flows |
| [[architecture/Layer Model]] | ARCH-003 | architecture | L1 (data) → L2 (analysis) → L3 (execution) layer definitions |
| [[architecture/Infrastructure Diagram]] | ARCH-004 | architecture | Full infrastructure Mermaid diagram (migrated from root) |

## Systems

(Empty — populated in Phase 2)

## Capabilities

(Empty — populated in Phase 3)

## Knowledge Assets

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Event Sourcing]] | KA-001 | knowledge_asset | State as immutable event sequence — motivates event-driven architecture |
| [[CQRS]] | KA-002 | knowledge_asset | Read/write model separation — motivates snapshot layer design |
| [[Supervisor Pattern Methodology]] | KA-003 | knowledge_asset | Meta-agent governance — motivates Supervisor Office |
| [[Office Action Methodology]] | KA-004 | knowledge_asset | Deterministic intervention state machine |
| [[Guardrail Philosophy]] | KA-005 | knowledge_asset | Hard constraints before autonomy — motivates Risk Control |
| [[Layer 2 Design Principles]] | KA-006 | knowledge_asset | Snapshot-as-truth-layer — foundational data contract |
| [[Context Engineering]] | KA-007 | knowledge_asset | Tokens as finite resource — motivates context assembly |
| [[Agent Safety Principles]] | KA-008 | knowledge_asset | Multi-layer safety — credential isolation, phased autonomy |
| [[Stateless Agent Architecture]] | KA-009 | knowledge_asset | Wake-Execute-Sleep — file-mediated agent continuity |
| [[Paper Trading Validation]] | KA-010 | knowledge_asset | Mandatory simulated validation before live deployment |

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
| ~~[[Infrastructure Diagram]]~~ | REF-004 | reference | DEPRECATED — migrated to architecture/Infrastructure Diagram (ARCH-004) |

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

- **Total content nodes**: 34 (architecture: 4, knowledge_asset: 10, governance: 7, reference: 3+1 deprecated, observability: 1, context_pack: 1, decision_record: 2, constraint: 3, api_doc_source: 2)
- **Structural files**: 4 (CLAUDE.md, index.md, log.md, README.md)
- **Total files**: 38
- **Active directories**: 23
- **Populated directories**: 10 (architecture, knowledge_assets, governance, constraints, decisions, api_docs, observability, context_packs + root)
- **Empty directories**: 15 (systems, capabilities, patterns, interfaces, events, modules, files, tests, gates, predicates, schemas, workflows, agents, skills, benchmarks)
- **Frontmatter coverage**: 34/34 content nodes (100%)
- **Canonical ID coverage**: 34/34 content nodes (100%)
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
- **Phase 1 completion date**: 2026-06-06
