---
type: governance
domain: governance
created: 2026-05-15
updated: 2026-05-15
status: active
aliases: [Migration Plan, Frontmatter Rollout Plan]
confidence: inferred
tags: []
---

# Metadata Migration Plan

## Definition

Three-phase governance architecture for introducing YAML frontmatter, Dataview observability, and MCP-aware graph operations into the existing Karpathy-style persistent synthesis wiki.

## Purpose

Establish deterministic metadata governance that enables structured querying, graph analytics, provenance tracing, and semantic tooling — without destabilizing the existing ontology, graph topology, or canonicalization rules.

## Architecture Role

Migration blueprint. This document governs all frontmatter introduction, schema evolution, and metadata lifecycle operations. All Claude sessions performing metadata operations MUST read this file and [[CLAUDE.md]] before modifying any page.

---

# Part 1 — Architecture Analysis

## 1.1 Current Vault Maturity Assessment

| Dimension | Status | Assessment |
|-----------|--------|------------|
| Ontology stability | Stable | 14 active domains, 4 empty (awaiting ingestion). Domain boundaries well-defined. |
| Page count | 58 wiki pages + index/log/CLAUDE.md | Manageable migration scope. |
| Frontmatter state | Zero pages have YAML frontmatter | Clean slate — no legacy schema to migrate from. |
| Tag usage | 2 inline tags (`#clippings` x1, `#contradiction` x1) | Minimal tag footprint. Tag governance in CLAUDE.md defines allowed set but adoption is near-zero. |
| Graph density | ~852 wikilinks / ~59 files = ~14.4 links/page | Exceeds the >=5 target by 2.8x. Graph is dense and well-connected. |
| Template compliance | All canonical pages follow the standard template | High structural consistency. |
| Source traceability | All claims cite `Source: [[SRC - ...]]` inline | Provenance exists but is unstructured (prose, not metadata). |
| Naming conventions | Strictly enforced Title Case + SRC prefix | No naming drift detected. |
| Canonical ownership | One page per concept, no detected duplicates | Anti-redundancy rules functioning. |
| Contradiction handling | 1 documented contradiction (options guardrail) | Process works; needs structured registry. |
| Dataview adoption | 1 page (`Graph Health Dashboard.md`) with 3 basic queries | Dataview installed and functional but underutilized. |
| MCP tooling | mcpvault connected, Smart Connections planned | MCP read/write operational; semantic search pending. |

## 1.2 Metadata Readiness

**Strengths:**
- Zero existing frontmatter means no schema migration debt
- Uniform page template provides predictable insertion points
- Source pages already have structured metadata tables (in markdown, not YAML)
- CLAUDE.md already defines allowed tags and governance rules
- Dataview plugin is installed and functional

**Risks:**
- Introducing frontmatter to 58 pages simultaneously risks entropy if schema is underspecified
- Source page metadata tables will need migration to YAML (semantic duplication risk)
- Tag governance exists in CLAUDE.md but has near-zero adoption — expanding without enforcement risks tag explosion
- No automated validation exists — schema drift is possible between sessions
- Dataview queries will fail silently on pages missing expected frontmatter fields

## 1.3 Migration Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Schema drift across sessions | High | Medium | Strict enum definitions + validation workflow in CLAUDE.md |
| Tag explosion from underspecified taxonomy | Medium | High | Closed enum for `type` and `domain`; no freeform tags |
| Frontmatter/content desync | Medium | Medium | Derived fields computed, not manually maintained |
| Dataview queries on partial rollout | Certain | Low | Queries must handle missing frontmatter gracefully |
| Source metadata duplication (YAML + prose table) | High | Medium | Phase 3 migrates prose tables to YAML; prose tables deprecated |
| Graph topology disruption | Low | Critical | Frontmatter-only changes; no page renames or link modifications |
| MCP tool incompatibility | Low | Medium | Schema designed for mcpvault/Smart Connections field access |

## 1.4 Scaling Bottlenecks

- **Manual frontmatter maintenance**: Without lint automation, schema compliance depends on Claude session discipline
- **Derived field staleness**: Fields like `link_count` require periodic recomputation
- **Ingestion workflow extension**: Every new page ingestion must now also produce frontmatter
- **Multi-session coordination**: Parallel Claude sessions could introduce conflicting frontmatter edits

---

