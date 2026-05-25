---
type: governance
status: planned
implementation_status: not-started
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: inferred
source_paths: []
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Neo4j Export Mapping

## Definition

Defines how dev_graph markdown nodes map to Neo4j graph database entities for future graph traversal via the neo4j MCP server.

## Purpose

Enables typed graph queries (shortest path, dependency chains, impact analysis) that go beyond Dataview's capabilities. Neo4j complements Obsidian for complex traversal patterns.

## Architecture Role

Export bridge between the markdown-based dev_graph and the Neo4j graph database. Designed for future activation when the neo4j MCP server is connected to a populated database.

## Node Mapping

Each dev_graph markdown file maps to one Neo4j node.

| Markdown Element | Neo4j Element |
|---|---|
| File name (without .md) | Node `name` property |
| `type` frontmatter | Node label (e.g., `:Module`, `:File`, `:Test`) |
| All frontmatter fields | Node properties |
| `canonical` field | Node `canonical` property |
| `created` / `updated` | Node `created` / `updated` properties |

### Label Mapping

| `type` value | Neo4j Label |
|---|---|
| `module` | `:Module` |
| `file` | `:File` |
| `test` | `:Test` |
| `gate` | `:Gate` |
| `predicate` | `:Predicate` |
| `artifact_schema` | `:ArtifactSchema` |
| `workflow` | `:Workflow` |
| `agent` | `:Agent` |
| `skill` | `:Skill` |
| `decision_record` | `:DecisionRecord` |
| `constraint` | `:Constraint` |
| `api_doc_source` | `:ApiDocSource` |
| `benchmark_result` | `:BenchmarkResult` |
| `context_pack` | `:ContextPack` |
| `governance` | `:Governance` |
| `observability` | `:Observability` |
| `reference` | `:Reference` |

## Edge Mapping

Relationships are extracted from two sources:

### Source 1: Frontmatter Arrays

| Frontmatter Field | Edge Type | Direction |
|---|---|---|
| `related_files` | `RELATES_TO_FILE` | outbound |
| `related_tests` | `RELATES_TO_TEST` | outbound |
| `related_constraints` | `CONSTRAINED_BY` | outbound |
| `related_decisions` | `DECIDED_BY` | outbound |
| `source_paths` | `SOURCED_FROM` | outbound |
| `depends_on` (modules) | `DEPENDS_ON` | outbound |
| `provides` (modules) | `PROVIDES` | outbound |
| `covers` (tests) | `COVERS` | outbound |
| `supersedes` (decisions) | `SUPERSEDES` | outbound |

### Source 2: Relationship Sections (wikilinks)

| Section Heading | Edge Type | Direction |
|---|---|---|
| `### Depends On` | `DEPENDS_ON` | outbound |
| `### Provides` | `PROVIDES` | outbound |
| `### Validated By` | `VALIDATED_BY` | outbound |
| `### Constrained By` | `CONSTRAINED_BY` | outbound |
| `### Supersedes` | `SUPERSEDES` | outbound |
| `### Used By` | `USED_BY` | outbound |
| `### Produces` | `PRODUCES` | outbound |
| `### Consumes` | `CONSUMES` | outbound |

## Example Cypher

```cypher
// Create a module node
MERGE (m:Module {name: "Trading Engine"})
SET m.status = "active",
    m.implementation_status = "not-started",
    m.canonical = true,
    m.created = date("2026-05-25"),
    m.updated = date("2026-05-25"),
    m.confidence = "confirmed"

// Create a constraint relationship
MATCH (m:Module {name: "Trading Engine"})
MATCH (c:Constraint {name: "No Wiki Mutation"})
MERGE (m)-[:CONSTRAINED_BY]->(c)
```

## Export Procedure

1. Parse all dev_graph markdown files
2. Extract frontmatter as node properties
3. Create nodes with appropriate labels
4. Parse frontmatter arrays for relationship edges
5. Parse `## Relationships` sections for additional edges
6. MERGE (not CREATE) to support incremental updates
7. Validate edge targets exist before creating relationships

## Sync Cadence

- **On-demand**: After significant dev_graph changes
- **Weekly**: As part of weekly maintenance
- Not yet automated — requires export script development

## Relationships

### Depends On
- [[Dev Graph Governance]]

### Provides
- Neo4j export schema for dev_graph

### Validated By

### Constrained By

### Supersedes

### Used By

### Produces
- Neo4j graph database populated from dev_graph

### Consumes
- Dev_graph markdown nodes
