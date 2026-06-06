---
type: knowledge_asset
canonical_id: KA-009
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
source_paths:
  - "wiki/memory/Agent Memory Architecture.md"
  - "wiki/agents/Stateless Agent Recovery.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions: []
knowledge_id: "KA-009"
knowledge_type: principle
source_wiki_pages:
  - "wiki/memory/Agent Memory Architecture.md"
  - "wiki/agents/Stateless Agent Recovery.md"
  - "wiki/infrastructure/Claude Routines.md"
informs_decisions: []
informs_architecture:
  - "[[Context Map]]"
external_references: []
---

# Stateless Agent Architecture

## Definition

The engineering principle that each agent invocation starts with zero inherent state. Continuity, discipline, and personality are reconstructed from persistent files read at the start of every session. The agent follows a Wake-Execute-Sleep cycle: read context, perform task, persist results.

## Purpose

Explains WHY the Agent Runtime system exists with State Persistence and Context Assembly as dedicated capabilities. The agent has no runtime memory between invocations — everything must be file-mediated.

## Architecture Role

Foundational knowledge asset. Motivates the Agent Runtime system, the Memory API interface, the file-based memory architecture, and git as the persistence layer.

## Core Principles

1. **Wake-Execute-Sleep**: Every routine invocation follows the same lifecycle. Wake: read CLAUDE.md, strategy, trade log, research log. Execute: perform the task. Sleep: write results, commit, push.
2. **Files are personality**: CLAUDE.md defines agent identity, rules, and constraints (500-2000 tokens). The agent's "discipline" is encoded in files, not in runtime state.
3. **Read-before-act, write-before-exit**: These are non-negotiable principles. An agent that acts without reading context is dangerous. An agent that exits without writing results loses work.
4. **Structural vs. operational memory**: Structural memory (CLAUDE.md, strategy.md, commands/) is read-mostly and defines WHO the agent is. Operational memory (trade-log, research-log, weekly-review) is read-write and records WHAT the agent has done.
5. **Git as persistence layer**: For remote routines (Railway, cloud), git commit + push after each session ensures memory survives across deployments.
6. **Token-budgeted memory**: With ~200K tokens per routine, every memory file loaded costs reasoning capacity. Memory must be concise and prioritized.

## Architectural Constraints

- Every agent session MUST read CLAUDE.md before any other action
- Every agent session MUST persist results before termination
- Memory files MUST be concise — trade logs may need truncation to prevent context overflow
- Git commit frequency: at least once per routine execution for remote deployments

## Relationships

### Provides
- Foundational principle for stateless agent continuity

### Used By
- [[Context Map]]

### Originates From
