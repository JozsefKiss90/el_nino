# SRC - LLM Wiki Methodology

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/llm-wiki.md` (actually root `llm-wiki.md`) |
| Type | Methodology document |
| Author | Karpathy-style pattern description |
| Date Ingested | 2026-05-09 |

## Summary

Defines the "persistent synthesis" pattern for building knowledge bases with LLMs. The LLM incrementally builds and maintains a structured wiki from raw sources, rather than re-deriving knowledge via RAG on every query. Three-layer architecture: raw sources (immutable), wiki (LLM-maintained), schema (configuration).

## Key Concepts Extracted

- [[Research Ingestion Workflow]] — ingest operation (read, extract, update, cross-link, index, log)
- [[Agent Memory Architecture]] — wiki as persistent, compounding artifact
- [[Context Budget Engineering]] — index.md as context-efficient navigation
- Lint workflow — contradiction detection, orphan detection, gap analysis

## Core Architecture

Three layers:
1. **Raw sources**: Immutable source documents. LLM reads but never modifies.
2. **Wiki**: LLM-generated markdown files. Summaries, entity pages, concept pages, cross-references.
3. **Schema**: Configuration document (CLAUDE.md) defining conventions and workflows.

## Operations

- **Ingest**: Process new source → update wiki pages → index → log
- **Query**: Search wiki → synthesize answer → optionally file back into wiki
- **Lint**: Health check for contradictions, orphans, stale content, gaps

## Key Insight

> "The wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read."

## Concepts Referenced

- [[Architecture Overview]]
- [[Research Ingestion Workflow]]
- [[Agent Memory Architecture]]
