# Dev Graph Operations Manual

schema_version: "2.2.0"

This file governs all Claude Code sessions that operate on the dev_graph. Every session that modifies dev_graph MUST read this file first.

The dev_graph is an ontology-governed Engineering Digital Twin — a typed Graph-RAG substrate for autonomous Claude-assisted software engineering. It complements the wiki knowledge graph (`wiki/`) with implementation artifacts, engineering knowledge, and architectural traceability.

**Critical constraint**: dev_graph sessions MUST NOT modify `wiki/**` or `raw/**`. See [[No Wiki Mutation]].

---

## Vault Structure

```
/dev_graph
  /architecture      — context maps, runtime topology, layer models
  /systems           — bounded contexts (major system boundaries)
  /capabilities      — abstract behaviors systems provide
  /interfaces        — API contracts between systems/modules
  /events            — domain events (boundary-crossing signals)
  /knowledge_assets  — foundational engineering knowledge and principles
  /patterns          — reusable architectural solutions
  /modules           — logical code module boundaries
  /files             — individual source file nodes
  /tests             — test file and test suite nodes
  /gates             — CI/CD gates and quality checks
  /predicates        — boolean conditions that must hold
  /schemas           — artifact schemas (JSON, YAML, protobuf)
  /workflows         — multi-step development workflows
  /agents            — agent implementation specifications
  /skills            — agent skill and tool capabilities
  /decisions         — Architecture Decision Records (ADRs)
  /constraints       — hard invariants that must not be violated
  /api_docs          — permitted API documentation references
  /benchmarks        — performance and correctness benchmarks
  /context_packs     — pre-assembled context for Claude sessions
  /observability     — dashboards and monitoring
  /governance        — governance policies and reference nodes
```

23 directories total. Type-to-directory binding: a node's `type` should match its directory.

---

## Object Hierarchy

The dev_graph models an explicit engineering hierarchy:

```
Knowledge Asset (WHY)
    ↓ originates_from
Architecture (WHAT shape) → System → Capability → Module → File
                                   → Interface → Schema
                                   → Workflow → Event
                                              → Gate → Predicate
Pattern (cross-cutting) ←── realizes ──→ Module/Capability
```

Conceptual backbone — the Closed-Loop Engineering Continuum:

```
KNOWLEDGE → DECISION → ARCHITECTURE → DESIGN → IMPLEMENTATION →
VERIFICATION → RUNTIME → EVALUATION → EVOLUTION → KNOWLEDGE
```

Each stage maps to ontology types:
- KNOWLEDGE: knowledge_asset
- DECISION: decision_record
- ARCHITECTURE: architecture, system, capability
- DESIGN: pattern, interface, artifact_schema
- IMPLEMENTATION: module, file
- VERIFICATION: test, gate, predicate
- RUNTIME: event, workflow
- EVALUATION: benchmark_result
- EVOLUTION: decision_record (new ADR — loop closes)

---

## Naming Conventions

- **File names**: Title Case with spaces (e.g., `Trading Engine Module.md`)
- **Module nodes**: Named after the module concept (e.g., `Order Execution.md`)
- **File nodes**: Named to include file context (e.g., `order_executor.py.md`)
- **Test nodes**: Named to include test context (e.g., `test_order_executor.md`)
- **Constraint nodes**: Named as imperative rules (e.g., `No Wiki Mutation.md`)
- **Reference nodes**: Prefixed with `REF -` (e.g., `REF - Wiki CLAUDE`)
- **Decision records**: Prefixed with `ADR -` (e.g., `ADR - Dev Graph Bootstrap.md`)
- **Knowledge assets**: Named after the engineering principle (e.g., `Event Sourcing.md`)
- **Patterns**: Named after the pattern (e.g., `Guardrail Pattern.md`)
- **Wikilinks**: Use `[[Page Name]]` format for all internal references

---

## Canonical Ownership Rules

