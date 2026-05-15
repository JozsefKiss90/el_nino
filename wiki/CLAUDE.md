# Wiki Maintenance Schema

This file governs all wiki maintenance operations. Every Claude session that modifies the wiki MUST read this file first.

## Vault Structure

```
/wiki
  /concepts        — atomic concept definitions (VWAP, EMA, RSI, etc.)
  /systems         — composite system architectures
  /agents          — agent types, roles, orchestration patterns
  /strategies      — trading strategy patterns and compositions
  /execution       — order execution, position management
  /memory          — memory architectures, context persistence
  /risk            — risk models, guardrails, exposure management
  /research        — research methodology, ingestion patterns
  /integrations    — external service integrations (APIs, MCP, webhooks)
  /market_structure — market microstructure, order types, venues
  /backtesting     — backtesting methodology, validation, metrics
  /infrastructure  — deployment, scheduling, environment management
  /evaluation      — performance evaluation, scoring, benchmarks
  /observability   — logging, monitoring, alerting patterns
  /security        — credential management, permission models
  /governance      — compliance, audit trails, operational safety
  /workflows       — end-to-end operational workflows
  /patterns        — reusable architectural and design patterns
  /sources         — source document summaries and metadata
  /glossary        — canonical term definitions
```

## Naming Conventions

- **File names**: Title Case with spaces (e.g., `VWAP Crossover Strategy.md`)
- **Canonical concept pages**: Named after the concept itself (e.g., `VWAP.md`, not `About VWAP.md`)
- **System pages**: Named after the system (e.g., `Trading Engine Pipeline.md`)
- **Source pages**: Prefixed with `SRC -` (e.g., `SRC - Claude for Financial Services.md`)
- **No duplicate aliases**: Each concept has exactly one canonical page
- **Wikilinks**: Use `[[Page Name]]` format, never raw markdown links for internal references

## Canonical Ownership Rules

1. Each concept/system/pattern has ONE canonical page
2. Before creating a new page, search for existing pages covering the same concept
3. If a concept is already covered, UPDATE the existing page rather than creating a new one
4. Other pages reference the canonical page via `[[wikilink]]`
5. Never duplicate a definition — reference it

## Page Template

Every canonical page MUST contain these sections (omit only if genuinely not applicable):

```markdown
# {Page Title}

## Definition
## Purpose
## Architecture Role
## Inputs
## Outputs
## Dependencies
## Failure Modes
## Tradeoffs
## Operational Constraints
## Related Concepts
## Implementation Notes
## Open Questions
## Future Extensions
## Source References
```

## Ingestion Workflow

When processing a new raw source:

1. **Read** the source document completely
2. **Identify** all concepts, entities, systems, workflows, and claims
3. **Search** existing wiki pages for each identified concept
4. **Update** existing canonical pages with new information
5. **Create** new canonical pages only for genuinely new concepts
6. **Cross-link** all related pages bidirectionally
7. **Update** `index.md` with any new pages
8. **Append** a timestamped entry to `log.md`
9. **Flag** any contradictions with existing wiki content
10. **Propose** architecture gaps and future research areas

## Canonicalization Rules

- Use the most precise technical term as the page name
- Prefer industry-standard terminology over source-specific wording
- If a source uses a non-standard term, create the page under the standard term and note the source's terminology
- Compound concepts get their own page only if they represent a distinct architectural unit

## Redundancy Prevention

Before writing any content:

1. `grep` the wiki for the concept name and synonyms
2. Check `index.md` for existing coverage
3. If found: update the existing page, add cross-links
4. If not found: create new page, add to index
5. Never write the same explanation in two places — link instead

## Cross-Linking Protocol

Every page must link to:
- **Upstream dependencies**: What this concept requires
- **Downstream consumers**: What depends on this concept
- **Sibling concepts**: Related concepts at the same abstraction level
- **Implementation pages**: How this is realized in specific systems
- **Risk implications**: What can go wrong

## Contradiction Handling

When two sources conflict:

1. Do NOT silently merge conflicting claims
2. Create a `## Contradictions` section on the canonical page
3. Document both claims with source attribution
4. Explicitly state the tradeoffs
5. If the contradiction is architectural, create a dedicated comparison page

## Source Traceability

Every synthesized claim must include:
- `Source: [[SRC - {source name}]]` reference
- Specific section or context from the source
- Confidence qualifier if speculative: `[speculative]`, `[inferred]`, `[confirmed]`

## Lint Workflow

Periodic maintenance checks:

1. **Orphan detection**: Find pages with no inbound links
2. **Broken links**: Find `[[wikilinks]]` that point to nonexistent pages
3. **Stale content**: Flag pages not updated in >30 days
4. **Missing sections**: Pages missing required template sections
5. **Duplicate concepts**: Semantic overlap between pages
6. **Index sync**: Ensure `index.md` lists all pages

## Update Procedures

- **Minor update**: Add information to existing section, add cross-link
- **Major update**: New section, restructured content, contradiction resolution
- **All updates**: Append to `log.md`, update `index.md` if page list changed

## Graph Maintenance

- Target: every page has >=3 inbound links and >=3 outbound links
- Hub pages (Architecture Overview, Trading Engine Pipeline) should have 10+ links
- Leaf pages should always link back to at least one hub
- Monitor graph density: total_links / total_pages should be >= 5

## Tags

Use sparingly. Allowed tags:
- `#concept` `#system` `#agent` `#strategy` `#integration` `#risk` `#infrastructure`
- `#stub` for pages that need expansion
- `#contradiction` for pages with unresolved conflicts
- `#deprecated` for superseded content

When frontmatter `tags:` field is present on a page, all inline `#hashtags` on that page must be removed. Frontmatter tags are the canonical tag location.

