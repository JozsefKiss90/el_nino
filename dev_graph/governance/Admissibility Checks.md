---
type: governance
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: inferred
source_paths:
  - "wiki/CLAUDE.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Admissibility Checks

## Definition

Nine validation checks that every dev_graph node must pass before it can be included as authoritative context in a coding context pack.

## Purpose

Prevents stale, deprecated, malformed, or contradicted nodes from polluting the implementation context. Ensures Claude Code sessions receive only validated, current, and canonical information.

## Architecture Role

Quality gate between semantic retrieval (which returns candidates) and context pack assembly (which requires validated nodes). This is the admissibility filter in the retrieval pipeline.

## The Nine Checks

### Check 1: Canonical Flag
```
node.canonical == true
```
Non-canonical nodes (if they exist) are aliases or drafts, not authoritative.

### Check 2: Status Not Deprecated
```
node.status != "deprecated"
```
Deprecated nodes are retained for history but must not guide implementation.

### Check 3: Implementation Status Not Deprecated
```
node.implementation_status != "deprecated"
```
Deprecated implementations must not be used as reference.

### Check 4: Type In Enum
```
node.type IN type_enum
```
Nodes with invalid or unknown types indicate schema drift.

### Check 5: Required Frontmatter Exists
```
node.frontmatter contains ALL universal fields:
  type, status, implementation_status, canonical,
  created, updated, confidence, source_paths,
  related_files, related_tests, related_constraints,
  related_decisions
```
Missing fields indicate incomplete or unmaintained nodes.

### Check 6: Source Paths Exist or Marked External
```
for all p in node.source_paths:
  file_exists(p) OR p.startswith("http") OR p == "external"
```
Broken source references indicate orphaned or stale nodes.

### Check 7: No Unresolved Contradiction
```
NOT (node.tags contains "contradiction" AND contradiction.resolved == false)
```
Contradicted nodes may provide incorrect guidance.

### Check 8: No Superseding Decision
```
NOT exists(adr WHERE adr.supersedes contains node
           AND adr.decision_status == "accepted")
```
Superseded nodes have been replaced by newer decisions.

### Check 9: Tests or Gates Identified
```
if node.type IN ["module", "file"]:
  node.related_tests is not empty
  OR node has explicit "no tests required" justification
```
Implementation nodes should have test coverage or explicit justification for lacking it.

## Failure Handling

If any check fails, the node:
- Is listed under "Deprecated / Excluded Notes" in the context pack
- Is NOT used as authoritative context
- Gets a brief reason for exclusion noted in the context pack

The failing check does NOT block context pack assembly — it only excludes the specific node.

## Bulk Admissibility

For context packs covering large modules with many nodes:
- Run all 9 checks per node
- Report summary: `N/M nodes admissible`
- List all excluded nodes with failure reasons
- If >50% of nodes fail, flag the context pack for human review

## Relationships

### Depends On
- [[Frontmatter Required]]
- [[Canonical Ownership]]

### Provides
- Admissibility validation for all context pack nodes

### Validated By

### Constrained By
- [[Frontmatter Required]]

### Supersedes

### Used By
- [[Context Pack Assembly Rules]]
- All context pack instances

### Produces
- Admissibility check results (pass/fail per node)

### Consumes
- Dev_graph node frontmatter and content