# Part 2 — Frontmatter Governance Design

## 2.1 Metadata Classification

All frontmatter fields belong to exactly one of four classes:

| Class | Description | Lifecycle | Examples |
|-------|-------------|-----------|----------|
| **Universal** | Required on every wiki page | Set at creation, updated on major edit | `type`, `domain`, `created`, `updated` |
| **Domain-specific** | Required for pages in a specific domain or type | Set at creation | `source_file`, `source_type` (source pages) |
| **Optional** | Additional context, not required | Added when relevant | `aliases`, `confidence`, `tags` |
| **Derived** | Computed during maintenance, not manually set | Recomputed during lint | `link_count`, `stub` |

## 2.2 Universal Schema (All Pages)

```yaml
---
type: <enum>        # Required. Page classification.
domain: <enum>      # Required. Ontology domain.
created: YYYY-MM-DD # Required. Date page was created.
updated: YYYY-MM-DD # Required. Date of last substantive edit.
status: <enum>      # Required. Page lifecycle state.
---
```

### Field Definitions

#### `type`

Page classification. Closed enum.

| Value | Description | Domains |
|-------|-------------|---------|
| `concept` | Atomic technical concept (indicator, metric, primitive) | concepts, glossary |
| `system` | Composite system architecture or pipeline | systems |
| `strategy` | Trading strategy pattern or composition | strategies |
| `agent` | Agent type, role, or orchestration pattern | agents |
| `integration` | External service integration (API, MCP, webhook) | integrations |
| `infrastructure` | Deployment, scheduling, runtime environment | infrastructure |
| `execution` | Order execution, position management | execution |
| `risk` | Risk model, guardrail, exposure management | risk |
| `memory` | Memory architecture, context persistence | memory |
| `workflow` | End-to-end operational workflow | workflows |
| `research` | Research methodology, ingestion pattern | research |
| `governance` | Compliance, audit, operational safety | governance |
| `security` | Credential management, permission model | security |
| `backtesting` | Backtesting methodology, validation, metrics | backtesting |
| `source` | Source document summary and metadata | sources |
| `reference` | Glossary, index, or utility page | glossary |
| `observability` | Monitoring, dashboards, analytics | observability |

#### `domain`

Ontology domain. Maps to directory. Closed enum.

| Value | Directory |
|-------|-----------|
| `concepts` | `/wiki/concepts/` |
| `systems` | `/wiki/systems/` |
| `strategies` | `/wiki/strategies/` |
| `agents` | `/wiki/agents/` |
| `integrations` | `/wiki/integrations/` |
| `infrastructure` | `/wiki/infrastructure/` |
| `execution` | `/wiki/execution/` |
| `risk` | `/wiki/risk/` |
| `memory` | `/wiki/memory/` |
| `workflows` | `/wiki/workflows/` |
| `research` | `/wiki/research/` |
| `governance` | `/wiki/governance/` |
| `security` | `/wiki/security/` |
| `backtesting` | `/wiki/backtesting/` |
| `sources` | `/wiki/sources/` |
| `glossary` | `/wiki/glossary/` |
| `observability` | `/wiki/observability/` |
| `market_structure` | `/wiki/market_structure/` |
| `evaluation` | `/wiki/evaluation/` |
| `patterns` | `/wiki/patterns/` |

**Constraint**: `domain` MUST match the page's directory location. If `domain: risk`, the file must reside in `/wiki/risk/`.

#### `status`

Page lifecycle state. Closed enum.

| Value | Description |
|-------|-------------|
| `active` | Page is current and maintained |
| `stub` | Page exists but needs substantial expansion |
| `deprecated` | Page is superseded; retained for reference |
| `draft` | Page is in progress, not yet canonical |

#### `created` / `updated`

ISO 8601 date format: `YYYY-MM-DD`. `updated` is refreshed on every substantive content edit. Frontmatter-only changes (e.g., lint corrections) do NOT update `updated`.

## 2.3 Optional Fields (All Pages)

```yaml
aliases: []          # Alternative names for this concept
confidence: <enum>   # Epistemic status of the page content
tags: []             # Controlled tags from the allowed set
```

#### `aliases`

List of alternative names or abbreviations. Used by Obsidian for link resolution and by MCP for semantic search.

Example: `aliases: [Volume Weighted Average Price, volume-weighted average price]`

