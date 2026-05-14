# API Credential Isolation

## Definition

The security practice of isolating API credentials from code, chat history, git repositories, and logs. Ensures that exchange and service API keys cannot be accidentally exposed.

## Purpose

Prevents credential leakage that could lead to unauthorized trading, fund theft, or service abuse. Non-negotiable security requirement.

## Architecture Role

Security foundation for all integrations in [[Claude-Assisted Trading Stack]].

## Isolation Rules

1. **Environment variables only**: All API keys stored in env vars, never in source files
2. **Never commit secrets**: `.env` files must be in `.gitignore`
3. **Never paste in chat**: Keys persist in conversation history
4. **Withdrawal disabled**: Exchange APIs must never have withdrawal permission
5. **Separate credentials**: Paper and live trading use separate key pairs
6. **Key rotation**: Rotate immediately if exposure suspected

## Incident Evidence

During migration from OpenClaw to Claude Code, the agent template contained **live Alpaca API keys** in a file being committed to git. Claude Code detected this and alerted the user.

> "It alerted me about something with security... it had my live Alpaca key in there so I'm going to go ahead and rotate those."

Source: [[SRC - Claude Opus Trader]]

## Exchange API Permission Model

| Permission | Enable? | Reason |
|-----------|---------|--------|
| Read | Yes | Account balance, positions |
| Trading | Yes | Place/cancel orders |
| Withdrawal | **NEVER** | "Even if something goes wrong your funds cannot be withdrawn" |

Source: [[SRC - Claude Cowork Trader]]

## Inputs

- API keys from service providers
- Security policy

## Outputs

- Securely stored, scoped credentials
- Audit trail of credential usage

## Dependencies

- [[Environment Variable Management]] — storage mechanism
- [[Claude Routines]] — cloud environment for remote keys
- [[Railway Deployment]] — deployment environment vars

## Failure Modes

- Keys committed to git → exposed in history
- Keys in chat → exposed in conversation logs
- Withdrawal permissions enabled → fund theft risk
- Keys not rotated after exposure → continued risk
- Env var name mismatch → silent auth failure masking exposure

## Related Concepts

- [[Environment Variable Management]]
- [[Guardrail Architecture]]
- [[Autonomous Trading Risk Model]]
- [[Claude-Assisted Trading Stack]]

## Source References

- Source: [[SRC - Claude Opus Trader]] — credential exposure incident, key rotation
- Source: [[SRC - Claude Cowork Trader]] — exchange API permissions, withdrawal disabled
- Source: [[SRC - Claude TradingView Integration]] — env file management, secret storage
