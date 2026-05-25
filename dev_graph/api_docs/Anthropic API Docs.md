---
type: api_doc_source
status: active
implementation_status: not-started
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
source_paths:
  - "wiki/infrastructure/Claude Code.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
provider: "Anthropic"
doc_source: "https://docs.anthropic.com"
doc_scope: "Messages API, Tool Use, Claude Agent SDK, Anthropic SDK"
allowed_for_tasks:
  - "agent implementation"
  - "tool use integration"
  - "prompt engineering"
  - "Claude API client code"
  - "agent orchestration"
freshness_requirement: current
---

# Anthropic API Docs

## Definition

API documentation source node for the Anthropic/Claude API. Canonical reference for all Claude integration and agent implementation code.

## Purpose

Ensures Claude Code sessions use current Anthropic API documentation when building agent orchestration, tool use, and LLM integration components of the trading system.

## Architecture Role

Core AI infrastructure documentation source. Claude is the primary runtime for the autonomous trading engine — both as the coding agent (Claude Code) and as the trading decision agent.

## API Scope

- **Messages API**: Core conversational API with system prompts, tool use, streaming
- **Tool Use**: Function calling, tool definitions, tool results
- **Claude Agent SDK**: Building custom agents with tool use and orchestration
- **Anthropic SDK**: Python (`anthropic`) and TypeScript (`@anthropic-ai/sdk`) client libraries
- **Model IDs**: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001

## Retrieval Method

**Primary**: context7 MCP
1. `resolve-library-id` with query "anthropic claude api sdk"
2. Select best match
3. `query-docs` with specific implementation question

**Fallback**: Web fetch from `https://docs.anthropic.com`

## Authentication

- API Key via `ANTHROPIC_API_KEY` environment variable
- Usage tracked per API key

## Wiki Reference

See `wiki/infrastructure/Claude Code.md` for Claude Code capabilities and integration patterns.

## Version Notes

- Latest model family: Claude 4.5/4.6
- Messages API is current; legacy Completion API is deprecated
- Tool use supports parallel tool calls
- Agent SDK supports custom agent workflows

## Relationships

### Depends On

### Provides
- Anthropic API documentation for implementation context packs

### Validated By

### Constrained By
- [[API Documentation Policy]]

### Supersedes

### Used By
- Future agent implementation module nodes
- Future orchestration workflow nodes

### Produces

### Consumes
