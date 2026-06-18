# Dev Graph Index

Last updated: 2026-06-18 (Two ADR-009 amendments + the Chain Orchestrator. **(A) Computed Cooldown** — PRED-008 [[Cooldown OK]]; MOD-007 `runtime_policy_version 0.1.0 → 0.2.0` (computed L3 cooldown replaces the v0 echo; duplicate-first); goldens BENCH-003/004/006 re-pinned (identity-only). **(B) Live Operational Feed** — FILE-036 [[operational_feed.py]] + TEST-026 under MOD-010 (deterministic MarketCalendarFeed behind the OperationalInput seam, captured for replay / quarantined off the replay path; additive — no contract/`*_version` change). Both **HARD-PAUSED for operator review, nothing committed**. **The Chain Orchestrator** — MOD-010 + FILE-031..035 + TEST-023..025 + BENCH-006 (committed golden chain_bench.json): the end-to-end Layer-3 composition root (consume→…→[GATE-001]→execute→persist, in-hand direction/gold_price ADR-011 D1); pure composition; realizes PAT-004, operationalizes WF-001. Full suite **950 green**.)

## Architecture

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[architecture/Context Map]] | ARCH-001 | architecture | Formal bounded context diagram — 6 systems and interactions |
| [[architecture/Runtime Topology]] | ARCH-002 | architecture | Runtime component interaction model — events, data flows |
| [[architecture/Layer Model]] | ARCH-003 | architecture | L1 (data) → L2 (analysis) → L3 (execution) layer definitions |
| [[architecture/Infrastructure Diagram]] | ARCH-004 | architecture | Full infrastructure Mermaid diagram (migrated from root) |

## Systems

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[systems/Data Pipeline]] | SYS-001 | system | Market data ingestion, feature engineering, snapshot assembly (L1+L2) |
| [[systems/Trading Engine]] | SYS-002 | system | Signal generation, order management, stop-loss, position tracking (L3) |
| [[systems/Risk Control]] | SYS-003 | system | Guardrail enforcement, exposure tracking, circuit breaking |
| [[systems/Agent Runtime]] | SYS-004 | system | State persistence, context assembly, trade logging |
| [[systems/Evaluation Loop]] | SYS-005 | system | Performance scoring, promotion validation, lifecycle management |
| [[systems/Supervisor Office]] | SYS-006 | system | Decision making, treasury management, upgrade evaluation, orchestration |

## Capabilities

| Node | ID | Parent System | Summary |
|------|----|---------------|---------|
| [[capabilities/Market Scanning]] | CAP-001 | Data Pipeline | Scan universe, rank by momentum/volatility/ATR, produce watchlist |
| [[capabilities/Feature Engineering]] | CAP-002 | Data Pipeline | Calculate indicators, build feature vectors |
| [[capabilities/Snapshot Assembly]] | CAP-003 | Data Pipeline | Assemble L2 snapshot — foundational data contract |
| ~~[[capabilities/Signal Generation]]~~ | CAP-004 | Trading Engine | DEPRECATED 2026-06-08 — superseded by Gold Decision Generation (CAP-020) |
| [[capabilities/Order Management]] | CAP-005 | Trading Engine | Route orders, size positions, manage execution |
| [[capabilities/Stop-Loss Management]] | CAP-006 | Trading Engine | Place and adjust stops (fixed, trailing, floor-ratcheting) |
| [[capabilities/Position Tracking]] | CAP-007 | Trading Engine | Track open positions, monitor P&L, detect exits |
| [[capabilities/Guardrail Enforcement]] | CAP-008 | Risk Control | Evaluate predicates, enforce gates, approve/block trades |
| [[capabilities/Exposure Tracking]] | CAP-009 | Risk Control | Calculate exposure, detect threshold breaches |
| [[capabilities/State Persistence]] | CAP-010 | Agent Runtime | Read/write memory files, git persistence |
| [[capabilities/Context Assembly]] | CAP-011 | Agent Runtime | Assemble context window within token budget |
| [[capabilities/Trade Logging]] | CAP-012 | Agent Runtime | Structured trade journaling for compliance and evaluation |
| [[capabilities/Performance Scoring]] | CAP-013 | Evaluation Loop | Calculate metrics, generate evaluation scorecards |
| [[capabilities/Promotion Validation]] | CAP-014 | Evaluation Loop | Evaluate promotion criteria, manage promotion gate |
| [[capabilities/Decision Making]] | CAP-015 | Supervisor Office | Score upgrades, select best option under treasury constraints |
| [[capabilities/Treasury Management]] | CAP-016 | Supervisor Office | Track budget, enforce spend policy, approve/deny |
| [[capabilities/Upgrade Evaluation]] | CAP-017 | Supervisor Office | Simulate upgrades, run paper trading, evaluate outcomes |
| [[capabilities/Team Orchestration]] | CAP-018 | Supervisor Office | Manage agent desk assignments, coordinate upgrades |
| [[capabilities/Market Regime Classification]] | CAP-019 | Trading Engine | Classify a feature vector into one deterministic macro regime (SCHEMA-010) |
| [[capabilities/Gold Decision Generation]] | CAP-020 | Trading Engine | FeatureVector + RegimeClassification → paper Gold DecisionPacket (SCHEMA-011); supersedes CAP-004 |
| [[capabilities/Paper-Trade Admission]] | CAP-021 | Trading Engine | GoldDecisionPacket + runtime state → ADMIT/HOLD/REJECT RuntimeDecisionRecord (SCHEMA-012); computes L3 duplicate_ok/operational_ok |

