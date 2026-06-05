# Dev Graph Operations Manual

This file governs all Claude Code sessions that operate on the dev_graph. Every session that modifies dev_graph MUST read this file first.

The dev_graph is an ontology-governed implementation graph — a typed RAG / Graph-RAG substrate for coding tasks. It complements the wiki knowledge graph (`wiki/`) with implementation artifacts.

**Critical constraint**: dev_graph sessions MUST NOT modify `wiki/**` or `raw/**`. See [[No Wiki Mutation]].

---

## Vault Structure

```
/dev_graph
  /modules         — logical code module boundaries
  /files           — individual source file nodes
  /tests           — test file and test suite nodes
  /gates           — CI/CD gates and quality checks
  /predicates      — boolean conditions that must hold
  /schemas         — artifact schemas (JSON, YAML, protobuf)
  /workflows       — multi-step development workflows
  /agents          — agent implementation specifications
  /skills          — agent skill and tool capabilities
  /decisions       — Architecture Decision Records (ADRs)
  /constraints     — hard invariants that must not be violated
  /api_docs        — permitted API documentation references
  /benchmarks      — performance and correctness benchmarks
  /context_packs   — pre-assembled context for Claude sessions
  /observability   — dashboards and monitoring
  /governance      — governance policies and reference nodes
```

---

## Naming Conventions

- **File names**: Title Case with spaces (e.g., `Trading Engine Module.md`)
- **Module nodes**: Named after the module concept (e.g., `Order Execution.md`)
- **File nodes**: Named to include file context (e.g., `order_executor.py.md`)
- **Test nodes**: Named to include test context (e.g., `test_order_executor.md`)
- **Constraint nodes**: Named as imperative rules (e.g., `No Wiki Mutation.md`)
- **Reference nodes**: Prefixed with `REF -` (e.g., `REF - Wiki CLAUDE`)
- **Decision records**: Prefixed with `ADR -` (e.g., `ADR - Dev Graph Bootstrap.md`)
- **Wikilinks**: Use `[[Page Name]]` format for all internal references

---

## Canonical Ownership Rules

1. Each implementation concept has ONE canonical node in dev_graph
2. Before creating a new node, search existing nodes for the same concept
3. If a concept is already covered, UPDATE the existing node
4. Other nodes reference the canonical node via `[[wikilink]]`
5. Never duplicate a definition — link instead
6. See [[Canonical Ownership]] constraint

---

## Node Template

Every dev_graph content node MUST contain these sections (omit only if genuinely not applicable):

```markdown
# {Node Title}

## Definition
## Purpose
## Architecture Role
## Inputs (or Dependencies)
## Outputs (or Provides)
## Constraints
## Implementation Notes
## Open Questions

## Relationships

### Depends On
### Provides
### Validated By
### Constrained By
### Supersedes
### Used By
### Produces
### Consumes
```

The `## Relationships` section with its subsections is REQUIRED for Neo4j export readiness. Use `[[wikilinks]]` in relationship subsections.

---

## Frontmatter Governance

### Universal Schema (All Content Nodes)

Every dev_graph node (except structural files: CLAUDE.md, index.md, log.md, README.md) MUST have:

```yaml
---
type: <type_enum>
status: <status_enum>
implementation_status: <impl_status_enum>
canonical: true
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: <confidence_enum>
source_paths: []
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
---
```

### Allowed Enums

**`type` (17 values)**:
`module`, `file`, `test`, `gate`, `predicate`, `artifact_schema`, `workflow`, `agent`, `skill`, `decision_record`, `constraint`, `api_doc_source`, `benchmark_result`, `context_pack`, `governance`, `observability`, `reference`

**`status` (7 values)**:
`active`, `planned`, `implemented`, `validated`, `deprecated`, `blocked`, `draft`

**`implementation_status` (7 values)**:
`not-started`, `in-progress`, `implemented`, `tested`, `validated`, `deprecated`, `blocked`

**`confidence` (4 values)**:
`confirmed`, `single-source`, `inferred`, `speculative`

### Domain-Specific Extensions

**Module nodes** add:
```yaml
module_name: <string>
module_path: <path>
responsibility: <short string>
depends_on: []
provides: []
```

**File nodes** add:
```yaml
file_path: <path>
language: <string>
module: <wikilink or name>
owns: []
used_by: []
```

**Test nodes** add:
```yaml
test_path: <path>
test_type: unit|integration|e2e|regression|benchmark
covers: []
required_for: []
```