1. Each implementation concept has ONE canonical node in dev_graph
2. Before creating a new node, search existing nodes for the same concept
3. If a concept is already covered, UPDATE the existing node
4. Other nodes reference the canonical node via `[[wikilink]]`
5. Never duplicate a definition — link instead
6. See [[Canonical Ownership]] constraint
7. Each system boundary has ONE canonical system node
8. Each capability is owned by exactly ONE system
9. Each module implements ONE primary capability
10. Wiki concepts are NEVER duplicated — dev_graph references wiki via source_paths

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
### Contains
### Implements
### Validated By
### Constrained By
### Supersedes
### Used By
### Produces
### Consumes
### Emits
### Triggered By
### Guards
### Originates From
### Justified By
### Realizes
### Composes
```

The `## Relationships` section with its subsections is REQUIRED for Neo4j export readiness. Use `[[wikilinks]]` in relationship subsections. Include only applicable subsections — omit empty ones.

---

## Frontmatter Governance

### Universal Schema (All Content Nodes)

Every dev_graph node (except structural files: CLAUDE.md, index.md, log.md, README.md) MUST have:

```yaml
---
type: <type_enum>
canonical_id: <TYPE_PREFIX-NUMBER>
status: <status_enum>
implementation_status: <impl_status_enum>
canonical: true
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: <confidence_enum>
evidence: []
source_paths: []
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
---
```

The `canonical_id` is assigned at creation and NEVER changes, even if the node is renamed or moved. It is globally unique within the dev_graph and serves as the primary key for Neo4j export.

### Canonical ID Prefixes

| Type | Prefix | Example |
|------|--------|---------|
| knowledge_asset | KA | KA-001 |
| pattern | PAT | PAT-001 |
| architecture | ARCH | ARCH-001 |
| system | SYS | SYS-001 |
| capability | CAP | CAP-001 |
| interface | INT | INT-001 |
| event | EVT | EVT-001 |
| module | MOD | MOD-001 |
| file | FILE | FILE-001 |
| test | TEST | TEST-001 |
| workflow | WF | WF-001 |
| artifact_schema | SCHEMA | SCHEMA-001 |
| gate | GATE | GATE-001 |
| predicate | PRED | PRED-001 |
| agent | AGT | AGT-001 |
| skill | SKILL | SKILL-001 |
| decision_record | ADR | ADR-001 |
| constraint | CON | CON-001 |
| governance | GOV | GOV-001 |
| observability | OBS | OBS-001 |
| reference | REF | REF-001 |
| api_doc_source | API | API-001 |
| benchmark_result | BENCH | BENCH-001 |
| context_pack | CTX | CTX-001 |

### Allowed Enums

**`type` (24 values)**:
`architecture`, `system`, `capability`, `interface`, `event`, `knowledge_asset`, `pattern`, `module`, `file`, `test`, `gate`, `predicate`, `artifact_schema`, `workflow`, `agent`, `skill`, `decision_record`, `constraint`, `api_doc_source`, `benchmark_result`, `context_pack`, `governance`, `observability`, `reference`

**`status` (7 values)**:
`active`, `planned`, `implemented`, `validated`, `deprecated`, `blocked`, `draft`

**`implementation_status` (7 values)**:
`not-started`, `in-progress`, `implemented`, `tested`, `validated`, `deprecated`, `blocked`

**`confidence` (5 values)**:
`confirmed`, `single-source`, `inferred`, `speculative`, `experimental`

**`evidence` (7 allowed values — array field)**:
`wiki`, `layer2`, `code`, `benchmark`, `ADR`, `external`, `design`

### Domain-Specific Extensions

**Architecture nodes** add:
```yaml
architecture_type: context_map|runtime_topology|layer_model
scope: <string>
```

**System nodes** add:
```yaml
system_id: <string>
bounded_context: <string>
contains_capabilities: []
upstream_systems: []
downstream_systems: []
```

**Capability nodes** add:
```yaml
capability_id: <string>
parent_system: <wikilink>
implemented_by: []
interfaces: []
```

