---
type: security
domain: security
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [Env Vars, Environment Variables]
confidence: confirmed
tags: []
---

# Environment Variable Management

## Definition

The practice of storing API credentials and configuration parameters in environment variables rather than in code files, `.env` files committed to git, or chat prompts.

## Purpose

Prevents credential exposure in git history, chat logs, and shared code. Mandatory security practice for all trading system deployments.

## Architecture Role

Security foundation in [[Claude-Assisted Trading Stack]]. All integrations ([[Alpaca API]], [[Exchange API Integration]], [[Perplexity API]]) must read credentials from environment variables.

## Storage Locations

| Context | Storage | Details |
|---------|---------|---------|
| Claude Routines (remote) | Cloud environment | Configured in Claude Desktop → Environments |
| Railway | Railway env vars | Configured in Railway dashboard |
| Local development | Local .env (NOT committed to git) | Gitignored file |
| Claude Co-work | In-app prompt | Stored in Co-work session |

## Required Variables

```
# Brokerage
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...

# Exchange (Crypto)
BITGET_API_KEY=...
BITGET_SECRET_KEY=...
BITGET_PASSPHRASE=...

# Research
PERPLEXITY_API_KEY=...

# Notifications
CLICKUP_API_KEY=...

# Configuration
PAPER_TRADING=true
PORTFOLIO_VALUE=500
MAX_TRADE_SIZE=100
MAX_TRADES_PER_DAY=10
```

## Critical Rules

1. **NEVER** commit API keys to git repositories
2. **NEVER** hardcode keys in source files
3. **NEVER** paste keys directly into chat/prompt (they persist in history)
4. Variable names must match EXACTLY between routine prompt and environment configuration
5. Always disable withdrawal permissions on exchange APIs

## Naming Precision

Environment variable names must be spelled exactly as referenced in routine prompts. A mismatch (e.g., `ALPACA_API_SECRET` vs `ALPACA_SECRET_KEY`) causes silent failure — the agent won't find the key.

Source: [[SRC - Claude Opus Trader]] — "they weren't spelled exactly word for word letter for letter"

## Inputs

- API credentials from service providers
- Configuration parameters

## Outputs

- Securely stored, accessible credentials
- Runtime configuration values

## Dependencies

- [[API Credential Isolation]] — security model
- [[Claude Routines]] — cloud environment
- [[Railway Deployment]] — cloud env vars

## Failure Modes

- Variable name mismatch → silent auth failure
- Key rotation without updating all environments
- Accidental commit of .env to git
- Key exposure during migration (see [[SRC - Claude Opus Trader]] incident)

## Related Concepts

- [[API Credential Isolation]]
- [[Claude Routines]]
- [[Railway Deployment]]
- [[Claude-Assisted Trading Stack]]

## Source References

- Source: [[SRC - Claude Opus Trader]] — env var setup in cloud environments, naming precision
- Source: [[SRC - Claude TradingView Integration]] — Railway env vars, .env file management
- Source: [[SRC - Claude Cowork Trader]] — exchange API key storage
