# SRC - Build Spec

## Metadata

| Field | Value |
|-------|-------|
| Source File | `raw/build-spec.md` |
| Type | Product requirements document |
| Project | Syndicate Squad |
| Context | Hackathon demo specification |
| Date Ingested | 2026-05-09 |

## Summary

Build specification for the Syndicate Squad hackathon demo. Defines the product as a wallet-native supervisor that assembles, funds, evaluates, and improves agent teams under treasury constraints. MVP screens, demo flow, domain model, and integration requirements.

## Key Concepts Extracted

- [[Syndicate Squad Architecture]] — product definition
- [[Treasury Policy System]] — treasury budget and spend visibility
- [[Office Action Loop]] — demo flow (8-step sequence)
- [[Multi-Agent Orchestration]] — "office of agents where the supervisor is the product"

## MVP Requirements

### Visible Elements
- Team versioning (v1, v2)
- Supervisor interventions
- Treasury budget and spend
- x402-backed upgrade purchase path
- Performance metrics (before/after)
- Institutional memory
- OWS/XMTP integration readiness

### Demo Flow
1. Office with Team v1 (5 desks)
2. Evaluator flags weakness
3. Supervisor proposes treasury spend
4. Treasury policy approves/denies
5. Team v2 deploys (if approved)
6. Evaluator compares v1 vs v2
7. Institutional memory records intervention
8. Denied path shows audit of failure

## Domain Model Types

`MissionRecord`, `AgentIdentity`, `TreasuryRequest`, `TreasuryPolicyView`, `PerformanceMetric`, `TeamVersion`, `InterventionRecord`, `InstitutionMemoryEntry`, `UpgradeOption`, `OfficeOverviewStage`

## Key Quote

> "We built an office of agents. A wallet-native supervisor assembles specialist teams, evaluates their performance, spends treasury on upgrades under policy constraints, and records whether interventions helped."
