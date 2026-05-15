---
type: infrastructure
domain: infrastructure
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Claude Code CLI, AI Coding Agent]
confidence: confirmed
tags: [infrastructure]
---

# Claude Code

## Definition

Anthropic's AI coding agent operated via CLI or IDE extension. The primary runtime environment for building, testing, and executing autonomous trading systems. Users interact in natural language; Claude writes, runs, and tests code autonomously.

## Purpose

Serves as both the development environment (building the trading system) and the execution runtime (running trading routines). The agent loop (observe → plan → execute → verify) provides the autonomous capability that differentiates this from static automation.

## Architecture Role

Core runtime in [[Claude-Assisted Trading Stack]]. Hosts [[Claude Routines]], executes [[Trading Engine Pipeline]], and manages [[Agent Memory Architecture]].

## Key Capabilities

- **Natural language coding**: Describe what you want; Claude writes the code
- **Autonomous agent loop**: Observe, plan, execute, verify cycle
- **File system access**: Read, write, create files and directories
- **Shell execution**: Run commands, scripts, API calls
- **Git integration**: Commit, push, manage repositories
- **MCP integration**: Connect to external tools via [[MCP Architecture]]
- **VS Code extension**: IDE integration with file browser
- **Desktop app**: Standalone with routine scheduling

## Operational Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Interactive | User and Claude collaborate in real-time | Development, debugging |
| Plan mode | Claude proposes plan before executing | Architecture, strategy design |
| Auto mode | Claude handles permission prompts automatically | Trusted routine execution |
| Routines | Scheduled autonomous execution | Production trading |

## Claude Code vs. Claude Co-work vs. Claude Chat

| Feature | Claude Code | Claude Co-work | Claude Chat |
|---------|------------|----------------|-------------|
| Code execution | Yes | Limited | No |
| File access | Full | Folder-scoped | No |
| Computer use | No | Yes | No |
| Scheduled tasks | Via routines | Built-in | No |
| Memory across sessions | Via files/CLAUDE.md | Built-in context | No |
| Shell access | Full | Via computer use | No |

## Context Management

- Session context: Up to 200K tokens (standard), 1M tokens (extended)
- `/clear` resets context within session
- CLAUDE.md loaded at session start (always in context)
- See [[Context Budget Engineering]]

## Subscription Tiers

| Tier | Price | Relevance |
|------|-------|-----------|
| Pro | $20/month | Basic access to Claude Code |
| Max | Higher | Extended limits for heavy routine usage |

## Inputs

- User prompts (natural language)
- CLAUDE.md (project configuration)
- Files in project directory
- Environment variables (API keys)

## Outputs

- Code files
- Shell command results
- File modifications
- Git commits
- API responses

## Dependencies

- Claude model (Opus 4.6 recommended)
- GitHub (for remote routines)
- Environment variables (for API keys)

## Failure Modes

- Session token exhaustion → incomplete task
- Permission denial blocking autonomous operation
- Environment variable misconfiguration
- Network timeout on API calls

## Related Concepts

- [[Claude Routines]]
- [[Claude Co-work]]
- [[Claude-Assisted Trading Stack]]
- [[Agent Memory Architecture]]
- [[Context Budget Engineering]]
- [[MCP Architecture]]

## Source References

- Source: [[SRC - Claude Stock Trader]] — "AI coding agent from Anthropic, you talk to it in plain English"
- Source: [[SRC - Claude Opus Trader]] — VS Code integration, plan mode, auto mode, context management
- Source: [[SRC - Claude TradingView Integration]] — CLI usage, dangerously-skip-permissions mode
