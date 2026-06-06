---
type: governance
canonical_id: GOV-006
status: planned
implementation_status: not-started
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: inferred
evidence:
  - design
source_paths: []
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Database MCP Mapping

## Definition

Defines how dev_graph metadata maps to PostgreSQL tables for future structured queries via the postgres MCP server.

## Purpose

Enables SQL-based queries for implementation tracking, benchmark analysis, and validation records that benefit from relational data operations (aggregation, joins, time-series analysis).

## Architecture Role

Export bridge between the markdown-based dev_graph and the PostgreSQL database (`layer_3_wiki` on `localhost:5432`). Complements Dataview for heavy analytical queries.

## Table Definitions

### Table: `dev_nodes`

Primary table for all dev_graph nodes.

```sql
CREATE TABLE dev_nodes (
  id            SERIAL PRIMARY KEY,
  name          TEXT NOT NULL UNIQUE,
  type          TEXT NOT NULL,
  status        TEXT NOT NULL,
  impl_status   TEXT NOT NULL,
  canonical     BOOLEAN NOT NULL DEFAULT true,
  created       DATE NOT NULL,
  updated       DATE NOT NULL,
  confidence    TEXT NOT NULL,
  file_path     TEXT,
  description   TEXT
);

CREATE INDEX idx_dev_nodes_type ON dev_nodes(type);
CREATE INDEX idx_dev_nodes_status ON dev_nodes(status);
CREATE INDEX idx_dev_nodes_impl ON dev_nodes(impl_status);
```

### Table: `dev_relationships`

Typed edges between nodes.

```sql
CREATE TABLE dev_relationships (
  id                SERIAL PRIMARY KEY,
  source_node_id    INTEGER REFERENCES dev_nodes(id),
  target_node_id    INTEGER REFERENCES dev_nodes(id),
  relationship_type TEXT NOT NULL,
  created           DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_dev_rel_source ON dev_relationships(source_node_id);
CREATE INDEX idx_dev_rel_target ON dev_relationships(target_node_id);
CREATE INDEX idx_dev_rel_type ON dev_relationships(relationship_type);
```

### Table: `dev_benchmarks`

Benchmark and validation results.

```sql
CREATE TABLE dev_benchmarks (
  id              SERIAL PRIMARY KEY,
  node_id         INTEGER REFERENCES dev_nodes(id),
  benchmark_type  TEXT NOT NULL,
  metric_name     TEXT NOT NULL,
  metric_value    NUMERIC,
  unit            TEXT,
  run_date        TIMESTAMP NOT NULL DEFAULT NOW(),
  run_context     TEXT
);

CREATE INDEX idx_dev_bench_node ON dev_benchmarks(node_id);
CREATE INDEX idx_dev_bench_date ON dev_benchmarks(run_date);
```

### Table: `dev_context_packs`

Implementation task records linked to context packs.

```sql
CREATE TABLE dev_context_packs (
  id              SERIAL PRIMARY KEY,
  task_id         TEXT NOT NULL,
  task_type       TEXT NOT NULL,
  created         TIMESTAMP NOT NULL DEFAULT NOW(),
  completed       TIMESTAMP,
  node_count      INTEGER,
  admissible_count INTEGER,
  outcome         TEXT
);
```

## Relationship Type Enum

```sql
CREATE TYPE relationship_type AS ENUM (
  'DEPENDS_ON', 'PROVIDES', 'VALIDATED_BY', 'CONSTRAINED_BY',
  'SUPERSEDES', 'USED_BY', 'PRODUCES', 'CONSUMES',
  'RELATES_TO_FILE', 'RELATES_TO_TEST', 'DECIDED_BY', 'SOURCED_FROM',
  'COVERS'
);
```

## Query Patterns

```sql
-- Which files must change for a given module?
SELECT dn.name, dn.file_path
FROM dev_nodes dn
JOIN dev_relationships dr ON dr.target_node_id = dn.id
WHERE dr.source_node_id = (SELECT id FROM dev_nodes WHERE name = 'ModuleName')
AND dr.relationship_type IN ('RELATES_TO_FILE', 'PROVIDES')
AND dn.type = 'file';

-- Which constraints apply to a module?
SELECT c.name, c.description
FROM dev_nodes c
JOIN dev_relationships dr ON dr.target_node_id = c.id
WHERE dr.source_node_id = (SELECT id FROM dev_nodes WHERE name = 'ModuleName')
AND dr.relationship_type = 'CONSTRAINED_BY';

-- Implementation status distribution
SELECT impl_status, COUNT(*) FROM dev_nodes GROUP BY impl_status;
```

## Sync Procedure

1. Parse dev_graph markdown files
2. Upsert into `dev_nodes` (match on `name`)
3. Rebuild `dev_relationships` from frontmatter arrays and relationship sections
4. Append to `dev_benchmarks` from benchmark_result nodes
5. Append to `dev_context_packs` from context_pack nodes

## Relationships

### Depends On
- [[Dev Graph Governance]]

### Provides
- PostgreSQL schema for dev_graph analytics

### Validated By

### Constrained By

### Supersedes

### Used By

### Produces
- PostgreSQL tables populated from dev_graph

### Consumes
- Dev_graph markdown nodes
