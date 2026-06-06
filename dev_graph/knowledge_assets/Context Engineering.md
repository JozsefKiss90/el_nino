---
type: knowledge_asset
canonical_id: KA-007
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
source_paths:
  - "wiki/memory/Context Budget Engineering.md"
  - "wiki/memory/Agent Memory Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
knowledge_id: "KA-007"
knowledge_type: principle
source_wiki_pages:
  - "wiki/memory/Context Budget Engineering.md"
  - "wiki/memory/Agent Memory Architecture.md"
  - "wiki/integrations/MCP Architecture.md"
informs_decisions: []
informs_architecture:
  - "[[Context Map]]"
external_references: []
---

# Context Engineering

## Definition

The engineering principle that LLM agent context windows are finite resources that must be budgeted, prioritized, and managed like financial capital. Every file read, every tool call, every piece of memory loaded into context costs tokens and reduces the remaining budget for reasoning.

## Purpose

Explains WHY the Agent Runtime system has Context Assembly as a dedicated capability, WHY context packs are typed and admissibility-checked, and WHY the dev_graph itself serves as a structured retrieval substrate rather than dumping all knowledge into context.

## Architecture Role

Foundational knowledge asset. Motivates the Context Assembly capability, the Context Pack Assembly Rules, the Admissibility Checks governance, and the token budget allocation model.

## Core Principles

1. **Tokens are money**: "Treat tokens like money. Every file that you ask the agent to read is going to cost you." Every context loading decision has an opportunity cost.
2. **Budget before load**: Estimate token cost of each context element before loading it. Prioritize: constraints > decisions > in-scope files > tests > related modules > docs.
3. **Structured retrieval over full dump**: Use typed nodes, frontmatter filtering, and graph traversal to select exactly the right context — not "load everything related."
4. **Admissibility gates**: Not every node deserves context space. The 9 admissibility checks filter out deprecated, stale, malformed, and contradicted nodes.
5. **Intent-aware routing**: Different tasks need different context. Implementation tasks start at capabilities; architecture questions start at architecture nodes. The routing table prevents loading irrelevant context.
6. **Context budget structure**: System instructions (~5%), structural memory (~10%), operational memory (~15%), API calls (~20%), reasoning (~30%), output (~10%).

## Architectural Constraints

- Context packs should target <50% of available context window to leave room for reasoning
- If over budget, trim optional reads first, then related modules
- Every context pack must include CLAUDE.md as the first read

## Relationships

### Provides
- Foundational principle for context-aware agent design

### Used By
- [[Context Map]]

### Originates From
