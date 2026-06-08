---
type: capability
canonical_id: CAP-010
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
  - "wiki/agents/Stateless Agent Recovery.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
capability_id: "state-persistence"
parent_system: "[[Agent Runtime]]"
implemented_by: []
interfaces:
  - "[[Memory API]]"
---

# State Persistence

## Definition

The capability to read, write, and manage persistent memory files that enable stateless agent invocations to maintain continuity. Implements the Wake (read) and Sleep (write) phases of the agent lifecycle.

## Purpose

Solves the fundamental statelessness problem. Each routine fires with no inherent state — State Persistence reconstructs context from files and persists results before session end.

## Architecture Role

Foundation capability of Agent Runtime. All other systems depend on memory for operational continuity.

## Inputs

- Memory files: CLAUDE.md, strategy.md, trade-log, research-log, weekly-review, memory-notes
- Git state (for remote persistence)

## Outputs

- Reconstructed agent context (wake phase)
- Updated memory files (sleep phase)
- Git commits (remote persistence)

## Constraints

- Read-before-act: agent MUST read CLAUDE.md before any action
- Write-before-exit: agent MUST persist results before termination
- Git commit after every routine for remote deployments

## Relationships

### Contains

### Depends On

### Provides
- Memory services to all systems via Memory API

### Realizes
- [[Context Assembly Pattern]]

### Justified By
- [[ADR - Ontology Redesign]]

### Originates From
- [[Stateless Agent Architecture]]
