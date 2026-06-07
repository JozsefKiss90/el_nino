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