**Interface nodes** add:
```yaml
interface_id: <string>
interface_version: <semver>
parent_capability: <wikilink>
input_schema: <wikilink or null>
output_schema: <wikilink or null>
implemented_by: []
stability: stable|evolving|experimental
```

**Event nodes** add:
```yaml
event_id: <string>
emitted_by: <wikilink>
consumed_by: []
triggers: []
payload_schema: <wikilink or null>
```

**Knowledge asset nodes** add:
```yaml
knowledge_id: <string>
knowledge_type: principle|methodology|guidance|pattern_theory
source_wiki_pages: []
informs_decisions: []
informs_architecture: []
external_references: []
```

Note: Knowledge assets do NOT have `implementation_status` — they are conceptual foundations, never "implemented."

**Pattern nodes** add:
```yaml
pattern_id: <string>
pattern_type: structural|behavioral|governance|coordination
instances: []
realized_by_capabilities: []
realized_by_modules: []
related_knowledge: []
```

Note: Patterns do NOT have `implementation_status` — they are referenced, not implemented.

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
schema_version: <semver>
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

**Benchmark result nodes** add:
```yaml
measures: []
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
5. `evidence` values must be from the closed evidence enum
6. `canonical_id` must be unique across all nodes and follow the prefix convention
7. `created` is set once at node creation and NEVER modified
8. `updated` is refreshed ONLY on substantive content edits
9. No frontmatter keys beyond those defined in this file
10. Flat YAML only — no nested objects
11. Type-to-directory binding: a node's `type` should match its directory

### Anti-Entropy Rules

1. No freeform frontmatter fields — every key must be defined above
2. No nested YAML objects — flat key-value pairs and scalar arrays only
3. No duplicate semantics — do not create fields that overlap existing fields
4. No metadata without content — frontmatter must reflect actual node content

---

## Relationship Model

17 relationship types organized by category.

### Structural Relationships

| Relationship | Semantics | Example |
|-------------|-----------|---------|
| Contains | Hierarchical ownership (parent → child) | System → Capability, Capability → Module |
| Implements | Realization of abstract contract | Module → Interface, Agent → Capability |

### Existing Relationships (from v1.0.0)

| Relationship | Semantics | Example |
|-------------|-----------|---------|
| Depends On | Runtime or build dependency | Module A → Module B |
| Provides | What this node makes available | Module → Interface |
| Validated By | What tests/gates verify this | Module → Test, Capability → Gate |
| Constrained By | What invariants bind this | System → Constraint |
| Supersedes | Temporal replacement | ADR v2 → ADR v1 |
| Used By | Reverse dependency | Schema → Module |
| Produces | Output generation | Module → Schema, Module → Event |
| Consumes | Input consumption | Module → Schema, Module → Event |

### Behavioral Relationships

| Relationship | Semantics | Example |
|-------------|-----------|---------|
| Emits | Event production at runtime | Module → Event |
| Triggered By | Event consumption | Workflow → Event |
| Guards | Quality check on transition | Gate → Workflow, Predicate → Gate |

### Traceability Relationships

| Relationship | Semantics | Example |
|-------------|-----------|---------|
| Originates From | Conceptual foundation | ADR → Knowledge Asset |
| Justified By | Decision authorization | Module/Capability → ADR |
| Realizes | Pattern implementation | Module/Capability → Pattern |

### Composition Relationship

| Relationship | Semantics | Example |
|-------------|-----------|---------|
| Composes | Pattern structural composition | Supervisor Pattern → Multi-Agent Coordination |

---

## Cross-Linking Protocol

- Every **module** MUST link to its file nodes and constraints
- Every **file** MUST link to its parent module and test nodes
- Every **test** MUST link to what it covers (files or modules)
- Every **gate** MUST link to its predicate nodes
- Every **decision** MUST link to what it constrains or enables
- Every **context pack** MUST list all required nodes
- Every **capability** MUST reference its parent system
- Every **interface** MUST reference its parent capability
- Every **pattern** MUST reference at least 2 realizing modules/capabilities
- Every **knowledge asset** MUST reference at least 1 ADR it informs
- Every node MUST have >=1 outbound wikilink (no orphans)
- Hub nodes (architecture, system, governance) should have 5+ inbound links

---

## Context Pack Assembly Protocol

See [[Context Pack Assembly Rules]] for the full assembly sequence.

Summary:
1. Parse task request
1.5. **Intent Classification** — classify task intent to select entry point (see Routing Table below)
2. Semantic retrieval via Smart Connections
3. Dataview filtering (canonical, status, type, implementation_status)
4. Graph expansion (dependencies, files, tests, constraints, decisions)
5. Codebase grounding via filesystem/Git MCP
6. Docs retrieval via context7 per [[API Documentation Policy]]
7. Admissibility check (9 checks from [[Admissibility Checks]])
8. Assemble typed context pack using [[Context Pack Template]]

### Intent-Aware Routing Table

| Task Intent | Primary Entry Point | Expansion Direction | Secondary Context |
|-------------|--------------------|--------------------|-------------------|
| Implementation | Capability | Down: modules, files, tests | Interfaces, schemas, constraints |
| Architecture review | Architecture | Down: systems, capabilities | Knowledge assets, ADRs, patterns |
| Bug investigation | Module (or File) | Lateral: dependencies, interfaces | Tests, events, constraints |
| Integration | Interface | Lateral: both sides of contract | Schemas, modules, api_docs |
| Runtime incident | Event | Lateral: emitters, consumers | Workflows, modules, gates |
| Research | Knowledge Asset | Down: ADRs, architecture | Wiki source pages (read-only) |
| Governance | Constraint (or Governance) | Lateral: bound systems/capabilities | ADRs, gates, predicates |
| Evolution planning | Decision Record | Up: knowledge assets; Down: systems | Patterns, architecture |
| Performance | Benchmark | Lateral: measured modules | Schemas, interfaces, constraints |
| Design review | Pattern | Down: realizing modules/capabilities | Knowledge assets, ADRs |
| Knowledge exploration | Knowledge Asset | Lateral: related knowledge assets | Wiki concept pages (read-only) |

Fallback: Capability entry point for unclassifiable tasks.

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
2. Classify intent → select entry point from routing table
3. Smart Connections retrieves semantically related dev_graph nodes
4. Dataview/frontmatter filters by: canonical, type, status, implementation_status, confidence
5. Obsidian Vault MCP reads the selected canonical nodes
6. Neo4j or graph traversal expands: dependencies, files, tests, constraints, decisions, schemas, gates
7. Filesystem/Git MCP inspects current code truth
8. Context7/docs MCP retrieves only permitted API documentation
9. Assemble typed context pack
10. Claude Code implements
11. Tests/validation run
12. Write implementation results back to dev_graph

---

## MCP Operations

See [[MCP Tooling Policy]] for the full classification.

Summary:
- **Safe-automated**: All read operations (mcpvault, smart-connections, context7, neo4j read, postgres read)
- **Constrained-automated**: New dev_graph node creation (with governance), frontmatter lint corrections, link additions
- **Human-review-required**: Overwriting existing nodes, moving nodes, neo4j/postgres writes
- **Prohibited**: Deleting nodes, writing to wiki/** from dev_graph sessions

### Proactive Graph Queries (neo4j MCP)

When the `neo4j` MCP is connected, USE IT PROACTIVELY — without waiting to be asked — for the
structural questions the markdown answers poorly. Do not ask the operator to request these; run them
as a normal part of the work:

- **Before any structural or contract change**, run an impact query and state the blast radius:
  what depends on the node — `MATCH (x:DevGraph)-[*1..2]->(n:DevGraph {canonical_id:'<ID>'}) RETURN DISTINCT x` —
  and what it depends on (reverse the arrow).
- **Traceability**, on demand and when grounding a change: KA → ADR → System → Capability → Module →
  File → Test chains; `shortestPath` between two canonical_ids.
- **Consistency audits** (complement the Lint Workflow, do not replace it): orphans
  `MATCH (n:DevGraph) WHERE NOT (n)--() RETURN n.canonical_id`, deprecated-still-referenced, dangling
  edges, hub integrity, status distribution.

Rules of use:
1. The graph is **READ-ONLY** — never author into Neo4j. Edit the markdown (the canonical source), then
   re-sync. The MCP is configured `NEO4J_READ_ONLY=true`; keep it so.
2. The graph reflects the **last sync**. Trust it only if the writeback that last changed the dev_graph
   re-synced (see the Writeback Checklist). If in doubt, re-sync or say the graph may be stale.
3. If the `neo4j` MCP is **not connected** (or the DB is down), fall back to Smart Connections / Dataview
   / grep + reading the markdown, and say which you used — never invent edges from memory.
4. Do **not** query the graph for trivial, non-structural edits (typos, formatting) — reach for it when
   traversal genuinely beats grep/Dataview/reading.

This makes graph-grounded impact/traceability/audit a default behavior of dev_graph sessions, not a
thing the operator must request each time. (Instruction-level habit, not a hard gate; for mechanical
enforcement add an orchestration hook per the workflow-governance model.)

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

### Check 4: Stale Node Detection (Type-Aware Thresholds)

| Type Category | Types | Threshold |
|--------------|-------|-----------|
| Stable foundations | knowledge_asset, pattern, architecture | 180 days |
| Governance | governance, constraint, decision_record | 120 days |
| Structural | system, capability, interface | 90 days |
| Behavioral | event, workflow, artifact_schema | 60 days |
| Implementation + all others | module, file, test, + default | 30 days |

```
Dataview: LIST FROM "dev_graph" WHERE date(updated) < date(today) - dur(30 days) AND status != "deprecated"
```
Action: Review and update or set `status: deprecated`. Apply type-aware thresholds from table above.

### Check 5: Broken Wikilinks
Find `[[wikilinks]]` pointing to nonexistent nodes.
Action: Create missing nodes or fix links.

### Check 6: Constraint Coverage
Check that module/file nodes have `related_constraints` populated.
Action: Add relevant constraint references.

### Check 7: Test Coverage
Check that module/file nodes have `related_tests` populated or explicit justification.
Action: Add test references or document why tests are not needed.

### Check 8: Type-Content Alignment
Verify that a node's body sections match its type. A module node should have Implementation Notes. An ADR should have Status, Context, Decision, Consequences. A knowledge asset should have source_wiki_pages referencing live wiki pages.
Action: Manual per-session check on touched nodes. Full audit monthly.

### Check 9: Deprecated Reference Detection
Find nodes whose relationship sections contain wikilinks to deprecated nodes.
Action: Update references to point to successor nodes.

### Check 10: Canonical ID Uniqueness
Verify no two nodes share the same canonical_id value.
Action: Reassign duplicate IDs immediately.

### Check 11: Evidence-Confidence Coherence
Verify nodes with `confidence: confirmed` have `evidence: []` with at least one value.
Action: Add evidence source or reassess confidence level.

---

## Maintenance Cadences

| Cadence | Scope | Trigger |
|---------|-------|---------|
| Per-session | Lint checks 1-11 on touched nodes, update log.md | Every session modifying dev_graph |
| Weekly | Full lint across all nodes, dashboard review | Every 7 days |
| Monthly | Ontology audit, API doc freshness check, constraint review, type-content alignment (check 8) | First session of month |

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

### Migration Runbook Template

```
# Migration: [old_version] → [new_version]
## Changes: [list of schema changes]
## Affected Nodes: [Dataview query or list]
## Steps:
1. Update CLAUDE.md
2. Create ADR documenting the change
3. Run migration
4. Verify with lint checks
5. Update schema_version
6. Log in log.md
## Rollback: [procedure]
## Verification: [Dataview queries]
```

---

## Ontology Evolution Procedures

### Merge Procedure
When two nodes describe the same engineering concept:
1. Identify which node is at the correct abstraction level
2. Migrate content from the subordinate node into the canonical node
3. Update all wikilinks pointing to the subordinate node
4. Set subordinate to `status: deprecated` with `### Supersedes` reference
5. The surviving node retains its canonical_id
6. Log merge in log.md

