---
type: governance
canonical_id: GOV-007
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - external
source_paths:
  - "wiki/integrations/MCP Architecture.md"
  - "wiki/integrations/Alpaca API.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# API Documentation Policy

## Definition

Governs which API documentation sources are admissible in coding context packs, how they are retrieved, and how freshness is maintained.

## Purpose

Ensures Claude Code sessions use current, verified API documentation rather than stale training data. Prevents hallucinated API calls by requiring explicit documentation source nodes.

## Architecture Role

Controls the docs layer of the retrieval pipeline. Only API documentation sources with a corresponding `api_doc_source` node in `dev_graph/api_docs/` are admissible.

## Admissibility Rules

1. **Node required**: Every API used in code MUST have a corresponding `api_doc_source` node in `dev_graph/api_docs/`
2. **No undocumented APIs**: If no `api_doc_source` node exists, create one before using the API in a context pack
3. **Freshness check**: The `freshness_requirement` field on the node determines how current docs must be
4. **Version match**: The `doc_scope` and any version fields must match the version actually used in code

## Freshness Requirements

| Freshness Level | Meaning | Max Age |
|---|---|---|
| `current` | Must be fetched fresh each session | 0 days (always re-fetch) |
| `required` | Must be verified within 90 days | 90 days |
| `stable` | Unlikely to change; verify quarterly | 180 days |

## Retrieval Methods

### Context7 (preferred for library docs)
1. `resolve-library-id` with the library name
2. Select best match by: exact name, description relevance, snippet count, source reputation
3. `query-docs` with the selected library ID and the user's full question
4. Cite the retrieved docs in the context pack

### Web Fetch (for REST APIs)
1. Fetch the canonical documentation URL from the `api_doc_source` node
2. Parse relevant sections
3. Cite with URL and retrieval date

### Manual (for local/private docs)
1. Read documentation from local filesystem paths specified in the node
2. Cite with file path

## Permitted Documentation Sources (Initial)

| Provider | Node | Retrieval Method |
|---|---|---|
| Alpaca | [[Alpaca API Docs]] | context7 |
| Anthropic | [[Anthropic API Docs]] | context7 |

Additional providers should be added as `api_doc_source` nodes when their APIs are actively used in implementation.

## Stale Documentation Handling

1. Before using API docs in a context pack, check the `freshness_requirement` against last retrieval date
2. If stale, re-fetch before including in context
3. If re-fetch fails, note staleness in the context pack and proceed with caution
4. Update `freshness_check` date on the `api_doc_source` node after successful retrieval

## Context Pack Integration

API documentation is included in context packs under the "Required API Docs" section:
- List each API doc source with its provider and version
- Note retrieval method and date
- Flag any freshness warnings

## Relationships

### Depends On
- [[Dev Graph Governance]]

### Provides
- API documentation governance for all context packs

### Validated By

### Constrained By

### Supersedes

### Used By
- [[Context Pack Assembly Rules]]
- [[Alpaca API Docs]]
- [[Anthropic API Docs]]

### Produces

### Consumes
