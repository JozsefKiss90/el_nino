---
type: integration
domain: integrations
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Perplexity, AI Research API]
confidence: single-source
tags: [integration]
---

# Perplexity API

## Definition

AI-powered web search API used for market research, catalyst identification, and news analysis in pre-market trading routines. Alternative to Claude Code's native web search and web fetch.

## Purpose

Provides structured, high-quality web research for the [[Trading Engine Pipeline]] research stage. Preferred over native web search for depth and relevance.

## Architecture Role

Research tool in [[Claude-Assisted Trading Stack]]. Feeds into pre-market routine of [[Claude Routines]].

## Usage

The pre-market routine (6:00 AM) uses Perplexity to:
- Scan for overnight market-moving news
- Identify earnings catalysts
- Research macro events
- Check sector rotation signals

## Configuration

```
PERPLEXITY_API_KEY=...
```

API key found in Perplexity settings under "API platform" → "API keys."

Source: [[SRC - Claude Opus Trader]]

## Inputs

- Research queries (market news, company analysis, macro events)
- API key from environment variables

## Outputs

- Structured research findings
- Source citations
- Catalyst assessments

## Dependencies

- [[Claude Code]] or [[Claude Routines]] — runtime
- [[Environment Variable Management]] — key storage

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Perplexity vs. native web search | Better structured results vs. additional API dependency and cost |

## Related Concepts

- [[Claude-Assisted Trading Stack]]
- [[Trading Engine Pipeline]]
- [[Claude Routines]]
- [[Research Ingestion Workflow]]

## Source References

- Source: [[SRC - Claude Opus Trader]] — "use Perplexity for research rather than just the native Cloud Code web search"