---

## Frontmatter Governance

Full schema specification lives in [[Metadata Migration Plan]]. This section defines the operational rules that every Claude session MUST follow.

### Required Fields (All Pages)

Every wiki page (except `index.md`, `log.md`, `CLAUDE.md`) MUST have this frontmatter block as the first content in the file:

```yaml
---
type: <enum>
domain: <enum>
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: <enum>
---
```

### Allowed Enums

**`type`**: `concept`, `system`, `strategy`, `agent`, `integration`, `infrastructure`, `execution`, `risk`, `memory`, `workflow`, `research`, `governance`, `security`, `backtesting`, `source`, `reference`, `observability`

**`domain`**: `concepts`, `systems`, `strategies`, `agents`, `integrations`, `infrastructure`, `execution`, `risk`, `memory`, `workflows`, `research`, `governance`, `security`, `backtesting`, `sources`, `glossary`, `observability`, `market_structure`, `evaluation`, `patterns`

**`status`**: `active`, `stub`, `deprecated`, `draft`

**`confidence`** (optional): `confirmed`, `single-source`, `inferred`, `speculative`

**`source_type`** (source pages only): `youtube_transcript`, `architecture_doc`, `product_spec`, `announcement`, `methodology`

### Schema Validation Rules

1. `domain` MUST match the page's directory (e.g., page in `/wiki/risk/` must have `domain: risk`)
2. `type` must be from the closed enum — no freeform values
3. `created` is set once at page creation and NEVER modified
4. `updated` is refreshed ONLY on substantive content edits (not frontmatter-only corrections)
5. Source pages (`SRC - *`) MUST also include `source_file`, `source_type`, `date_ingested`
6. No frontmatter keys beyond those defined in [[Metadata Migration Plan]]

### Optional Fields

```yaml
aliases: []       # Alternative names (flat string array)
confidence: <enum> # Epistemic status
tags: []          # From allowed tag set only
```

---

## Metadata Lifecycle

### Creation Rules

- Every new wiki page MUST include the universal frontmatter block
- Source pages MUST include source-specific fields (`source_file`, `source_type`, `date_ingested`)
- `created` is set to the current date at page creation
- `updated` is set equal to `created` at page creation
- `status` defaults to `active` unless the page is intentionally a stub

### Update Rules

- `updated` changes when page content is substantively edited
- `updated` does NOT change for: frontmatter corrections, link additions, typo fixes
- Adding optional frontmatter fields does NOT change `updated`
- Enum values are never renamed — only new values may be appended (requires governance update)

### Deprecation Rules

- Set `status: deprecated` instead of deleting a page
- Deprecated pages retain all frontmatter and content
- Deprecated pages are excluded from active Dataview queries
- Deprecated pages still participate in graph links (do not break references)

### Derived Metadata Rules

- No derived fields exist in the current schema
- Future derived fields (e.g., `link_count`) will be computed by lint workflows only
- Never manually set a field designated as "derived"

---

## Dataview Governance

### Approved Query Patterns

All Dataview queries MUST:
1. Scope to `FROM "wiki"` to exclude raw source files
2. Filter `WHERE type != null` to exclude structural files (index, log, CLAUDE.md)
3. Handle missing fields gracefully (null-safe comparisons)
4. Use `SORT updated DESC` as default unless domain-specific sort applies

### Dashboard Ownership

All observability dashboards reside in [[Graph Health Dashboard]] (`/wiki/observability/`). This is a single consolidated dashboard page. Creating additional dashboard pages requires an update to [[Metadata Migration Plan]].

### Observability Standards

The following metrics MUST be monitored during lint workflows:

| Metric | Target | Action if violated |
|--------|--------|--------------------|
| Frontmatter coverage | 100% of canonical pages | Add frontmatter to uncovered pages |
| Schema compliance | 0 invalid enum values | Correct to nearest valid enum |
| Domain-directory consistency | 100% match | Correct `domain` field |
| Orphan pages | 0 pages with 0 inbound links | Add cross-links |
| Stale pages (>30 days) | < 10% of active pages | Review and update or mark as stub |
| Link density | >= 5.0 links/page | Add cross-links to under-connected pages |

---

## MCP Compatibility

### Graph Traversal Assumptions

MCP tools (mcpvault, Smart Connections, future semantic MCPs) may use frontmatter to:
- Filter pages by `type`, `domain`, `status`, `confidence`
- Use `aliases` for fuzzy name resolution
- Use `updated` for freshness-based ranking
- Traverse the ontology via `domain` grouping

### Semantic Tooling Assumptions

- `type` and `domain` enable filtered semantic search
- `aliases` improve embedding quality by surfacing alternative phrasings
- `status: deprecated` signals exclusion from active semantic indexes

### Ontology Stability Guarantees

For MCP interoperability:
1. **Enum values are append-only**: Existing values are never renamed or removed
2. **Field names are stable**: Once defined, a field name does not change
3. **Schema changes require governance update**: Modify [[Metadata Migration Plan]] and this file
4. **Domain-directory binding is permanent**: `domain` always maps to directory path

---

## Metadata Anti-Entropy Rules

### Prohibited Practices

1. **No freeform frontmatter fields**: Every key must be defined in [[Metadata Migration Plan]]
2. **No nested YAML objects**: Frontmatter must be flat key-value pairs or scalar arrays
3. **No duplicate semantics**: Do not create fields that overlap existing fields
4. **No inline tags alongside frontmatter tags**: If `tags:` exists in frontmatter, remove all inline `#hashtags`
5. **No manual derived fields**: Fields designated as "derived" are set by lint workflows only
6. **No metadata without content**: Frontmatter must reflect actual page content

