# Dev Graph Log

Chronological record of dev_graph operations. Each entry uses format: `## [DATE] operation | details`

---

## [2026-05-25] init | Dev graph bootstrap

### Created

**Directory structure** (16 subdirectories):
modules, files, tests, gates, predicates, schemas, workflows, agents, skills, decisions, constraints, api_docs, benchmarks, context_packs, observability, governance

**Structural files** (4, no frontmatter):
- CLAUDE.md — operations manual (~400 lines)
- index.md — master index
- log.md — this file
- README.md — orientation document

**Constraint nodes** (3):
- No Wiki Mutation — MUST NOT modify wiki/** or raw/**
- Frontmatter Required — every content node needs valid frontmatter
- Canonical Ownership — one concept = one node

**Decision records** (1):
- ADR - Dev Graph Bootstrap — why dev_graph exists, alternatives considered

**Governance documents** (7):
- Dev Graph Governance — root governance node
- Context Pack Assembly Rules — 8-step assembly sequence
- Admissibility Checks — 9 validation checks
- MCP Tooling Policy — operation safety classifications
- Neo4j Export Mapping — graph export schema
- Database MCP Mapping — Postgres table definitions
- API Documentation Policy — doc source governance

**Reference nodes** (3):
- REF - Wiki CLAUDE.md — links to wiki governance source
- REF - Wiki Metadata Migration Plan — links to schema design source
- REF - Wiki Graph Health Dashboard — links to Dataview pattern source

**API doc source nodes** (2):
- Alpaca API Docs — Alpaca trading API v2
- Anthropic API Docs — Anthropic/Claude API and SDK

**Observability** (1):
- Dev Graph Dashboard — 12 Dataview queries

**Context pack templates** (1):
- Context Pack Template — canonical template for context packs

### Architecture Decisions

- Separate type ontology from wiki (17 dev_graph types vs 17 wiki types)
- Universal frontmatter with implementation_status and relationship arrays
- No placeholder module/file/test nodes (create when code exists)
- Reference nodes link to wiki governance for inheritance
- Context pack template ready for first coding session
- Relationship sections on every node for Neo4j export readiness

### Bootstrap Metrics

- Total content nodes: 18
- Structural files: 4
- Total files: 22
- Frontmatter coverage: 18/18 (100%)
- Active directories: 16
- Empty directories awaiting code: 10
- Type enum values: 17
- Status enum values: 7
- Implementation status enum values: 7
- Confidence enum values: 4
- Dataview dashboard queries: 12

---

## [2026-06-06] schema | Phase 0: Ontology Redesign — Governance Foundation

### Schema Changes (v1.0.0 → v2.2.0)

**Type enum**: 17 → 24 values. Added: `architecture`, `system`, `capability`, `interface`, `event`, `knowledge_asset`, `pattern`.

**Confidence enum**: 4 → 5 values. Added: `experimental`.

**Evidence field**: NEW universal field. Allowed values: `wiki`, `layer2`, `code`, `benchmark`, `ADR`, `external`, `design`.

**canonical_id field**: NEW universal field. Stable identifier per node (TYPE_PREFIX-NUMBER). Primary key for Neo4j export. Never changes on rename.

**Relationship types**: 8 → 17. Added: `Contains`, `Implements`, `Emits`, `Triggered By`, `Guards`, `Originates From`, `Justified By`, `Realizes`, `Composes`.

**Lint checks**: 7 → 11. Added: Check 8 (type-content alignment), Check 9 (deprecated reference detection), Check 10 (canonical ID uniqueness), Check 11 (evidence-confidence coherence).

**Stale thresholds**: Uniform 30-day → type-aware (30-180 days).

**Dashboard queries**: 12 → 20. Added: #13-20 (canonical ID coverage, evidence coverage, pattern realization, traceability gaps, population progress, population debt x3).

### New Directories (7)

architecture/, systems/, capabilities/, interfaces/, events/, knowledge_assets/, patterns/

### Nodes Created (1)

- ADR - Ontology Redesign (ADR-002) — documents the redesign decision

### Nodes Updated (19)

All existing content nodes migrated to add `canonical_id` and `evidence` fields:
- CON-001: No Wiki Mutation
- CON-002: Frontmatter Required
- CON-003: Canonical Ownership
- ADR-001: ADR - Dev Graph Bootstrap
- GOV-001: Dev Graph Governance
- GOV-002: Context Pack Assembly Rules
- GOV-003: Admissibility Checks
- GOV-004: MCP Tooling Policy
- GOV-005: Neo4j Export Mapping
- GOV-006: Database MCP Mapping
- GOV-007: API Documentation Policy
- REF-001: REF - Wiki CLAUDE
- REF-002: REF - Wiki Metadata Migration Plan
- REF-003: REF - Wiki Graph Health Dashboard
- REF-004: Infrastructure Diagram
- API-001: Alpaca API Docs
- API-002: Anthropic API Docs
- OBS-001: Dev Graph Dashboard
- CTX-001: Context Pack Template

### Governance Updates

- CLAUDE.md: Complete rewrite (431 → ~580 lines) with v2.2.0 schema
- Neo4j Export Mapping: 7 new labels, 9 new edge types, canonical_id as primary key
- Dev Graph Dashboard: 8 new Dataview queries (#13-20)
- index.md: Updated with canonical_ids, new sections, updated statistics

### Phase 0 Metrics

- Total content nodes: 20 (19 migrated + 1 new ADR)
- Canonical ID coverage: 20/20 (100%)
- Evidence field coverage: 20/20 (100%)
- Schema version: 2.2.0
- Type enum values: 24
- Relationship types: 17
- Directories: 23 (16 existing + 7 new)
- Lint checks: 11
- Dashboard queries: 20

### Design Documents (frozen, not part of dev_graph)

- audit_plan.md — Ontology Redesign
- audit_plan_addendum.md — Architecture Review Addendum
- final_strategic_review.md — Final Strategic Ontology Review
- population_strategy.md — Population Strategy and Execution Roadmap

---

## [2026-06-06] populate | Phase 1: Architecture Skeleton + Knowledge Foundations

### Nodes Created (14)

**Architecture nodes (4)**:
- Context Map (ARCH-001) — formal bounded context diagram, 6 systems, 8 interfaces
- Runtime Topology (ARCH-002) — runtime event/data flow model, 12 domain events, scheduling
- Layer Model (ARCH-003) — L1 (data) → L2 (analysis) → L3 (execution) with snapshot-as-truth contract
- Infrastructure Diagram (ARCH-004) — migrated from root-level REF-004, retyped reference → architecture

**Knowledge asset nodes (10)**:
- Event Sourcing (KA-001) — immutable event sequences, replay, audit trails
- CQRS (KA-002) — read/write model separation, snapshot layer design
- Supervisor Pattern Methodology (KA-003) — meta-agent governance, treasury constraints, institutional memory
- Office Action Methodology (KA-004) — deterministic state machine interventions, integration checkpoints
- Guardrail Philosophy (KA-005) — hard constraints before autonomy, non-negotiable limits
- Layer 2 Design Principles (KA-006) — snapshot-as-truth-layer, deterministic assembly, schema stability
- Context Engineering (KA-007) — tokens as money, structured retrieval, budget management
- Agent Safety Principles (KA-008) — credential isolation, self-verification, phased autonomy
- Stateless Agent Architecture (KA-009) — Wake-Execute-Sleep, file-based personality, git persistence
- Paper Trading Validation (KA-010) — mandatory simulated validation, quantitative promotion criteria

### Nodes Deprecated (1)

- Infrastructure Diagram (REF-004) at dev_graph root → deprecated, replaced by ARCH-004 in architecture/

### Source Wiki Pages Referenced

Architecture Overview, Trading Engine Pipeline, Three-Layer Trading System, Claude-Assisted Trading Stack, Syndicate Squad Architecture, Guardrail Architecture, Autonomous Trading Risk Model, Agent Memory Architecture, Context Budget Engineering, Office Action Loop, Paper Trading, Stateless Agent Recovery, Agent Self-Verification, Trade Logging, Treasury Policy System, Multi-Agent Orchestration, API Credential Isolation, Walk-Forward Optimization, MCP Architecture

### Phase 1 Metrics

- Total content nodes: 34 (20 from Phase 0 + 14 new)
- Active nodes: 33 (1 deprecated: REF-004)
- Architecture nodes: 4
- Knowledge asset nodes: 10
- Canonical ID coverage: 34/34 (100%)
- Evidence field coverage: 34/34 (100%)
- Wiki pages referenced via source_paths: 19
- Populated directories: 10 / 23
- Empty directories: 15 (awaiting Phase 2+)
- Population roadmap target: 30-32 nodes. Actual: 34 (on track)

---

## [2026-06-06] populate | Phase 2: System Boundaries

### Nodes Created (7)

**System nodes (6)**:
- Data Pipeline (SYS-001) — market data ingestion, feature engineering, snapshot assembly (L1+L2)
- Trading Engine (SYS-002) — signal generation, order management, stop-loss, position tracking (L3)
- Risk Control (SYS-003) — guardrail enforcement, exposure tracking, circuit breaking
- Agent Runtime (SYS-004) — state persistence, context assembly, trade logging
- Evaluation Loop (SYS-005) — performance scoring, promotion validation, lifecycle management
- Supervisor Office (SYS-006) — decision making, treasury management, upgrade evaluation, orchestration

**Workflow nodes (1)**:
- System Lifecycle (WF-001) — 9-state lifecycle: Cold → Initialized → PaperTrading → Validated → Candidate → Production → Paused → Emergency → Archived

### Relationship Summary

All 6 system nodes include:
- `contains_capabilities` forward references to Phase 3 capability nodes
- `upstream_systems` / `downstream_systems` defining inter-system data flow
- `Originates From` edges to knowledge assets established in Phase 1
- `source_paths` referencing wiki pages for domain knowledge context

System dependency graph:
```
Data Pipeline → Trading Engine ↔ Risk Control
                Trading Engine → Agent Runtime
                Agent Runtime → Evaluation Loop → Supervisor Office → Trading Engine
```

### Phase 2 Metrics

- Total content nodes: 41 (34 from Phase 1 + 7 new)
- Active nodes: 40 (1 deprecated: REF-004)
- System nodes: 6
- Workflow nodes: 1
- Populated directories: 12 / 23
- Empty directories: 13
- Population roadmap target: 38-40 nodes. Actual: 41 (on track)
- Knowledge-to-system traceability: all 6 systems link to knowledge assets via Originates From

---

## [2026-06-06] populate | Phase 3: Capabilities + Patterns

### Nodes Created (28)

**Capability nodes (18)**:

Data Pipeline (3):
- Market Scanning (CAP-001) — realizes Pipeline Pattern
- Feature Engineering (CAP-002) — realizes Pipeline Pattern
- Snapshot Assembly (CAP-003) — realizes CQRS Pattern; originates from Layer 2 Design Principles

Trading Engine (4):
- Signal Generation (CAP-004) — realizes Pipeline Pattern, Event Sourcing Pattern
- Order Management (CAP-005) — realizes Pipeline Pattern, Guardrail Pattern
- Stop-Loss Management (CAP-006) — realizes Guardrail Pattern
- Position Tracking (CAP-007) — realizes Event Sourcing Pattern

Risk Control (2):
- Guardrail Enforcement (CAP-008) — realizes Guardrail Pattern; originates from Guardrail Philosophy
- Exposure Tracking (CAP-009) — realizes Guardrail Pattern

Agent Runtime (3):
- State Persistence (CAP-010) — realizes Context Assembly Pattern; originates from Stateless Agent Architecture
- Context Assembly (CAP-011) — realizes Context Assembly Pattern; originates from Context Engineering
- Trade Logging (CAP-012) — realizes Event Sourcing Pattern

Evaluation Loop (2):
- Performance Scoring (CAP-013) — realizes Evaluation Loop Pattern
- Promotion Validation (CAP-014) — realizes Promotion Pattern, Guardrail Pattern; originates from Paper Trading Validation

Supervisor Office (4):
- Decision Making (CAP-015) — realizes Supervisor Pattern; originates from Supervisor Pattern Methodology
- Treasury Management (CAP-016) — realizes Treasury Approval Pattern; originates from Supervisor Pattern Methodology
- Upgrade Evaluation (CAP-017) — realizes Evaluation Loop Pattern
- Team Orchestration (CAP-018) — realizes Multi-Agent Coordination Pattern; originates from Supervisor Pattern Methodology

**Pattern nodes (10)**:
- Supervisor Pattern (PAT-001) — coordination; composes Multi-Agent Coordination + Treasury Approval
- Guardrail Pattern (PAT-002) — governance; 4 realizing capabilities
- Evaluation Loop Pattern (PAT-003) — behavioral; 2 realizing capabilities
- Pipeline Pattern (PAT-004) — structural; 4 realizing capabilities
- Event Sourcing Pattern (PAT-005) — behavioral; 2 realizing capabilities
- Context Assembly Pattern (PAT-006) — structural; 2 realizing capabilities
- Treasury Approval Pattern (PAT-007) — governance; 1 realizing capability
- Promotion Pattern (PAT-008) — governance; 1 realizing capability
- CQRS Pattern (PAT-009) — structural; 1 realizing capability
- Multi-Agent Coordination Pattern (PAT-010) — coordination; 1 realizing capability

### Edge Summary

- Realizes edges: 23 (capabilities → patterns)
- Composes edges: 2 (Supervisor Pattern → Multi-Agent Coordination, Treasury Approval)
- Originates From edges: 12 (capabilities/systems → knowledge assets)
- All capabilities reference parent_system
- All patterns reference related_knowledge

### Phase 3 Metrics

- Total content nodes: 69 (41 from Phase 2 + 28 new)
- Active nodes: 68 (1 deprecated: REF-004)
- Capability nodes: 18 (3+4+2+3+2+4 across 6 systems)
- Pattern nodes: 10 (3 structural + 3 governance + 2 behavioral + 2 coordination)
- Pattern realization coverage: 18/18 capabilities have at least one realizes edge (100%)
- Populated directories: 14 / 23
- Empty directories: 11
- Population roadmap target: 68-72 nodes. Actual: 69 (on target)
- Structural skeleton complete: Architecture → Systems → Capabilities fully populated

---

## [2026-06-06] populate | Phase 4.5 Contracts + Phase 5 Implementation-Readiness

Architectural review of the original Phase 5 plan determined that creating module nodes whose
contracts existed only in prose would invert the ontology's contract-before-implementation priority
(§3.20) and leave the pre-existing dangling capability interface refs unresolved. A minimal
**Phase 4.5 Contract Layer** was inserted: only the 2 interfaces + 3 schemas the first
implementation slice requires. Canonical IDs preserve the Population Strategy §4.6 reservations
(non-contiguous by design); §4.6 numbering NOT deprecated.

### Nodes Created (8)

**Interface nodes (2)**:
- Risk Check API (INT-003) — Risk Control → Trading Engine; implemented by Guardrail Engine
- Decision API (INT-006) — Supervisor Office → Trading Engine; implemented by Decision Engine

**Artifact schema nodes (3)**:
- Decision Packet Schema (SCHEMA-004) — Decision API output; produced by Decision Engine
- Trade Validation Request Schema (SCHEMA-007) — Risk Check API input; consumed by Guardrail Engine
- Trade Validation Decision Schema (SCHEMA-008) — Risk Check API output; produced by Guardrail Engine

**Module nodes (2, plan-only — no application code)**:
- Guardrail Engine (MOD-001) — implements Risk Check API; realizes Guardrail Pattern; status planned / not-started
- Decision Engine (MOD-002) — implements Decision API; realizes Supervisor Pattern; status planned / not-started

**Context pack nodes (1)**:
- Phase 5 Bootstrap Context (CTX-002) — first coding-session pack: substrate ADR-003 + Guardrail Engine

### Changes

- CAP-008 Guardrail Enforcement: `implemented_by` += [[Guardrail Engine]]; existing `[[Risk Check API]]` ref now RESOLVES
- CAP-015 Decision Making: `implemented_by` += [[Decision Engine]]; existing `[[Decision API]]` ref now RESOLVES
- CLAUDE.md: appended "## Phase 5: Implementation Node Authoring" (module/file/test templates + 10-step writeback checklist). No schema/enum change; schema_version unchanged (2.2.0).
- Dev Graph Dashboard (OBS-001): added query #21 "Population Debt: Modules Without Tests" (queries #13–20 already present — not duplicated)
- index.md: Interfaces / Schemas / Modules sections populated; CTX-002 added; statistics updated

### Reserved (NOT created — out of first slice / acceptable debt)

- Interfaces INT-001/002/004/005/007/008; Schemas SCHEMA-001/002/003/005/006 → future Phase 4
- All FILE-* / TEST-* nodes → created at writeback when real files/tests exist
- Snapshot Consumer module → when Layer 2 Snapshot Schema (SCHEMA-001) exists
- Substrate ADR-003 (tech stack / repo layout) → produced in the first coding session via CTX-002

### Phase 4.5 + 5 Metrics

- Total content nodes: 77 (69 from Phase 3 + 8 new). Active: 76 (REF-004 deprecated).
- New type counts: interface 2, artifact_schema 3, module 2; context_pack 1 → 2.
- Governance nodes: 7 (UNCHANGED) — §10.3 "governance > implementation" bloat rule satisfied.
- Canonical ID coverage: 77/77 (100%). Evidence coverage: 77/77 (100%).
- Realizes edges: 25 (23 capabilities + 2 modules). Dashboard queries: 21.
- Orphans introduced: 0 (interfaces ← capability `interfaces` + module `Implements`; schemas ← interface input/output + module Consumes/Produces; modules ← capability `implemented_by`).
- Dangling wikilinks resolved: 2 (CAP-008 → Risk Check API, CAP-015 → Decision API).
- vs Phase 5 soft ceiling 200: 77 (well under).
- ID scheme: Population Strategy §4.6 reservations preserved; non-contiguous IDs accepted.

---

## [2026-06-06] session | Phase 5 first coding session — Guardrail Engine vertical slice

Drove the first real application code from [[Phase 5 Bootstrap Context]] (CTX-002): substrate
ADR → Guardrail Engine implementation → tests → writeback. **15 tests pass** (pytest 9.0.2 /
Python 3.10.6). This is the first source code in the repository.

### Decision records (1)

- ADR - Implementation Substrate (ADR-003) — Python 3.10+, `src/` layout mirroring module_path,
  uv + PEP 621 pyproject, pytest, mypy --strict, stdlib dataclasses (pydantic deferred),
  fail-closed env-var config.

### Application code created (not dev_graph nodes)

- `pyproject.toml` (zero runtime deps; `[tool.pytest.ini_options] pythonpath=["src"]`)
- `src/risk/guardrail_engine/`: `models.py`, `predicates.py`, `guardrail_engine.py` (+ `__init__.py`)
- `tests/risk/`: `test_predicates.py` (7), `test_guardrail_engine.py` (8)

### Writeback — dev_graph nodes created (5)

**File nodes (3)** — all `module: [[Guardrail Engine]]`, evidence [code]:
- guardrail_engine.py (FILE-001), predicates.py (FILE-002), models.py (FILE-003)

**Test nodes (2)** — evidence [code], implementation_status tested:
- test_predicates (TEST-001) covers predicates.py; test_guardrail_engine (TEST-002) covers guardrail_engine.py

### Writeback — nodes updated (5)

- MOD-001 Guardrail Engine: status planned→active, implementation_status not-started→**tested**;
  evidence += code; confidence inferred→confirmed; related_files (3) + related_tests (2) populated;
  Contains / Validated By edges added.
- INT-003 Risk Check API: planned→active, not-started→**implemented**; evidence += code;
  confidence→confirmed; stability experimental→evolving; Validated By → test_guardrail_engine.
- SCHEMA-007 / SCHEMA-008: planned→active, not-started→**implemented**; evidence += code;
  confidence→confirmed; `schema_path` → `src/risk/guardrail_engine/models.py`; Used By += models.py.
- CAP-008 Guardrail Enforcement: implementation_status not-started→**in-progress**; evidence += code.

### Metrics

- Total content nodes: 83 (77 + 6: ADR-003, FILE-001/002/003, TEST-001/002). Active: 82 (REF-004 deprecated).
- New type counts: decision_record 2→3, file 3, test 2. Governance: 7 (unchanged).
- Canonical ID + evidence coverage: 83/83 (100%). Realizes edges: 26.
- Test result: 15 passed in 0.13s. Implementation→test traceability complete for MOD-001.
- Populated directories: 19 / 23 (files, tests now populated). Empty: 6.
- vs Phase 5 soft ceiling 200: 83.

### Deferred (next)

- Phase 6 #1 Trade Validation Gate + predicate nodes (now unblocked — predicates exist in
  `predicates.py`; gate/predicate nodes can link to FILE-002 / TEST-001).
- ruff + mypy not yet installed → lint/type gates declared in ADR-003 but not run this session.

---

## [2026-06-06] populate | Phase 6 #1 — Trade Validation Gate + predicates

First quality-infrastructure nodes, created after the Guardrail Engine code exists (predicates
live in `predicates.py` / FILE-002, tested by `test_predicates` / TEST-001). Resolves CAP-008's
Phase-6 forward-reference. Gate/predicate nodes were deliberately deferred until code existed.

### Nodes Created (6)

**Gate (1)**:
- Trade Validation Gate (GATE-001) — blocking checkpoint; gate logic = `GuardrailEngine.validate()`; `in-progress` (validation logic tested, not yet wired into a live trade pipeline — no order router yet)

**Predicates (5)** — each `implemented_in: src/risk/guardrail_engine/predicates.py`, `validated_by: [[test_predicates]]`, status tested:
- Position Size OK (PRED-001) — `position_size_ok`
- Daily Loss Cap OK (PRED-002) — `daily_loss_cap_ok`
- Max Trades OK (PRED-003) — `max_trades_ok`
- Max Positions OK (PRED-004) — `max_positions_ok`
- Withdrawal Disabled (PRED-005) — `withdrawal_disabled`

### Changes

- CAP-008 Guardrail Enforcement: `### Contains` prose forward-ref replaced with real links to GATE-001 + the 5 predicates.
- index.md: Gates + Predicates sections populated; statistics updated.

### Edges

- Each predicate `Guards` → [[Trade Validation Gate]]; gate `Depends On` → the 5 predicates; gate `Guards` → [[Guardrail Enforcement]].
- Gate `Consumes` → [[Trade Validation Request Schema]]; `Validated By` → [[test_guardrail_engine]].

### Metrics

- Total content nodes: 89 (83 + 6). Active: 88 (REF-004 deprecated).
- New type counts: gate 1, predicate 5. Governance: 7 (unchanged).
- Canonical ID + evidence coverage: 89/89 (100%).
- Populated directories: 21 / 23 (gates, predicates now populated). Empty: 4 (events, agents, skills, benchmarks).
- vs Phase 5 soft ceiling 200: 89.

---

## [2026-06-06] session | Phase 5 second coding session — Decision Engine vertical slice

Second vertical slice (MOD-002). Contract-sufficiency check found the Decision API output
contract (SCHEMA-004) complete but the **input contract missing** (`input_schema: null`). Created
the one minimal contract required — SCHEMA-005 Evaluation Scorecard Schema (reserved §4.6 id) —
then implemented and tested the engine. **27 tests pass** (15 prior + 12 new).

### Contract created (1)

- Evaluation Scorecard Schema (SCHEMA-005) — Decision API input; fills INT-006 `input_schema: null`.
  Treasury state / upgrade catalog / institutional memory kept as internal value objects (intra-system,
  not schema nodes). Evaluation API (INT-007) transport deferred.

### Application code created

- `src/supervisor/decision_engine/`: `models.py`, `scoring.py`, `decision_engine.py` (+ `__init__.py`)
- `tests/supervisor/`: `test_scoring.py` (5), `test_decision_engine.py` (7)

### Writeback — dev_graph nodes created (5)

**File nodes (3)** — `module: [[Decision Engine]]`, evidence [code]:
- decision_engine.py (FILE-004), scoring.py (FILE-005), models.py (supervisor) (FILE-006)
  - Note: FILE-006 named `models.py (supervisor)` to avoid an Obsidian basename collision with FILE-003.

**Test nodes (2)** — evidence [code], implementation_status tested:
- test_scoring (TEST-003) covers scoring.py; test_decision_engine (TEST-004) covers decision_engine.py

### Writeback — nodes updated (5)

- MOD-002 Decision Engine: planned/not-started → active/**tested**; evidence += code; confidence
  inferred→confirmed; related_files (3) + related_tests (2); Consumes / Contains / Validated By edges added.
- INT-006 Decision API: planned/not-started → active/**implemented**; `input_schema: null` →
  [[Evaluation Scorecard Schema]]; evidence += code; confidence→confirmed; stability experimental→evolving.
- SCHEMA-004 Decision Packet: → active/**implemented**; `schema_path` → `src/supervisor/decision_engine/models.py`; evidence += code.
- SCHEMA-005 Evaluation Scorecard: → active/**implemented**; evidence += code.
- CAP-015 Decision Making: implementation_status not-started → **in-progress**; evidence += code.

### Metrics

- Total content nodes: 95 (89 + 6: SCHEMA-005, FILE-004/005/006, TEST-003/004). Active: 94 (REF-004 deprecated).
- New type counts: artifact_schema 3→4, file 3→6, test 2→4. Governance: 7 (unchanged).
- Canonical ID + evidence coverage: 95/95 (100%). Realizes edges: 27.
- Test result: 27 passed. Two modules (MOD-001, MOD-002) now implemented + tested.
- vs Phase 5 soft ceiling 200: 95.

## 2026-06-07 writeback | Layer 2 Snapshot contract (SCHEMA-001 / INT-001) + Snapshot Consumer vertical slice

**Decision context.** Reordered the next slice to build the *upstream* Layer-2 truth contract before the
Decision Packet consumer — building the downstream consumer first would pin it to an unstable input and
force rework. Two forks resolved by the user: (1) "wire INT-006 downstream" dropped — INT-006 is today's
treasury-upgrade Decision API, not the gold DecisionPacket v0; INT-006 untouched. (2) SCHEMA-001 grounded
in **real** Ripley artifacts (`snapshot_sources/`), not inferred from prose. Reserved §4.6 ids honoured:
SCHEMA-001 = Layer 2 Snapshot, INT-001 = Snapshot API. No execution/order/trade nodes created;
INT-002, SCHEMA-002/003/006 remain reserved and uncreated.

### Nodes Created (6)

- **SCHEMA-001 Layer 2 Snapshot Schema** (artifact_schema, active/implemented) — the foundational data
  contract, grounded against `snapshot_sources/latest_snapshot.json` + `snapshot_publisher.py`. Captures
  the 21-key payload, the SeriesValue/Guards/QualitySummary shapes, and the deterministic `snapshot_id`.
- **INT-001 Snapshot API** (interface, active/implemented) — Layer 2 → Layer 3 read contract. Output
  schema SCHEMA-001, `input_schema: null` (pull contract). Mode 1 (latest_snapshot.json) implemented;
  mode 2 (query by snapshot_id) specified but deferred. parent_capability CAP-003.
- **MOD-003 Snapshot Consumer** (module, active/tested) — fail-closed Layer-3 ingestion gate.
- **FILE-007 models.py (snapshot)** + **FILE-008 consumer.py** — `src/snapshot/snapshot_consumer/`.
  Basename-disambiguated from FILE-003 `models.py` and FILE-006 `models.py (supervisor)`.
- **TEST-005 test_models (snapshot)** + **TEST-006 test_consumer** — 16 tests.

### Code shipped

- `src/snapshot/snapshot_consumer/{models,consumer}.py` (+ `__init__`), stdlib-only frozen dataclasses
  per ADR-003. `Snapshot.recompute_id()` mirrors the publisher's `compute_snapshot_id` and **reproduces
  the real artifact's id `952cc83a…afaef`** — the SCHEMA-001 grounding anchor.
- Fail-closed contract: `consume()` returns a snapshot only if `verdict == PASS ∧ guards.snapshot_ok ∧
  ¬forced ∧ ¬dry_run`; absent file / failed gate → None ("output nothing"); malformed payload →
  `SnapshotContractError` (loud, never masked as absence).
- `tests/snapshot/` with PASS (verbatim real artifact) + derived FAIL/FORCED fixtures.
- `pyproject.toml` wheel packages updated (`src/risk`, `src/supervisor`, `src/snapshot`).

### Changes to existing nodes

- `index.md`: INT-001, SCHEMA-001, MOD-003, FILE-007/008, TEST-005/006 added; reserved placeholders
  trimmed (INT-001, SCHEMA-001 removed from the reserved lists); statistics refreshed.

### Metrics

- Total content nodes: 101 (95 + 6). Active: 100 (REF-004 deprecated).
- Type counts: interface 2→3, artifact_schema 4→5, module 2→3, file 6→8, test 4→6.
- Canonical ID + frontmatter coverage: 101/101 (100%).
- Test result: **43 passed** (27 prior + 16 new). Three modules now implemented + tested
  (MOD-001 Guardrail, MOD-002 Decision Engine, MOD-003 Snapshot Consumer).
- vs Phase 5 soft ceiling 200: 101.

### Deferred / open

- INT-001 mode 2 (query by `snapshot_id` from `layer2_truth.db`) — needed for replay/counterfactual.
- CAP-003 Snapshot Assembly describes the Layer-2 *producer*; MOD-003 is the Layer-3 *consumer* — a
  producer/consumer seam flagged for the generic→Ripley re-grounding ADR (not split this slice).
- Next in the data path: Layer 2 snapshot → features/decision → Decision Packet v0 → consumer.

## 2026-06-07 governance | Decision Layer Re-grounding (ADR-004) + clarify-in-place of treasury decision branch

**Driver.** A read-only multi-agent audit (7 audits → synthesis → 3 adversarial verifiers) confirmed MOD-002 /
INT-006 / SCHEMA-004 / SCHEMA-005 carry **treasury-upgrade** semantics, not gold trading — and the adversarial
pass **rejected** a proposed "Guard Mapper" next slice (redundant with `Snapshot Consumer.is_consumable()`;
emits guard verdicts into a vacuum since v0 is deferred). No ontology redesign; no canonical_id changes; no
execution/order/trade nodes.

### Nodes Created (1)

- **ADR-004 Decision Layer Re-grounding** (decision_record, active/implemented). Records: (1) the four nodes are
  the Supervisor Office treasury-upgrade branch; (2) the Gold Trading Decision branch will be NEW ontology
  objects with NEW canonical_ids (gold v0 = a future SCHEMA-00x, never SCHEMA-004); (3) canonical_id
  immutability + no in-place reclassification (split-only for type changes); (4) the Gold v0 **determinism
  invariant** (depends only on deterministic SCHEMA-001-derived features + versioned artifacts; never raw
  payloads/implicit state); (5) next slice = MOD-004 Feature Builder.

### Clarify-in-place (4 nodes — canonical_ids unchanged, no renames, no splits)

- MOD-002 Decision Engine, INT-006 Decision API, SCHEMA-004 Decision Packet Schema, SCHEMA-005 Evaluation
  Scorecard Schema each gained a `## Scope` section ("Supervisor Office treasury-upgrade path — not the gold
  DecisionPacket v0"), `updated`→2026-06-07, and `related_decisions += [[ADR - Decision Layer Re-grounding]]`.

### Changes to existing nodes

- `index.md`: ADR-004 added to Decisions; statistics refreshed (decision_record 3→4).

### Metrics

- Total content nodes: 102 (101 + ADR-004). Active: 101 (REF-004 deprecated).
- decision_record 3→4. Canonical ID + frontmatter coverage: 102/102 (100%). No code changed (suite still 43).
- vs Phase 5 soft ceiling 200: 102.

### Deferred / open (blueprint for next session)

- **MOD-004 Feature Builder** is the sanctioned next slice: deterministic, stateless, pure, replay-safe,
  snapshot-local only. Allowed feature classes: spreads / ratios / levels / arithmetic transforms (e.g.
  curve_2s10s, real_yield_10y, breakeven_10y, usd_level, vol_level). Forbidden: moving averages, momentum,
  rolling windows, z-scores, percentiles, look-ahead, inferred regimes, learned embeddings — anything needing
  history (a snapshot is temporally independent). Output contract (Feature Vector Schema, a new SCHEMA-00x) to
  be authored contract-first at the start of that slice.
- Gold DecisionPacket v0 authoring remains gated on real SCHEMA-001-derived features existing.

## 2026-06-07 writeback | MOD-004 Feature Builder vertical slice (ADR-005 + SCHEMA-009)

**Slice.** Implemented the deterministic, snapshot-local Feature Layer — the prerequisite that produces the
real SCHEMA-001-derived features ADR-004 requires before a Gold DecisionPacket v0 may be authored. Contract
authored first (ADR-005 + SCHEMA-009), then code, then writeback. No gold-decision / execution / order / trade
nodes; INT-006 / SCHEMA-004 / SCHEMA-005 / MOD-002 untouched; no regime/guard-mapper logic.

### Nodes Created (6)

- **ADR-005 Feature Layer Contract** (decision_record, active). Governs: deterministic eligibility
  (levels/spreads/ratios/arithmetic), forbidden classes (MA/momentum/rolling/z-score/percentile/smoothing/
  regimes/embeddings — anything needing history), provenance requirements, the replay determinism rule
  (same snapshot_id + schema_version ⇒ identical output), MOD-003-only input boundary (never raw JSON),
  and the relationship to ADR-004.
- **SCHEMA-009 Feature Vector Schema** (artifact_schema, active/implemented). FeatureVector{snapshot_id,
  schema_version, features map, unavailable_features} + Feature{name, value, inputs, max_staleness_days,
  revision_risk}. NEW canonical id (not reusing SCHEMA-004); 002/003/006 stay reserved.
- **MOD-004 Feature Builder** (module, active/tested).
- **FILE-009 models.py (features)** + **FILE-010 feature_builder.py** — `src/features/feature_builder/`.
  FILE-009 basename-disambiguated (4th `models.py`: risk/supervisor/snapshot/features).
- **TEST-007 test_feature_builder** — 10 tests.

### Code shipped

- `src/features/feature_builder/{models,feature_builder}.py` (+ `__init__`), stdlib frozen dataclasses
  (ADR-003), zero deps. `build_features(snapshot) -> FeatureVector`: pure, total, no IO/clock/randomness.
- 14-feature v0.1.0 registry (levels + spreads only): real_yield_10y/5y, breakeven_10y/5y/5y5y_fwd,
  curve_2s10s, curve_5s10s, policy_spread, usd_level, vol_level, rates_vol, equity_level, gold_price, gold_flow.
- Provenance per feature: `max_staleness_days` (max over inputs), `revision_risk` (OR over inputs), read from
  SCHEMA-001 fields. Missing input ⇒ feature listed in `unavailable_features` (no partial values).
- Tests grounded in the real artifact (consumed via MOD-003 `consume()`): exact level values, spread arithmetic
  (curve_2s10s≈0.50, curve_5s10s≈0.37, policy_spread==0.0), provenance (EFFR/DFF max staleness=2),
  determinism (build==build), revision_risk propagation, unavailable-feature on dropped DGS5, input-boundary.
- `pyproject.toml` wheel packages += `src/features`.

### Changes to existing nodes

- `index.md`: added MOD-004, SCHEMA-009, ADR-005, FILE-009/010, TEST-007; statistics refreshed.

### Metrics

- Total content nodes: 108 (102 + 6). Active: 107 (REF-004 deprecated).
- Type counts: module 3→4, file 8→10, test 6→7, artifact_schema 5→6, decision_record 4→5.
- Canonical ID + frontmatter coverage: 108/108 (100%).
- Test result: **53 passed** (43 prior + 10 new). Four modules now implemented + tested
  (MOD-001 Guardrail, MOD-002 Decision Engine, MOD-003 Snapshot Consumer, MOD-004 Feature Builder).
- vs Phase 5 soft ceiling 200: 108.

### Deferred / open

- Capability seam: CAP-002 Feature Engineering is L2-producer-framed; MOD-004 derives features L3-side — resolve
  in a future re-grounding step (same pattern as CAP-003/MOD-003), not forced here.
- Ratio features admissible by ADR-005 but none in v0.1.0 (no unit-safe denominator in the initial set).
- **Gold DecisionPacket v0 is now grounded**: real deterministic SCHEMA-001-derived features exist, so a
  planning ADR for v0 is unblocked (regime_class/confidence inputs can cite concrete features). Next.

## 2026-06-07 governance | ADR-006 Gold DecisionPacket v0 Planning

**Driver.** ADR-004's gate is satisfied (MOD-004 + ADR-005 + SCHEMA-009 give real deterministic
SCHEMA-001-derived features), so the Gold DecisionPacket v0 planning ADR is unblocked. Authored as a
**governance / architectural-boundary** record that answers *"under what constraints may a Gold
DecisionPacket contract be created?"* — NOT the contract itself. No schema frozen; no code; no
schema/module/interface/file/test nodes; no execution/order/broker/position/trade/live-trading nodes.
Treasury branch (MOD-002 / INT-006 / SCHEMA-004 / SCHEMA-005) untouched and kept permanently separate.

### Nodes Created (1)

- **ADR-006 Gold DecisionPacket v0 Planning** (decision_record, `status: draft` = "Proposed",
  `implementation_status: not-started`, `evidence: [design, ADR]`). Records, for the future gold
  decision layer: (1) net-new, permanently separate bounded context vs the Supervisor treasury branch;
  (2) input boundary — consumes only SCHEMA-009 FeatureVectors / versioned artifacts / future L3 guard
  outputs, never raw SCHEMA-001, raw JSON, external APIs, implicit state, or unversioned/history-dependent
  signals; (3) replay invariant — `snapshot_id + feature_schema_version + model_version +
  decision_policy_version + configuration ⇒ identical packet`; (4) provenance must trace to
  source_snapshot_id + MOD-004 feature provenance; (5) feature grounding cites only the 14 real MOD-004
  features (no inventions; gaps deferred); (6) `duplicate_ok`/`operational_ok` are future L3 guards, not
  MOD-004 features; (7) no schema freeze — normative contract is a future SCHEMA node (new id, never
  SCHEMA-004; SCHEMA-010 named non-binding; 002/003/006 stay reserved); (8) Creation Gates — normative
  schema only after MOD-004 ✅ + feature-coverage validated + replay finalized + regime taxonomy +
  confidence semantics agreed. Includes an explicitly **illustrative/provisional/non-normative** field
  sketch.

### Changes to existing nodes

- `index.md`: ADR-006 added to Decisions; statistics refreshed (decision_record 5→6; total nodes 108→109;
  total files 112→113; coverage 109/109); "Last updated" → 2026-06-07.
- `ADR - Decision Layer Re-grounding` (ADR-004): added `[[ADR - Gold DecisionPacket v0 Planning]]` to
  `related_decisions` + one Future Work line (v0 governance now recorded in ADR-006).
- `ADR - Feature Layer Contract` (ADR-005): added `[[ADR - Gold DecisionPacket v0 Planning]]` to
  `related_decisions`.

### Metrics

- Total content nodes: 109 (108 + 1). Active: 108 (REF-004 deprecated).
- Type counts: decision_record 5→6. All others unchanged.
- Canonical ID + frontmatter coverage: 109/109 (100%). canonical_id ADR-006 unique.
- No code changed: 0 files under `src/**` or `tests/**`. No tests run (governance-only slice).
- vs Phase 5 soft ceiling 200: 109.

### Deferred / open

- Creation Gates (b)–(e) remain open: deterministic feature-coverage validation, replay-requirement
  finalization, regime taxonomy, and confidence semantics — all prerequisites before the normative Gold
  DecisionPacket SCHEMA node may be authored.
- Future objects named as non-binding candidates only (not reserved/created): Gold DecisionPacket
  artifact_schema (e.g. SCHEMA-010), gold decision builder module, L3 guards (`duplicate_ok`,
  `operational_ok`, …), regime taxonomy.
- ADR-006 `status: draft` is the governed stand-in for "Proposed" (no `proposed` enum value); promote to
  `active` on acceptance.

## 2026-06-08 session | Deterministic Regime Taxonomy slice (MOD-005 / SCHEMA-010 / ADR-007)

**Slice.** Implemented the deterministic, snapshot-local Regime Taxonomy layer — the canonical semantic
abstraction between MOD-004 Feature Builder and the future Gold Decision Builder. Satisfies **ADR-006 §8(d)**
(the explicit open creation gate). Contract-first (ADR-007 + SCHEMA-010 authored), then code, tests, benchmark,
writeback. No Gold builder / execution / order / trade nodes (ADR-006 §8 still holds); MOD-001/002/003/004,
INT-006, SCHEMA-001/004/005/009 untouched except additive downstream links on MOD-004 / SCHEMA-009.

**ADR-005 reconciliation.** ADR-005 §2 forbids "inferred regimes" *as a feature class*, deferring such logic to
"a later, explicitly stateful node with its own ADR." This is that node — and it is **rule-based and
deterministic, not inferred/learned**. No contradiction: ADR-005 governs feature purity; ADR-007 governs a
separate downstream classification layer that consumes pure features.

**User refinements folded in:** scalar named `rule_margin` (rule-local activation margin, not confidence, with
`rule_threshold`/`rule_scale` carried); thresholds config-driven + versioned (`RegimeConfig`, fingerprint
coherence); rule-selection-first output (`matched_rule_id` primary, `regime` projected); NEUTRAL is the sole
catch-all (conflict surfaced via `secondary_matching_rules`/`near_matching_rules`, no MIXED_SIGNAL); audit
fields (`evaluated_rule_ids`, `skipped_rule_ids`, `failed_required_features`); independent
`classification_trace_version`.

### Nodes Created (14)

- **ADR-007 Deterministic Regime Taxonomy** (decision_record, active/implemented).
- **KA-011 Regime Taxonomy** (knowledge_asset) — why deterministic enumerated regimes belong between features and decisions.
- **PAT-011 Regime Classification Pattern** (pattern, behavioral) — Snapshot → semantic abstraction → decision; composes Pipeline Pattern.
- **CAP-019 Market Regime Classification** (capability, active/tested) — parent system Trading Engine (SYS-002).
- **INT-007 Regime Classification API** (interface, active/implemented) — `classify(FeatureVector) -> RegimeClassification`; canonical upstream contract for the future Gold builder.
- **SCHEMA-010 Regime Classification Schema** (artifact_schema, active/implemented).
- **MOD-005 Market Regime Classifier** (module, active/tested).
- **FILE-011 regime_classifier.py**, **FILE-012 taxonomy.py**, **FILE-013 config.py (regime)**, **FILE-014 models.py (regime)** — `src/regime/regime_classifier/`. FILE-013/014 basename-disambiguated (5th/6th `models.py`/`config.py`).
- **TEST-008 test_regime_classifier**, **TEST-009 test_regime_bench**.
- **BENCH-001 Regime Distribution Benchmark** (benchmark_result) — first benchmark node; populates the previously-empty `benchmarks/` directory.

### Code shipped

- `src/regime/regime_classifier/{models,config,taxonomy,regime_classifier}.py` (+ `__init__` ×2), stdlib frozen
  dataclasses (ADR-003), zero runtime deps. `classify(fv, config, as_of) -> RegimeClassification`: pure, total,
  no IO/clock/randomness/history. 12 regimes (11 signal + INDETERMINATE); priority-ordered RULE_TABLE; real PASS
  fixture → RESTRICTIVE_RATES (rule_margin 0.46).
- `tests/regime/{test_regime_classifier,test_regime_bench}.py` — ~65 tests incl. exhaustive grid sweep, golden
  determinism, fail-closed, config coherence, trace metadata, taxonomy completeness.
- `benchmarks/regime/run_regime_bench.py` + committed golden `artifacts/regime_bench.json` (deterministic
  harness: real-replay byte-identical = true; synthetic sweep coverage 11/11; entropy ≈ 3.01 bits).
- `pyproject.toml` wheel packages += `src/regime`.

### Changes to existing nodes (5)

- **MOD-004 Feature Builder**: `updated`→2026-06-08; added `### Used By → [[Market Regime Classifier]]`; Open
  Questions updated (regime consumer now exists).
- **SCHEMA-009 Feature Vector Schema**: `updated`→2026-06-08; `consumed_by += [[Market Regime Classifier]]`;
  `### Used By += [[Market Regime Classifier]]`.
- **SYS-002 Trading Engine**: `updated`→2026-06-08; `contains_capabilities += [[Market Regime Classification]]`;
  Contains relationship added.
- **ADR-006 Gold DecisionPacket v0 Planning**: `updated`→2026-06-08; added `[[ADR - Deterministic Regime Taxonomy]]`
  to `related_decisions`; §8 update note (gate (d) satisfied; (b)/(c)/(e) advanced; SCHEMA-010 now used for regime →
  Gold packet candidate shifts to next free id).
- **index.md**: all 14 new nodes added; benchmarks section populated; statistics refreshed; "Last updated" → 2026-06-08.

### Canonical-id reassignments (both non-binding reservations, assigned at authoring per ADR-004/006 precedent)

- **SCHEMA-010**: ADR-006 §7 named it a *candidate* for the future Gold DecisionPacket; used here for the regime
  contract → Gold DecisionPacket candidate shifts to the next free schema id.
- **INT-007**: loosely earmarked as a future "Evaluation API" in a prior parenthetical; used here for the Regime
  Classification API → the Evaluation API candidate shifts to INT-008. Index reserved note updated accordingly.

### Metrics

- Total content nodes: 124 (110 + 14). Active: 123 (REF-004 deprecated). (The pre-slice base was 110; the prior index headline of 109 was a long-standing off-by-one, corrected here and in index.md.)
- Type counts: capability 18→19, interface 3→4, artifact_schema 6→7, module 4→5, file 10→14, test 7→9,
  pattern 10→11, knowledge_asset 10→11, decision_record 6→7, benchmark_result 0→1.
- Canonical ID + frontmatter coverage: 123/123 (100%). Populated dirs 21→22 (benchmarks); empty 4→3.
- Test result: **772 passed** (53 prior + 719 regime: 714 classifier + 5 bench). `mypy --strict` clean on
  `src/regime` + tests; `ruff` clean. Five modules now implemented + tested (MOD-001..005).
- vs Phase 5 soft ceiling 200: 123.

### Lint (11 checks, touched nodes)

Frontmatter ✓, enums ✓, orphans ✓ (every new node has ≥1 inbound link), stale ✓, broken wikilinks ✓ (all
new links resolve to created nodes), module `related_constraints` ✓ (MOD-005 → Canonical Ownership),
module `related_tests` ✓, type-content alignment ✓, deprecated refs ✓, canonical_id uniqueness ✓,
evidence-confidence coherence ✓.

### Deferred / open

- Gold DecisionPacket v0 SCHEMA/module/L3-guards remain unauthored (ADR-006 §8); SCHEMA-010 exposed via INT-007
  as the canonical input when that slice runs.
- Domain-anchored thresholds await a real historical snapshot corpus for governed recalibration (future
  `taxonomy_version` bump); replay/coverage evidence today = real determinism + clearly-labelled synthetic sweep.
- Pre-existing: 2 mypy lambda-inference findings in `feature_builder.py` (MOD-004), surfaced by a newer mypy;
  out of this slice's scope.
- Optional `python dev_graph/sync_to_neo4j.py` when Neo4j is up (no script change needed — `benchmark_result`
  and interface/relationship mappings already exist).

## 2026-06-08 governance | ADR-008 Gold Decision Confidence Semantics — closes ADR-006 §8(e); promotes ADR-006 draft→active

**Slice.** Governance + design slice closing the single load-bearing open Gold-DecisionPacket creation gate. After MOD-005 closed gate (d), gate **(e) "Confidence semantics agreed"** was the only genuinely-open gate: the regime `rule_margin` is, per ADR-007 §Decision-3, a *rule-local activation margin* explicitly NOT epistemic confidence, so the Gold confidence scalar was undefined. Authored **ADR-008** to FIX the v0 confidence/uncertainty model; promoted **ADR-006** draft→active with all five §8 gates now passing. **No `src`/`tests`/schema/code** (ADR-006 §8 honored) — the Gold SCHEMA/builder/API/L3-guards remain for the next slice. STEP-0 brief: `GOLD_CONFIDENCE_IMPLEMENTATION_BRIEF.md`.

### Nodes Created (1)

- **ADR-008 Gold Decision Confidence Semantics** (decision_record, active/not-started, confidence confirmed, evidence [design, ADR, code]). Fixes: (1) v0 `confidence` ∈ [0,1] = deterministic **ordinal trust score**, explicitly NOT a calibrated probability; (2) anchor = within-matched-rule normalized `rule_margin` (never raw per-rule scales 0.5–50); (3) discounts = `secondary_matching_rules` (ambiguity), `near_matching_rules` (fragility), cited-feature `revision_risk`/`max_staleness_days` (data quality), `failed_required_features`/`unavailable_features` (coverage); (4) floors = NEUTRAL confident-quiet, INDETERMINATE → min confidence/max uncertainty; (5) `uncertainty` = structural-penalty aggregate (not strict `1−confidence`); (6) REJECTS ADR-004's 3-component performance/calibration/sample_quality variant and forbids SCHEMA-005 calibration bleed (ADR-004 separation); (7) confidence form/weights governed by `decision_policy_version` (bump it, never `taxonomy_version`); empirical recalibration an expected v1 amendment; (8) finalizes the Gold replay key (gate c; `model_version` N/A for the rule-based v0); (9) accepts the 7 reserved-feature gaps (gate b); (10) records the CAP-004 deprecate-and-supersede decision; (11) no schema/code.

### Changes to existing nodes (2)

- **ADR-006 Gold DecisionPacket v0 Planning**: `status: draft → active`; Status "Proposed" → "Accepted" (reconciles prose vs `decision_status: active` — DEBT-18); §8 gate board re-marked — (a)/(d) Closed, (b) Satisfied (gaps accepted), (c) Closed, (e) Closed → "all five gates now pass"; corrected the prior 2026-06-08 note's "(e) materially advanced via rule_margin" framing (rule_margin is NOT the Gold confidence) and added an ADR-008 update note; `related_decisions += [[ADR - Gold Decision Confidence Semantics]]`.
- **index.md**: ADR-008 row added to Decisions; Statistics refreshed (decision_record 7→8; total content nodes 124→125; total files 128→129; coverage 125/125).

### Decision content folded in (per the STEP-0 brief, user-resolved)

- **CAP-004 "Signal Generation" = deprecate-and-supersede** (NOT keep-as-legacy, NOT repurpose-in-place). Rationale: CAP-004 is a not-started, wiki-derived intraday indicator-stack (VWAP/EMA/RVOL over raw L2 → trade signals to Order Management) — obsolete vs the realized deterministic pipeline (SCHEMA-001→MOD-003→MOD-004→MOD-005→Gold; FeatureVector+RegimeClassification → paper DecisionPacket). Decision recorded in ADR-008 §10; **execution deferred to the next slice** — the `status: deprecated` flip + `### Supersedes → [[Signal Generation]]` are applied on the new gold-decision capability node when authored (deprecate-with-successor, no dangling deprecation). Distinct from CAP-015 treasury (SYS-006), untouched.

### Verification (governance slice — no pytest)

- **Empirical sanity check** (the one real snapshot `952cc83a…`, via `consume→build_features→classify`): RESTRICTIVE_RATES / R04 / `rule_margin` 0.46 (real_yield_10y 1.96 vs 1.50, scale 1.0); `secondary`=∅, `near`={R08_strong_usd}, `failed_required`=∅, `unavailable`=∅; provenance staleness 2, revision_risk False. Illustrative v0 weights → confidence ≈ 0.40 / uncertainty ≈ 0.60 (sensible: a modest restrictive-rates call with one competing regime nearby earns middling trust). Floors behave (NEUTRAL>0; INDETERMINATE→0/1). Validates the *structure*; weights stay non-frozen under `decision_policy_version`. (temp script created + deleted; no repo artifact.)
- **11 dev_graph lint checks** on touched nodes (ADR-008, ADR-006, index.md): frontmatter ✓, enums ✓ (status active / impl not-started / confidence confirmed / evidence ⊆ allowed), orphan/≥1 inbound ✓ (ADR-008 ← ADR-006 `related_decisions` + its Justified-By targets), stale ✓, broken wikilinks ✓ (all ADR-008 outbound links resolve: ADR-006/007/004/005, Regime Classification Schema, Feature Vector Schema, Canonical Ownership, Signal Generation, Decision Making), module checks N/A, type-content alignment ✓ (ADR has Status/Context/Decision/Consequences), deprecated refs ✓ (CAP-004 still active until Slice 2), canonical_id uniqueness ✓ (ADR-008 new), evidence-confidence coherence ✓ (confirmed + 3 evidence values).
- **Gate-board coherence**: ADR-006 §8 reads all-pass; advanced-vs-satisfied wording collision corrected (no contradiction for admissibility check #7).
- **DEBT-05**: index per-type tally verified to sum to the headline (125) — coherent.

### Metrics

- Total content nodes: 125 (124 + ADR-008). Active: 124 (REF-004 deprecated). decision_record 7→8; all other type counts unchanged.
- Canonical ID + frontmatter coverage: 125/125 (100%). No code changed: 0 files under `src/**` or `tests/**`. No tests run (governance-only slice).
- vs Phase 5 soft ceiling 200: 125.

### Deferred / open (Slice 2 — now unblocked)

- **Gold DecisionPacket v0**: author contract-first the normative SCHEMA (next free id, never SCHEMA-004), the gold decision builder module (next free MOD id) realizing it, the Gold Decision API (next free INT id — re-derive; do not assume INT-009), tests + a confidence-distribution benchmark; wire INT-007 `output_schema consumed_by` → the gold builder.
- **CAP-004 execution**: deprecate CAP-004 + author the gold-decision capability (next free CAP id) under SYS-002 carrying `### Supersedes → [[Signal Generation]]`; add it to SYS-002 `contains_capabilities`.
- **L3 guards** (`duplicate_ok`/`operational_ok` + the six-guard taxonomy): own governing ADR; never MOD-004 features (ADR-005 / ADR-006 §6).
- **Hygiene pass (separate, before first trusted Neo4j/Graph-RAG export)**: DEBT-02/03/07 export-edge fixes + DEBT-04 KA→ADR backlinks. DEBT-01 publisher NameError rides with the real-corpus work.
- **Real snapshot corpus**: converts gate (b) from accepted-gaps to fully-validated; enables governed `decision_policy_version` recalibration.

## 2026-06-08 contract | Gold DecisionPacket v0 — Slice 2 STEP 1-2 (contract layer + capability + CAP-004 deprecation)

**Slice (in progress).** Contract-first build of the Gold DecisionPacket v0 lineage, now that all ADR-006 §8 gates pass (ADR-008 closed (e); (b)/(c) finalized). This entry covers STEP 1 (contract nodes, no code) + STEP 2 (capability + CAP-004 deprecation). **Paused at the STEP-2 checkpoint for review before any code.** STEP-0 brief: `GOLD_DECISIONPACKET_V0_BRIEF.md`.

### Nodes Created (3)

- **SCHEMA-011 Gold DecisionPacket v0 Schema** (artifact_schema, planned/not-started, confidence inferred, evidence [design, ADR]). The `GoldDecisionPacket` contract — `paper_only`, instrument `GLD`. Field groups: decision (`packet_id`, `decision_mode`, `regime`, `direction` enum LONG/FLAT/AVOID/WATCH, `confidence`, `uncertainty`, `rationale`), provenance/identity (`source_snapshot_id` + echoed regime versions + `matched_rule_id` + `cited_features`), `decision_policy_version`, trust trace (`confidence_inputs`), `guard_refs` (six-guard taxonomy, bool|null), safety (`non_execution_notice`, `constraints`). New canonical id (002/003/006 reserved; never SCHEMA-004). `produced_by` empty until MOD-006.
- **INT-009 Gold Decision API** (interface, planned/not-started, stability experimental). `build_decision(fv, rc, guards=None, config=DEFAULT, as_of=None) -> GoldDecisionPacket`. `input_schema` (primary) SCHEMA-010; Consumes both SCHEMA-009 + SCHEMA-010; output SCHEMA-011. INT-008 left earmarked for the future Evaluation API → this took **INT-009**.
- **CAP-020 Gold Decision Generation** (capability, active/not-started) under SYS-002. `### Supersedes → [[Signal Generation]]`; consumes SCHEMA-009/010, produces SCHEMA-011, provides INT-009, realizes Pipeline Pattern; permanently separate from CAP-015 treasury (ADR-004).

### CAP-004 deprecate-and-supersede (executed per ADR-008 §10)

- **CAP-004 Signal Generation**: status active→deprecated, implementation_status not-started→deprecated, updated→2026-06-08; prominent DEPRECATED banner naming successor CAP-020 + ADR-008 §10 + the Deprecation Procedure (retained; excluded by admissibility #2). Outbound edges retained as historical (Procedure step 4).
- **Inbound-edge rewiring (lint check 9):**
  - **PAT-004 Pipeline Pattern**: `[[Signal Generation]]` → `[[Gold Decision Generation]]` in `instances`, `realized_by_capabilities`, and `### Realized By` (CAP-020 is the successor pipeline stage); updated→2026-06-08.
  - **CAP-005 Order Management**: `### Depends On [[Signal Generation]]` annotated (deprecated; live order routing deferred per ADR-006 Non-Goals; the paper-only gold successor does NOT feed Order Management — annotated, not redirected); updated→2026-06-08.
  - **SYS-002 Trading Engine**: `contains_capabilities` + `### Contains`: `[[Signal Generation]]` → `[[Gold Decision Generation]]` (others kept); `## Capabilities` prose reconciled (was stale — said "4 capabilities", omitted CAP-019) → now lists CAP-004 deprecated + 005/006/007/019/020.

### Design decision settled (regime → direction)

- The regime→direction mapping is **versioned decision-policy config under `decision_policy_version` v0, NOT a companion ADR** — no separation/governance hazard comparable to confidence (gold-internal, paper-only, structurally identical to RegimeConfig thresholds; already governed by ADR-008's `decision_policy_version` axis). Direction enum LONG/FLAT/AVOID/WATCH; INDETERMINATE→WATCH (fail-closed). The per-regime gold thesis is documented in SCHEMA-011 + the brief, flagged provisional/calibration-deferred, to be pinned + fingerprint-coherence-tested in the implementation config. Rationale in `GOLD_DECISIONPACKET_V0_BRIEF.md`.

### Changes to existing nodes (5)

- **index.md**: CAP-004 row struck through (deprecated); CAP-020 / INT-009 / SCHEMA-011 rows added; Statistics refreshed (capability 19→20 incl. 1 deprecated, interface 4→5, artifact_schema 7→8; total content nodes 125→128; total files 129→132; coverage 128/128); INT-008 reserved note clarified (Evaluation API).
- **PAT-004**, **CAP-005**, **SYS-002**, **Signal Generation (CAP-004)** — as above.

### Verification (contract checkpoint — no code yet)

- **11 lint checks** on touched nodes: frontmatter ✓ (NO freeform keys — a stray `updated_note` mistakenly added to CAP-005 was caught and removed); enums ✓; orphans/≥1 inbound ✓ (SCHEMA-011 ← INT-009 output + CAP-020 produces; INT-009 ← CAP-020; CAP-020 ← SYS-002 + PAT-004 + INT-009); stale ✓; broken wikilinks ✓ (all new links resolve); **deprecated-reference (check 9) ✓** — post-flip, no ACTIVE node references `[[Signal Generation]]` except CAP-020's sanctioned `### Supersedes` and CAP-005's explicitly-annotated Depends-On; PAT-004 + SYS-002 redirected to the successor; type-content alignment ✓; canonical_id uniqueness ✓; evidence-confidence coherence ✓.
- **Gate-board coherence**: ADR-006 §8 unchanged (still all-pass).
- **Contract-first discipline**: zero `src/**`, `tests/**`, `benchmarks/**` changes; no module/file/test nodes yet (per the checkpoint).

### Metrics

- Total content nodes: 128 (125 + 3). Active: 126 (REF-004 + CAP-004 deprecated). capability 19→20, interface 4→5, artifact_schema 7→8.
- Canonical ID + frontmatter coverage: 128/128 (100%). No code changed.
- vs Phase 5 soft ceiling 200: 128.

### Deferred / next (STEP 3-6, post-checkpoint)

- **MOD-006 Gold Decision Builder** (`src/gold/decision_builder/`): `models.py` (SCHEMA-011 dataclasses + `Direction` enum), `config.py` (`DecisionPolicyConfig` — confidence weights + regime→direction table + `decision_policy_version` + `decision_policy_fingerprint`), `policy.py` (`trust_score` + `direction_for`), `decision_builder.py` (`build_decision`). Pure/total/stdlib/fail-closed; implement the ADR-008 confidence model.
- **PRED-006 Duplicate OK / PRED-007 Operational OK + GATE-002 Gold Decision Gate** (L3 guard contracts; stateful computation deferred to the paper-trading runtime, ADR-006 Non-Goals).
- **Tests + BENCH-002** (determinism, fail-closed, fingerprint coherence, golden artifact).
- **Writeback**: file/test nodes (FILE-015+, TEST-010/011); bump CAP-020/MOD-006 implementation_status; wire INT-007 / SCHEMA-009 / SCHEMA-010 `consumed_by` → the gold builder; index.md + log.md; 11 lint checks; gate-board coherence.

## 2026-06-08 session | Gold DecisionPacket v0 — Slice 2 STEP 0/3-6 (builder, guards, tests, benchmark, writeback)

**Slice complete.** Built the Gold Decision Builder (MOD-006) on the approved frozen contract (SCHEMA-011 / INT-009 / CAP-020). Contract fix first (STEP 0), then code, L3 guard nodes, tests, benchmark, writeback. All ADR-006 §8 gates pass; the gold lineage is now implemented + tested. Deferred (ADR-006 Non-Goals) unchanged.

### STEP 0 — contract fix (packet_id)

- **SCHEMA-011**: `packet_id` redefined as `gold-v0:` + first-16-hex SHA-256 over the **full identity tuple** (`source_snapshot_id`, `source_feature_schema_version`, `regime_taxonomy_version`, `regime_classifier_version`, `decision_policy_version`, `decision_policy_fingerprint`) — mirrors `Snapshot.recompute_id`. Closes an id-collision hazard across version/config bumps. Field row + determinism rule updated; pinned in the golden test.

### Code shipped (MOD-006, `src/gold/decision_builder/`)

- `models.py` — SCHEMA-011 dataclasses (`GoldDecisionPacket`, `Direction`/`DecisionMode` enums, `FeatureCitation`, `ConfidenceInputs`, `GuardRefs`) + byte-stable `to_dict()` + `compute_packet_id`.
- `config.py` — `DecisionPolicyConfig` (confidence weights + floors + regime→direction table + `decision_policy_version`), `DEFAULT_DECISION_POLICY_CONFIG`, fail-closed `from_mapping`/`load_config`, `decision_policy_fingerprint()`.
- `policy.py` — pure `trust_score` (ADR-008: within-rule `rule_margin` anchor, four structural discounts, NEUTRAL/INDETERMINATE floors, uncertainty = `1 − structural` penalty aggregate) + `direction_for`.
- `builder.py` — `build_decision(fv, rc, guards=None, config=DEFAULT, as_of=None)`: snapshot-id consistency fail-closed → trust score → direction → cited features → templated rationale → packet. Pure/total/stdlib; no clock/RNG/IO/history.
- `pyproject.toml` wheel packages += `src/gold`.

### Confidence model + direction policy (pinned as `decision_policy_version` 0.1.0)

- Weights: ambiguity 0.15/secondary, fragility 0.10/near, staleness 0.02/day (cap 0.5), revision 0.15, coverage 0.05/unavailable (cap 0.5); NEUTRAL floor 0.5; INDETERMINATE → conf 0.0 / unc 1.0. `decision_policy_fingerprint = 555c3fb9…9bdb`.
- Regime→direction table (12 regimes, total; INDETERMINATE→WATCH): LIQUIDITY_STRESS/RISK_OFF/REFLATION→LONG; VOLATILE/RISK_ON/LOW_VOL/NEUTRAL→FLAT; RESTRICTIVE_RATES/DISINFLATION/STRONG_USD→AVOID; CURVE_INVERSION/INDETERMINATE→WATCH. **Provisional** — `LONG`-vs-`FLAT`-only and the DISINFLATION cell await user confirmation; both are one-line `decision_policy_version` config changes, not a rebuild.

### L3 guard nodes (STEP 4 — contracts; runtime deferred)

- **PRED-006 Duplicate OK**, **PRED-007 Operational OK** (predicates, planned/not-started) — the two net-new L3 guards (ADR-004 / ADR-006 §6); stateful computation deferred (ADR-006 Non-Goals); L3 guards, not MOD-004 features.
- **GATE-002 Gold Decision Gate** (gate, planned/not-started, `blocking: false`) — composes the guards a packet's `guard_refs` cite; advisory in v0 (the pure builder always emits a packet; `guard_refs` = null for unevaluated guards).

### Tests + benchmark (STEP 5)

- `tests/gold/test_decision_builder.py` (TEST-010, 20 tests): real-snapshot golden (RESTRICTIVE_RATES → AVOID / confidence 0.39744 / uncertainty 0.136 / `packet_id gold-v0:0ebde87216151527`), byte-identical replay, INDETERMINATE fail-closed floor (WATCH/0.0/1.0), NEUTRAL confident-quiet floor, direction-table totality, fingerprint pin + drift + version-exclusion, packet_id sensitivity to both `decision_policy_version` and the config fingerprint, snapshot-mismatch fail-closed, guard-ref null/passthrough, config fail-closed.
- `tests/gold/test_gold_bench.py` (TEST-011, 6 tests) + `benchmarks/gold/run_gold_bench.py` (BENCH-002) + committed golden `artifacts/gold_bench.json`: real-replay byte-identical (3 consumable), all 4 directions reachable, regime→direction map ↔ policy, artifact-in-sync.

### Writeback — nodes created (11)

- MOD-006 Gold Decision Builder; FILE-015 models.py (gold), FILE-016 config.py (gold), FILE-017 policy.py, FILE-018 builder.py; TEST-010 test_decision_builder, TEST-011 test_gold_bench; PRED-006/007; GATE-002; BENCH-002.

### Writeback — nodes updated

- **SCHEMA-011 / INT-009 / CAP-020**: planned/not-started → active/implemented (CAP-020 → tested); confidence inferred→confirmed; evidence += code; `produced_by`/`implemented_by` → [[Gold Decision Builder]]; related_files/tests wired; Open Questions refreshed.
- **SCHEMA-009 + SCHEMA-010**: `consumed_by` += [[Gold Decision Builder]] (SCHEMA-010 was empty); `### Used By` updated. **INT-007** Open Question updated (gold builder now consumes SCHEMA-010).
- **index.md**: 11 new rows; SCHEMA-011/INT-009 "(planned)" dropped; Statistics (total content nodes 128→139; module 5→6, file 14→18, test 9→11, gate 1→2, predicate 5→7, benchmark_result 1→2; total files 132→143; coverage 139/139; Realizes 29→31).

### Verification

- **pytest: 798 passed** (772 prior + 26 new gold). **mypy --strict clean** on `src/gold` (only the 2 pre-existing MOD-004 lambda-inference findings remain, out of scope). **ruff clean** on src/gold + tests/gold + benchmarks/gold.
- Determinism: real snapshot replayed byte-identical; `decision_policy_fingerprint` coherence test green.
- **11 dev_graph lint checks** on touched nodes: frontmatter ✓, enums ✓, orphan/≥1 inbound ✓, stale ✓, broken wikilinks ✓ (all new links resolve), module `related_constraints`/`related_tests` ✓ (MOD-006 → Canonical Ownership + 2 tests), type-content alignment ✓, deprecated refs ✓ (no active node references CAP-004 except the sanctioned Supersedes/annotation), canonical_id uniqueness ✓ (11 new ids), evidence-confidence coherence ✓.
- **Gate-board coherence**: ADR-006 §8 unchanged (all-pass).

### Metrics

- Total content nodes: 139 (128 + 11). Active: 137 (REF-004 + CAP-004 deprecated). Six modules implemented + tested (MOD-001..006).
- Canonical ID + frontmatter coverage: 139/139 (100%). vs Phase 5 soft ceiling 200: 139.

### Deferred / open (unchanged — ADR-006 Non-Goals)

- Direction-table confirmation (user): (a) long-or-flat-only, (b) the DISINFLATION cell — both `decision_policy_version` config changes, not a rebuild.
- Paper-trading runtime + stateful L3 guard computation (`duplicate_ok`/`operational_ok`); live execution / broker / order routing / position sizing; learned/history-dependent regimes; real-corpus accumulation.
- Hygiene pass DEBT-01/02/03/04/07 (separate, before the first trusted Neo4j/Graph-RAG export).

## 2026-06-08 finalize | Gold direction table v0 finalized — DISINFLATION AVOID→FLAT (`decision_policy_version` stays 0.1.0 — finalizing the provisional v0, nothing consumed; new `decision_policy_fingerprint be7e3192…a8a5`; real packet_id rehashes → `gold-v0:5653d07a0b3949d5`; `gold_bench.json` regenerated + 2 pinned tests + MOD-006/BENCH-002 nodes re-pinned; 4-way enum kept — AVOID is informational headwind, not SHORT, on long-only GLD; `LIQUIDITY_STRESS→LONG` dash-for-cash caveat recorded on MOD-006 Open Questions).

## 2026-06-08 harden | Gold v0 epoch hardening — Stage 2 (hygiene + first trusted Neo4j export) + Stage 3 (full-chain E2E)

### Stage 2 — hygiene + export

- **DEBT-01**: `snapshot_publisher.py:625` `H_get_engine_version()` → `_get_engine_version()` (restores the producer leg — `main()` no longer NameErrors).
- **DEBT-02**: MOD-003 Snapshot Consumer — dropped `provides: [[Snapshot API]]` + the `### Implements`/`### Provides` sections (a pure consumer cannot provide/implement the read contract; it `### Consumes` it).
- **DEBT-03**: MOD-002 Decision Engine — removed the upward module→capability `depends_on` / `### Depends On` (Performance Scoring, Treasury Management) layer inversion (the real data dependency is already the `### Consumes [[Evaluation Scorecard Schema]]` edge).
- **DEBT-07**: normalized path-qualified `[[dir/Name]]` → `[[Name]]` across 22 content nodes (parent_system + exported relationship sections); the exporter also tolerates path-qualified forms defensively.
- **DEBT-04**: wired the 10 empty KA `informs_decisions` back-links (KA-001..010 → the ADR each principle informs; KA-011 already wired) — the KNOWLEDGE→DECISION leg is no longer 100% unwired.
- **Exporter aligned to GOV-005** (`sync_to_neo4j.py`): all 23 content labels (was 17; added architecture/system/capability/interface/event/knowledge_asset/pattern), all 17 relationship sections (was 8; added Contains/Implements/Emits/Triggered By/Guards/Originates From/Justified By/Realizes/Composes), and **MERGE on `canonical_id`** (the GOV-005 primary key — resolves the Infrastructure Diagram REF-004/ARCH-004 basename collision); name→canonical_id resolution prefers the non-deprecated node; neo4j import made lazy so `--dry-run` validates offline (pyyaml installed into the venv).
- **Export validation** (`--dry-run`): **139 nodes, 910 relationships, 5 skipped** — all 5 legitimate non-graph refs (deprecated Infrastructure Diagram → structural `CLAUDE`/`wiki/CLAUDE`; SYS-006 → 2 uncreated wiki-concept nodes). **Zero wikilink-form drops; zero deprecated-node dangling refs — CAP-004's `SUPERSEDES`/`DEPENDS_ON` edges all resolve.** A live sync needs Neo4j running + the `neo4j` package.

### Stage 3 — full-chain E2E

- **TEST-012 test_e2e_pipeline** (`tests/gold/test_e2e_pipeline.py`, e2e, 3 tests): `snapshot → consume → build_features → classify → build_decision` — byte-identical packet replay across two runs; the `snapshot_id` threads every stage unchanged + `recompute_id()` matches the published id; golden real packet (RESTRICTIVE_RATES → AVOID / 0.39744 / `gold-v0:5653d07a0b3949d5`). Closes the Regime Taxonomy audit's Warning 4.

### Writeback / verification

- Nodes created (1): TEST-012. Updated: MOD-002, MOD-003 (DEBT-02/03), 10 KAs (DEBT-04), 22 normalized nodes, `sync_to_neo4j.py`, `snapshot_publisher.py`; index.md (TEST-012 row; total content nodes 139→140; test 11→12; total files 143→144; coverage 140/140).
- **pytest: 801 passed** (798 + 3 E2E). mypy/ruff unaffected (changed code files are tooling/producer, outside `src`).
- 11 lint checks on touched nodes: frontmatter ✓, enums ✓, orphans ✓, broken wikilinks ✓ (export dry-run confirms 0 form-drops), deprecated refs ✓ (CAP-004 wired), canonical_id uniqueness ✓ (TEST-012 new), evidence-confidence ✓. Gate-board coherence: ADR-006 §8 unchanged (all-pass).

## 2026-06-08 audit | Gold v0 final audit (Stage 4) + post-audit remediation

- **GOLD_DECISIONPACKET_V0_FINAL_AUDIT.md** produced — independent adversarial audit (8 read-only dimension auditors → adversarial verification, 0 critical candidates produced/survived → lead synthesis). **Verdict PASS, readiness 94/100**; all 8 dimensions PASS (Architecture, Replay Determinism, Ontology, ADR, Treasury/Gold Separation, Schema Correctness, Graph Integrity, Gold-Layer Readiness). No code/graph changes during the audit. Live export re-verified: 140 nodes / 920 edges / 5 legitimate skips.
- **Post-audit remediation** (the audit's actionable low-severity findings, all numerically no-op): (1) `policy.py` coverage now reads `set(unavailable_features) | set(failed_required_features)` — literal ADR-008 §3 compliance; `failed_required ⊆ unavailable` so confidence/packet_id/fingerprint/`gold_bench.json` are unchanged; (2) added `src/gold/__init__.py` (package marker every sibling has); (3) cleared doc drift — MOD-006 node "26"→"29 gold tests"; audit doc records the export as 140/920 (the log Stage-2 139/910 was the pre-E2E count).
- Re-verification: **pytest 801 passed; mypy --strict clean on src/gold; ruff clean.** Pinned real-snapshot facts unchanged (RESTRICTIVE_RATES / AVOID / 0.39744 / `gold-v0:5653d07a0b3949d5`). Gate-board coherence: ADR-006 §8 still all-pass.
- **Gold DecisionPacket v0 epoch is closed.** Next epochs (not started — each needs its own planning ADR): (a) the paper-trading runtime that consumes the packet + computes the stateful L3 guards (`duplicate_ok`/`operational_ok`); (b) real-corpus accumulation (unblocked by DEBT-01) to convert the provisional domain-anchored regime thresholds + confidence weights + direction table from domain-anchored to empirically calibrated.