**Gate nodes** add:
```yaml
gate_id: <string>
gate_scope: <string>
required_artifacts: []
blocking: true
```

**Predicate nodes** add:
```yaml
predicate_id: <string>
predicate_scope: <string>
implemented_in: <path>
validated_by: []
```

**Artifact schema nodes** add:
```yaml
schema_id: <string>
schema_path: <path>
validated_by: []
consumed_by: []
produced_by: []
```

**API doc source nodes** add:
```yaml
provider: <string>
doc_source: <string>
doc_scope: <string>
allowed_for_tasks: []
freshness_requirement: current|required|stable
```

**Decision record nodes** add:
```yaml
decision_id: <string>
decision_date: YYYY-MM-DD
supersedes: []
superseded_by: []
decision_status: active|superseded|deprecated
```

**Context pack nodes** add:
```yaml
task_id: <string>
task_type: implementation|refactor|validation|debugging|migration
required_nodes: []
required_files: []
required_tests: []
required_docs: []
admissibility_checked: true|false
```

### Schema Validation Rules

1. `type` must be from the closed type enum — no freeform values
2. `status` must be from the closed status enum
3. `implementation_status` must be from the closed implementation_status enum
4. `confidence` must be from the closed confidence enum
5. `created` is set once at node creation and NEVER modified
6. `updated` is refreshed ONLY on substantive content edits
7. No frontmatter keys beyond those defined in this file
8. Flat YAML only — no nested objects
9. Type-to-directory binding: a node's `type` should match its directory

### Anti-Entropy Rules

1. No freeform frontmatter fields — every key must be defined above
2. No nested YAML objects — flat key-value pairs and scalar arrays only
3. No duplicate semantics — do not create fields that overlap existing fields
4. No metadata without content — frontmatter must reflect actual node content

---

## Cross-Linking Protocol

- Every **module** MUST link to its file nodes and constraints
- Every **file** MUST link to its parent module and test nodes
- Every **test** MUST link to what it covers (files or modules)
- Every **gate** MUST link to its predicate nodes
- Every **decision** MUST link to what it constrains or enables
- Every **context pack** MUST list all required nodes
- Every node MUST have >=1 outbound wikilink (no orphans)
- Hub nodes (governance, constraints) should have 5+ inbound links

---

## Context Pack Assembly Protocol

See [[Context Pack Assembly Rules]] for the full 8-step assembly sequence.

Summary:
1. Parse task request
2. Semantic retrieval via Smart Connections
3. Dataview filtering (canonical, status, type, implementation_status)
4. Graph expansion (dependencies, files, tests, constraints, decisions)
5. Codebase grounding via filesystem/Git MCP
6. Docs retrieval via context7 per [[API Documentation Policy]]
7. Admissibility check (9 checks from [[Admissibility Checks]])
8. Assemble typed context pack using [[Context Pack Template]]

---

## Admissibility Rules

Before a node can be used in a coding context pack, it must pass all 9 checks:

1. `canonical: true`
2. `status` is not `deprecated`
3. `implementation_status` is not `deprecated`
4. `type` is in the allowed enum
5. Required frontmatter fields exist
6. Source paths exist or are explicitly marked external
7. No unresolved contradiction affecting the task
8. No more recent decision record supersedes it
9. Relevant tests or validation gates identified (for module/file nodes)

If any check fails, the node is listed under "Deprecated / Excluded Notes" but NOT used as authoritative context.

---

## Retrieval Pipeline

Future coding tasks should use this sequence:

1. Parse task request
2. Smart Connections retrieves semantically related dev_graph nodes
3. Dataview/frontmatter filters by: canonical, type, status, implementation_status, confidence
4. Obsidian Vault MCP reads the selected canonical nodes
5. Neo4j or graph traversal expands: dependencies, files, tests, constraints, decisions, schemas, gates
6. Filesystem/Git MCP inspects current code truth
7. Context7/docs MCP retrieves only permitted API documentation
8. Assemble typed context pack
9. Claude Code implements
10. Tests/validation run
11. Write implementation results back to dev_graph

---

## MCP Operations

See [[MCP Tooling Policy]] for the full classification.