### Prevention of Schema Drift

- All Claude sessions that modify frontmatter MUST read this file and [[Metadata Migration Plan]] first
- Any new field or enum value proposal must be documented in [[Metadata Migration Plan]] before use
- Schema evolution is append-only for enums; field additions require governance approval

### Prevention of Tag Explosion

- Tags in frontmatter `tags:` field MUST use only values from the allowed tag set (see Tags section above)
- No freeform tags
- Tag set expansion requires an update to this file

---

## Metadata Lint Workflow

Extend the existing Lint Workflow with these additional checks. Run during every ingestion session or weekly maintenance.

### Step 1: Missing Frontmatter Detection

Find pages without frontmatter:
```
Dataview: LIST FROM "wiki" WHERE type = null AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```
**Action**: Add universal frontmatter block to listed pages.

### Step 2: Invalid Enum Detection

For each page with frontmatter, verify all enum fields contain valid values from the allowed sets defined above.

**Action**: Correct invalid values to nearest valid enum.

### Step 3: Domain-Directory Consistency

Verify `domain` field matches the page's directory location for every page.

**Action**: Correct `domain` to match directory.

### Step 4: Stale Metadata Detection

```
Dataview: LIST FROM "wiki" WHERE updated != null AND date(updated) < date(today) - dur(60 days) AND status = "active"
```
**Action**: Review pages. Update content or set `status: stub`.

### Step 5: Orphan Frontmatter Fields

Check for frontmatter keys not defined in [[Metadata Migration Plan]] schema.

**Action**: Remove undefined fields.

### Step 6: Source Page Schema Compliance

All `SRC - *` pages must have `source_file`, `source_type`, `date_ingested` in addition to universal fields.

**Action**: Add missing source-specific fields.

---

## Continuous Ontology Operations

Defines recurring maintenance cadences and operational procedures for sustained ontology health. All cadences reference the lint checks in the Lint Workflow and Metadata Lint Workflow sections above.

### Maintenance Cadence

| Cadence | Scope | Trigger | Owner |
|---------|-------|---------|-------|
| Per-session | Lint checks on pages touched during session | Every Claude session that modifies wiki content | Active Claude session |
| Weekly | Full vault lint + graph repair + stale review + contradiction review | Every 7 days or after 3+ ingestion sessions | Dedicated maintenance session |
| Monthly | Ontology audit + semantic drift detection + domain health assessment | First session of each calendar month | Dedicated audit session |

### Per-Session Operations

1. Run all 6 Metadata Lint Workflow steps on pages touched during session
2. Verify all new/modified pages have >=3 outbound wikilinks
3. Check that no new orphan pages were created (0 inbound links)
4. Verify `index.md` reflects any new pages
5. Append session summary to `log.md`

### Weekly Operations

1. Run full Metadata Lint Workflow (all 6 steps) across entire vault
2. Run original Lint Workflow (orphan detection, broken links, stale content, missing sections, duplicate concepts, index sync)
3. Review [[Graph Health Dashboard]] — all 14 queries
4. Remediate orphan pages: add >=3 inbound links or mark `status: stub` with justification
5. Remediate stale pages (>30 days without update): review content, update or set `status: stub`
6. Review all pages tagged `contradiction` — assess whether resolution is possible
7. Verify graph density remains >= 5.0 links/page
8. Log weekly maintenance results to `log.md` with `## [DATE] maintenance | Weekly lint` format

### Monthly Operations

1. **Semantic drift detection**: Review all pages in each domain for ontological consistency. Verify each page's `type` still accurately describes its content.
2. **Domain health assessment**: For each non-empty domain, verify: page count, average link density, stale page ratio, stub ratio. Flag domains where stubs exceed 20% of domain pages.
3. **Contradiction review**: All open contradictions MUST be assessed for resolution. Contradictions older than 60 days require explicit "unresolvable with current sources" annotation or resolution.
4. **Hub connectivity audit**: Verify hub pages (Architecture Overview, Trading Engine Pipeline, Claude-Assisted Trading Stack, Agent Memory Architecture, Autonomous Trading Risk Model) maintain >=10 inbound links each.
5. **Empty domain review**: Assess `market_structure`, `evaluation`, `patterns` for readiness to populate. Document assessment in `log.md`.
6. Log monthly audit results to `log.md` with `## [DATE] audit | Monthly ontology audit` format.

### Operational Thresholds

| Metric | Green | Yellow | Red | Action |
|--------|-------|--------|-----|--------|
| Orphan pages | 0 | 1-2 | 3+ | Red: immediate remediation in current session |
| Stale pages (>30d) | <10% of active | 10-20% | >20% | Yellow: schedule review. Red: mandatory remediation |
| Broken wikilinks | 0 | 1-3 | 4+ | Red: fix all before session ends |
| Pages below 3 inbound links | <5% | 5-15% | >15% | Yellow: add links at next weekly. Red: immediate |
| Graph density (links/page) | >=5.0 | 4.0-4.99 | <4.0 | Red: cross-linking sprint required |
| Hub pages below 10 links | 0 | 1 | 2+ | Red: hub repair in current session |
| Open contradictions >60d | 0 | 1-2 | 3+ | Red: contradiction review session required |

### Graph Repair Procedures

1. **Orphan repair**: Identify the orphan's natural upstream/downstream/sibling concepts. Add wikilinks from at least 3 existing pages. Update the orphan's Related Concepts section.
2. **Weak link repair**: For pages with <3 inbound links, search for pages that mention the concept by name but lack a wikilink. Convert mentions to `[[wikilinks]]`.
3. **Hub repair**: For hubs below 10 links, review all pages in connected domains. Ensure every page in the hub's domain links to the hub. Add the hub to Related Concepts sections where architecturally relevant.
4. **Density repair**: Prioritize pages with <3 outbound links. Add links to Dependencies, Related Concepts, and Architecture Role sections.

