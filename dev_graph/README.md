# Dev Graph

Ontology-governed implementation graph for the Layer 3 Wiki autonomous trading engine ecosystem.

## What Is This?

The dev_graph is a typed knowledge graph of implementation artifacts — modules, files, tests, constraints, gates, predicates, schemas, and workflows. It serves as a RAG / Graph-RAG substrate for Claude Code sessions building the trading engine.

This is not ordinary top-k chunk RAG. This is a typed, governed context-pack system where:
- Semantic retrieval proposes context
- Dataview/frontmatter determines whether context is admissible
- Graph traversal determines dependencies and constraints
- Codebase MCPs determine current implementation truth
- Docs MCPs determine permitted API documentation
- The final coding context is explicit, typed, and validated

## How Does It Relate to ./wiki/?

| Layer | Purpose | Schema | Owner |
|-------|---------|--------|-------|
| `./raw/` | Immutable source documents | None | Human |
| `./wiki/` | Persistent synthesis knowledge base | `wiki/CLAUDE.md` | Claude (knowledge) |
| `./dev_graph/` | Implementation graph for coding | `dev_graph/CLAUDE.md` | Claude (code) |

The wiki answers "what do we know?" The dev_graph answers:
- Which files must change?
- Which tests must be added or updated?
- Which constraints must not be violated?
- Which design notes are canonical?
- Which API documentation sources are permitted?
- Which gates or predicates must pass?
- Which artifact schemas constrain the implementation?
- Which modules depend on the change?

## Quick Start

1. Read `CLAUDE.md` — operations manual
2. Read `index.md` — what exists
3. Read `governance/Dev Graph Governance.md` — governance rules
4. Read `decisions/ADR - Dev Graph Bootstrap.md` — why this exists

## Architecture

```
Claude / IDE Agent
  -> MCP tools (mcpvault, smart-connections, Dataview)
    -> dev_graph (this graph)
      -> Codebase MCPs (filesystem, Git, GitHub, SQLite/Postgres, Neo4j, Context7)
        -> Typed context packs for coding tasks
          -> Claude Code implementation
```

## MCP Access

- **mcpvault**: Read/write dev_graph notes
- **smart-connections**: Semantic search across dev_graph
- **Dataview**: Metadata queries via frontmatter
- **Future**: neo4j (graph traversal), postgres (analytics), context7 (API docs)

## Directory Structure

| Directory | Contents | Node Type |
|-----------|----------|-----------|
| `/governance` | Policies, reference nodes | governance, reference |
| `/observability` | Dashboards | observability |
| `/context_packs` | Context pack templates and instances | context_pack |
| `/decisions` | Architecture Decision Records | decision_record |
| `/constraints` | Hard invariant rules | constraint |
| `/api_docs` | Permitted API documentation sources | api_doc_source |
| `/modules` | Code module boundaries | module |
| `/files` | Source file nodes | file |
| `/tests` | Test file nodes | test |
| `/gates` | CI/CD quality gates | gate |
| `/predicates` | Boolean conditions | predicate |
| `/schemas` | Artifact schemas | artifact_schema |
| `/workflows` | Development workflows | workflow |
| `/agents` | Agent specifications | agent |
| `/skills` | Agent capabilities | skill |
| `/benchmarks` | Performance benchmarks | benchmark_result |