Summary:
- **Safe-automated**: All read operations (mcpvault, smart-connections, context7, neo4j read, postgres read)
- **Constrained-automated**: New dev_graph node creation (with governance), frontmatter lint corrections, link additions
- **Human-review-required**: Overwriting existing nodes, moving nodes, neo4j/postgres writes
- **Prohibited**: Deleting nodes, writing to wiki/** from dev_graph sessions

---

## Dataview Governance

All Dataview queries in dev_graph MUST:
1. Scope to `FROM "dev_graph"` to exclude wiki and raw sources
2. Filter `WHERE type != null` to exclude structural files
3. Handle missing fields gracefully (null-safe comparisons)
4. Use `SORT updated DESC` as default unless specific sort applies

Dashboard: [[Dev Graph Dashboard]] is the single consolidated observability page.

---

## Lint Workflow

Run during every session that modifies dev_graph:

### Check 1: Missing Frontmatter
```
Dataview: LIST FROM "dev_graph" WHERE type = null
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE" AND file.name != "README"
```
Action: Add universal frontmatter to listed nodes.

### Check 2: Invalid Enum Values
Verify all enum fields contain values from allowed sets.
Action: Correct to nearest valid enum.

### Check 3: Orphan Node Detection
Find nodes with 0 inbound links (excluding structural files).
Action: Add wikilinks from related nodes.

### Check 4: Stale Node Detection
```
Dataview: LIST FROM "dev_graph" WHERE date(updated) < date(today) - dur(30 days) AND status != "deprecated"
```
Action: Review and update or set `status: deprecated`.

### Check 5: Broken Wikilinks
Find `[[wikilinks]]` pointing to nonexistent nodes.
Action: Create missing nodes or fix links.

### Check 6: Constraint Coverage
Check that module/file nodes have `related_constraints` populated.
Action: Add relevant constraint references.

### Check 7: Test Coverage
Check that module/file nodes have `related_tests` populated or explicit justification.
Action: Add test references or document why tests are not needed.

---

## Maintenance Cadences

| Cadence | Scope | Trigger |
|---------|-------|---------|
| Per-session | Lint checks 1-7 on touched nodes, update log.md | Every session modifying dev_graph |
| Weekly | Full lint across all nodes, dashboard review | Every 7 days |
| Monthly | Ontology audit, API doc freshness check, constraint review | First session of month |

---

## Schema Evolution

Adapted from wiki governance principles:

1. **Append-only enums**: Values are never renamed or removed. New values appended via governance update.
2. **Additive fields**: New fields may be added. Existing fields are never renamed or removed.
3. **Governance-first**: Every schema change documented in this file BEFORE being applied.
4. **No silent evolution**: Schema changes not in this file are schema drift (prohibited).
5. **Backward compatibility**: All Dataview queries on [[Dev Graph Dashboard]] must continue to work.

### Enum Append Procedure
1. Justify: why existing values are insufficient
2. Verify no semantic overlap with existing values
3. Update this file's Allowed Enums section
4. Log: `## [DATE] schema | Enum extension: <field>.<value>` in log.md

### Field Addition Procedure
1. Justify: why existing fields are insufficient
2. Define: field name, data type, allowed values, default
3. Update this file's Frontmatter Governance section
4. Roll out to affected nodes
5. Log: `## [DATE] schema | Field addition: <field_name>` in log.md

---

## Confidence Lifecycle

Same as wiki governance:

| From | To | Trigger |
|---|---|---|
| `speculative` | `inferred` | Logical derivation from confirmed facts |
| `inferred` | `single-source` | Source document directly supports claims |
| `single-source` | `confirmed` | Second independent source corroborates |
| `confirmed` | `single-source` | One source retracted or unreliable |
| `single-source` | `inferred` | Supporting source deprecated |
| `inferred` | `speculative` | Reasoning chain found weak |
| Any | `speculative` | Contradiction detected |

Promotion updates both `confidence` and `updated` fields.
Demotion MUST be logged in `log.md`.

---

## Relationship to Wiki

- dev_graph INHERITS governance principles from `wiki/CLAUDE.md` via [[REF - Wiki CLAUDE]]
- dev_graph has its OWN type ontology (17 types) separate from wiki's 17 types
- dev_graph has its OWN frontmatter schema (extended with implementation_status and relationship arrays)
- dev_graph may READ wiki nodes for domain knowledge (safe-automated)
- dev_graph MUST NOT WRITE to wiki nodes (prohibited — see [[No Wiki Mutation]])
- Cross-references use standard wikilinks: `[[wiki/Page Name]]` format

---

## Structural Files

These files have NO frontmatter (exempt by governance):
- `CLAUDE.md` — this operations manual
- `index.md` — master index of all nodes
- `log.md` — chronological operations log
- `README.md` — human-readable orientation
