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
