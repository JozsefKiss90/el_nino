---
type: architecture
canonical_id: ARCH-004
status: active
implementation_status: implemented
canonical: true
created: 2026-06-01
updated: 2026-06-15
confidence: confirmed
evidence:
  - design
source_paths:
  - "[[dev_graph/CLAUDE.md]]"
  - "[[wiki/CLAUDE.md]]"
related_files:
  - .mcp.json
  - neo4j.env
  - dev_graph/sync_to_neo4j.py
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Canonical Ownership]]"
  - "[[Frontmatter Required]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
  - "[[ADR - Ontology Redesign]]"
architecture_type: context_map
scope: "Full infrastructure topology — all substrates, MCP servers, databases, and data flows"
---

# Infrastructure Diagram

Mermaid diagram illustrating the project's full infrastructure, data flow, and dependencies. Migrated from dev_graph root to architecture/ during Phase 1 ontology redesign.

## Diagram

```mermaid
graph TB
    subgraph Sources["Raw Sources (raw/ - immutable)"]
        S1["build-spec.md"]
        S2["Claude for Financial Services.md"]
        S3["claude_stock_trader.md"]
        S4["claude_opus_trader.md"]
        S5["claude_tradingview.md"]
        S6["claude_cowork_trader.md"]
        S7["ows-dev-squad.md"]
        S8["calude_alpaca_trader.md"]
        S9["llm-wiki.md<br/>(methodology)"]
    end

    subgraph Wiki["Wiki Knowledge Graph (wiki/ - 57 pages, 852 wikilinks)"]
        W_CLAUDE["CLAUDE.md<br/>(877-line ops manual)"]
        W_INDEX["index.md"]
        W_LOG["log.md"]
        subgraph WikiDomains["20 Domain Directories"]
            WD1["agents/ (4)"]
            WD2["integrations/ (7)"]
            WD3["systems/ (6)"]
            WD4["strategies/ (5)"]
            WD5["infrastructure/ (4)"]
            WD6["sources/ (9)"]
            WD7["+ 14 more domains"]
        end
    end

    subgraph DevGraph["Dev Graph (dev_graph/ - 24-type ontology, schema v2.2.0)"]
        DG_CLAUDE["CLAUDE.md<br/>(~580-line ops manual)"]
        DG_INDEX["index.md"]
        subgraph DGContent["Content Nodes"]
            DG_ARCH["architecture/ (4)"]
            DG_KA["knowledge_assets/ (10)"]
            DG_GOV["governance/ (7)"]
            DG_REF["references (3)"]
            DG_CON["constraints/ (3)"]
            DG_API["api_docs/ (2)"]
            DG_ADR["decisions/ (2)"]
            DG_CTX["context_packs/ (1)"]
            DG_OBS["observability/ (1)"]
        end
        subgraph DGEmpty["Empty (awaiting Phase 2+)"]
            DG_E["systems, capabilities, patterns,<br/>interfaces, events, modules,<br/>files, tests, gates, predicates,<br/>schemas, workflows, agents,<br/>skills, benchmarks"]
        end
        SYNC["sync_to_neo4j.py<br/>(Python: yaml, neo4j driver)"]
    end

    subgraph Obsidian["Obsidian Vault (.obsidian/)"]
        OB_CORE["Core Plugins<br/>(graph, backlink, search,<br/>templates, properties)"]
        OB_DV["Dataview Plugin<br/>(YAML queries)"]
        OB_SC["Smart Connections Plugin<br/>(semantic search)"]
    end

    subgraph SmartEnv[".smart-env/ (9.5 MB)"]
        SE_EMB["Embedding Model<br/>TaylorAI/bge-micro-v2"]
        SE_VEC["101 .ajson vectors<br/>(block-level embeddings)"]
        SE_CTX["Context Templates<br/>(XML structured)"]
    end

    subgraph MCP["MCP Servers (.mcp.json - 5 servers)"]
        MCP_V["mcpvault<br/>(npx @bitbonsai/mcpvault)<br/>Vault read/write"]
        MCP_SC["smart-connections<br/>(npx @yejianye/smart-connections-mcp)<br/>Semantic retrieval"]
        MCP_C7["context7<br/>(HTTPS: mcp.context7.com)<br/>Library docs"]
        MCP_N4["neo4j<br/>(python neo4j_mcp_server)<br/>Graph queries"]
        MCP_PG["postgres<br/>(npx mcp-postgres-server)<br/>Relational queries"]
    end

    subgraph Databases["Databases (localhost)"]
        NEO4J["Neo4j<br/>bolt://localhost:7688<br/>APOC plugin<br/>(Graph-RAG)"]
        POSTGRES["PostgreSQL<br/>localhost:5432<br/>db: layer_3_wiki"]
    end

    subgraph Claude["Claude Code Session"]
        CC["Claude Opus 4.6"]
        SERENA["Serena<br/>(code navigation)"]
        PERMS["Permissions<br/>(42 allowlist entries)"]
        MEM["Auto-Memory<br/>(.claude/projects/)"]
    end

    %% Data Flow
    Sources -->|"ingestion<br/>(10-step workflow)"| Wiki
    Wiki -->|"reference nodes<br/>(REF - prefix)"| DevGraph
    DevGraph -->|"MUST NOT modify"| Wiki

    %% Obsidian renders both
    Wiki --- Obsidian
    DevGraph --- Obsidian
    OB_DV -->|"queries frontmatter"| Wiki
    OB_DV -->|"queries frontmatter"| DevGraph
    OB_SC -->|"indexes into"| SmartEnv

    %% Sync pipeline
    SYNC -->|"MERGE Cypher<br/>(17 rel types)"| NEO4J

    %% MCP connections
    MCP_V -->|"reads/writes"| Wiki
    MCP_V -->|"reads/writes"| DevGraph
    MCP_SC -->|"queries"| SmartEnv
    MCP_N4 -->|"read-only queries"| NEO4J
    MCP_PG -->|"read-only queries"| POSTGRES

    %% Claude uses MCPs
    CC -->|"tool calls"| MCP
    CC --- SERENA
    CC --- PERMS
    CC --- MEM

    %% External
    MCP_C7 -.->|"HTTPS"| EXT["External Docs<br/>(context7.com)"]

    %% Styling
    classDef source fill:#f9e2af,stroke:#f5c211,color:#000
    classDef wiki fill:#a6e3a1,stroke:#40a02b,color:#000
    classDef devgraph fill:#89b4fa,stroke:#1e66f5,color:#000
    classDef mcp fill:#cba6f7,stroke:#8839ef,color:#000
    classDef db fill:#f38ba8,stroke:#d20f39,color:#000
    classDef obsidian fill:#94e2d5,stroke:#179299,color:#000
    classDef claude fill:#fab387,stroke:#fe640b,color:#000

    class S1,S2,S3,S4,S5,S6,S7,S8,S9 source
    class W_CLAUDE,W_INDEX,W_LOG,WD1,WD2,WD3,WD4,WD5,WD6,WD7 wiki
    class DG_CLAUDE,DG_INDEX,DG_ARCH,DG_KA,DG_GOV,DG_REF,DG_CON,DG_API,DG_ADR,DG_CTX,DG_OBS,DG_E,SYNC devgraph
    class MCP_V,MCP_SC,MCP_C7,MCP_N4,MCP_PG mcp
    class NEO4J,POSTGRES db
    class OB_CORE,OB_DV,OB_SC,SE_EMB,SE_VEC,SE_CTX obsidian
    class CC,SERENA,PERMS,MEM claude
```

