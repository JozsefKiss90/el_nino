---
type: constraint
status: active
implementation_status: validated
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
source_paths:
  - "wiki/CLAUDE.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# No Wiki Mutation

## Definition

Claude Code sessions operating on dev_graph MUST NOT modify any files in `wiki/**` or `raw/**`.

## Purpose

Preserves the integrity of the mature knowledge graph. The wiki has its own governance model (878-line CLAUDE.md) and must not receive ungovernered edits from implementation-focused sessions.

## Architecture Role

Hard boundary between the knowledge layer (`wiki/`) and the implementation layer (`dev_graph/`). This constraint is foundational to the two-graph architecture.

## Constraint Expression

```
for all f in modified_files:
  NOT (f.startswith("wiki/") OR f.startswith("raw/"))
```

## Severity

**Error** (blocking). Violation of this constraint invalidates the entire session.

## Verification

- **Pre-commit**: Check `git diff --name-only` for `wiki/` or `raw/` paths
- **Session audit**: Review `dev_graph/log.md` for any wiki write operations
- **MCP audit**: `write_note` and `patch_note` calls targeting `wiki/` paths are prohibited

## Exceptions

None. This constraint has no exceptions.

## Relationships

### Depends On

### Provides
- Graph isolation guarantee between wiki and dev_graph

### Validated By
- Pre-commit git diff check
- MCP operation audit

### Constrained By

### Supersedes

### Used By
- [[Dev Graph Governance]]
- [[MCP Tooling Policy]]
- [[ADR - Dev Graph Bootstrap]]

### Produces

### Consumes