#### `confidence`

Epistemic qualifier for the page's core claims.

| Value | Description |
|-------|-------------|
| `confirmed` | Multiple independent sources agree |
| `single-source` | Derived from one source only |
| `inferred` | Synthesized by Claude, not directly stated in sources |
| `speculative` | Hypothetical or exploratory |

#### `tags`

Controlled list. MUST only use values from the allowed set defined in CLAUDE.md. The `tags` field in frontmatter replaces inline `#hashtag` usage.

Allowed values: `concept`, `system`, `agent`, `strategy`, `integration`, `risk`, `infrastructure`, `stub`, `contradiction`, `deprecated`

## 2.4 Source Page Schema (Domain-Specific)

Source pages (`SRC - *`) require additional fields:

```yaml
---
type: source
domain: sources
source_file: <string>    # Required. Path to raw source document.
source_type: <enum>      # Required. Source document type.
date_ingested: YYYY-MM-DD # Required. When source was processed.
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---
```

#### `source_type`

| Value | Description |
|-------|-------------|
| `youtube_transcript` | Transcribed video content |
| `architecture_doc` | System architecture document |
| `product_spec` | Product requirements document |
| `announcement` | Official announcement or blog post |
| `methodology` | Methodology or process document |

## 2.5 Prohibited Practices

1. **No freeform fields**: Every frontmatter key must be defined in this schema. Custom keys are prohibited.
2. **No nested objects**: Frontmatter must be flat key-value pairs or arrays of scalars.
3. **No computed values in manual fields**: Fields like `link_count` are derived; never set them manually.
4. **No duplicate semantics**: Do not create fields that overlap with existing fields (e.g., no `category` alongside `type`).
5. **No inline tags alongside frontmatter tags**: Once a page has `tags:` in frontmatter, all inline `#hashtags` must be removed from that page.
6. **No frontmatter on `index.md`, `log.md`, or `CLAUDE.md`**: These are structural files, not ontology pages.

## 2.6 Metadata Lifecycle Rules

### Creation
- Every new wiki page MUST include the universal frontmatter block at creation time.
- Source pages MUST include the source-specific fields.
- `created` is set once at page creation and NEVER modified.

### Update
- `updated` is refreshed on every substantive content edit.
- Frontmatter-only corrections (lint fixes, enum normalization) do NOT trigger `updated` change.
- Adding a new optional field to an existing page does NOT trigger `updated` change.

### Deprecation
- Set `status: deprecated` instead of deleting pages.
- Deprecated pages retain all frontmatter and content for reference.
- Deprecated pages should be excluded from active Dataview queries.

### Derived Metadata
- Derived fields are computed during lint workflows, not set by authors.
- Current derived fields: none in Phase 1-2. Phase 3 may introduce `link_count`, `inbound_count`.

---

# Part 3 — Phased Rollout Plan

## Phase 1 — Hub Page Metadata Foundation

**Target**: 5 major hub pages only
**Duration**: Single session
**Blast radius**: 5 pages (~8.6% of vault)

### Target Pages

| Page | Domain | Type |
|------|--------|------|
| Architecture Overview | systems | system |
| Trading Engine Pipeline | systems | system |
| Claude-Assisted Trading Stack | systems | system |
| Agent Memory Architecture | memory | memory |
| Autonomous Trading Risk Model | risk | risk |

### Goals

1. Establish the canonical frontmatter schema on the highest-connectivity pages
2. Validate that frontmatter insertion does not break existing wikilinks or content
3. Validate Dataview compatibility with the schema
4. Confirm MCP (mcpvault) can read frontmatter fields
5. Establish operational patterns for subsequent phases

### Implementation Checklist

- [ ] Read this document and CLAUDE.md before starting
- [ ] For each target page:
  - [ ] Read the full page content
  - [ ] Insert YAML frontmatter block at line 1 (before `# Title`)
  - [ ] Set `type`, `domain`, `created`, `updated`, `status`
  - [ ] Set `aliases` if the page has well-known alternative names
  - [ ] Set `confidence` based on source coverage
  - [ ] Verify the page still renders correctly in Obsidian
- [ ] Create/update pilot Dataview queries on Graph Health Dashboard
- [ ] Validate mcpvault `get_frontmatter` works on modified pages
- [ ] Append Phase 1 completion entry to `log.md`

