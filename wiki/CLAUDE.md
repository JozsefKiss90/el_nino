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