## Knowledge Assets

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Event Sourcing]] | KA-001 | knowledge_asset | State as immutable event sequence — motivates event-driven architecture |
| [[CQRS]] | KA-002 | knowledge_asset | Read/write model separation — motivates snapshot layer design |
| [[Supervisor Pattern Methodology]] | KA-003 | knowledge_asset | Meta-agent governance — motivates Supervisor Office |
| [[Office Action Methodology]] | KA-004 | knowledge_asset | Deterministic intervention state machine |
| [[Guardrail Philosophy]] | KA-005 | knowledge_asset | Hard constraints before autonomy — motivates Risk Control |
| [[Layer 2 Design Principles]] | KA-006 | knowledge_asset | Snapshot-as-truth-layer — foundational data contract |
| [[Context Engineering]] | KA-007 | knowledge_asset | Tokens as finite resource — motivates context assembly |
| [[Agent Safety Principles]] | KA-008 | knowledge_asset | Multi-layer safety — credential isolation, phased autonomy |
| [[Stateless Agent Architecture]] | KA-009 | knowledge_asset | Wake-Execute-Sleep — file-mediated agent continuity |
| [[Paper Trading Validation]] | KA-010 | knowledge_asset | Mandatory simulated validation before live deployment |
| [[Regime Taxonomy]] | KA-011 | knowledge_asset | Why deterministic enumerated regimes belong between features and decisions |

## Patterns

| Node | ID | Type | Realized By |
|------|----|------|-------------|
| [[patterns/Supervisor Pattern]] | PAT-001 | coordination | Decision Making, Team Orchestration, Upgrade Evaluation |
| [[patterns/Guardrail Pattern]] | PAT-002 | governance | Guardrail Enforcement, Promotion Validation, Stop-Loss Mgmt, Order Mgmt |
| [[patterns/Evaluation Loop Pattern]] | PAT-003 | behavioral | Performance Scoring, Upgrade Evaluation |
| [[patterns/Pipeline Pattern]] | PAT-004 | structural | Market Scanning, Feature Engineering, Signal Generation, Order Mgmt |
| [[patterns/Event Sourcing Pattern]] | PAT-005 | behavioral | Trade Logging, Position Tracking |
| [[patterns/Context Assembly Pattern]] | PAT-006 | structural | State Persistence, Context Assembly |
| [[patterns/Treasury Approval Pattern]] | PAT-007 | governance | Treasury Management |
| [[patterns/Promotion Pattern]] | PAT-008 | governance | Promotion Validation |
| [[patterns/CQRS Pattern]] | PAT-009 | structural | Snapshot Assembly |
| [[patterns/Multi-Agent Coordination Pattern]] | PAT-010 | coordination | Team Orchestration |
| [[patterns/Regime Classification Pattern]] | PAT-011 | behavioral | Market Regime Classification, Market Regime Classifier |

## Interfaces

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Snapshot API]] | INT-001 | interface | Data Pipeline → Trading Engine Layer-2 snapshot read contract |
| [[Risk Check API]] | INT-003 | interface | Risk Control → Trading Engine trade-validation contract |
| [[Decision API]] | INT-006 | interface | Supervisor Office → Trading Engine upgrade-decision contract |
| [[Regime Classification API]] | INT-007 | interface | Feature Vector → Regime Classification contract (canonical upstream for Gold) |
| [[Gold Decision API]] | INT-009 | interface | FeatureVector + RegimeClassification → paper Gold DecisionPacket contract |
| [[Paper Runtime API]] | INT-010 | interface | GoldDecisionPacket + runtime state → RuntimeDecisionRecord + new ledger (evaluate / run_once / run_sequence) |
| [[Execution API]] | INT-011 | interface | Execution port (planned) — ADMIT RuntimeDecisionRecord (SCHEMA-012) + portfolio state → ExecutionRecord (SCHEMA-014) + new PortfolioState; simulated + Alpaca-paper adapters; parent CAP-005 |

(INT-002, 004/005, 008 reserved for future Phase 4 contracts; INT-008 earmarked for a future Evaluation API)

## Events

(Empty — populated in Phase 7)

