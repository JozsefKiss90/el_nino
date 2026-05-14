# SRC - Claude Opus Trader

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/claude_opus_trader.md` |
| Type | YouTube transcript |
| Topic | 24/7 AI trading agent with Opus 4.6 + Claude Code Routines |
| Capital | $10,000 (migrated from OpenClaw agent) |
| Benchmark | Beat S&P 500 by ~8% in 30 days |
| Date Ingested | 2026-05-09 |

## Summary

Documents migrating a stock trading agent from OpenClaw to Claude Code routines. Covers the complete setup: routine scheduling (5 daily crons), memory architecture (file-based personality), context budget management, Alpaca API, Perplexity for research, ClickUp notifications, environment variable management, local vs. remote routines, GitHub-based persistence.

## Key Concepts Extracted

- [[Claude Routines]] — complete routine setup, local vs. remote, cron scheduling
- [[Agent Memory Architecture]] — "files are the agent's full personality and discipline"
- [[Stateless Agent Recovery]] — "wakes up essentially stateless... files and context"
- [[Context Budget Engineering]] — "treat tokens like money", ~200K budget
- [[Guardrail Architecture]] — "if you don't give it guardrails it might go off the rails"
- [[Claude Code]] — VS Code integration, plan mode, auto mode
- [[Alpaca API]] — paper vs. live trading setup
- [[Perplexity API]] — market research integration
- [[Environment Variable Management]] — exact naming requirement
- [[API Credential Isolation]] — key exposure incident during migration
- [[Multi-Agent Orchestration]] — subagent delegation, sequential routines
- [[Agent Self-Verification]] — Opus 4.6 "self-verifying outputs"
- [[LLM Failure Modes in Trading]] — eager agent, context rot, benchmark misinterpretation
- [[Claude-Assisted Trading Stack]] — complete stack definition

## Routine Schedule

| Time | Routine | Purpose |
|------|---------|---------|
| 6:00 AM M-F | Pre-Market | Research, catalysts, draft trades |
| 8:30 AM M-F | Market Open | Execute trades, set stops |
| 12:00 PM M-F | Midday | Cut losers, tighten stops |
| 3:00 PM M-F | Market Close | EOD summary, notifications |
| 4:00 PM Friday | Weekly Review | Performance vs S&P, grading |

## Key Insights

- Files as personality: CLAUDE.md + strategy.md define agent behavior
- Context resets: summarize → /clear → re-inject summary
- Remote routines require git push for memory persistence
- Environment variable names must match EXACTLY
- Opus 4.6 agentic financial analysis benchmark ≠ day trading ability
- Self-grading: agent rated itself C for the week

## Caveats

- Previous OpenClaw system claimed 8% over S&P in 30 days — unverified
- Benchmark interpretation section important for tempering expectations
