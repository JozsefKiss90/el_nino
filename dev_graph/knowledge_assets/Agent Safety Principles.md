---
type: knowledge_asset
canonical_id: KA-008
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - wiki
  - external
source_paths:
  - "wiki/risk/Autonomous Trading Risk Model.md"
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/agents/Agent Self-Verification.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions: []
knowledge_id: "KA-008"
knowledge_type: guidance
source_wiki_pages:
  - "wiki/risk/Autonomous Trading Risk Model.md"
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/agents/Agent Self-Verification.md"
  - "wiki/security/API Credential Isolation.md"
informs_decisions: []
informs_architecture:
  - "[[Context Map]]"
external_references:
  - "raw/Claude for Financial Services.md"
---

# Agent Safety Principles

## Definition

The engineering guidance — derived from Anthropic's approach to AI safety in financial services and from the project's own risk model — that autonomous trading agents must be designed with multiple layers of safety: credential isolation, action constraints, self-verification, phased autonomy, and human oversight.

## Purpose

Explains WHY the system has API credential isolation (withdrawal always disabled), WHY agents self-verify outputs before execution (Opus 4.6 capability), WHY autonomy is phased (paper → monitored → autonomous), and WHY the risk model identifies AI-specific failure modes distinct from market risk.

## Architecture Role

Foundational knowledge asset. Cross-cuts all systems. Motivates constraint nodes, the paper trading gate, agent self-verification behaviors, and the credential isolation architecture.

## Core Principles

1. **Credential isolation**: API keys stored in environment variables only. Withdrawal capability ALWAYS disabled. No credential in agent-accessible memory files.
2. **Self-verification**: Agent validates its own outputs before execution. Opus 4.6 provides "self-verifying outputs" as a built-in capability.
3. **Phased autonomy**: Paper trading → monitored live trading → autonomous live trading. Each phase gate requires quantitative validation.
4. **AI-specific risk taxonomy**: Beyond market risk (volatility, liquidity) and execution risk (slippage, fills), the system identifies AI-specific risks: hallucination, stale context, overfitting, action bias, context overflow.
5. **Human review period**: During initial deployment, every routine run is monitored. The system earns autonomy through demonstrated correctness.
6. **Fail-safe defaults**: On error, the system holds positions (no panic selling) or stands aside (no forced trading). The default action is always the safe action.

## Architectural Constraints

- No API key may appear in a file that an agent can read/write
- Withdrawal API calls are permanently disabled at the credential level
- Every new strategy must pass paper trading validation before live deployment

## Relationships

### Provides
- Cross-cutting safety guidance for all systems

### Used By
- [[Context Map]]

### Originates From
