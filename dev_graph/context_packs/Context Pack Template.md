---
type: context_pack
canonical_id: CTX-001
status: draft
implementation_status: not-started
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: inferred
evidence:
  - design
source_paths:
  - "wiki/memory/Context Budget Engineering.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
task_id: "template"
task_type: implementation
required_nodes: []
required_files: []
required_tests: []
required_docs: []
admissibility_checked: false
---

# Context Pack Template

## Definition

Canonical template for creating implementation context packs that prime Claude Code sessions. Copy this template and fill in the sections for each coding task.

## Purpose

A context pack is an ordered, typed, admissibility-checked reading list of dev_graph nodes that gives Claude Code all the information needed for a specific coding task. This is not ordinary top-k chunk RAG — it is a governed context-pack system.

---

## Task

**Task ID**: (unique identifier)
**Task Type**: (implementation | refactor | validation | debugging | migration)
**Description**: (what coding task is this context pack for?)

## Retrieved Nodes

Nodes proposed by Smart Connections semantic retrieval:
- (list semantically retrieved dev_graph nodes)

## Canonical Nodes

Nodes confirmed as canonical after Dataview/frontmatter filtering:
- (list nodes that passed canonical/status/type filtering)

## Required Files

Source files that must be read or modified:
- (list actual filesystem paths)

## Required Tests

Test files that must pass or be updated:
- (list test file paths)

## Required Constraints

Constraints that must not be violated:
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]
- (add task-specific constraints)

## Required API Docs

API documentation sources needed for this task:
- (list api_doc_source nodes with provider and version)

## Relevant Decisions

Architecture Decision Records that govern this task:
- [[ADR - Dev Graph Bootstrap]]
- (add task-specific ADRs)

## Deprecated / Excluded Notes

Nodes that failed admissibility checks (not used as authoritative context):

| Node | Failure Reason |
|---|---|
| (node name) | (which admissibility check failed) |

## Admissibility Check

- Total nodes evaluated: _
- Nodes admissible: _
- Nodes excluded: _
- All 9 checks from [[Admissibility Checks]] applied: [ ] yes / [ ] no

## Implementation Plan

1. (ordered steps for the implementation)
2. ...

## Validation Plan

1. (how to verify the implementation is correct)
2. (which tests to run)
3. (which gates must pass)

## Writeback Plan

After implementation, update dev_graph:
1. Create/update file nodes for new/modified files
2. Create/update test nodes for new/modified tests
3. Update `implementation_status` on affected module nodes
4. Append session summary to `dev_graph/log.md`
5. Update `dev_graph/index.md` if new nodes were created

## Relationships

### Depends On
- [[Context Pack Assembly Rules]]
- [[Admissibility Checks]]

### Provides
- Implementation context for a coding task

### Validated By
- [[Admissibility Checks]]

### Constrained By
- [[Frontmatter Required]]

### Supersedes

### Used By

### Produces
- Implementation artifacts (files, tests, updated nodes)

### Consumes
- Dev_graph nodes, codebase files, API documentation