### Split Procedure
When one node covers two distinct engineering concepts:
1. Create two new nodes, each with correct type and placement
2. Distribute content appropriately
3. New nodes reference original via `### Supersedes`
4. Set original to `status: deprecated`
5. Update all wikilinks to point to appropriate new node
6. Log split in log.md

### Deprecation Procedure
1. Set `status: deprecated`
2. Record deprecation reason in the node body
3. Reference replacement node via `### Supersedes` on the replacement
4. Node is retained indefinitely (never deleted)
5. Excluded from context packs by admissibility check #2

---

## Confidence Lifecycle

| From | To | Trigger |
|---|---|---|
| `speculative` | `inferred` | Logical derivation from confirmed facts |
| `inferred` | `single-source` | Source document directly supports claims |
| `single-source` | `confirmed` | Second independent source corroborates |
| `confirmed` | `single-source` | One source retracted or unreliable |
| `single-source` | `inferred` | Supporting source deprecated |
| `inferred` | `speculative` | Reasoning chain found weak |
| Any | `speculative` | Contradiction detected |
| `speculative` | `experimental` | Engineering hypothesis under active testing |
| `experimental` | `inferred` | Test results support the hypothesis |

Promotion updates both `confidence` and `updated` fields.
Demotion MUST be logged in `log.md`.