### Example: Architecture Overview Frontmatter

```yaml
---
type: system
domain: systems
created: 2026-05-09
updated: 2026-05-15
status: active
aliases: [Architecture Map, System Overview]
confidence: confirmed
tags: [system]
---
```

### Pilot Dataview Queries

Add to `Graph Health Dashboard.md` after Phase 1:

```dataview
TABLE type, domain, status, updated
FROM "wiki"
WHERE type != null
SORT updated DESC
```

```dataview
TABLE type, confidence
FROM "wiki"
WHERE type != null AND confidence = "single-source"
SORT domain ASC
```

### Rollback Strategy

Frontmatter insertion is fully reversible:
1. Delete the `---` fenced YAML block from each modified page
2. No content, links, or filenames are modified during Phase 1
3. Dataview queries gracefully handle missing frontmatter (return empty results)
4. Git commit before Phase 1 begins provides full rollback point

### Success Criteria

- [ ] All 5 hub pages have valid frontmatter
- [ ] Dataview query returns all 5 pages with correct metadata
- [ ] mcpvault `get_frontmatter` returns parsed YAML for each page
- [ ] No broken wikilinks introduced
- [ ] No rendering issues in Obsidian

---

## Phase 2 — Canonical Page Expansion

**Target**: All remaining canonical pages (concepts, strategies, integrations, infrastructure, execution, risk, memory, agents, backtesting, security, governance, workflows, research)
**Duration**: 1-2 sessions
**Blast radius**: ~43 pages (74% of vault)
**Prerequisite**: Phase 1 success criteria met

### Target Pages by Domain

| Domain | Count | Pages |
|--------|-------|-------|
| concepts | 4 | VWAP, EMA Crossover, Relative Volume Filter, Options Trading |
| strategies | 5 | VWAP Crossover Strategy, Signal Confirmation, Paper Trading, Wheel Strategy, Copy Trading Strategy |
| integrations | 7 | Alpaca API, TradingView Integration, Exchange API Integration, Perplexity API, MCP Architecture, Webhook Architecture, Capital Trades Integration |
| infrastructure | 4 | Claude Code, Claude Co-work, Claude Routines, Railway Deployment |
| execution | 2 | Position Sizing, Stop-Loss Systems |
| risk | 1 | Guardrail Architecture |
| memory | 1 | Context Budget Engineering |
| agents | 4 | Supervisor Decision Engine, Multi-Agent Orchestration, Stateless Agent Recovery, Agent Self-Verification |
| backtesting | 3 | Walk-Forward Optimization, Overfitting Detection, Backtesting Methodology |
| security | 2 | API Credential Isolation, Environment Variable Management |
| governance | 2 | Trade Logging, Treasury Policy System |
| workflows | 1 | Office Action Loop |
| research | 1 | Research Ingestion Workflow |
| systems | 3 | Three-Layer Trading System, LLM Failure Modes in Trading, Syndicate Squad Architecture |
| glossary | 1 | Glossary |
| observability | 1 | Graph Health Dashboard |

### Implementation Checklist

- [ ] Git commit current state as pre-Phase-2 checkpoint
- [ ] For each domain, process all pages:
  - [ ] Read page content
  - [ ] Insert frontmatter with universal fields
  - [ ] Set domain-appropriate `type` value
  - [ ] Set `confidence` based on source diversity
  - [ ] Add `aliases` only where genuinely useful
- [ ] Validate via Dataview: all canonical pages appear in metadata query
- [ ] Run schema validation: check for missing required fields
- [ ] Run enum validation: check for invalid `type` or `domain` values
- [ ] Append Phase 2 completion entry to `log.md`

### Type/Domain Assignment Rules

1. `type` MUST match the page's architectural role, not just its directory
2. `domain` MUST match the page's directory location
3. When a page could fit multiple types, prefer the type that matches its directory
4. The Glossary page gets `type: reference`
5. Graph Health Dashboard gets `type: observability`

### Metadata Inheritance Rules

There is no inheritance. Each page carries its own complete frontmatter. This prevents:
- Hidden coupling between pages
- Cascading metadata failures
- Ambiguity about which metadata applies

### Graph Validation Workflow (Post-Phase-2)

Run these Dataview queries to validate completeness:

