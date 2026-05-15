---
type: source
domain: sources
source_file: raw/ows-dev-squad.md
source_type: architecture_doc
date_ingested: 2026-05-09
created: 2026-05-09
updated: 2026-05-09
status: active
confidence: single-source
tags: []
---

# SRC - OWS Dev Squad

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/ows-dev-squad.md` |
| Type | Technical architecture document |
| Project | Syndicate Squad |
| Stack | Next.js, TypeScript |
| Date Ingested | 2026-05-09 |

## Summary

Detailed technical architecture of the Syndicate Squad — a wallet-native supervisor system for agent team management. Comprehensive specification covering: supervisor decision engine, upgrade simulator, multi-round evolution, paper trading engine, replay proof harness, OWS/XMTP/x402/MoonPay integrations, session persistence, and what is real vs. simulated.

## Key Concepts Extracted

- [[Syndicate Squad Architecture]] — complete system specification
- [[Supervisor Decision Engine]] — scoring, treasury constraints, evidence-based decisions
- [[Multi-Agent Orchestration]] — supervisor-worker pattern with desks
- [[Office Action Loop]] — state machine for interventions
- [[Treasury Policy System]] — budget constraints, burn-on-attempt
- [[Paper Trading]] — full propose/verify/execute/close/score cycle
- [[Agent Self-Verification]] — replay proof as verification mechanism

## Core Domain Types

- `MissionRecord`, `AgentIdentity`, `TreasuryPolicyView`, `TreasuryRequest`
- `UpgradeOption`, `InterventionRecord`, `TeamVersion`
- `InstitutionMemoryEntry`, `PerformanceMetric`
- `WatchlistSymbol`, `MarketSnapshot`, `TradeIdea`, `PaperPosition`
- `EvaluationWindow`, `EvaluationScorecard`, `UpgradeExperiment`

## Architecture Thesis

> "The product is the supervisor — watches the office, identifies a weak desk, chooses an upgrade, spends treasury under policy, evaluates whether the upgrade helped, records the result in institutional memory."

## Key Design Decisions

1. Treasury burns on every attempt (not just successes)
2. Promotion requires: 3+ metrics improved, no regressions, >=12% avg improvement
3. Replay harness proves supervisor isn't scripted
4. Live-or-fallback pattern for all integrations
5. Paper trading provides real evidence for upgrade decisions

## Current Gaps (as documented)

- OWS REST/proxy limited to first diagnosis slice
- x402 receipt attribution is best-effort
- XMTP depends on local machine state
- Paper trading uses demo market data, not live
- MoonPay is sandbox-only