---

## Relationship to Wiki

- dev_graph INHERITS governance principles from `wiki/CLAUDE.md` via [[REF - Wiki CLAUDE]]
- dev_graph has its OWN type ontology (24 types) separate from wiki's 17 types
- dev_graph has its OWN frontmatter schema (extended with canonical_id, evidence, implementation_status, and relationship arrays)
- dev_graph may READ wiki nodes for domain knowledge (safe-automated)
- dev_graph MUST NOT WRITE to wiki nodes (prohibited — see [[No Wiki Mutation]])
- Cross-references use standard wikilinks: `[[wiki/Page Name]]` format
- Knowledge assets reference wiki pages via `source_wiki_pages` for domain knowledge context
- The wiki describes; the dev_graph defines

---

## Structural Files

These files have NO frontmatter (exempt by governance):
- `CLAUDE.md` — this operations manual
- `index.md` — master index of all nodes
- `log.md` — chronological operations log
- `README.md` — human-readable orientation

---

## Phase 5: Implementation Node Authoring

Authoring aids for the leaf implementation node types (module / file / test) plus the executable
end-of-coding-session writeback checklist. These are templates and process — no schema change.
Operationalizes population_strategy §3.7–3.9, §3.20, §7.3, §7.5 and [[Context Pack Assembly Rules]]
Step 8. Module nodes may be created from a concrete implementation plan BEFORE code (§3.7); file and
test nodes are created ONLY at writeback, when the real file exists.