---

## MCP Operational Governance

Governs all write operations performed via MCP tools (mcpvault, future MCPs). The MCP Compatibility section above defines read assumptions; this section defines write safety constraints.

### Operation Classification

| Operation | Classification | MCP Tool | Requires Human Review |
|-----------|---------------|----------|----------------------|
| `read_note` | Safe-automated | mcpvault | No |
| `read_multiple_notes` | Safe-automated | mcpvault | No |
| `get_frontmatter` | Safe-automated | mcpvault | No |
| `search_notes` | Safe-automated | mcpvault | No |
| `get_notes_info` | Safe-automated | mcpvault | No |
| `list_all_tags` | Safe-automated | mcpvault | No |
| `list_directory` | Safe-automated | mcpvault | No |
| `get_vault_stats` | Safe-automated | mcpvault | No |
| `update_frontmatter` | Constrained-automated | mcpvault | No, if lint correction only |
| `manage_tags` | Constrained-automated | mcpvault | No, if adding from allowed set |
| `patch_note` | Constrained-automated | mcpvault | Yes, if modifying content sections |
| `write_note` (new page) | Human-review-required | mcpvault | Yes |
| `write_note` (overwrite) | Human-review-required | mcpvault | Yes |
| `move_note` / `move_file` | Human-review-required | mcpvault | Yes |
| `delete_note` | Prohibited | mcpvault | N/A — never permitted |

### Prohibited MCP Operations

1. **Page deletion via MCP**: NEVER use `delete_note`. Set `status: deprecated` instead.
2. **Bulk overwrite without diff review**: NEVER use `write_note` to overwrite existing pages without first reading and diffing content.
3. **Frontmatter field invention**: `update_frontmatter` MUST NOT introduce keys not defined in [[Metadata Migration Plan]].
4. **Enum value invention**: `update_frontmatter` MUST NOT set enum fields to values outside allowed sets.
5. **Cross-domain page moves**: `move_note` MUST NOT move pages to directories that would violate domain-directory binding.
6. **Structural file modification**: NEVER modify `index.md`, `log.md`, or `CLAUDE.md` via automated MCP operations without active Claude session governance.
7. **Tag set expansion via MCP**: `manage_tags` MUST NOT introduce tags outside the allowed set.

### Constrained-Automated Rules

1. `update_frontmatter` may correct enum values to valid values (lint correction) without human review
2. `update_frontmatter` may set `updated` date on substantive content edits without human review
3. `manage_tags` may add tags from the allowed set without human review
4. `manage_tags` may remove inline `#hashtags` when frontmatter `tags:` exists without human review
5. `patch_note` may add wikilinks to Related Concepts, Dependencies, or Source References sections without human review
6. All constrained-automated operations MUST be logged in the active session's `log.md` entry

### Canonical Ownership Protection

1. A page's canonical ownership (one concept = one page) MUST NOT be violated by MCP operations
2. No MCP operation may create a page that duplicates an existing concept — the Redundancy Prevention workflow applies to MCP writes identically
3. `write_note` for new pages MUST be preceded by a `search_notes` call confirming no existing page covers the concept
4. Page renames via `move_note` MUST update all inbound wikilinks across the vault. If this cannot be verified, the operation requires human review.

### MCP Session Logging

All MCP write operations (constrained-automated and human-review-required) MUST be included in the session's `log.md` entry with:
- Operation name (e.g., `update_frontmatter`)
- Target page
- Fields/content modified
- Justification (e.g., "lint correction", "ingestion", "graph repair")

---

## Semantic Retrieval Governance

Governs semantic search and retrieval operations, including Smart Connections MCP and any future embedding-based retrieval tools. Ensures canonical ontology precedence over similarity-based results.

### Canonical Precedence Rules

1. **Exact wikilink match always wins**: If a query matches a page name or alias exactly, that page is the canonical result regardless of embedding similarity scores
2. **Alias resolution before semantic search**: The `aliases` frontmatter field MUST be consulted before falling back to embedding-based similarity
3. **Deprecated pages excluded**: Pages with `status: deprecated` MUST be excluded from semantic retrieval results by default. Include only when explicitly querying historical content.
4. **Stub pages de-prioritized**: Pages with `status: stub` SHOULD be ranked below `status: active` pages at equal similarity scores
5. **Confidence-weighted ranking**: When multiple pages match with similar scores, prefer `confirmed` > `single-source` > `inferred` > `speculative`

### Semantic Ambiguity Handling

1. If two or more pages have similarity scores within 5% of each other, present all candidates to the requesting session and let the context determine which is canonical
2. If ambiguity recurs for the same query pattern, add `aliases` to the most relevant page to improve future resolution
3. NEVER silently pick one candidate over another when scores are within the ambiguity threshold — surface the ambiguity

### Duplicate Detection via Embeddings

1. When creating a new page, compute semantic similarity against all existing pages in the same domain
2. If any existing page has similarity > 85% with the proposed page title + definition section, flag as potential duplicate
3. Potential duplicates MUST be reviewed before page creation proceeds: either merge into the existing page or document why the new page is distinct
4. Periodic duplicate scan (monthly cadence): run semantic similarity across all page pairs within each domain. Flag pairs with > 80% similarity for review.

### False-Positive Mitigation