**Pages missing frontmatter:**
```dataview
LIST
FROM "wiki"
WHERE type = null
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```

**Pages with invalid domain (domain doesn't match directory):**
Manual check — compare `domain` field against `file.folder` for each page.

**Type distribution:**
```dataview
TABLE length(rows) AS Count
FROM "wiki"
WHERE type != null
GROUP BY type
```

### Rollback Strategy

- Pre-Phase-2 git commit enables full revert
- Individual page rollback: remove frontmatter block only
- Dataview queries continue to function on partial frontmatter coverage

---

## Phase 3 — Source + Observability Layer

**Target**: Source pages (9), observability dashboards, ingestion metadata, provenance enhancement
**Duration**: 1-2 sessions
**Blast radius**: 9 source pages + dashboard pages
**Prerequisite**: Phase 2 success criteria met

### 3A: Source Page Metadata Migration

Each source page currently has a markdown metadata table:

```markdown
## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/...` |
| Type | YouTube transcript |
| ...  | ... |
```

**Migration action**: Add source-specific frontmatter, retain the prose table during Phase 3 transition period, deprecate prose tables in a future session.

#### Source Page Frontmatter Examples

**SRC - Claude Stock Trader:**
```yaml
---
type: source
domain: sources
source_file: raw/claude_stock_trader.md
source_type: youtube_transcript
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
---
```

**SRC - OWS Dev Squad:**
```yaml
---
type: source
domain: sources
source_file: raw/ows-dev-squad.md
source_type: architecture_doc
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
---
```

### 3B: Provenance Schema

Provenance metadata enables tracking which source documents contributed to which canonical pages. This is NOT stored in frontmatter (would create excessive coupling). Instead, provenance is queried dynamically:

**Dataview query — pages citing a specific source:**
```dataview
LIST
FROM "wiki"
WHERE contains(file.outlinks, [[SRC - Claude Opus Trader]])
```

**Dataview query — source coverage map:**
```dataview
TABLE length(filter(file.outlinks, (l) => startswith(meta(l).path, "wiki/sources"))) AS "Source Citations"
FROM "wiki"
WHERE type != null AND type != "source"
SORT "Source Citations" DESC
```

### 3C: Observability Dashboards

Expand `Graph Health Dashboard.md` into a comprehensive observability suite.

#### Dashboard 1: Ontology Overview

```dataview
TABLE length(rows) AS "Page Count"
FROM "wiki"
WHERE type != null
GROUP BY domain
SORT length(rows) DESC
```

#### Dashboard 2: Stale Page Detection

```dataview
TABLE updated, status, domain
FROM "wiki"
WHERE type != null AND updated != null
AND date(updated) < date(today) - dur(30 days)
AND status = "active"
SORT updated ASC
```

#### Dashboard 3: Stub Tracking

```dataview
TABLE domain, updated
FROM "wiki"
WHERE status = "stub"
SORT domain ASC
```

#### Dashboard 4: Confidence Distribution

```dataview
TABLE length(rows) AS Count
FROM "wiki"
WHERE confidence != null
GROUP BY confidence
```

#### Dashboard 5: Source Coverage

```dataview
TABLE source_file, source_type, date_ingested
FROM "wiki/sources"
WHERE type = "source"
SORT date_ingested DESC
```

#### Dashboard 6: Orphan Page Detection

```dataview
TABLE file.inlinks AS "Inbound Links"
FROM "wiki"
WHERE length(file.inlinks) = 0
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```

#### Dashboard 7: Weakly Connected Pages

```dataview
TABLE length(file.inlinks) AS Inbound, length(file.outlinks) AS Outbound, domain
FROM "wiki"
WHERE type != null AND (length(file.inlinks) < 3 OR length(file.outlinks) < 3)
SORT length(file.inlinks) ASC
```

#### Dashboard 8: Contradiction Registry

```dataview
LIST
FROM "wiki"
WHERE contains(tags, "contradiction") OR contains(file.tags, "#contradiction")
```

#### Dashboard 9: Recently Modified Pages

```dataview
TABLE updated, type, domain
FROM "wiki"
WHERE type != null
SORT updated DESC
LIMIT 15
```

#### Dashboard 10: Ingestion Monitor

```dataview
TABLE source_type, date_ingested, status
FROM "wiki/sources"
WHERE type = "source"
SORT date_ingested DESC
```

### 3D: Graph Health Metrics

Target metrics to monitor post-migration:

| Metric | Target | Query Method |
|--------|--------|-------------|
| Frontmatter coverage | 100% of canonical pages | Count pages where `type = null` |
| Link density | >= 5.0 links/page | Dataview outlinks count |
| Orphan pages | 0 | Inbound links = 0 |
| Stale pages (>30 days) | < 10% of active pages | Date comparison on `updated` |
| Stub pages | < 5% of total | `status = "stub"` count |
| Source coverage | All sources ingested | Source page count vs raw file count |
| Schema compliance | 0 invalid enum values | Lint workflow |

### 3E: Contradiction Registry Architecture

Contradictions are currently documented inline in page `## Contradictions` sections. Phase 3 adds structured tracking:

1. Pages with contradictions get `tags: [contradiction]` in frontmatter
2. Dashboard 8 aggregates all contradiction pages
3. Each contradiction section documents: both claims, both sources, resolution status, resolution date

Future enhancement: dedicated contradiction registry page with Dataview aggregation across all contradiction-tagged pages.

### Implementation Checklist

- [ ] Git commit pre-Phase-3 checkpoint
- [ ] Add source-specific frontmatter to all 9 source pages
- [ ] Expand Graph Health Dashboard with dashboards 1-10
- [ ] Validate all Dataview queries render correctly
- [ ] Run full schema lint across vault
- [ ] Append Phase 3 completion entry to `log.md`
- [ ] Update `index.md` statistics with frontmatter coverage metrics

---

# Part 4 — Dataview Integration Design

## 4.1 Query Architecture

All Dataview queries follow these conventions:

1. **FROM clause**: Always scope to `"wiki"` to exclude raw sources
2. **WHERE clause**: Always filter `type != null` to exclude structural files
3. **NULL handling**: All queries must handle missing fields gracefully
4. **SORT clause**: Default sort by `updated DESC` unless domain-specific sort applies

## 4.2 Canonical Dashboard Architecture

| Dashboard | Purpose | Location | Owner |
|-----------|---------|----------|-------|
| Ontology Overview | Domain distribution, type counts | Graph Health Dashboard | CLAUDE.md lint workflow |
| Stale Page Detection | Pages not updated in >30 days | Graph Health Dashboard | CLAUDE.md lint workflow |
| Source Coverage | Ingestion tracking, provenance | Graph Health Dashboard | Ingestion workflow |
| Graph Connectivity | Orphans, weak links, hub metrics | Graph Health Dashboard | CLAUDE.md graph maintenance |
| Contradiction Registry | Unresolved conflicts | Graph Health Dashboard | Contradiction handling workflow |

## 4.3 Dashboard Ownership

All observability dashboards reside in `Graph Health Dashboard.md` in `/wiki/observability/`. This is a single-page dashboard that aggregates all health queries. Creating additional dashboard pages requires governance approval (update to this document).

---

# Part 5 — MCP Readiness Design

## 5.1 Compatibility Requirements

The frontmatter schema is designed for compatibility with three MCP-class tools:

### mcpvault (Current)

- `read_note` / `write_note`: Full page access including frontmatter
- `get_frontmatter` / `update_frontmatter`: Direct YAML field access
- `search_notes`: Full-text search across content
- `manage_tags`: Tag operations on frontmatter
- `list_all_tags`: Tag frequency analysis

**Schema compatibility**: All fields are flat key-value or scalar arrays. mcpvault can read/write all defined fields natively.

### Smart Connections MCP (Planned)

- Semantic similarity search across vault
- Embedding-based retrieval

**Schema compatibility**: `type` and `domain` fields enable filtered semantic search (e.g., "find similar pages of type `strategy`"). `aliases` improve embedding quality by surfacing alternative phrasings.

### Future Semantic MCPs

- Graph traversal via metadata fields
- Ontology introspection via type/domain enums
- Automated graph lint via frontmatter validation

## 5.2 Graph Traversal Assumptions

MCP tools can use frontmatter to:

1. **Filter by type**: Retrieve all `system` pages for architecture analysis
2. **Filter by domain**: Scope operations to a single ontology domain
3. **Filter by status**: Exclude `deprecated` or `stub` pages from active queries
4. **Filter by confidence**: Prioritize `confirmed` pages over `speculative` ones
5. **Filter by freshness**: Use `updated` to find stale content
6. **Resolve aliases**: Use `aliases` for fuzzy name matching

## 5.3 Ontology Stability Guarantees

For MCP tools to reliably query the graph:

1. **Enum values are append-only**: New values may be added; existing values are never renamed or removed
2. **Field names are stable**: Once a field is in the schema, its name does not change
3. **Schema changes require governance update**: Any schema modification must update this document and CLAUDE.md
4. **Domain-directory binding is permanent**: `domain` value always matches directory path

## 5.4 Graph Lint Automation (MCP-Assisted)

Future MCP tooling can automate the CLAUDE.md lint workflow:

1. **Missing frontmatter**: `search_notes` for pages, `get_frontmatter` to check fields
2. **Invalid enums**: `get_frontmatter` + validate against schema
3. **Stale metadata**: `get_frontmatter` + date comparison
4. **Orphan detection**: `get_notes_info` for link analysis
5. **Schema compliance**: Iterate all pages, validate field presence and types

---

# Part 6 — Metadata Anti-Entropy Architecture

## 6.1 Entropy Sources

| Source | Risk | Prevention |
|--------|------|-----------|
| Freeform field creation | Schema drift across sessions | Prohibited — all fields must be defined in this schema |
| Enum value invention | Type/domain fragmentation | Closed enums — new values require governance update |
| Duplicate semantic fields | Overlapping metadata meanings | Prohibited — no `category` alongside `type` |
| Inconsistent date formats | Query failures | ISO 8601 enforced (`YYYY-MM-DD`) |
| Tag proliferation | Uncontrolled classification | Closed tag set — same as CLAUDE.md allowed tags |
| Stale `updated` fields | False freshness signals | `updated` only changes on substantive content edits |
| Missing frontmatter on new pages | Coverage gaps | Ingestion workflow requires frontmatter at creation |

## 6.2 Anti-Entropy Rules

1. **No field without schema**: Every frontmatter key must exist in this document's schema definition
2. **No enum without governance**: Every enum value must be listed in the enum table above
3. **No tag without approval**: Only tags from the CLAUDE.md allowed set may appear in `tags:`
4. **No metadata without content**: Frontmatter metadata must reflect actual page content, not aspirational content
5. **No manual derived fields**: Fields designated as "derived" are set only by lint workflows
6. **Date discipline**: `created` is immutable; `updated` reflects last substantive edit only

## 6.3 Metadata Lint Workflow

Run periodically (recommended: every ingestion session, or weekly):

### Step 1: Missing Frontmatter Detection
```
Dataview: LIST FROM "wiki" WHERE type = null AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```
**Action**: Add frontmatter to any listed pages.

### Step 2: Invalid Enum Detection
For each page with frontmatter, verify:
- `type` value exists in the `type` enum table
- `domain` value exists in the `domain` enum table
- `status` value exists in the `status` enum table
- `confidence` value (if present) exists in the `confidence` enum table
- `source_type` value (if present) exists in the `source_type` enum table

**Action**: Correct invalid values to nearest valid enum.

### Step 3: Domain-Directory Consistency
Verify `domain` field matches the page's directory location.

**Action**: Correct `domain` to match directory.

### Step 4: Stale Metadata Detection
```
Dataview: LIST FROM "wiki" WHERE updated != null AND date(updated) < date(today) - dur(60 days) AND status = "active"
```
**Action**: Review listed pages for staleness. Update content or set `status: stub` if content is insufficient.

### Step 5: Orphan Frontmatter Fields
Check for any frontmatter keys not defined in the schema.

**Action**: Remove undefined fields.

---

# Dependencies

- [[CLAUDE.md]] — governance rules extended with metadata sections
- [[Graph Health Dashboard]] — observability queries
- [[Research Ingestion Workflow]] — updated with frontmatter requirements

## Related Concepts

- [[Architecture Overview]] — Phase 1 target
- [[Trading Engine Pipeline]] — Phase 1 target
- [[Claude-Assisted Trading Stack]] — Phase 1 target
- [[Agent Memory Architecture]] — Phase 1 target
- [[Autonomous Trading Risk Model]] — Phase 1 target

## Source References

- Source: [[SRC - LLM Wiki Methodology]] — persistent synthesis architecture that motivates metadata governance
