---
type: governance
canonical_id: GOV-002
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: inferred
evidence:
  - design
  - wiki
source_paths:
  - "wiki/memory/Context Budget Engineering.md"
  - "wiki/CLAUDE.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
  - "[[Frontmatter Required]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Context Pack Assembly Rules

## Definition

Rules governing how typed implementation context packs are assembled for Claude Code sessions.

## Purpose

Context packs are ordered reading lists of dev_graph nodes that give Claude Code all the information needed for a specific coding task. This document defines how to assemble them correctly.

## Architecture Role

Bridges the gap between semantic retrieval (which proposes context) and validated implementation context (which Claude Code uses). Context packs are the final output of the retrieval pipeline.

## Assembly Sequence

### Step 1: Parse Task Request
Identify the task type (implementation, refactor, validation, debugging, migration) and the affected modules/files.

### Step 2: Semantic Retrieval
Use Smart Connections to find semantically related dev_graph nodes.

### Step 3: Dataview Filtering
Filter retrieved nodes by:
- `canonical: true`
- `status` is not `deprecated`
- `implementation_status` is not `deprecated`
- `type` is in the allowed type enum
- Required frontmatter fields exist

### Step 4: Graph Expansion
From filtered nodes, expand via relationship sections:
- Dependencies (modules that the change depends on)
- Files (actual source files in scope)
- Tests (test files that must pass or be updated)
- Constraints (hard rules that must not be violated)
- Decisions (ADRs that govern the change)
- Schemas (artifact schemas that constrain outputs)
- Gates/Predicates (checks that must pass)

### Step 5: Codebase Grounding
Use filesystem/Git MCP to verify current state of referenced files. Discard nodes pointing to files that no longer exist unless the task is to create them.

### Step 6: Docs Retrieval
Use context7/docs MCP to retrieve only permitted API documentation per [[API Documentation Policy]].

### Step 7: Admissibility Check
Run all 9 admissibility checks from [[Admissibility Checks]] on every node in the pack.

### Step 8: Assemble Pack
Create the final context pack using the [[Context Pack Template]] format.

## Required Reads (always include, in order)

1. `dev_graph/CLAUDE.md` — always first
2. Relevant constraint nodes from `dev_graph/constraints/`
3. Relevant decision records from `dev_graph/decisions/`
4. Relevant governance policies (only if task touches governance)
5. Module/file nodes in scope of change
6. Test nodes that must be updated or verified
7. Gate/predicate nodes that must pass

## Optional Reads (if token budget allows)

- Related module nodes for broader context
- API doc source nodes for external reference
- Wiki pages for domain knowledge (read-only)
- Benchmark nodes for performance baselines

## Token Budget Management

- Estimate tokens per node: ~500-2000 tokens for governance, ~200-500 for file/test nodes
- Total context pack should target < 50% of available context window
- Prioritize: constraints > decisions > in-scope files > tests > related modules > docs
- If over budget, trim optional reads first, then related modules

## Writeback Rules

After implementation, the session MUST:
1. Create or update dev_graph nodes for any new/modified files
2. Create or update test nodes for any new/modified tests
3. Update `implementation_status` on affected nodes
4. Append session summary to `dev_graph/log.md`

## Relationships

### Depends On
- [[Admissibility Checks]]
- [[Context Pack Template]]
- [[API Documentation Policy]]

### Provides
- Assembly protocol for all context packs

### Validated By

### Constrained By
- [[Canonical Ownership]]
- [[Frontmatter Required]]

### Supersedes

### Used By
- All future context pack instances

### Produces
- Typed, admissibility-checked context packs

### Consumes
- Dev_graph nodes, codebase files, API documentation