1. Semantic similarity alone is NOT sufficient evidence of duplication. Pages covering related but distinct concepts (e.g., "Position Sizing" vs "Stop-Loss Systems") may have high similarity but are legitimately separate.
2. Duplicate determination requires: (a) same core definition, (b) same architectural role, (c) same dependencies. All three must overlap.
3. False positives from duplicate scans MUST be annotated so future scans skip known-distinct pairs. Store annotations in [[Graph Health Dashboard]] under a "Known Distinct Pairs" section.
4. Domain boundaries are a strong anti-duplication signal: pages in different domains with high similarity are almost certainly distinct concepts viewed from different architectural angles.

### Retrieval Scope Rules

| Query Context | Retrieval Scope | Exclusions |
|---------------|----------------|------------|
| Ingestion (new source) | All active pages across all domains | deprecated, structural files |
| Graph repair | Pages in target domain + directly linked pages | deprecated |
| Contradiction check | All active pages with overlapping source citations | stubs, deprecated |
| General query | All active + stub pages | deprecated, structural files |
| Historical audit | All pages including deprecated | structural files only |

---

## Ontology Evolution Procedures

Defines formal procedures for modifying the ontology schema: adding/removing enum values, splitting/merging domains, and evolving the type system. All ontology changes are governed by the append-only principle with explicit exceptions for structural changes.

### Change Classification

| Classification | Scope | Examples | Approval | Migration Required |
|---------------|-------|---------|----------|-------------------|
| Minor | New enum value appended | New `type` value, new `source_type` value | Update CLAUDE.md + [[Metadata Migration Plan]] in same session | No |
| Structural | Domain split/merge, type reclassification | Splitting `systems` into `systems` + `pipelines` | Documented proposal in `log.md` + update governance files + migrate affected pages | Yes |
| Breaking | Enum value rename, field rename, field removal | Renaming `type: system` to `type: architecture` | Prohibited under current schema. Requires `schema_version` introduction (see Schema Evolution Procedures) | Full migration |

### Enum Append Procedure (Minor Change)

1. **Justify**: Document why existing enum values are insufficient. The new value MUST NOT overlap semantically with existing values.
2. **Verify no overlap**: For `type`, confirm the new value does not duplicate an existing type's definition (see type table in [[Metadata Migration Plan]]). For `domain`, confirm no existing domain covers the same ontological space.
3. **Update governance files**: Add the new value to the enum table in [[Metadata Migration Plan]] AND to the Allowed Enums list in this file (Frontmatter Governance section).
4. **Update vault structure**: If adding a new `domain`, create the corresponding directory under `/wiki/` and add it to the Vault Structure tree in this file.
5. **Log**: Append `## [DATE] governance | Enum extension: <field>.<value>` to `log.md`.

### Domain Split Procedure (Structural Change)

1. **Proposal**: Document the split rationale in `log.md` with: reason, affected pages, proposed new domain names, page reassignment plan
2. **Impact analysis**: List all pages in the domain being split. For each page, assign it to one of the new domains. Identify ambiguous cases.
3. **Resolve ambiguities**: For each ambiguous page, determine canonical domain based on the page's primary architectural role
4. **Execute**: Create new directory/directories. Move pages. Update `domain` frontmatter on all moved pages. Update `index.md`.
5. **Update governance**: Add new domain(s) to enum tables. Update Vault Structure. Do NOT remove the original domain enum value if any pages remain.
6. **Validate**: Run Domain-Directory Consistency check (Metadata Lint Step 3) across full vault
7. **Log**: Append detailed split record to `log.md`

### Domain Merge Procedure (Structural Change)

1. **Proposal**: Document merge rationale. List all pages in both domains. Identify the surviving domain name.
2. **Execute**: Move all pages from deprecated domain to surviving domain directory. Update `domain` frontmatter.
3. **Deprecate domain**: The deprecated domain's enum value remains in the enum table (append-only) but is annotated as `[deprecated — merged into <surviving>]`.
4. **Update governance**: Annotate deprecated domain in enum table. Update Vault Structure.
5. **Validate**: Run full Metadata Lint Workflow.
6. **Log**: Append merge record to `log.md`

### Domain Deprecation (Without Merge)

1. A domain may be deprecated if it contains 0 pages and no pages are expected
2. The enum value remains in the enum table, annotated as `[deprecated]`
3. The directory may be removed from the vault structure tree but the enum value is NEVER removed
4. Log the deprecation in `log.md`

### Migration Logging Requirements

Every ontology change MUST produce a `log.md` entry with:

| Field | Required | Example |
|-------|----------|---------|
| Date | Yes | `2026-05-15` |
| Change type | Yes | `enum-append`, `domain-split`, `domain-merge`, `domain-deprecate` |
| Affected field(s) | Yes | `type`, `domain` |
| Old value(s) | If applicable | `systems` |
| New value(s) | Yes | `systems`, `pipelines` |
| Pages affected | Yes | Count + list |
| Governance files updated | Yes | `CLAUDE.md`, `Metadata Migration Plan` |

---

## Observability Operations

Defines operational procedures for interpreting [[Graph Health Dashboard]] metrics, triggering remediation, and maintaining observability infrastructure. The Observability Standards table in the Dataview Governance section above defines targets; this section defines the response procedures.

### Dashboard Review Cadence

| Cadence | Dashboard Sections to Review | Action |
|---------|------------------------------|--------|
| Per-session | Pages Missing Frontmatter, Orphan Pages | Fix any issues found before session ends |
| Weekly | All 14 queries | Log results summary in `log.md` |
| Monthly | All 14 queries + trend analysis (compare to previous month) | Document trends, flag degradation |

### Per-Metric Remediation Workflows

