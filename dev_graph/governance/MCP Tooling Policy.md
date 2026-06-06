---
type: governance
canonical_id: GOV-004
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
source_paths:
  - "wiki/CLAUDE.md"
  - ".mcp.json"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# MCP Tooling Policy

## Definition

Operation safety classification for all MCP tools when operating on the dev_graph. Adapted from wiki/CLAUDE.md MCP Operational Governance for implementation artifacts.

## Purpose

Defines which MCP operations are safe to automate, which require human review, and which are prohibited. Ensures dev_graph integrity while enabling efficient automation.

## Architecture Role

Safety layer between Claude Code sessions and the MCP tool stack. All MCP write operations must comply with this classification.

## Configured MCP Servers

| Server | Transport | Purpose |
|---|---|---|
| context7 | HTTP | API documentation retrieval |
| mcpvault | npx | Obsidian vault read/write |
| smart-connections | npx | Semantic search and similarity |
| neo4j | Python stdio | Graph database (future) |
| postgres | npx | Relational database (future) |

## Operation Classification — Dev Graph

| Operation | Classification | MCP Tool | Requires Human Review |
|---|---|---|---|
| `read_note` (dev_graph) | Safe-automated | mcpvault | No |
| `read_multiple_notes` (dev_graph) | Safe-automated | mcpvault | No |
| `get_frontmatter` (dev_graph) | Safe-automated | mcpvault | No |
| `search_notes` (dev_graph) | Safe-automated | mcpvault | No |
| `get_notes_info` (dev_graph) | Safe-automated | mcpvault | No |
| `list_directory` (dev_graph) | Safe-automated | mcpvault | No |
| `get_vault_stats` | Safe-automated | mcpvault | No |
| `list_all_tags` | Safe-automated | mcpvault | No |
| `write_note` (dev_graph, new) | Constrained-automated | mcpvault | No, if follows governance |
| `update_frontmatter` (dev_graph) | Constrained-automated | mcpvault | No, if lint correction |
| `patch_note` (dev_graph, links only) | Constrained-automated | mcpvault | No |
| `write_note` (dev_graph, overwrite) | Human-review-required | mcpvault | Yes |
| `move_note` (dev_graph) | Human-review-required | mcpvault | Yes |
| `delete_note` (dev_graph) | Prohibited | mcpvault | N/A |
| `lookup` | Safe-automated | smart-connections | No |
| `connection` | Safe-automated | smart-connections | No |
| `query-docs` | Safe-automated | context7 | No |
| `resolve-library-id` | Safe-automated | context7 | No |
| neo4j `query` (read) | Safe-automated | neo4j | No |
| neo4j `execute` (write) | Human-review-required | neo4j | Yes |
| postgres `query` (read) | Safe-automated | postgres | No |
| postgres `execute` (write) | Human-review-required | postgres | Yes |

## Operation Classification — Wiki (from dev_graph sessions)

| Operation | Classification |
|---|---|
| `read_note` (wiki) | Safe-automated |
| `read_multiple_notes` (wiki) | Safe-automated |
| `search_notes` (wiki) | Safe-automated |
| `get_frontmatter` (wiki) | Safe-automated |
| `write_note` (wiki) | **Prohibited** |
| `patch_note` (wiki) | **Prohibited** |
| `update_frontmatter` (wiki) | **Prohibited** |
| `move_note` (wiki) | **Prohibited** |
| `delete_note` (wiki) | **Prohibited** |

## Constrained-Automated Rules

1. `write_note` for new dev_graph nodes is permitted without human review IF:
   - The node follows the universal frontmatter schema
   - A `search_notes` call confirmed no duplicate exists
   - The node is logged in `dev_graph/log.md`
2. `update_frontmatter` may correct enum values (lint correction) without human review
3. `patch_note` may add wikilinks to Relationship sections without human review
4. All constrained-automated operations MUST be logged

## Prohibited Operations

1. **Never** `delete_note` on any dev_graph node — deprecate instead
2. **Never** write to `wiki/**` from a dev_graph session
3. **Never** introduce frontmatter keys not defined in `dev_graph/CLAUDE.md`
4. **Never** set enum fields to values outside allowed sets
5. **Never** modify structural files (CLAUDE.md, index.md, log.md) via unattended automation

## Automation Boundaries

- Batch size limit: 15 nodes per unreviewed batch
- Error rate threshold: halt if >10% of batch operations produce unexpected results
- Logging mandatory: every write operation logged or operation halts

## Relationships

### Depends On
- [[No Wiki Mutation]]
- [[Dev Graph Governance]]

### Provides
- MCP operation safety framework for dev_graph

### Validated By

### Constrained By
- [[No Wiki Mutation]]

### Supersedes

### Used By
- All Claude Code sessions operating on dev_graph

### Produces

### Consumes
