---
type: system
canonical_id: SYS-004
status: active
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/memory/Agent Memory Architecture.md"
  - "wiki/memory/Context Budget Engineering.md"
  - "wiki/governance/Trade Logging.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
system_id: "agent-runtime"
bounded_context: "State persistence, context assembly, and trade logging. Provides the memory and continuity infrastructure that enables stateless agent invocations to behave as a continuous system. Services all other systems via the Memory API."
contains_capabilities:
  - "[[State Persistence]]"
  - "[[Context Assembly]]"
  - "[[Trade Logging]]"
upstream_systems: []
downstream_systems: []
---

# Agent Runtime

## Definition

Bounded context responsible for agent memory persistence, context window assembly, and trade logging. Implements the Wake-Execute-Sleep lifecycle that enables stateless Claude invocations to maintain continuity across sessions. Provides memory services to ALL other systems.

## Purpose

Solves the fundamental problem of agentic trading: each routine fires with no inherent state. The Agent Runtime reconstructs operational context from persistent files, provides it to the executing agent, and persists results before the session ends.

## Architecture Role

Infrastructure system that services all other bounded contexts. Unlike the Data Pipeline → Trading Engine → Evaluation Loop pipeline, the Agent Runtime operates LATERALLY — every system reads from and writes to agent memory. The Memory API is the most widely consumed interface in the system.

## Bounded Context Scope

| In Scope | Out of Scope |
|----------|-------------|
| File-based memory (CLAUDE.md, strategy, trade-log, research-log) | Market data acquisition |
| Context window assembly and token budgeting | Signal generation |
| Trade log persistence and journaling | Order execution |
| Git-based remote persistence (commit + push) | Risk validation |
| Memory file truncation and rotation | Performance scoring |

## Capabilities

3 capabilities (created in Phase 3):
1. **State Persistence** (CAP-010) — read/write memory files, git persistence, file rotation
2. **Context Assembly** (CAP-011) — assemble context window within token budget, prioritize reads
3. **Trade Logging** (CAP-012) — structured trade journaling for compliance, evaluation, and learning

## Key Interfaces

- **Memory API** (INT-004) — bidirectional with all systems (memory read/write)
- **Trade Log API** (INT-005) — receives trade data from Trading Engine, serves Evaluation Loop

## Constraints

- Every agent session MUST read CLAUDE.md before any other action
- Every agent session MUST persist results before termination
- Memory files must be concise — trade logs may need truncation to prevent context overflow
- Git commit frequency: at least once per routine for remote deployments
- Token budget: ~200K per routine, allocated across structural memory, operational memory, reasoning, and output

## Relationships

### Contains
- (Forward references: State Persistence, Context Assembly, Trade Logging — Phase 3)

### Depends On

### Provides
- Memory services to all systems
- Trade log data to Evaluation Loop

### Constrained By

### Used By
- [[Trading Engine]]
- [[Evaluation Loop]]
- [[Supervisor Office]]
- [[Data Pipeline]]

### Originates From
- [[Stateless Agent Architecture]]
- [[Context Engineering]]