**Frontmatter Coverage (target: 100%)**
- Trigger: Any page appears in "Pages Missing Frontmatter" query
- Action: Add universal frontmatter block immediately. Set `created` to page's git creation date. Set `updated` to current date. Set `status: draft` until content is verified.
- Escalation: None — always fixable in-session.

**Schema Compliance (target: 0 invalid enums)**
- Trigger: Any enum value not in allowed set
- Action: Correct to nearest valid enum. If no clear nearest value exists, document the ambiguity in `log.md` and select the best fit.
- Escalation: If the invalid value represents a genuinely new concept type, trigger Enum Append Procedure (see Ontology Evolution Procedures).

**Domain-Directory Consistency (target: 100%)**
- Trigger: `domain` field does not match page's directory
- Action: Correct `domain` to match directory. If the page is in the wrong directory, assess whether to move the page (requires human review) or correct the `domain` field.
- Escalation: If many pages in a domain have wrong directories, suspect an unmigrated domain split. Trigger full domain audit.

**Orphan Pages (target: 0)**
- Trigger: Any page with 0 inbound links (excluding structural files)
- Action: Follow Graph Repair Procedure for orphans (see Continuous Ontology Operations). Add >=3 inbound links from architecturally related pages.
- Escalation: If an orphan has no natural connections to any existing page, flag for human review — it may indicate a missing domain or a page that should not exist.

**Stale Pages >30 days (target: <10% of active)**
- Trigger: Count of stale active pages exceeds 10% of total active pages
- Action: Review each stale page. Three outcomes: (a) update content if outdated, (b) confirm content is current and touch `updated` date, (c) set `status: stub` if content is insufficient.
- Escalation: If stale pages exceed 20%, dedicate a full maintenance session to stale page remediation.

**Link Density (target: >=5.0 links/page)**
- Trigger: Vault-wide links/page ratio drops below 5.0
- Action: Identify pages with lowest outbound link counts. Add wikilinks to Dependencies, Related Concepts, Architecture Role sections.
- Escalation: If density drops below 4.0, cross-linking sprint required (see Graph Repair Procedures).

**Weakly Connected Pages (<3 inbound or <3 outbound)**
- Trigger: Page appears in Weakly Connected query
- Action: Add links until page has >=3 in each direction
- Escalation: None — always fixable.

**Stub Count (target: <5% of total)**
- Trigger: Stub count exceeds 5% of total pages (currently >2.85 pages at 57 total)
- Action: Prioritize stubs by domain importance. Expand highest-value stubs first.
- Escalation: If stubs exceed 10%, dedicate a session to stub expansion.

**Source Coverage**
- Trigger: Raw source file exists in `/raw/` with no corresponding `SRC -` page in `/wiki/sources/`
- Action: Ingest the unprocessed source using the Ingestion Workflow.
- Escalation: None — always actionable.

**Contradiction Registry**
- Trigger: Any page tagged `contradiction` with no resolution for >60 days
- Action: Review contradiction. Attempt resolution with available sources. If unresolvable, annotate with "unresolvable with current sources — requires additional ingestion".
- Escalation: If open contradictions exceed 3, schedule dedicated contradiction resolution session.

### Escalation Logic Summary

| Condition | Escalation Level | Response |
|-----------|-----------------|----------|
| Single metric in Yellow | Normal | Address during next scheduled maintenance cadence |
| Single metric in Red | Elevated | Address in current session before concluding |
| 2+ metrics in Red | Critical | Dedicate full session to remediation; log as `## [DATE] emergency | Graph health remediation` |
| Metric trend degrading over 3+ weeks | Structural | Review whether governance rules need amendment; consider new lint checks |

### Dashboard Maintenance

1. [[Graph Health Dashboard]] is the single source of truth for all observability queries. No additional dashboard pages without governance approval.
2. New Dataview queries may be added to the dashboard during any session, but MUST follow Dataview Governance approved query patterns.
3. Queries that become obsolete (e.g., migration-era checks after stability is confirmed) may be annotated with `<!-- historical -->` but MUST NOT be deleted.
4. Dashboard page itself has `type: observability` and follows all frontmatter rules.

---

## Semantic Confidence Lifecycle

Defines the promotion, demotion, and staleness rules for the `confidence` enum field. Confidence reflects the epistemic status of a page's core claims and MUST be actively maintained, not set once and forgotten.

### Confidence State Transitions

| From | To | Trigger | Action |
|------|----|---------|--------|
| `speculative` | `inferred` | Claude synthesis provides logical derivation from confirmed facts | Add reasoning chain to page. Update `confidence`. |
| `inferred` | `single-source` | A source document directly supports the page's claims | Add `Source: [[SRC - ...]]` citation. Update `confidence`. |
| `single-source` | `confirmed` | A second independent source corroborates the claims | Add second source citation. Update `confidence`. |
| `confirmed` | `single-source` | One of two sources is retracted, deprecated, or found unreliable | Remove unreliable source citation. Update `confidence`. |
| `single-source` | `inferred` | The supporting source is deprecated or found unreliable | Remove source citation. Document why claim is still believed. Update `confidence`. |
| `inferred` | `speculative` | Reasoning chain found to be weak or based on incorrect assumptions | Document the weakness. Update `confidence`. |
| Any | `speculative` | Contradiction detected with a higher-confidence source | Tag page with `contradiction`. Document conflicting claims. Demote `confidence` to `speculative` pending resolution. |

### Promotion Rules

1. **speculative -> inferred**: Requires documented reasoning chain connecting the page's claims to confirmed facts. The reasoning must be explicit in the page content.
2. **inferred -> single-source**: Requires at least one `Source: [[SRC - ...]]` reference that directly states (not implies) the page's core claims.
3. **single-source -> confirmed**: Requires two or more independent source citations. "Independent" means different source documents, not different sections of the same document.
4. Promotion MUST update the `confidence` field AND the `updated` field (this counts as a substantive content edit because source attribution changed).