### Module Node Template

Path: `dev_graph/modules/<Module Name>.md`. canonical_id: next free `MOD-NNN`.

```yaml
---
type: module
canonical_id: MOD-NNN
status: planned          # planned (plan only) → active (code exists)
implementation_status: not-started   # → in-progress → tested → validated
canonical: true
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: inferred     # → single-source/confirmed as code/tests land
evidence: [design, wiki] # add `code` at writeback
source_paths: []
related_files: []        # populated at writeback
related_tests: []        # populated at writeback
related_constraints: []
related_decisions: ["[[ADR - ...]]"]
module_name: "<snake_case>"
module_path: "<planned src path>"
responsibility: "<one line>"
depends_on: []
provides: ["[[<Interface>]]"]
---
```
Body (required; omit only if genuinely N/A): Definition, Purpose, Architecture Role, Inputs,
Outputs, Constraints, **Implementation Notes** (REQUIRED — a concrete plan, never "TBD"; lint
check 8), Open Questions (record deferred contract deps here), Relationships (`### Implements →
interface`, `### Consumes`/`### Produces → schemas`, `### Depends On`, `### Realizes → pattern`,
`### Justified By → ADR`, `### Originates From → knowledge asset`). Use resolvable wikilinks only.

### File Node Template

Path: `dev_graph/files/<filename.ext>.md`. Create ONLY at writeback when the real file exists AND
passes the §7.5 threshold (primary implementation / public API / schema / config / test file —
NOT boilerplate, generated, vendored, or interface-less utilities).