## Governance

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Dev Graph Governance]] | GOV-001 | governance | Root governance node for dev_graph |
| [[Context Pack Assembly Rules]] | GOV-002 | governance | Context pack assembly sequence with intent-aware routing |
| [[Admissibility Checks]] | GOV-003 | governance | 9 validation checks for context pack inclusion |
| [[MCP Tooling Policy]] | GOV-004 | governance | MCP operation safety classifications |
| [[Neo4j Export Mapping]] | GOV-005 | governance | Note-to-node mapping with canonical_id as primary key |
| [[Database MCP Mapping]] | GOV-006 | governance | Postgres table definitions for future integration |
| [[API Documentation Policy]] | GOV-007 | governance | Permitted doc sources, freshness, retrieval rules |
| [[REF - Wiki CLAUDE]] | REF-001 | reference | Reference to wiki governance operations manual |
| [[REF - Wiki Metadata Migration Plan]] | REF-002 | reference | Reference to wiki schema design patterns |
| [[REF - Wiki Graph Health Dashboard]] | REF-003 | reference | Reference to wiki Dataview query patterns |
| ~~[[Infrastructure Diagram]]~~ | REF-004 | reference | DEPRECATED — migrated to architecture/Infrastructure Diagram (ARCH-004) |

## Observability

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Dev Graph Dashboard]] | OBS-001 | observability | 22 Dataview queries for dev_graph health |

## Context Packs

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Context Pack Template]] | CTX-001 | context_pack | Canonical template for context pack creation |
| [[Phase 5 Bootstrap Context]] | CTX-002 | context_pack | First coding-session pack — substrate ADR + Guardrail Engine |

## Decisions

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[ADR - Dev Graph Bootstrap]] | ADR-001 | decision_record | Bootstrap decision — why dev_graph exists |
| [[ADR - Ontology Redesign]] | ADR-002 | decision_record | Ontology redesign — 24-type hierarchy with canonical_id |
| [[ADR - Implementation Substrate]] | ADR-003 | decision_record | Tech stack / repo layout / config policy for the first coding session |
| [[ADR - Decision Layer Re-grounding]] | ADR-004 | decision_record | Separates Supervisor treasury-upgrade branch from future Gold Trading Decision branch |
| [[ADR - Feature Layer Contract]] | ADR-005 | decision_record | Deterministic snapshot-local feature rules; replay determinism; MOD-003-only input |
| [[ADR - Gold DecisionPacket v0 Planning]] | ADR-006 | decision_record | Governance boundary for a future Gold DecisionPacket layer; creation gates + replay invariants; consumes SCHEMA-009 only; non-normative |
| [[ADR - Deterministic Regime Taxonomy]] | ADR-007 | decision_record | Deterministic, config-driven, fail-closed regime taxonomy; satisfies ADR-006 gate (d) |
| [[ADR - Gold Decision Confidence Semantics]] | ADR-008 | decision_record | Fixes the Gold v0 confidence/uncertainty model (deterministic ordinal trust score); closes ADR-006 §8 gate (e), finalizes (b)/(c) |
| [[ADR - Paper-Trading Runtime Planning]] | ADR-009 | decision_record | Planning ADR for epoch (a) — stateful paper-trading runtime; wrap-not-enrich (packet stays pure), self-describing ledger, computes L3 duplicate_ok/operational_ok; Creation Gates all pass |
| [[ADR - JARVIS GraphRAG Integration]] | ADR-010 | decision_record | Governance boundary for wiring the JARVIS console to the dev_graph — read-only consumer; bridge extended (not a new server); answers cite canonical_ids + evidence-class; offline graph.json / live Neo4j duality; non-normative |
| [[ADR - Execution Layer Planning]] | ADR-011 | decision_record | Governance boundary for the execution/portfolio epoch — port/adapter determinism split (deterministic offline fill-simulator core vs non-replayable Alpaca paper adapter); paper_only / virtual-money; re-grounds the live path CAP-020 → MOD-007 ADMIT → execution + wires GATE-001 / PRED-001..005; decoupled from DEBT-01 & epoch (b); **accepted 2026-06-16**, Creation Gates remain open; non-normative |
| [[ADR - Empirical Calibration Methodology]] | ADR-012 | decision_record | Epoch (b) calibration governance — version-axis mapping (regime thresholds → taxonomy_version; confidence weights + regime→direction table → decision_policy_version; never crossed); empirical-readiness gate (G0 N≥60 + per-target G1/G2/G3 coverage + walk-forward holdout); replay/PIT preservation; rule-based only. Corpus N=5 monochromatic → all 3 targets DEFER, no bump; **draft** |

