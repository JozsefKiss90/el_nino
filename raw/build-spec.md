# The Syndicate Squad Build Spec

## Goal

Build a hackathon-ready demo where a wallet-native supervisor assembles, funds, evaluates, and improves agent teams under treasury constraints:

- visible team versioning (v1, v2)
- visible supervisor interventions
- visible treasury budget and spend
- visible x402-backed upgrade purchase path
- visible performance metrics (before/after)
- visible institutional memory
- visible OWS/XMTP integration readiness

## What We Are Building

Not a task approval pipeline. Not a trading system.

An office of agents where the supervisor is the product. The supervisor creates teams, identifies weaknesses, spends treasury on upgrades, and measures whether interventions helped.

## MVP Screens

1. Office overview — mission stages from intake to promotion
2. Supervisor desk — mission objective and treasury summary
3. Agent roster — desk names, budgets, versions, performance notes
4. Treasury and intervention rail — policy-gated decisions (Validate Weakness, Approve/Deny Upgrade, Evaluate Team)
5. Performance desk — v1 vs v2 metric comparison (disagreement, confidence, convergence, cost)
6. Version history — team versions, intervention log, institutional memory
7. XMTP message rail — structured office handoffs
8. Audit trail — every intervention visible
9. Wallet and policy inspector — OWS access and XMTP desk permissions

## Demo Flow

1. User opens the office and sees Team v1 with 5 desks
2. Evaluator flags weakness in strategy desk convergence
3. Supervisor proposes treasury spend for strategist upgrade
4. Treasury policy approves or denies
5. If approved, Team v2 deploys with upgraded strategy desk
6. Evaluator compares v1 vs v2 metrics
7. Institutional memory records the intervention
8. The denied path shows: spend denied, team stays v1, audit records the failure

## Architecture

### Frontend

- Next.js app router
- Derived demo scenario with office-native state
- Inspector backed by `/api/integration-status`
- Athena-inspired operator dashboard

### Domain Model

- `MissionRecord` — office mission with round and version tracking
- `AgentIdentity` — desk, budget, versionTag, performanceNote, upgradeRole
- `TreasuryRequest` — policy-gated spend requests with cost
- `TreasuryPolicyView` — budget, deployed, available, spend limit
- `PerformanceMetric` — v1 vs v2 comparison with direction
- `TeamVersion` — versioned team snapshots
- `InterventionRecord` — upgrade decisions with cost and outcome
- `InstitutionMemoryEntry` — cross-round learning records
- `UpgradeOption` — upgrade catalog
- `OfficeOverviewStage` — mission-to-promotion pipeline

### Integration

- OWS wallet/policy/sign request transport preserved
- XMTP messaging transport preserved
- x402 upgrade purchase transport preserved
- Three server actions remapped to office semantics:
  - sign-review -> evaluator attests weakness diagnosis
  - grant-authority -> treasury approves or denies upgrade spend
  - verify-task -> evaluator promotes or rejects team version

## Winning Story

We built an office of agents. A wallet-native supervisor assembles specialist teams, evaluates their performance, spends treasury on upgrades under policy constraints, and records whether interventions helped. The human funds the institution and lets it cook.