## Key Architecture Summary

| Layer | Component | Role |
|-------|-----------|------|
| **Knowledge** | `raw/` (9 docs) → `wiki/` (57 pages) | Immutable sources ingested into LLM-maintained wiki |
| **Implementation** | `dev_graph/` (24-type ontology, v2.2.0) | Engineering Digital Twin with canonical_id, evidence, 17 relationship types |
| **Semantic Index** | `.smart-env/` (101 vectors) | Block-level embeddings via TaylorAI/bge-micro-v2 |
| **Graph DB** | Neo4j (via `sync_to_neo4j.py`) | 17 relationship types, APOC plugin, Graph-RAG queries |
| **Relational DB** | PostgreSQL (`layer_3_wiki`) | Runtime instance data (trades, evaluations, telemetry) |
| **MCP Integration** | 5 servers | mcpvault, smart-connections, context7, neo4j, postgres |
| **Orchestration** | Claude Code + Serena | 42-permission allowlist, auto-memory, code navigation |

## Critical Constraint

Dev graph sessions are forbidden from modifying `wiki/` or `raw/` — enforced by the [[No Wiki Mutation]] constraint node.

## Relationships

### Depends On
- [[Context Map]] — bounded context diagram this infrastructure supports
- [[dev_graph/CLAUDE.md]] — governance rules that define the ontology

### Provides
- Visual overview of all infrastructure components and data flow
- Quick reference for onboarding new sessions

### Constrained By
- [[No Wiki Mutation]]
- [[Canonical Ownership]]
- [[Frontmatter Required]]

### Supersedes

### Used By
- [[Dev Graph Dashboard]]
- [[Context Pack Template]]