```yaml
---
type: file
canonical_id: FILE-NNN
status: implemented
implementation_status: implemented
canonical: true
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: confirmed
evidence: [code]
source_paths: []
related_files: []
related_tests: ["[[test_<name>]]"]
related_constraints: []
related_decisions: []
file_path: "<actual repo path>"
language: "<python|...>"
module: "[[<Parent Module>]]"   # REQUIRED inbound link
owns: []
used_by: []
---
```
Body: Definition, Purpose, Architecture Role, Constraints, Implementation Notes, Relationships
(`### Depends On → parent module` [REQUIRED], `### Validated By → test nodes`). Add the file to the
parent module's `related_files`.

### Test Node Template

Path: `dev_graph/tests/test_<name>.md`. Create at writeback when the test file exists.

```yaml
---
type: test
canonical_id: TEST-NNN
status: implemented
implementation_status: tested
canonical: true
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: confirmed
evidence: [code]
source_paths: []
related_files: ["[[<file under test>]]"]
related_tests: []
related_constraints: []
related_decisions: []
test_path: "<actual repo path>"
test_type: unit            # unit|integration|e2e|regression|benchmark
covers: ["[[<Module or File>]]"]   # REQUIRED
required_for: []
---
```
Body: Definition, Purpose, Constraints, Implementation Notes, Relationships (`### Validated By`,
`### Used By → covered module/file` [REQUIRED by cross-link protocol]). Add the test to the covered
node's `related_tests`.

### End-of-Coding-Session Writeback Checklist (executable)

Run at the end of EVERY session that creates or modifies code:

1. List changed files: `git status --porcelain` and `git diff --name-only`.
2. For each NEW source file, apply the §7.5 threshold — CREATE a file node if it is a primary
   implementation file, public API, schema, config, or test file; otherwise note it in the parent
   module's Implementation Notes (no node for boilerplate/generated/vendored/interface-less).
3. Each new file node: fill the File template; set `file_path`, `language`, `module` (REQUIRED
   inbound link); add the file to the parent module's `related_files`.
4. Each new test: create a test node; set `covers`; add it to the covered node's `related_tests`.
5. Update the parent MODULE node: bump `implementation_status` (not-started → in-progress on code;
   → tested on green tests); set `status: active`; add `code` to `evidence`; bump `updated`.
6. Update the parent CAPABILITY node: bump `implementation_status` to `in-progress` once any
   implementing module has code; refresh `updated`.
7. Run all 11 lint checks on TOUCHED NODES ONLY (frontmatter, enums, orphan/≥1 inbound, stale,
   broken wikilinks, module `related_constraints`, module `related_tests`, type-content alignment,
   deprecated refs, canonical_id uniqueness, evidence-confidence coherence).
8. Append `## [DATE] writeback | <title>` to `dev_graph/log.md` (Nodes Created / Changes / Metrics).
9. Update `dev_graph/index.md` (move nodes out of "(Empty …)" placeholders; refresh Statistics).
10. **Re-sync Neo4j** when this writeback changed the dev_graph and Neo4j is up:
    `python dev_graph/sync_to_neo4j.py --clear` — regenerates the read-only graph the `neo4j` MCP
    serves, so the next session's proactive graph queries (see MCP Operations → Proactive Graph
    Queries) are current. Skip only if no node or edge changed. Never edit Neo4j directly; the markdown
    is canonical and `--clear` re-projection is idempotent.