## Constraints

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[No Wiki Mutation]] | CON-001 | constraint | MUST NOT modify wiki/** or raw/** |
| [[Frontmatter Required]] | CON-002 | constraint | Every content node must have valid frontmatter |
| [[Canonical Ownership]] | CON-003 | constraint | One implementation concept = one canonical node |

## API Documentation Sources

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Alpaca API Docs]] | API-001 | api_doc_source | Alpaca trading API v2 documentation |
| [[Anthropic API Docs]] | API-002 | api_doc_source | Anthropic/Claude API and SDK documentation |

## Modules

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Guardrail Engine]] | MOD-001 | module | Predicate-based trade validation at the Risk Control boundary (plan only) |
| [[Decision Engine]] | MOD-002 | module | Deterministic upgrade scoring under treasury constraints (plan only) |
| [[Snapshot Consumer]] | MOD-003 | module | Fail-closed Layer-3 ingestion of the Layer-2 truth snapshot |
| [[Feature Builder]] | MOD-004 | module | Deterministic snapshot-local Layer-2 → feature vector transform |
| [[Market Regime Classifier]] | MOD-005 | module | Deterministic feature-vector → one macro regime (rule-selection engine) |
| [[Gold Decision Builder]] | MOD-006 | module | FeatureVector + RegimeClassification → deterministic paper-only Gold DecisionPacket (SCHEMA-011) |
| [[Paper-Trading Runtime]] | MOD-007 | module | Stateful L3 admission — wraps the pure packet, computes duplicate_ok/operational_ok, append-only ledger |
| [[Execution]] | MOD-008 | module | Paper execution — ADMIT → (paper) fill + portfolio state; deterministic simulated-broker core behind INT-011; wires GATE-001; realizes CAP-005, produces CAP-007 state |
| [[Gold Forward-Return Labeler]] | MOD-009 | module | Downstream, read-only labeler of banked gold decisions with realized forward gold returns (ADR-012 gate G3 measurement prerequisite); measurement only, no decision-path/config change; NOT CAP-013 |
| [[Chain Orchestrator]] | MOD-010 | module | End-to-end Layer-3 composition root — threads consume→…→execute→persist, forwards in-hand direction/gold_price (ADR-011 D1), runs GATE-001 in the orchestrator; pure composition, no contract/`*_version` change |

## Files

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[guardrail_engine.py]] | FILE-001 | file | GuardrailEngine.validate() + fail-closed config loader (MOD-001) |
| [[predicates.py]] | FILE-002 | file | Hard-limit guardrail predicates (pure functions) |
| [[models.py]] | FILE-003 | file | Dataclasses realizing SCHEMA-007 / SCHEMA-008 |
| [[decision_engine.py]] | FILE-004 | file | DecisionEngine.decide() — deterministic upgrade selection (MOD-002) |
| [[scoring.py]] | FILE-005 | file | Weakness scoring (pure functions) |
| [[models.py (supervisor)]] | FILE-006 | file | Dataclasses realizing SCHEMA-004 / SCHEMA-005 |
| [[models.py (snapshot)]] | FILE-007 | file | Dataclasses realizing SCHEMA-001 (Layer 2 Snapshot) + deterministic id |
| [[consumer.py]] | FILE-008 | file | Fail-closed snapshot reader/gate (INT-001 consumer side) |
| [[models.py (features)]] | FILE-009 | file | Dataclasses realizing SCHEMA-009 (Feature + FeatureVector + version) |
| [[feature_builder.py]] | FILE-010 | file | FEATURE_REGISTRY + build_features() deterministic transform (MOD-004) |
| [[regime_classifier.py]] | FILE-011 | file | classify() rule-selection driver (MOD-005) |
| [[taxonomy.py]] | FILE-012 | file | Priority-ordered RULE_TABLE + margin/near helpers |
| [[config.py (regime)]] | FILE-013 | file | RegimeConfig (versioned thresholds) + fail-closed loader |
| [[models.py (regime)]] | FILE-014 | file | SCHEMA-010 models (Regime enum, RegimeClassification) |
| [[models.py (gold)]] | FILE-015 | file | SCHEMA-011 models (GoldDecisionPacket, Direction enum, packet_id) |
| [[config.py (gold)]] | FILE-016 | file | DecisionPolicyConfig — confidence weights + regime→direction table + fingerprint |
| [[policy.py]] | FILE-017 | file | trust_score (ADR-008) + direction_for (pure helpers) |
| [[builder.py]] | FILE-018 | file | build_decision() — Gold Decision API driver (MOD-006) |
| [[models.py (paper_runtime)]] | FILE-019 | file | SCHEMA-012/013 dataclasses (RuntimeDecisionRecord, RuntimeLedger, OperationalInput) + record_id |
| [[config.py (paper_runtime)]] | FILE-020 | file | RuntimePolicyConfig + runtime_policy_fingerprint + fail-closed loaders |
| [[predicates.py (paper_runtime)]] | FILE-021 | file | duplicate_ok / operational_ok + snapshot echoes (pure (passed, reason) guards) |
| [[engine.py]] | FILE-022 | file | pure evaluate() — guard conjunction + fail-closed verdict + ledger append |
| [[runtime.py]] | FILE-023 | file | IO boundary shell (run_once) + pure run_sequence replay driver |
| [[models.py (execution)]] | FILE-024 | file | SCHEMA-014/015 dataclasses (ExecutionRecord, PortfolioState/Position/ExecutionEntry, Fill, GuardResult) + compute_execution_id |
| [[config.py (execution)]] | FILE-025 | file | ExecutionPolicyConfig (fixed default_size) + FillModelConfig + fingerprints + fail-closed loaders |
| [[adapters.py]] | FILE-026 | file | ExecutionPort Protocol + SimulatedBrokerAdapter (deterministic fill); Alpaca-paper adapter deferred |
| [[engine.py (execution)]] | FILE-027 | file | pure execute() — fail-closed fill decision + portfolio transition + record (no IO/risk) |
| [[runtime.py (execution)]] | FILE-028 | file | IO shell + GATE-001 guard-wiring orchestrator (run_once / pure run_sequence) — the only src/risk importer |
| [[run_execution_bench.py]] | FILE-029 | file | BENCH-004 harness — deterministic real + synthetic replay over execution run_sequence; emits the committed golden artifact |
| [[run_forward_return_labels.py]] | FILE-030 | file | MOD-009 harness — pure forward-return label/aggregate math + read-only corpus driver; emits the committed golden forward_return_labels.json (ADR-012 G3 input) |
| [[models.py (orchestration)]] | FILE-031 | file | ChainResult (frozen aggregate of the 5 records + 2 state artifacts) + deterministic to_dict + ChainContractError (MOD-010) |
| [[config.py (orchestration)]] | FILE-032 | file | Captured DEFAULT_OPERATIONAL_INPUT + DEFAULT_GUARD_CONFIG — the explicit operational/guard seams (never read live on the replay path) |
| [[engine.py (orchestration)]] | FILE-033 | file | pure run_chain() — the full-chain core (features→regime→decision→evaluate→[GATE-001]→execute); in-hand path, wrap-not-enrich, fail-closed |
| [[runtime.py (orchestration)]] | FILE-034 | file | IO shell — run_once (persist portfolio-then-ledger, atomic) + pure run_sequence replay driver + find_latest_snapshot + CLI |
| [[run_chain_bench.py]] | FILE-035 | file | BENCH-006 harness — real-corpus end-to-end replay over run_sequence; emits the committed golden chain_bench.json (full replay key) |
| [[operational_feed.py]] | FILE-036 | file | Live operational-status feed adapter (MOD-010 seam) — OperationalFeed port + deterministic MarketCalendarFeed + capture (read on IO path only, captured for replay; ADR-009 amendment) |

## Tests

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[test_predicates]] | TEST-001 | test | Unit tests for the guardrail predicates (7 tests) |
| [[test_guardrail_engine]] | TEST-002 | test | Behavioral tests for the Guardrail Engine (8 tests) |
| [[test_scoring]] | TEST-003 | test | Unit tests for Decision Engine scoring (5 tests) |
| [[test_decision_engine]] | TEST-004 | test | Behavioral tests for the Decision Engine (7 tests) |
| [[test_models (snapshot)]] | TEST-005 | test | Unit tests for SCHEMA-001 models incl. id recomputation (8 tests) |
| [[test_consumer]] | TEST-006 | test | Fail-closed Snapshot Consumer gate tests (8 tests) |
| [[test_feature_builder]] | TEST-007 | test | Feature Builder tests — arithmetic, determinism, provenance (10 tests) |
| [[test_regime_classifier]] | TEST-008 | test | Regime classifier — units, grid, determinism, fail-closed, completeness (~60) |
| [[test_regime_bench]] | TEST-009 | test | Benchmark/replay harness determinism + coverage (5 tests) |
| [[test_decision_builder]] | TEST-010 | test | Gold builder — units, determinism, fail-closed, golden, fingerprint (20 tests) |
| [[test_gold_bench]] | TEST-011 | test | Gold benchmark determinism + artifact-in-sync (6 tests) |
| [[test_e2e_pipeline]] | TEST-012 | test | Full-chain snapshot→consume→features→regime→gold E2E determinism + forwarded provenance (4 tests) |
| [[test_paper_runtime_guards]] | TEST-013 | test | Guard predicate units — dedup once-ever, operational, echoes, default-closed (14 tests) |
| [[test_paper_runtime_engine]] | TEST-014 | test | evaluate() verdicts + fail-closed record __post_init__ (14 tests) |
| [[test_paper_runtime_determinism]] | TEST-015 | test | Byte-identical record replay + runtime_policy_fingerprint coherence (6 tests) |
| [[test_paper_runtime_ledger]] | TEST-016 | test | Ledger idempotency, seq continuity, sequence replay, IO round-trip (8 tests) |
| [[test_paper_runtime_bench]] | TEST-017 | test | BENCH-003 determinism, idempotency, verdict sweep, artifact-in-sync (8 tests) |
| [[test_execution_engine]] | TEST-018 | test | execute() fill/no-fill paths, portfolio math, fail-closed + idempotency, record invariants (10 tests) |
| [[test_execution_determinism]] | TEST-019 | test | BENCH-004 core — byte-identical replay, persist/load round-trip, idempotent sequence (5 tests) |
| [[test_execution_guards]] | TEST-020 | test | GATE-001 guard-wiring — APPROVE/BLOCK mapping, no-fill on block, env-independent captured config (5 tests) |
| [[test_execution_bench]] | TEST-021 | test | BENCH-004 determinism, real-corpus grounding, fill/idempotency/guard-block attribution, artifact-in-sync (15 tests) |
| [[test_forward_return_labels]] | TEST-022 | test | MOD-009/BENCH-005 — synthetic correctness (all 4 directions, 6 regimes, 3 statuses), dedup, artifact-in-sync, + static look-ahead containment guard (19 tests) |
| [[test_chain_engine]] | TEST-023 | test | MOD-010 core — ADMIT/no-fill, in-hand price/direction forwarding, wrap-not-enrich, forwarded provenance, guard-block attribution, idempotency, fail-closed, bounded-context hygiene (12 tests) |
| [[test_chain_determinism]] | TEST-024 | test | MOD-010 — byte-identical end-to-end replay, admission idempotency, env-independent captured config, run_once persist/reload round-trip + non-consumable→None (7 tests) |
| [[test_chain_bench]] | TEST-025 | test | BENCH-006 — end-to-end replay determinism + idempotency, real-corpus grounding, full replay key complete, artifact-in-sync (8 tests) |
| [[test_operational_feed]] | TEST-026 | test | MOD-010 live operational feed (FILE-036) — calendar open/closed/fail-closed, capture round-trip, replay-path quarantine (capture freezes value; run_sequence never reads the feed) (10 tests) |

## Gates

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Trade Validation Gate]] | GATE-001 | gate | Blocking trade-validation checkpoint (Risk Control) — enforced by GuardrailEngine.validate() |
| [[Gold Decision Gate]] | GATE-002 | gate | Composes the L3 guards a Gold DecisionPacket cites (advisory; blocking surface is GATE-003) |
| [[Runtime Admission Gate]] | GATE-003 | gate | Blocking admission over the runtime record — composes the evaluated guards into ADMIT/HOLD/REJECT |

## Predicates

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Position Size OK]] | PRED-001 | predicate | size ≤ min(equity·pct, absolute cap) |
| [[Daily Loss Cap OK]] | PRED-002 | predicate | daily_pnl > -daily_loss_cap |
| [[Max Trades OK]] | PRED-003 | predicate | trades_today < max_trades_per_day |
| [[Max Positions OK]] | PRED-004 | predicate | open_positions < max_positions |
| [[Withdrawal Disabled]] | PRED-005 | predicate | withdrawals must be disabled |
| [[Duplicate OK]] | PRED-006 | predicate | L3 idempotency guard — snapshot not already ADMITted (implemented in MOD-007) |
| [[Operational OK]] | PRED-007 | predicate | L3 operational guard — venue tradeable / preconditions hold (implemented in MOD-007) |
| [[Cooldown OK]] | PRED-008 | predicate | L3 **computed** cooldown guard (v0.2.0) — min gap since the last ADMIT of a different snapshot (from the ledger's `as_of`); replaces the v0.1.0 echo |

## Schemas

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Layer 2 Snapshot Schema]] | SCHEMA-001 | artifact_schema | Snapshot API output — Layer-2 truth payload (deterministic id, guards, series) |
| [[Feature Vector Schema]] | SCHEMA-009 | artifact_schema | Feature Builder output — deterministic SCHEMA-001-derived features + provenance |
| [[Regime Classification Schema]] | SCHEMA-010 | artifact_schema | Regime Classifier output — matched rule, regime, rule_margin, provenance, trace |
| [[Gold DecisionPacket v0 Schema]] | SCHEMA-011 | artifact_schema | Gold Decision Builder output — direction, confidence/uncertainty, cited features, guard_refs, snapshot_guards (v0.2.0); consumed by the runtime |
| [[Runtime Decision Record Schema]] | SCHEMA-012 | artifact_schema | Paper runtime output — packet ref + six-guard block + ADMIT/HOLD/REJECT verdict + ledger hashes |
| [[Runtime Ledger Schema]] | SCHEMA-013 | artifact_schema | Append-only self-describing dedup/admission state keyed by source_snapshot_id |
| [[Execution Record Schema]] | SCHEMA-014 | artifact_schema | Execution layer output (planned) — wraps an ADMIT record + (paper) fill + guard provenance; paper_only; replayable flag |
| [[Portfolio State Schema]] | SCHEMA-015 | artifact_schema | Execution layer state (planned) — append-only self-describing per-instrument positions + executions history (mark-to-snapshot P&L); realizes CAP-007 |
| [[Decision Packet Schema]] | SCHEMA-004 | artifact_schema | Decision API output — selected upgrade, ranked options, rationale |
| [[Evaluation Scorecard Schema]] | SCHEMA-005 | artifact_schema | Decision API input — performance evidence (pnl, calibration, drawdown, disagreement) |
| [[Trade Validation Request Schema]] | SCHEMA-007 | artifact_schema | Risk Check API input — trade params + portfolio context |
| [[Trade Validation Decision Schema]] | SCHEMA-008 | artifact_schema | Risk Check API output — approve/block + triggered predicate |

(SCHEMA-002/003, 006 reserved for future Phase 4 schemas)

## Workflows

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[workflows/System Lifecycle]] | WF-001 | workflow | Cold → Initialized → PaperTrading → Validated → Candidate → Production → Paused → Emergency → Archived |

## Agents

(Empty — populated in Phase 5 when agent implementations exist)

## Skills

(Empty — populated in Phase 5 when agent skills are defined)

## Benchmarks

| Node | ID | Type | Summary |
|------|----|------|---------|
| [[Regime Distribution Benchmark]] | BENCH-001 | benchmark_result | Regime replay determinism + synthetic distribution/coverage/entropy |
| [[Gold Decision Distribution Benchmark]] | BENCH-002 | benchmark_result | Gold packet replay determinism + direction/confidence distribution |
| [[Paper-Trading Runtime Benchmark]] | BENCH-003 | benchmark_result | Runtime replay determinism + idempotency + verdict distribution (real + synthetic) |
| [[Execution Layer Benchmark]] | BENCH-004 | benchmark_result | Execution byte-identical sequence-replay determinism + idempotency + fill/guard-block distribution (real + synthetic); closes ADR-011 gate (d) |
| [[Gold Forward-Return Label Set]] | BENCH-005 | benchmark_result | Per (gold-decision × horizon) realized forward gold-return labels + per regime×horizon aggregate (the ADR-012 gate G3 input); committed golden forward_return_labels.json; measurement only |
| [[Chain Orchestrator Benchmark]] | BENCH-006 | benchmark_result | End-to-end byte-identical sequence-replay over MOD-010 run_sequence + admission idempotency on the real corpus; committed golden chain_bench.json; carries the full replay key (every layer version + captured fingerprints) |

---

## Statistics

- **Total content nodes**: 193 (architecture: 4, system: 6, capability: 21 (incl. 1 deprecated), interface: 7, artifact_schema: 12, module: 10, file: 36, test: 26, gate: 3, predicate: 8, pattern: 11, workflow: 1, knowledge_asset: 11, governance: 7, reference: 3+1 deprecated, observability: 1, context_pack: 2, decision_record: 12, constraint: 3, api_doc_source: 2, benchmark_result: 6)
- **Structural files**: 4 (CLAUDE.md, index.md, log.md, README.md)
- **Total files**: 197
- **Active directories**: 23
- **Populated directories**: 22 (architecture, systems, capabilities, interfaces, schemas, modules, files, tests, gates, predicates, patterns, workflows, knowledge_assets, governance, constraints, decisions, api_docs, observability, context_packs, benchmarks + root)
- **Empty directories**: 3 (events, agents, skills)
- **Frontmatter coverage**: 193/193 content nodes (100%)
- **Canonical ID coverage**: 193/193 content nodes (100%)
- **Schema version**: 2.2.0
- **Type enum**: 24 values
- **Relationship types**: 17
- **Realizes edges**: 37 (24 capabilities + 10 modules + 3 files → patterns) — recounted from the materialized graph (prior hand-maintained statistic had drifted)
- **Composes edges**: 3 (Supervisor Pattern → Multi-Agent Coordination, Treasury Approval; Regime Classification → Pipeline)
- **Originates From edges**: 21 (capabilities/systems/modules/schemas/decisions → knowledge assets)
- **Status enum**: 7 values
- **Implementation status enum**: 7 values
- **Confidence enum**: 5 values
- **Evidence enum**: 7 values
- **Lint checks**: 11
- **Dashboard queries**: 22
- **Bootstrap date**: 2026-05-25
- **Ontology redesign date**: 2026-06-06
- **Phase 1 completion date**: 2026-06-06
- **Phase 2 completion date**: 2026-06-06
- **Phase 3 completion date**: 2026-06-06
- **Phase 4.5 (contract layer) date**: 2026-06-06
- **Phase 5 (implementation readiness) date**: 2026-06-06
- **Phase 5 (first coding session — Guardrail Engine) date**: 2026-06-06
- **Phase 6 #1 (Trade Validation Gate + predicates) date**: 2026-06-06
- **Phase 5 (second coding session — Decision Engine) date**: 2026-06-06
- **MOD-004 (Feature Builder) date**: 2026-06-07
- **Regime Taxonomy (MOD-005 / SCHEMA-010 / ADR-007 / CAP-019 / INT-007 / KA-011 / PAT-011 / BENCH-001) date**: 2026-06-08
- **Gold DecisionPacket v0 (MOD-006 / SCHEMA-011 / ADR-006 / ADR-008 / CAP-020 / INT-009 / GATE-002 / PRED-006-007 / BENCH-002) date**: 2026-06-08
- **Paper-Trading Runtime (MOD-007 / SCHEMA-012-013 / ADR-009 / CAP-021 / INT-010 / GATE-003 / BENCH-003; SCHEMA-011 → v0.2.0) date**: 2026-06-09
- **JARVIS GraphRAG Integration (ADR-010) date**: 2026-06-14
- **Execution Layer Planning (ADR-011) date**: 2026-06-16 (drafted + accepted)
- **Execution layer contract — STEP 1 (INT-011 / SCHEMA-014 / SCHEMA-015; CAP-005 re-grounded, CAP-007 realized) date**: 2026-06-16
- **Execution layer simulator core — STEP 2 (MOD-008 Execution + FILE-024..028 + TEST-018..020; INT-011/SCHEMA-014/015 → implemented; GATE-001 wired in-progress→implemented; src/execution + 19 tests) date**: 2026-06-16
- **Execution layer replay benchmark — STEP 4 (BENCH-004 Execution Layer Benchmark + FILE-029 run_execution_bench.py + TEST-021 test_execution_bench; committed golden execution_bench.json; ADR-011 §7 gate (d) Closed, gates (a)–(e) reconciled Closed, (f) deferred; full suite 887 green) date**: 2026-06-16
- **Epoch (b) empirical-calibration governance (ADR-012 Empirical Calibration Methodology, draft; EPOCH_B_CALIBRATION_RUNBOOK.md) date**: 2026-06-17 — corpus assessment N=5 (1 committed el_nino fixture + 4 Mr-Ripley forward archives), monochromatic RESTRICTIVE_RATES/AVOID (regimes 1/12, directions 1/4); empirical-readiness gate G0+G1/G2/G3 all FAIL; all three targets (taxonomy_version thresholds; decision_policy_version weights + regime→direction table) DEFER; **NO `*_version` bump, NO value change, NO benchmark re-pin**; ADR-007/008 cross-linked forward to ADR-012
- **Chain Orchestrator — MOD-010 + FILE-031..035 + TEST-023..025 + BENCH-006 (committed golden benchmarks/orchestration/artifacts/chain_bench.json) date**: 2026-06-18 — the end-to-end Layer-3 composition root threading consume→build_features→classify→build_decision→evaluate→[GATE-001]→execute→persist; forwards the in-hand FeatureVector direction/gold_price (ADR-011 D1); GATE-001 run in the orchestrator (only cross-context importer); **pure composition — NO layer-logic / contract / `*_version` change**; realizes PAT-004, operationalizes WF-001 PaperTrading, closes MOD-008's chain-orchestrator Open Question; end-to-end byte-identical replay + admission idempotency proven (real corpus monochromatic RESTRICTIVE_RATES→AVOID, deterministic ADMIT+no-fill; fill path stays BENCH-004's synthetic sweep); operational status an explicit captured input (live feed deferred), cooldown stays MOD-007's echo, scheduling an operator action — all named follow-ups; full suite 933 green
- **Epoch (b) gate-G3 prerequisite — Gold Forward-Return Labeler (MOD-009 + FILE-030 run_forward_return_labels.py + TEST-022 + BENCH-005 Gold Forward-Return Label Set; committed golden benchmarks/calibration/artifacts/forward_return_labels.json) date**: 2026-06-17 — deterministic, strictly-downstream, read-only labeling of banked gold decisions with realized forward gold returns per regime×horizon (the G3 input); look-ahead containment enforced by a static import guard + adversarially verified; horizons 5/20/60 td-equiv, nearest-at-or-after exit + gap tolerance, realized/pending/no_exit_in_tolerance statuses; **measurement only — NO decision-path/config/`*_version` change; G3 stays deferred** (corpus monochromatic: committed 1 snapshot all-pending, full corpus 5 snapshots all RESTRICTIVE_RATES/AVOID pending/no-exit, 0 realized; synthetic set proves the math: 4 directions, 6 regimes, 3 statuses, 9 realized); NOT a CAP-013 realization (treasury bounded-context separation); full suite 906 green