### Demotion Rules

1. Demotion occurs when supporting evidence is weakened, not when new evidence merely adds nuance
2. Source deprecation (source page set to `status: deprecated`) triggers review of all pages citing that source. If the deprecated source was the only source, demote from `single-source` to `inferred`.
3. Contradiction discovery triggers immediate demotion to `speculative` for the lower-confidence side of the contradiction. If both sides are equal confidence, both demote.
4. Demotion MUST be logged in the session's `log.md` entry with: page name, old confidence, new confidence, reason

### Multi-Source Validation Standards

1. For `confirmed` status, sources must be **independent**: distinct documents from distinct contexts. Two YouTube transcripts from the same creator describing the same system count as one source (same perspective).
2. For `confirmed` status, sources must **agree on core claims**. Agreement on peripheral details is insufficient.
3. Source types carry different weight for validation purposes but all count equally toward the two-source threshold for `confirmed`:
   - `architecture_doc` + `product_spec` from the same project = 1 source perspective (not independent)
   - `youtube_transcript` from creator A + `architecture_doc` from creator B = 2 independent sources

### Stale Confidence Detection

A page's confidence is considered **stale** if: the page has `confidence: single-source` or `confidence: inferred` AND `updated` is older than 60 days AND no new sources have been ingested in the page's domain since the page was last updated.

Stale confidence does NOT automatically trigger demotion. It triggers review during the monthly audit (see Continuous Ontology Operations).

Dataview query for stale confidence:

```dataview
TABLE confidence, updated, domain
FROM "wiki"
WHERE confidence != null AND confidence != "confirmed"
AND date(updated) < date(today) - dur(60 days)
AND status = "active"
SORT confidence ASC, updated ASC
```

### Contradiction-Triggered Confidence Review

1. When a contradiction is discovered between two pages, assess the `confidence` of both pages
2. The page with lower confidence is demoted first (see Demotion Rules)
3. If both pages have equal confidence, both receive `tags: [contradiction]` and both are demoted one level
4. Resolution of the contradiction restores confidence based on which claim survives. The surviving claim's page may be promoted; the losing claim's page is corrected.
5. All contradiction-triggered confidence changes MUST be documented in both pages' `## Contradictions` sections and in `log.md`

---

## Schema Evolution Procedures

Defines formal procedures for evolving the frontmatter schema: adding fields, extending enums, deprecating fields, and managing backward compatibility. The Metadata Anti-Entropy Rules above define what is prohibited; this section defines the safe evolution paths.

### Evolution Principles

1. **Append-only enums**: Enum values are never renamed or removed. New values may be appended via the Enum Append Procedure.
2. **Additive field changes**: New fields may be added; existing fields are never renamed or removed.
3. **Backward compatibility**: All existing Dataview queries on [[Graph Health Dashboard]] MUST continue to function after any schema change.
4. **Governance-first**: Every schema change is documented in [[Metadata Migration Plan]] and this file BEFORE being applied to any page.
5. **No silent evolution**: Schema changes not reflected in governance files are schema drift and are prohibited.

### Field Addition Procedure

1. **Justify**: Document why existing fields cannot represent the needed information. New fields MUST NOT overlap semantically with existing fields.
2. **Classify**: Assign the field to a metadata class: Universal, Domain-specific, Optional, or Derived (see [[Metadata Migration Plan]] Part 2.1).
3. **Define**: Specify field name, data type (string, date, enum, array), allowed values (if enum), and default value (if any).
4. **Impact assessment**: Determine how many existing pages need the new field. If Universal, all pages require update. If Optional, no existing pages require update.
5. **Dataview impact**: Verify that existing Dataview queries on [[Graph Health Dashboard]] will not break. Add null-safety if the new field is queried.
6. **Update governance**: Add field definition to [[Metadata Migration Plan]] schema section AND this file's Frontmatter Governance section.
7. **Roll out**: Apply the field to affected pages. For Universal fields, use a phased approach (hub pages first, then remaining). For Optional fields, add only where relevant.
8. **Validate**: Run Metadata Lint Workflow to confirm all pages remain compliant.
9. **Log**: Append `## [DATE] schema | Field addition: <field_name>` to `log.md`.

### Enum Extension Procedure

Additional constraints beyond the Enum Append Procedure in Ontology Evolution Procedures:

1. New enum values MUST be lowercase, hyphen-separated (matching existing convention: `single-source`, `youtube_transcript`)
2. New enum values MUST NOT be substrings of existing values (e.g., do not add `system` if `systems` already exists in a different enum)
3. New enum values MUST be documented with a description in the enum table in [[Metadata Migration Plan]]
4. After adding an enum value, verify that all Dataview queries using `GROUP BY` on that enum's field correctly include the new value

### Field Deprecation Procedure

1. Fields are NEVER removed from the schema. Deprecated fields are annotated as `[deprecated]` in governance files.
2. Deprecated fields may remain in existing page frontmatter. They are ignored by lint workflows.
3. New pages MUST NOT include deprecated fields.
4. Dataview queries MUST NOT rely on deprecated fields. Update queries to use replacement fields.
5. Document deprecation: which field is deprecated, why, what replaces it (if anything), date of deprecation.
6. Log: Append `## [DATE] schema | Field deprecation: <field_name>` to `log.md`.

### Schema Version Introduction Conditions

A `schema_version` field is NOT currently in the schema. It SHOULD be introduced when ANY of these conditions are met:

1. A breaking change is unavoidable (field rename, enum rename, field removal)
2. The schema has undergone 5+ cumulative field additions since migration completion
3. An external tool (MCP, automation) requires version-gated field access
4. A migration from one schema shape to another affects >50% of pages

When introduced:
- `schema_version` becomes a Universal required field
- Initial value: `1` (integer)
- All existing pages receive `schema_version: 1` via batch update
- Future schema changes increment the version when they cross breaking-change boundaries
- Dataview queries and MCP tools may use `schema_version` to handle multi-version pages during migration windows

### Backward Compatibility Rules

1. Every schema change MUST include a Dataview compatibility assessment: will existing queries on [[Graph Health Dashboard]] return correct results?
2. If a schema change would cause a query to silently return wrong results (not just empty results), the change is classified as breaking and requires `schema_version` introduction
3. Queries MUST always use null-safe comparisons (`WHERE field != null`) to handle pages that may not yet have new fields
4. During migration windows (when some pages have new fields and others do not), Dataview queries MUST gracefully handle both states

---

## Automated Maintenance Governance

Defines the boundaries of automated (MCP-assisted or script-assisted) maintenance operations. Distinguishes safe-automated operations from those requiring human judgment. All automation operates under the governance constraints defined in MCP Operational Governance above.

### Operation Safety Classification

| Operation Category | Classification | Examples | Automation Permitted |
|-------------------|---------------|----------|---------------------|
| Read/query | Safe-automated | Dataview queries, `search_notes`, `get_frontmatter`, `get_vault_stats` | Yes, unrestricted |
| Lint detection | Safe-automated | Missing frontmatter scan, invalid enum scan, stale metadata scan | Yes, unrestricted |
| Lint correction (frontmatter) | Constrained-automated | Fix invalid enum, correct domain-directory mismatch, add missing required fields | Yes, with logging |
| Link addition | Constrained-automated | Add wikilink to Related Concepts section | Yes, with logging |
| Tag correction | Constrained-automated | Remove inline tags when frontmatter tags exist, add tags from allowed set | Yes, with logging |
| Content modification | Human-review-required | Rewriting sections, resolving contradictions, expanding stubs | No automation without human in loop |
| Page creation | Human-review-required | New canonical pages, new source pages | No automation without human in loop |
| Page deprecation | Human-review-required | Setting `status: deprecated` | No automation without human in loop |
| Schema modification | Human-review-required | Changing CLAUDE.md, [[Metadata Migration Plan]] | No automation without human in loop |
| Page deletion | Prohibited | Removing files from vault | Never automated, never permitted |
| Structural file modification | Prohibited-automated | `index.md`, `log.md`, `CLAUDE.md` via unattended automation | Requires active governance session |

### MCP-Assisted Maintenance Workflows

**Workflow 1: Automated Lint Pass**

Permitted as constrained-automated:
1. Use `get_vault_stats` to assess vault health
2. Use `list_directory` + `get_frontmatter` to scan all pages for schema compliance
3. For each non-compliant page, use `update_frontmatter` to correct: invalid enum values (to nearest valid), missing required fields (using defaults: `status: draft`, `created: <today>`, `updated: <today>`), domain-directory mismatches (correct `domain` to match directory)
4. Log all corrections to `log.md`

**Workflow 2: Automated Cross-Link Enhancement**

Permitted as constrained-automated:
1. Use `search_notes` to find pages that mention a concept by name but lack a wikilink
2. Use `patch_note` to add `[[wikilink]]` format where plain-text concept names appear
3. Scope: Only add links to existing pages. NEVER create new pages.
4. Scope: Only modify Related Concepts, Dependencies, or Architecture Role sections. NEVER modify Definition, Purpose, or other substantive sections.
5. Log all link additions to `log.md`

**Workflow 3: Automated Stale Detection Report**

Permitted as safe-automated:
1. Query all pages with `updated` > 30 days old and `status: active`
2. Generate a report listing stale pages by domain, sorted by staleness
3. Output report to active session. Do NOT modify any pages.
4. Human reviews report and decides which pages to update, stub, or confirm as current

### Automation Boundaries

1. **No autonomous content generation**: Automation may fix metadata, add links, and correct enums. It MUST NOT generate, rewrite, or expand page content without an active Claude governance session directing it.
2. **No autonomous page creation**: The decision to create a new page requires human judgment about canonical ownership, naming, domain assignment, and content scope.
3. **No autonomous deprecation**: Setting `status: deprecated` has graph-wide implications and requires human assessment.
4. **No autonomous contradiction resolution**: Contradictions require judgment about which claim is correct. Automation may detect contradictions but MUST NOT resolve them.
5. **Logging is mandatory**: Every automated write operation MUST produce a `log.md` entry. If logging fails, the automated operation MUST halt.
6. **Rollback capability**: Every automated batch operation MUST be preceded by a git commit, ensuring full rollback capability.
7. **Batch size limits**: Automated lint corrections MUST NOT modify more than 15 pages in a single unreviewed batch. Larger batches require mid-batch human review checkpoint.

### Automation Escalation Triggers

| Trigger | Condition | Response |
|---------|-----------|----------|
| Ambiguous enum correction | No single "nearest valid" enum exists | Stop. Log ambiguity. Request human decision. |
| Missing page for wikilink | Automated cross-link finds a concept name matching no existing page | Stop. Do not create page. Log the gap. |
| Domain-directory conflict | Page could belong to two domains | Stop. Log conflict. Request human decision. |
| Batch error rate >10% | More than 10% of corrections in a batch produce unexpected results | Halt batch. Log errors. Request human review. |
| Structural file encountered | Automation targets `index.md`, `log.md`, or `CLAUDE.md` | Skip file. Log skip. Requires governance session. |
