# Dev Graph Log

Chronological record of dev_graph operations. Each entry uses format: `## [DATE] operation | details`

---

## [2026-06-18] ADR | ADR-013 Operations Control Plane — ACCEPTED (status: draft → active)

Operator accepted ADR-013. `status: draft → active`, `implementation_status: not-started → tested`
(`decision_status` stays `active`); Status section promoted Draft → Accepted. The terminal-TUI
implementation is complete and green (MOD-011 + OBS-002 + FILE-039..043 + TEST-029..033; full suite 1050).
Both HARD-PAUSE gates were observed. No code change in this acceptance edit (governance only).

---

## [2026-06-18] writeback | Operations Control Plane console (ADR-013) — MOD-011 + OBS-002 + ops/ file/test nodes

### Nodes Created (12)
- **[[Operations Control Plane]]** (MOD-011, module, status active / implementation_status tested) — the
  `ops/` package: a local terminal operator console (headless read-model + Textual TUI) over the Layer-3
  runtime; reuses MOD-007/008/009/010; provides OBS-002.
- **[[Operations Control Plane Console]]** (OBS-002, observability) — the operator-facing monitor/control
  surface (header/status bar + Overview/Gates/Calibration/Artefacts/Processes/Plugs/Log panes).
- **File nodes** (FILE-039..043): [[core.py (ops)]] (read-model), [[app.py (ops)]] (Textual TUI),
  [[actions.py (ops)]] (Tier-2 safe), [[gated.py (ops)]] (Tier-3 gated-live), [[audit.py (ops)]]
  (append-only audit log). `ops/proc.py` (subprocess + secret-redact helper) is below the §7.5 threshold
  (interface-less utility) — noted in MOD-011 Implementation Notes, no node.
- **Test nodes** (TEST-029..033): [[test_ops_core]], [[test_ops_audit]], [[test_ops_actions]],
  [[test_ops_gated]], [[test_ops_app]].

### Code shipped (ops/ package — Steps 1-3 of ADR-013)
- **Step 1 (read-only):** `ops/core.py` headless read-model + `ops/app.py` Textual TUI (7 panes,
  auto-refresh, `--once`). Read-only; reuses governed loaders + the pure `run_sequence` preview.
- **Step 2 (safe tier):** `ops/actions.py` + `ops/audit.py` — run-chain-now (simulator), re-run
  calibration readiness, re-sync Neo4j; key-bound, audit-logged, never raise.
- **Step 3 (gated-live, post-HARD-PAUSE, operator chose the one-shot model):** `ops/gated.py` — one-shot
  Alpaca-paper run (fail-closed REFUSE without paper creds/host), register/unregister daily schedule,
  commit-or-DEFER calibration bump (never bumps a `*_version`); each behind a `ConfirmModal` + audit +
  server-side precondition; crash-proof thread workers.
- `pyproject.toml`: new `[project.optional-dependencies] ops` group (Textual/Rich); mypy/ruff/pytest
  extended to cover `ops/`. `src/` stays `dependencies = []` (ADR-003 preserved).

### Safety properties (verified)
Local-only/no listener; paper-only/no live-money; secrets never displayed (derived dormant/creds-present
only, KA-008); confirm+audit+server-side precondition on every mutation; reuse-governed-functions;
gate-respecting (bump branches on a discrete `eligible` flag, `executed=False` on every branch); engine
zero-dep. Three adversarial-review workflows (Steps 1/2/3) — critical invariants verified to HOLD; all
actionable (low) findings fixed + regression-tested (audit-write-never-raises, worker crash-proof,
full-audit-surface secret redaction, OSError-safe globs, eligible-flag coupling).

### Metrics
- Tests: 64 new ops tests (`tests/ops/`); full suite **1050 green** (was 986). `mypy --strict` + `ruff`
  clean on `ops/` (configured scope src/tests/ops clean).
- Pre-existing, out-of-scope (NOT touched): 2 mypy-2.1.0 lambda errors in `src/features/feature_builder.py`;
  13 ruff errors in `snapshot_sources/query_db.py` + a plugin trash file (outside the lint scope).

### Changes
- `index.md`: added MOD-011, OBS-002, FILE-039..043, TEST-029..033 rows; statistics (content nodes
  198→210; module 10→11, file 38→43, test 28→33, observability 1→2; total files 202→214).
- ADR-013 frontmatter: `related_files`/`related_tests` now point to the realized ops file/test nodes.
- 11 lint checks run on the touched nodes (clean: frontmatter/enums, ≥1 inbound, no broken wikilinks, no
  duplicate canonical_ids, constraint/test coverage, type-content, evidence-confidence).
- Neo4j: `python sync_to_neo4j.py --dry-run` validates the projection offline — **210 nodes**, all 12 new
  nodes + their edges resolve (the 5 skipped edges are pre-existing dangling refs, not ops). The live
  `--clear` re-projection is **deferred** (the DB is not up this session: no bolt on 127.0.0.1:7687,
  `NEO4J_PASSWORD` unset) — run `python sync_to_neo4j.py --clear` when the DB is up; the markdown is
  canonical and `--clear` is idempotent.

---

## [2026-06-18] ADR | ADR-013 Operations Control Plane (draft) — governance boundary, HARD-PAUSE for operator review

### Nodes Created
- [[ADR - Operations Control Plane]] (ADR-013, decision_record, **status: draft**, decision_status: active) —
  `dev_graph/decisions/ADR - Operations Control Plane.md`.

### What it records
Governance & architectural-boundary record (authors no code) for a **local terminal operator console**
(Textual TUI) over the Layer-3 runtime — a sibling of, and **not coupled to**, the JARVIS graph console
(ADR-010). Eleven bound invariants: (1) sibling boundary / own `ops/` package, may share a headless
ops-core only; (2) local-only, no network listener; (3) three action tiers (read-only / safe
non-destructive / gated-live) with a fixed action→tier→reused-function→precondition table; (4)
reuse governed functions, never reimplement safety/paper-only/gate logic (run_once, run_guard, load_*,
paper_adapter_from_env / clock_feed_from_env, build_report, register_daily_chain_task.ps1,
sync_to_neo4j.py); (5) paper-only / no live-money path ever; (6) secrets never displayed (derived
dormant/creds-present/enabled only, KA-008); (7) confirm + audit + server-side precondition on every
mutation; (8) gate-respecting (calibration bump returns DEFER unless ADR-012 gate passes; Alpaca
fail-closes); (9) engine stays zero-dep (ADR-003) — Textual/Rich in `[project.optional-dependencies] ops`,
`ops/` never imported by `src/`; (10) read-only before actions + **HARD PAUSE before gated-live**; (11) no
second source of truth. Non-binding candidate ids named (OBS-002 + ops/ file/test nodes); none reserved or
created.

### Grounding
8-agent parallel read of orchestration/paper_runtime/execution runtime + feed/adapter plugs +
MOD-009/ADR-012 calibration gate + scheduling scripts + governance-precedent ADRs (009/010/011/012) +
ADR-003/pyproject; exact governed-function signatures and fail-closed/paper-only properties cited in the
ADR. Confirmed: ADR-013 / OBS-002 are the next free ids; no readiness/bump callable exists (a bump is a
human-review-required manual config-version amendment), so the console's bump action can only DEFER.

### Changes
- `index.md`: added the ADR-013 Decisions row; bumped statistics (content nodes 197→198, files 201→202,
  decision_record 12→13, coverage 198/198).
- This log entry.

### Deferred to Step 4 (writeback slice)
OBS-002 observability node + `ops/` file/test nodes (§7.5), full 11-check lint sweep, and Neo4j re-sync —
authored when the console code lands. **HARD PAUSE: awaiting operator review of ADR-013 before any console
code is written.**

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

## 2026-06-09 decision | ADR-009 Paper-Trading Runtime Planning — epoch (a) planning slice (Slice 1)

Authored the planning / architectural-boundary ADR for epoch (a) — the first stateful Layer-3 component, the paper-trading runtime that consumes SCHEMA-011 and computes the two stateful L3 guards (`duplicate_ok`/`operational_ok`). **Governance only — no schema/module/interface/gate/code frozen** (that is Slice 2, gated on the checkpoint review of this ADR). Mirrors the ADR-006 → SCHEMA-011 contract-first rhythm. Architecture forks confirmed with the user (wrap-not-enrich; ADR-first then build slice; two named guards + echo snapshot guards) and hardened by an adversarial design review.

### Decision (9 constraints)

- **§2 Wrap, not enrich-in-place** — the runtime calls `build_decision(guards=None)` and emits a NEW decision record; the packet stays byte-identical/pure (`compute_packet_id` excludes `guard_refs`, so enriching would let one `packet_id` carry divergent content). Reconciles ADR-004 §3 / ADR-006 §3.
- **§4 Stateful determinism** — state is an explicit in/out value (prior ledger → new ledger); pure `evaluate()` core + thin IO shell (mirrors `consume()` / `load_config()`). §5 self-describing append-only ledger keyed by `source_snapshot_id`, `seq = len(prior.entries)`; the ledger alone is sufficient replay state. Governing precedent: KA-009 Stateless Agent Architecture.
- **§3 Input boundary** — core consumes only SCHEMA-011 + runtime state; snapshot guards + `as_of` forwarded through the packet (small forward-compat `snapshot_guards` block + `as_of = clock_ts` on SCHEMA-011, settled in Slice 2). Must not import `src/risk` — bounded-context hygiene (Context Map ARCH-001 / Canonical Ownership CON-003; **not** ADR-004).
- **§6 Guard scope** — compute `duplicate_ok` (once-ever, keyed on a prior ADMIT) + `operational_ok`; echo `data_ok`/`freshness_ok`/`cooldown_ok`; `supervisor_ok` = explicit None stub; **computed cooldown cut to Future Work**.
- **§1 CAP-008 disambiguation** — the future Paper-Trade Admission capability is complementary to but distinct from Guardrail Enforcement (CAP-008, Risk Control); no link/merge/supersede — recorded without a typed edge.
- **§8 Gate plan** — a new blocking gate (GATE-003 candidate) governs the record; GATE-002 stays advisory over the pure packet. No node created here.
- **§9 Creation Gates** — all five pass (pure packet, deterministic clock, named predicates, config/fingerprint + pure-engine/IO-boundary patterns) → contract authorable in Slice 2.

### Writeback — nodes created (1)

- ADR-009 [[ADR - Paper-Trading Runtime Planning]] (decision_record, active / not-started).

### Writeback — nodes updated

- ADR-004, ADR-006: `related_decisions` += [[ADR - Paper-Trading Runtime Planning]] (inbound links); `updated` → 2026-06-09.
- index.md: +1 Decisions row; Statistics (total content nodes 140→141; decision_record 8→9; total files 144→145; coverage 141/141).

### Lint (11 checks, touched nodes)

frontmatter ✓ (full decision_record schema); enums ✓ (status active, impl not-started, confidence confirmed, evidence [design,ADR,code]); orphan/≥1 inbound ✓ (ADR-004/006 backlinks); stale ✓ (created today); broken wikilinks ✓ — all targets exist (SCHEMA-011, MOD-003/006, ADR-004/006, KA-009, CON-003, ARCH-001, CAP-008, MOD-001, GATE-001/002, PRED-006/007); the uncreated Slice-2 nodes are named as **plain-text candidates only** (no wikilinks); module constraints/tests n/a (ADR); type-content alignment ✓ (Status/Context/Decision/Consequences/Relationships); deprecated refs ✓ (no link to CAP-004); canonical_id uniqueness ✓ (ADR-009 new); evidence-confidence coherence ✓.

### Note for the checkpoint review

- **Citation resolution**: the "no-import `src/risk`" rule cites the **Context Map (ARCH-001)** bounded-context boundary as the primary authority (index shows CON-003 = *Canonical Ownership*, not a bounded-context constraint), plus Canonical Ownership (CON-003) as referenced. ADR-004 is correctly scoped to the treasury/gold boundary only.

### Deferred (Slice 2 — gated on this ADR's review)

- SCHEMA-012 (record) + SCHEMA-013 (ledger) + MOD-007 + INT-010 + CAP-021 + GATE-003; implement PRED-006/007; BENCH-003; the SCHEMA-011 `snapshot_guards` forward-compat addition (+ re-pin `test_e2e_pipeline` / `gold_bench` goldens); tests TEST-013..016; full dev_graph writeback.

**CHECKPOINT — Slice 1 complete; paused for review before Slice 2.**

## 2026-06-09 session | Paper-Trading Runtime — contract-first build (Slice 2, ADR-009)

Built the stateful L3 paper-trading runtime that consumes the pure Gold DecisionPacket (SCHEMA-011) and computes the two stateful guards `duplicate_ok` (PRED-006) + `operational_ok` (PRED-007). **Wrap, not enrich-in-place**: `evaluate()` emits a NEW `RuntimeDecisionRecord` (SCHEMA-012) + a new `RuntimeLedger` (SCHEMA-013); the planning packet stays byte-identical/pure. Pure core + IO at the edge; self-describing append-only ledger; deterministic replay. Authored against ADR-009's nine constraints.

### Step 0 — SCHEMA-011 additive `snapshot_guards` + `as_of` threading (post-audit)

- Added a `SnapshotGuards` provenance block (`data_ok`/`freshness_ok`/`cooldown_ok`) to `GoldDecisionPacket`, **distinct from `guard_refs`** (the L3-outcome block). `build_decision(fv, rc, guards=None, snapshot_guards=None, config=DEFAULT, as_of=None)` — the chain orchestrator (which holds the snapshot) forwards `snapshot_guards` + `as_of = snapshot.clock_ts`; the builder copies them verbatim, never reads the snapshot. So the runtime consumes only SCHEMA-011, never raw SCHEMA-001.
- `PACKET_SCHEMA_VERSION` 0.1.0 → **0.2.0** (additive). **`packet_id` unchanged** (it digests only the version tuple — excludes `snapshot_guards`/`as_of`/`packet_schema_version`): real PASS still `gold-v0:5653d07a0b3949d5`. `test_e2e_pipeline` threads the provenance (+1 assertion test); `gold_bench.json` re-pinned (1-line `packet_schema_version` diff). This block **post-dates** the Gold v0 94/100 final audit.

### Implementation — `src/gold/paper_runtime/` (under the existing `src/gold` wheel; no pyproject change)

- `models.py` — SCHEMA-012 `RuntimeDecisionRecord` (+ `Verdict`, `GuardOutcome`), SCHEMA-013 `RuntimeLedger`/`LedgerEntry`, `OperationalInput`, `compute_record_id`, `digest_snapshot_guards`. Reuses `_GUARD_NAMES` from the packet module (single guard ordering). `record_id = paper-v0:` + SHA-256 over (`packet_id` + `runtime_policy_fingerprint` + `as_of` + `operational_fingerprint` + `snapshot_guards_digest` + `prior_ledger.state_hash()`) — a per-evaluation identity binding prior state. Ledger entries are self-describing (snapshot-guards digest + operational fingerprint + `as_of` + verdict + `seq = len(prior.entries)`); `has_admit` counts only prior ADMITs (once-ever).
- `config.py` — `RuntimePolicyConfig` (`require_operational`, `require_snapshot_guards`) + `runtime_policy_fingerprint()` (gold idiom verbatim; default `ab798cae…6f32`) + fail-closed `from_mapping`/`load_config`.
- `predicates.py` — `duplicate_ok` (once-ever on a prior ADMIT), `operational_ok` (instrument + tradeable/venue_open/not-halt/not-degraded), echo `data_ok`/`freshness_ok`/`cooldown_ok` from `packet.snapshot_guards`; `supervisor_ok` = explicit `None` stub. `(passed, reason)` shape mirrors the risk predicates — **pattern only, never imported** (Context Map / ARCH-001 bounded-context hygiene; not ADR-004).
- `engine.py` — pure `evaluate()`: full six-guard block (canonical order) + short-circuit conjunction over the required guards (first failure names it) → fail-closed verdict (WATCH/INDETERMINATE ⇒ HOLD; required-but-failed ⇒ REJECT; else ADMIT) → one ledger append. `RuntimeDecisionRecord.__post_init__`: ADMIT ⇔ no triggered guard; paper_only.
- `runtime.py` — IO shell (`load_ledger` absent⇒empty/malformed⇒raise; `load_operational` default-closed; `persist_ledger` atomic) + `run_once` + the pure `run_sequence` replay driver.

### Tests + benchmark (`tests/gold/`, `benchmarks/gold/`)

- TEST-013 guards (14), TEST-014 engine (14), TEST-015 determinism + fingerprint coherence (6), TEST-016 ledger idempotency/seq/replay/IO (8), TEST-017 bench (8). **50 runtime tests.**
- BENCH-003 `run_paper_runtime_bench.py` + committed `paper_runtime_bench.json` + in-sync test: real sequence (byte-identical, `no_enrich_back=true`; the 3 real paths are one content-identical snapshot ⇒ ADMIT then 3 duplicate REJECTs) + a clearly-labelled synthetic sweep exercising every verdict (ADMIT 3 / HOLD 1 / REJECT 3 with operational/data/duplicate attribution).

### Writeback — nodes created (17)

- SCHEMA-012 [[Runtime Decision Record Schema]], SCHEMA-013 [[Runtime Ledger Schema]]; INT-010 [[Paper Runtime API]]; MOD-007 [[Paper-Trading Runtime]]; CAP-021 [[Paper-Trade Admission]] (under SYS-002, downstream of CAP-020); GATE-003 [[Runtime Admission Gate]] (blocking, over the record); BENCH-003 [[Paper-Trading Runtime Benchmark]]; FILE-019..023 (models/config/predicates/engine/runtime); TEST-013..017.

### Writeback — nodes updated

- **PRED-006 / PRED-007**: planned/not-started → active/tested; `implemented_in` → `src/gold/paper_runtime/predicates.py`; `validated_by` → [[test_paper_runtime_guards]]; `### Guards` += [[Runtime Admission Gate]]; evidence += code.
- **SCHEMA-011**: `schema_version` 0.1.0 → 0.2.0; `snapshot_guards` field documented; `consumed_by` → [[Paper-Trading Runtime]]; `### Consumed By` added; Open Questions resolved.
- **GATE-002**: stays **advisory** (`blocking: false`); Open Question resolved — the blocking surface is GATE-003 over the record.
- **CAP-020** `### Used By` → [[Paper-Trade Admission]]; **MOD-006** `### Used By` → [[Paper-Trading Runtime]] + builder signature note; **FILE-015/FILE-018** snapshot_guards notes; **KA-009** `informs_decisions` += [[ADR - Paper-Trading Runtime Planning]], `### Used By` += the runtime/admission nodes.
- **index.md**: +17 rows; Statistics (total content nodes 141→158; capability 20→21, interface 5→6, artifact_schema 8→10, module 6→7, file 18→23, test 12→17, gate 2→3, benchmark_result 2→3; total files 145→162; coverage 158/158).

### Verification

- **pytest: 853 passed** (803 prior incl. Step-0 +2; +50 runtime). **mypy --strict** clean on `src/gold/paper_runtime` (only the 2 pre-existing MOD-004 lambda findings remain, out of scope). **ruff** clean on `src tests benchmarks`.
- Determinism proofs: `run_sequence` twice byte-identical records + identical ending `state_hash`; re-presented snapshot ⇒ `duplicate_ok=False`; halted op ⇒ REJECT/`operational_ok`; editing a `RuntimePolicyConfig` flag without a version bump fails TEST-015 fingerprint pin; the packet built inside the runtime has `guard_refs == GuardRefs()` (no enrich-back); SCHEMA-011 `packet_id` unchanged after the additive block.
- **11 lint checks** on touched nodes: frontmatter ✓, enums ✓, orphan/≥1 inbound ✓, stale ✓, broken wikilinks ✓, module `related_constraints`/`related_tests` ✓ (MOD-007 → Canonical Ownership + 5 tests), type-content alignment ✓, deprecated refs ✓ (CAP-021 carries **no** edge to CAP-004 / CAP-008 / Order Management), canonical_id uniqueness ✓ (17 new), evidence-confidence coherence ✓.

### Deferred (ADR-009 Non-Goals — unchanged)

- The wall-clock scheduler/daemon; live execution / broker / order routing / sizing / fills / P&L; a live operational-status feed; a **computed** cooldown guard (v0 echoes); multi-instrument; persistence beyond a local JSON ledger; a downstream paper-execution/evaluation layer. Epoch (b) real-corpus calibration stays blocked on DEBT-01.

## 2026-06-09 audit | Paper-Trading Runtime final audit (epoch baseline) + TD-1 fix

- **PAPER_TRADING_RUNTIME_FINAL_AUDIT.md** produced — read-only multi-agent audit (8 parallel dimension auditors → adversarial verification → lead synthesis with independent re-verification of every pinned fact). **Verdict PASS, readiness 97/100**; all 8 dimensions PASS (Stateful replay determinism 98, Ledger integrity 100, Idempotency 98, Wrap boundary 99, ADR-009 compliance 98, Bounded-context separation 100, Ontology/graph integrity 100, Honesty 92). **Zero critical/high candidates** surfaced; the one low candidate (concurrent ledger writes in a future driver) dismissed as a deployment concern (TD-2). No code/graph changes during the audit. Lead re-verified: `runtime_policy_fingerprint ab798cae…6f32`, `packet_id gold-v0:5653d07a0b3949d5` unchanged, `guard_refs == GuardRefs()`, `run_sequence` byte-identical + identical ending `state_hash`, BENCH-003 ADMIT 3/HOLD 1/REJECT 3; pytest tests/gold 81 / full suite 853.
- **TD-1 fix (the audit's only actionable item — doc precision):** ADR-009 §2 + MOD-007 §Constraints reworded — the runtime consumes a **pre-built** packet and never enriches it; it is the **chain orchestrator** that builds the packet with `build_decision(guards=None)` (the prior wording conflated "the runtime" with "the runtime's chain"). Behavior unchanged; no-enrich-back property already proven. No id/status/date change (both nodes already at 2026-06-09).
- **Paper-Trading Runtime epoch is accepted as the baseline.** Remaining work is future epochs, not gaps: the execution/portfolio layer; real-corpus calibration (epoch b, unblocked by fixing DEBT-01); computed cooldown; live operational feed; supervisor integration; scheduler + multi-instrument driver.

## 2026-06-11 epoch | Epoch (b) operationalized — real-corpus accumulation started (producer fixed, DB refreshed, first forward snapshot banked, daily job scheduled)

Operationalization slice only — **accumulates the corpus; does NOT calibrate.** No `src/` decision-logic change, no schema/module/interface/gate node created, no `*_version` bump. Calibration (provisional regime thresholds / confidence weights / direction table → empirical) remains a later, separately-governed bump gated on N real snapshots existing.

### DEBT-01 reconciliation (resolves the 957 vs 1061/1067 inconsistency)

- The log contradicted itself: **957** (2026-06-08 harden) declared the `H_get_engine_version → _get_engine_version` NameError *fixed* ("main() no longer NameErrors"); **1061** (2026-06-09 Non-Goals) said epoch (b) "stays **blocked** on DEBT-01"; **980/1067** said "unblocked by fixing DEBT-01."
- **Root cause (verified 2026-06-11 by running the producer):** the 957 fix was applied to the **vendored, non-runnable** copy `el_nino/snapshot_sources/snapshot_publisher.py`, *not* to the live producer `C:\Code\Mr-Ripley\layer2\adapters\snapshot_publisher.py`, whose `main()` line 625 still called `H_get_engine_version()` → `NameError`, exit 1, on every invocation (`--list`, `--dry-run` today, `--dry-run 2026-05-01`). The el_nino copy cannot import `layer2` (its `sys.path` bootstrap probes only `C:\Code` / `C:\Code\el_nino`; neither has `layer2/`) — it is a read-only reference snapshot, never the running producer. Classic two-copy drift — compounded by a third twist found at writeback: Mr-Ripley's **committed `HEAD` already held the correct `_get_engine_version()`**; the `H_…` typo existed only as an **uncommitted working-tree corruption** in the live repo, so the running producer NameError-ed on every invocation while `git status` showed nothing to fix. The 2026-06-11 edit restored the working tree to HEAD (`git diff` empty — there is no producer *source* commit to make; the running binary is now correct).
- **Resolution:** **1061 ("stays blocked") was the accurate line**; 957/1067 were true only of the dead copy. DEBT-01-the-NameError is now genuinely closed in the producer (Mr-Ripley `snapshot_publisher.py:625` → `_get_engine_version()`, 2026-06-11, verified: dry-run reaches the gate, PASS for a fresh clock). The broader "DEBT-01" had conflated two legs — (a) the NameError and (b) the *operational* corpus gap (stale DB + no schedule + the fix never reaching the producer); **both legs are now closed.**

### Step 1 — producer-readiness diagnosis (7-agent parallel trace, read-only)

- Confirmed the architecture: producer = `C:\Code\Mr-Ripley` (runnable `layer2/`, `layer2_truth.db` 15 MB / 89,247 obs / 24 series, `quality_gate.py`, 5 adapters, FRED key at `.secrets/fred_api_key.txt`); consumer/governance = `el_nino` (`src/` chain + dev_graph). `snapshot_sources/` is vendored reference only.
- True blockers found (two stacked): **(1)** the producer NameError (above); **(2)** fail-closed staleness — the DB stopped at obs 2026-04-30 (DTWEXBGS 2026-04-24), so at clock 2026-06-11 all 16 Tier-1 series were 42–48 d stale vs 3 d / 10 d (DTWEXBGS) thresholds → gate FAIL. The DB held exactly **1** snapshot (`952cc83a…`, clock 2026-05-01, PASS). Ingestion sources verified live today (FRED key valid; gold-api.com; Yahoo `^MOVE`/SPY/GLD). SCHEMA-001 conformance = `verdict==PASS ∧ guards.snapshot_ok ∧ ¬forced ∧ ¬dry_run`.

### Step 2 — close the gap to one clean run

- **Producer fix:** Mr-Ripley `layer2/adapters/snapshot_publisher.py:625` `H_get_engine_version()` → `_get_engine_version()` — a working-tree restore to the already-correct committed HEAD (`git diff` empty; no producer source commit needed; `layer2_truth.db` is gitignored). el_nino vendored copy left as read-only reference (recommended — avoids re-introducing the drift that caused this).
- **Ingestion (catch-up, real data):** `run_backfill.py --only fred move spy gld --start-date 2026-05-22 --end-date 2026-06-11` (real FRED/Yahoo history; captures the DTWEXBGS weekly print, latest 2026-06-05 = 6 d ≤ 10) + `--only gold` (5-day live spot, today 4139.90). All 16 Tier-1 series fresh; gold window kept short so current spot is not fabricated across past days. The ~40-day producer-outage gap (2026-05-02 … 06-10) is **not** back-banked as snapshots (no honest PIT for past days).
- **First forward snapshot banked:** `05c8369da5278d062b0d9dd87c4c8acc69c554b06b4eeb51bd0892c199b7184d`, clock_ts 2026-06-11T22:00Z, verdict **PASS**, Tier-1 16/16, 21 series. DB corpus now = 2 immutable rows (2026-05-01 + 2026-06-11).
- **Consumer chain verified on the new snapshot** (`consume → build_features → classify → build_decision → evaluate`, el_nino `.venv`): consumable; `id_matches=True` (recompute_id-stable); `RESTRICTIVE_RATES → AVOID`, confidence 0.5712, `packet_id gold-v0:3691a5a776f1d7ef`, snapshot_id threads all stages; runtime `evaluate` ADMIT (tradeable op), deterministic replay, `duplicate_ok` once-ever (2nd presentation → REJECT). `tests/gold` 81 passed (unchanged).

### Step 3 — operationalize daily accumulation (producer-native corpus)

- **Corpus = two immutable, content-id-keyed sinks:** (1) `layer2_truth.db` `snapshots`/`snapshot_values` (snapshot_id PK + `INSERT OR IGNORE`; publisher also dedups by `(clock_ts, engine_version, config_version)` → exactly one/day, same-day re-run = logged no-op); (2) `Mr-Ripley/runtime/snapshots/snapshot_<clock_date>__<id8>.json` (per-day immutable JSON; archive step skips if present). `latest_snapshot.json` is the latest-pointer, not the archive.
- **New Mr-Ripley scripts:** `scripts/daily_eod_snapshot.ps1` (injects `L2_ENGINE_VERSION` — the `.env` line is an inert comment, nothing loads dotenv on the pipeline path — runs `run_layer2_pipeline.py`, then archives immutably) and `scripts/register_daily_task.ps1`.
- **Scheduled:** Windows Scheduled Task **`MrRipley-Layer2-DailyEOD`**, daily 23:00 local (≈21:00 UTC; clock cut 22:00 UTC), `-StartWhenAvailable` (recovers a missed night). Validated by running the wrapper once: pipeline PASS (idempotent — today already banked) → archived `snapshot_2026-06-11__05c8369d.json`. NextRunTime 2026-06-11 23:00.
- **Runbook:** `el_nino/EPOCH_B_CORPUS_RUNBOOK.md` (architecture, corpus sinks, automated + manual operation, PIT/data-quality notes, troubleshooting, disable).

### Cross-repo note + scope discipline

- Changes outside el_nino were confined to the **Mr-Ripley producer repo** (1-line publisher fix; 2 new operational scripts; DB refreshed with real recent observations; one snapshot published). No el_nino `src/` change. dev_graph touched only here (this log entry) — no node/contract/`*_version` change. Producer/script files live in Mr-Ripley (a separate repo dev_graph does not track), so no file/test nodes were created for them.
- **Calibration stays out of scope** and now has a forward-accumulating corpus to gate on. DTWEXBGS (weekly, 10-d threshold) is the most likely single-series daily blocker to watch.

## [2026-06-14] writeback | ADR-010 JARVIS GraphRAG Integration (governance boundary)

**Nodes Created:** `decisions/ADR - JARVIS GraphRAG Integration.md` (ADR-010, decision_record, status active, implementation_status not-started, confidence confirmed, evidence [design, ADR, code]).

**Changes:**
- Authored ADR-010 as a governance/boundary record (mirrors ADR-006/ADR-009 structure). Records the JARVIS↔dev_graph boundary for the integration roadmap (`jarvis/JARVIS_INTEGRATION_ROADMAP.md`): (1) JARVIS is a READ-ONLY consumer — reads Neo4j (live) or graph.json (offline), never authors; markdown stays canonical. (2) The bridge is the EXISTING `jarvis/backend/app.py` extended (graph + future /ask + future /voice + static serving) — not a separate voice_bridge.py; the cytoscape view is the reused render block. (3) Every graph-grounded answer cites canonical_ids and carries the node's evidence-class (fail-closed assistant). (4) Offline graph.json and live Neo4j are interchangeable projections behind one typed layer — never hand-edited. (5) Re-sync Neo4j only when the dev_graph changes (this slice does; later app slices do not). Non-Goals: writing to the graph, autonomous code generation, voice-driven app-building, a second source of truth, exposing the bridge beyond localhost.
- index.md: added the ADR-010 row to the Decisions table and a dated entry to Statistics.

**Lint (11 checks, touched node ADR-010):** 1 frontmatter complete ✓ · 2 enums valid (type decision_record, status active, impl not-started, confidence confirmed, evidence ⊂ allowed) ✓ · 3 not an orphan — inbound from index.md + outbound to ADR-002/ADR-001/CON-001/CON-003/API-002 ✓ · 4 fresh (created today) ✓ · 5 wikilinks resolve (ADR - Ontology Redesign, ADR - Dev Graph Bootstrap, No Wiki Mutation, Canonical Ownership, Anthropic API Docs, ADR - Gold DecisionPacket v0 Planning, ADR - Paper-Trading Runtime Planning) ✓ · 6 n/a (ADR) · 7 n/a (ADR) · 8 type-content aligned (Status/Context/Decision/Alternatives/Consequences) ✓ · 9 no deprecated refs ✓ · 10 canonical_id ADR-010 unique ✓ · 11 confidence confirmed has evidence ✓.

**Metrics:** dev_graph nodes 158 → 159; decision_records 9 → 10 (ADR-001..010). Re-sync Neo4j (`python sync_to_neo4j.py --clear`) per the writeback checklist — this slice changed the dev_graph.

## [2026-06-14] writeback | JARVIS GraphRAG integration — Stages 1–5 (app code, no node changes)

Implemented the JARVIS<->dev_graph integration roadmap (`jarvis/JARVIS_INTEGRATION_ROADMAP.md`) under [[ADR - JARVIS GraphRAG Integration]] (ADR-010). Per ADR-010 §5, these are **application slices that do not change dev_graph nodes** — no node/edge/`*_version` change, **no Neo4j re-sync** (the Stage-0 ADR writeback already re-synced; the graph stays at 159 nodes / 1113 edges). No file/test nodes were created: this is JARVIS console/bridge tooling under `jarvis/`, outside the trading-engine (`src/`) implementation graph the dev_graph tracks.

**Slices (all read-only consumers of the graph):**
- **Stage 1** — `jarvis/export_graph_json.py`: deterministic offline projection reusing `sync_to_neo4j.py`'s parser; emits `jarvis/frontend/graph.json` (159 nodes / 1113 edges / 5 skipped — identical to the Neo4j sync). README note added.
- **Stage 2** — `jarvis/frontend/jarvis.html`: graph-grounded answering on the current console (matched node -> 1-hop neighborhood -> answer from the `## Definition` summary + typed edges, cited `[MOD-006 · confirmed]` with evidence-class), mini cytoscape view, live-bridge-or-`graph.json` data layer, Neo4j chip flips LIVE. Original `sources/...html` untouched.
- **Stage 3** — `jarvis/hud/` (Vite + React + TypeScript): typed data layer mirroring the FastAPI Pydantic models; **pure, Vitest-tested router** (`src/data/router.ts`, 16 tests green incl. the real-graph.json gate); hooks; components; ThemeContext (JARVIS/PIXEL); `/api` dev proxy. `npm run build` green.
- **Stage 4** — `POST /ask` on `jarvis/backend/app.py`: GraphRAG (seed match -> Neo4j/graph.json neighborhood -> context block with evidence-class -> Claude API), returns `{answer, citations, subgraph}`; fail-closed (no LLM on no-match); 503 without `ANTHROPIC_API_KEY`. React `useClaudeUplink` with offline-router fallback.
- **Stage 5** — voice router on the **same** app (`/voice/health|stt|tts`, Whisper/Piper optional -> graceful Web Speech fallback); built React `dist` mounted as StaticFiles -> single URL (`http://127.0.0.1:8000/`), API routes retain precedence.

**Governance check:** read-only throughout (no write Cypher; bridge READ access mode + `_guard` blocklist intact); answers cite canonical_ids + evidence-class; `graph.json`/Neo4j are interchangeable projections regenerated from the markdown, never hand-edited. Lint: no dev_graph content nodes touched (only this log entry + the Stage-0 ADR-010, already linted).

### [2026-06-14] addendum | adversarial review fixes (Stages 1-5)

Ran a 30-agent adversarial review of the JARVIS integration; 23 findings confirmed, the actionable ones fixed (read-only/governance preserved):
- Evidence-class on the live path: `sync_to_neo4j.py` now syncs the `evidence` array (added to `array_fields`); re-synced Neo4j (159/1113, idempotent) so the live bridge carries the same evidence-class as `graph.json` (ADR-010 sec 3). `graph.ts` mapBridgeNode extracts it. This is the only dev_graph-projection change in the review pass; no node CONTENT changed.
- Router/console: completed REL_IN inverses (RELATES_TO_FILE/TEST, REQUIRED_FOR, CONSUMED_BY, PRODUCED_BY, SUPERSEDED_BY) so incoming edges read naturally; +1 Vitest (17 green).
- Bridge hardening: /ask input bound (<=8000) + generic Claude/Whisper/Piper error messages (details server-side only); /voice/tts text bound (<=10000); Cypher _guard collapses whitespace + blocks apoc/call (defense-in-depth atop READ mode); clarified the StaticFiles mount-order/precedence comment.
- HUD: live neighborhood preferred for isolated nodes; useClaudeUplink marks unavailable on non-503 failures; Web Speech shown as standby (fallback), not active.
- Exporter: --stdout writes UTF-8 bytes (Windows console fix); docstring clarifies the summary extraction is novel (not shared with the sync parser).

---

## [2026-06-15] writeback | Neo4j host port 7687 -> 7688 (coexist with kg-dev-neo4j-1)

### Changes
- Host port conflict: `kg-dev-neo4j-1` (Knowledge-Graph-App) holds host 7687/7474. Remapped the
  JARVIS stack's **host-published** ports to 7688 (bolt) / 7475 (browser); the container still
  listens on 7687/7474 internally, so the in-compose `api` service (`bolt://neo4j:7687`) is unchanged.
- Repointed host-side clients to 7688: `jarvis/docker-compose.yml`, `.mcp.json` (neo4j MCP),
  `sync_to_neo4j.py` + `jarvis/backend/app.py` defaults, `jarvis/.env.example`, `jarvis/README.md`,
  HUD status chips (`ConnectorArray.tsx` + served Stage-2 HTML), `.claude/settings.local.json` probes.
- Docs/diagrams updated for consistency: `architecture/Context Map.md` (docker-run example),
  `architecture/Infrastructure Diagram.md` (ARCH-004) + deprecated `Infrastructure Diagram.md`
  (REF-004) mermaid bolt label, root roadmaps.

### Nodes Changed
- ARCH-001 (Context Map), ARCH-004 (Infrastructure Diagram): `updated` -> 2026-06-15 (body port text only).
- No nodes/edges added or removed; no relationship changes.

### Metrics
- Container recreated (external `elnino_neo4j_data` volume preserved); `--verify-only` over
  bolt://localhost:7688 returns the full graph. Both Neo4j containers now run simultaneously.

---

## [2026-06-16] decision | ADR-011 Execution Layer Planning

**Nodes Created:** `decisions/ADR - Execution Layer Planning.md` (ADR-011, decision_record, `status: draft` — the governed stand-in for "Proposed"; `implementation_status: not-started`; `confidence: confirmed`; `evidence: [design, ADR]`; `decision_status: active`). A **governance / architectural-boundary planning** record mirroring ADR-006/ADR-009/ADR-010 — it authors **no** schema / module / interface / gate / predicate / event / file / test / code, and freezes nothing.

**Changes:**
- Authored ADR-011 to open the **execution / portfolio layer** epoch — the sanctioned next epoch named in the 2026-06-09 Paper-Trading Runtime audit baseline ("Remaining work is future epochs … the execution/portfolio layer"). The seven recorded decisions: **(1) Scope & epoch boundary** — governs the layer that consumes an ADMIT and produces a paper fill + portfolio state; it is *not* the contract; permanently separate from the Supervisor treasury branch (ADR-004) and distinct-but-complementary to MOD-007 admission and CAP-008 risk control. **(2) The determinism boundary (load-bearing invariant)** — a port/adapter (hexagonal) split: a deterministic offline **fill-simulator** is the canonical replay-safe core (all tests/benchmarks/replay run against it), extending the replay key with a `fill_model_version` + seeded fill policy + explicit prior portfolio state; the **Alpaca Paper** API is an optional, explicitly **non-replayable** live adapter quarantined behind the same execution port at an IO boundary shell, exactly mirroring MOD-007's pure `evaluate()`/`run_sequence` core vs `run_once` IO shell — never on the replay path, never in benchmarks, logged-not-replayed. Stated as non-negotiable. **(3) paper_only / virtual-money posture** — honors KA-010 (mandatory simulated validation), the `non_execution_notice` discipline, and PRED-005 (withdrawals disabled, KA-008 credential isolation); Alpaca Paper trades virtual money only; **live-money trading is a Non-Goal**. **(4) Re-grounding the live path** (ADR-004 precedent) — CAP-020 Gold Decision → MOD-007 runtime admission (ADMIT) → execution; GATE-001 + PRED-001..005 wired into the actual trade pipeline (GATE-001's dormant "not yet wired … no order router yet" machinery activates here); CAP-005's deprecated-`Signal Generation` dependency + node-less `Execution API` placeholder are re-grounded in the later slice (deferred edit, like ADR-004's). **(5) Decouple from DEBT-01 & epoch (b)** — DEBT-01 resolved 2026-06-11 (both legs closed); the execution epoch is independent of it and of real-corpus calibration; sequencing caveat recorded — build the offline-sim core first, the Alpaca adapter yields low-information results until the provisional regime thresholds / confidence weights / direction table are calibrated, so it may be deferred or run parallel to epoch (b). **(6) No schema freeze** — candidate next-free ids named non-binding only (re-derived from index.md): execution interface `INT-011`; execution/portfolio schemas `SCHEMA-014`/`SCHEMA-015`; execution + portfolio modules `MOD-008`/`MOD-009`; sim-broker + Alpaca adapters `MOD-010`/`MOD-011` (or files); position/portfolio state; the versioned fill model; execution events `EVT-001` — none reserved or created. **(7) Creation Gates** (ADR-006 §8-style board) — six gates **all OPEN** at epoch start: (a) execution interface contract defined, (b) fill-simulation model specified & replay-keyed, (c) guard-wiring specified, (d) execution-determinism replay requirement finalized, (e) portfolio/position state model agreed, (f) Alpaca-adapter boundary (KA-008 credential isolation + non-replayable IO quarantine) specified. Non-Goals extend ADR-009's list (live-money; real broker routing beyond Alpaca paper; scheduler/daemon; multi-instrument — GLD only; learned/history-dependent logic; a second source of truth; persistence beyond the local ledger pattern).
- **ADR-004, ADR-006, ADR-009:** `related_decisions` += `[[ADR - Execution Layer Planning]]` (inbound links, per the ADR-009 boundary-ADR convention recorded at the 2026-06-09 writeback); `updated` → 2026-06-16. No body/semantic change.
- **index.md:** added the ADR-011 row to the Decisions table; **reconciled the Statistics breakdown** (it still read `decision_record: 9` / `158` total — the ADR-010 writeback added the table row + dated line but never bumped the numeric breakdown; now `decision_record: 11` / `160` total / `164` files / `160/160` coverage, ADR-001..011); added the dated Statistics line; `Last updated` → 2026-06-16.

**Directive-reframing rationale:** the determinism boundary is framed as a **port/adapter seam**, not as "Alpaca vs offline." Making the broker the organizing axis invites live, non-deterministic IO to leak into the core; making the *port* the axis yields one deterministic replay-safe core (the source of truth for correctness/replay/benchmarks) with interchangeable adapters behind it, of which Alpaca Paper is just a non-replayable plug. This directly extends the ADR-006 §3 / ADR-009 §4 replay invariants to execution and reuses MOD-007's proven pure-core-vs-IO-shell shape, rather than inventing a new boundary. The epoch is also explicitly decoupled from DEBT-01 (closed) and epoch (b) calibration, with a "simulator-first, adapter-when-calibrated" sequencing so work can start immediately without waiting on the corpus.

**Lint (11 checks, touched nodes — ADR-011 + the three back-linked ADRs):** 1 frontmatter complete (universal + decision_record extensions) ✓ · 2 enums valid (type decision_record; status draft; impl not-started; confidence confirmed; evidence ⊂ {design, ADR}; decision_status active) ✓ · 3 not an orphan — ADR-011 inbound from index.md + ADR-004/006/009 `related_decisions`; outbound to MOD-007, CAP-020, GATE-001, CAP-005, ADR-009/006/004, CON-003/001, KA-010/005/008 ✓ · 4 fresh (ADR-011 created today; the three back-linked ADRs bumped to 2026-06-16) ✓ · 5 wikilinks resolve — every `[[…]]` in ADR-011 maps to an existing node; the deprecated *Signal Generation* and the node-less *Execution API* placeholder are referenced as plain text / backticks only, never as wikilinks ✓ · 6 n/a (ADR — no module/file constraint coverage) · 7 n/a (ADR — no module/file test coverage) · 8 type-content aligned — Status / Context / Decision / Alternatives Considered / Consequences present (+ Creation Gates, Illustrative Field Sketch, Non-Goals, Future Work, Relationships) ✓ · 9 no deprecated refs in any relationship section (Signal Generation/CAP-004 kept out of the typed sections, in prose only) ✓ · 10 canonical_id ADR-011 unique (ADR-001..010 pre-existing) ✓ · 11 confidence `confirmed` backed by non-empty evidence `[design, ADR]` ✓.

**Metrics:** dev_graph content nodes 158 → 160 (reconciles the prior ADR-010 Statistics omission + adds ADR-011); decision_records breakdown 9 → 11 (Decisions table now ADR-001..011); typed edges += ADR-011's outbound relationships (Depends On ×3, Constrains ×1, Justified By ×3, Constrained By ×2, Originates From ×3) + 3 inbound back-links from ADR-004/006/009. Re-sync Neo4j (`python sync_to_neo4j.py --clear`, repo-root script) per the writeback checklist — this slice changed the dev_graph; new node/edge counts recorded after sync.

**Deferred / open:** no normative execution nodes are created — all are gated behind the six **open** Creation Gates (§7), to be authored contract-first in a separate post-checkpoint slice. The CAP-005 live-path re-grounding (retiring the deprecated dependency, resolving the `Execution API` placeholder to a real interface) is a deferred just-in-time edit. The Alpaca Paper adapter may be deferred or run parallel to epoch (b) calibration. Paused for operator review before any design or code.

---

## [2026-06-16] decision | ADR-011 promoted draft→active (Accepted)

**Slice.** Governance promotion of [[ADR - Execution Layer Planning]] (ADR-011) from `draft`/"Proposed" to `active`/"Accepted" at checkpoint review, mirroring the 2026-06-08 ADR-006 promotion (`status: draft → active`; Status "Proposed" → "Accepted"). **Acceptance accepts the boundary record as governing; it does NOT close the §7 Creation Gates** — all six remain **Open** and are closed by the contract-first design slice described in the STEP-0 brief `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` (authored this session, repo root, not a dev_graph node). No `src`/`tests`/schema/contract nodes (ADR-011 §7 honored). Also resolves the two open loose ends from the 2026-06-16 authoring entry.

**Changes to existing nodes (2):**
- **ADR-011 Execution Layer Planning:** `status: draft → active`; `updated` → 2026-06-16 (`decision_status: active` and `created: 2026-06-16` unchanged). Status section "**Proposed** — drafted…" → "**Accepted** — drafted 2026-06-16, accepted 2026-06-16 (promoted at checkpoint review)", and added an explicit **acceptance ≠ gate-closure** paragraph (the §7 gates govern downstream contract authoring, not this ADR's acceptance; closed by the design slice, not the promotion). The §6 candidate ids and §7 gate board are unchanged (still all Open).
- **ADR-008 Gold Decision Confidence Semantics:** `related_decisions += [[ADR - Execution Layer Planning]]` (the reciprocal back-link for ADR-011's one prior contextual citation — closes the asymmetry noted at review; ADR-011 cites ADR-008 in §5 for the provisional-calibration point); `updated` → 2026-06-16. No body/semantic change.
- **source_paths resolution:** ADR-011 `source_paths: ["ultimateplan.md"]` verified to resolve at repo root (admissibility check #6 satisfied) — kept as-is, not external, not dropped.
- **index.md:** ADR-011 row annotated "**accepted 2026-06-16**, Creation Gates remain open"; `Last updated` → "ADR-011 accepted"; dated Statistics line annotated "(drafted + accepted)". **No node-count change** (a status property flip adds no node); coverage stays 160/160.

**Lint (11 checks, touched nodes — ADR-011, ADR-008):** 1 frontmatter complete ✓ · 2 enums valid (ADR-011 now `status: active`; ADR-008 unchanged `active`; both impl/confidence/evidence/decision_status valid) ✓ · 3 not orphan — ADR-011 inbound from ADR-004/006/009 + ADR-008 + index.md; ADR-008 inbound from ADR-006/CAP-020 + now ADR-011 ✓ · 4 fresh (both `updated` 2026-06-16) ✓ · 5 wikilinks resolve — ADR-008's new `[[ADR - Execution Layer Planning]]` resolves; ADR-011 links unchanged ✓ · 6/7 n/a (ADRs) · 8 type-content aligned — ADR-011 still has Status/Context/Decision/Alternatives/Consequences ✓ · 9 no deprecated refs in typed sections ✓ · 10 canonical_id unique (no new ids) ✓ · 11 confidence `confirmed` + non-empty evidence on both ✓.

**Metrics:** node count unchanged at 160 (status flip, not a new node); decision_records still 11. Typed edges += 1 (ADR-008 → ADR-011 `DECIDED_BY`, the reciprocal). Re-sync Neo4j (`python sync_to_neo4j.py --clear`, repo-root script) — a `status` property + one edge changed; new counts recorded after sync.

**Deferred / open (unchanged by acceptance):** the six §7 Creation Gates stay **Open**, closed only by the design slice the STEP-0 brief plans (gate-closing design → contract-first authoring → code → tests/BENCH-004 → writeback). No execution contract node, no `src/execution`, no `tests/execution` created. The CAP-005 re-grounding remains a deferred just-in-time edit in that slice. Paused for operator review before any contract authoring or implementation.

---

## [2026-06-16] contract | Execution layer — STEP 1 (contract nodes: INT-011, SCHEMA-014, SCHEMA-015; CAP-005 re-grounded, CAP-007 realized)

**Slice (contract-first, no code).** STEP 1 of the execution epoch per `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` and [[ADR - Execution Layer Planning]] (ADR-011, accepted). Authored the three execution **contract** nodes and re-grounded the two existing Trading-Engine capabilities — **no `src/`/`tests/` code, no module/file/test/gate/event node** (those are STEP 2/3). **Paused at the CONTRACT CHECKPOINT for review before any code.** Settled checkpoint decisions D1 (price re-derivation, no SCHEMA-011/012 mutation) and D2 (sizing deferred) are honored throughout. Candidate ids re-derived from index.md (160-node state): INT → **INT-011**, SCHEMA → **SCHEMA-014/015** (next free; 002/003/006 reserved).

**Nodes Created (3):**
- **INT-011 [[Execution API]]** (interface, planned/not-started, confidence inferred, evidence [design, ADR]). The port both adapters implement: `execute(admit: SCHEMA-012, instrument_price, prior_portfolio: SCHEMA-015, guard_result, fill_model, config) -> (ExecutionRecord SCHEMA-014, new PortfolioState)`; pure core + `run_once`/`run_sequence` IO shell (mirrors INT-010). `input_schema` SCHEMA-012, `output_schema` SCHEMA-014, `parent_capability` CAP-005, `stability: experimental`. **Resolves CAP-005's previously node-less `Execution API` placeholder** (ADR-011 §4).
- **SCHEMA-014 [[Execution Record Schema]]** (artifact_schema, planned/not-started). Wraps an ADMIT SCHEMA-012 by reference + records the (paper) fill + forwarded guard provenance; `execution_mode` simulated|alpaca_paper, `replayable` flag, `paper_only` fixed; self-describing for its own replay (records re-derived `instrument_price` + `fill_model_version` + prior-state hash, D1) — **no change to the frozen SCHEMA-011/012**.
- **SCHEMA-015 [[Portfolio State Schema]]** (artifact_schema, planned/not-started). Append-only, self-describing per-instrument positions + `executions` history keyed by `source_snapshot_id`; threaded in/out of `execute()` (the SCHEMA-013 ledger idiom); mark-to-snapshot P&L at the re-derived price (D1). Realizes CAP-007.

**Changes to existing nodes (2 — re-grounding, ADR-011 §4):**
- **CAP-005 [[Order Management]]** re-grounded **in place** (canonical_id unchanged; not a type reclassification, so ADR-004's no-reclassify rule is not triggered). `updated → 2026-06-16`; `evidence += ADR`; `related_decisions += [[ADR - Decision Layer Re-grounding]] + [[ADR - Execution Layer Planning]]`. Body: a new `## Scope` section records the re-grounding; **retired the deprecated `### Depends On [[Signal Generation]]`** (CAP-004) → now `### Depends On [[Paper-Trade Admission]]` (CAP-021) + `### Consumes [[Runtime Decision Record Schema]]`; `### Provides [[Execution API]]` (the resolved placeholder) + `### Produces [[Execution Record Schema]]`; `### Justified By += ADR-004 + ADR-011`. **Scoped down "calculate position sizes" → "apply a fixed/configured v0 paper size; adaptive sizing deferred" (D2)**; `paper_only` (§3). `implemented_by` stays empty until MOD-008 (STEP 2). Retiring the Signal Generation edge also clears CAP-005's standing lint-9 deprecated-reference.
- **CAP-007 [[Position Tracking]]** realized as the SCHEMA-015 owner. `updated → 2026-06-16`; `evidence += ADR`; `related_decisions += [[ADR - Execution Layer Planning]]`; `### Produces [[Portfolio State Schema]]` + `### Consumes [[Execution Record Schema]]` + `### Justified By += ADR-011`; Architecture Role notes MOD-009 (STEP 3) implements it. `implementation_status` stays `not-started` (no code yet).

**No new capability created** (ADR-011 §4 confirmed): execution re-grounds the existing CAP-005; portfolio realizes the existing CAP-007 (which already `Depends On` CAP-005). SYS-002 `contains_capabilities` unchanged.

**Lint (11 checks, touched nodes — INT-011, SCHEMA-014, SCHEMA-015, CAP-005, CAP-007):** 1 frontmatter complete (universal + per-type extensions) ✓ · 2 enums valid (new nodes `status: planned` / `implementation_status: not-started` / `confidence: inferred` / `evidence ⊂ {design, ADR}`; CAP-005/007 `active`/`not-started`/`confirmed`) ✓ · 3 no orphans — every new node ≥1 inbound (INT-011 ← CAP-005 Provides + parent_capability; SCHEMA-014 ← INT-011/CAP-005 Produces; SCHEMA-015 ← INT-011 Consumes + CAP-007 Produces) and ≥1 outbound ✓ · 4 fresh (all 2026-06-16) ✓ · 5 wikilinks resolve — every `[[…]]` maps to an existing node (incl. the now-real [[Execution API]]); no plain-text dangling refs ✓ · 6 constraint coverage n/a (no module/file nodes this slice) · 7 test coverage n/a (no module/file nodes) · 8 type-content alignment ✓ (interface has Definition/Contract/Stability; schemas have Schema Definition/Validation Rules; capabilities have Definition/Scope/Relationships) · 9 **deprecated-reference: improved** — CAP-005's `[[Signal Generation]]` edge retired; no touched node references a deprecated node in a typed section ✓ · 10 canonical_id uniqueness — INT-011 / SCHEMA-014 / SCHEMA-015 each appear once ✓ · 11 evidence-confidence coherence — `confirmed` CAP-005/007 carry non-empty evidence; `inferred` new nodes carry [design, ADR] ✓.

**Metrics:** dev_graph content nodes 160 → 163 (+INT-011, +SCHEMA-014, +SCHEMA-015); interface 6→7, artifact_schema 10→12; decision_records 11 (unchanged); capabilities 21 (unchanged — re-grounded in place). Total files 164→167; coverage 163/163. Typed edges: +contract-node relationships (INT-011 Consumes×2/Produces×1/Justified-By/Constrained-By/Originates-From; the two schemas' Consumes/Justified-By/Constrained-By/Originates-From) + CAP-005/CAP-007 re-wiring (−1 Signal Generation, +Paper-Trade Admission/Consumes/Produces/Provides/Justified-By). Re-sync Neo4j (`python sync_to_neo4j.py --clear`, repo-root script) — counts recorded after sync.

**Deferred / open (STEP 2+ — gated behind this checkpoint's approval):** the execution module (MOD-008) + simulated-broker adapter + guard-wiring (advance GATE-001 in-progress→implemented); the portfolio module (MOD-009); the deterministic fill model (`fill_model_version`) + BENCH-004 byte-identical replay; the deferred Alpaca-paper adapter (gate f, ADR-011 §5); file/test nodes (FILE-024+, TEST-018+) at writeback. `implemented_by`/`produced_by`/`consumed_by`/`validated_by` on the new nodes are populated when code lands. **Paused for operator review before any STEP-2 code.**

---

## [2026-06-16] writeback | Execution layer — STEP 2 (simulator core: MOD-008 + src/execution + tests; GATE-001 wired)

**Slice.** STEP 2 of the execution epoch per `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` (after the STEP-1 contract checkpoint was approved): the deterministic **simulated-broker core** — `src/execution/` (models, config, adapters, pure `engine`, IO/orchestrator `runtime`) + tests — and its dev_graph writeback. Honors the determinism boundary (ADR-011 §2: pure `execute()` core + `run_once`/`run_sequence` IO shell mirroring MOD-007), the D1 price re-derivation (the orchestrator forwards `instrument_price`; no SCHEMA-011/012 mutation), D2 (fixed `default_size`, sizing deferred), and gate c (the orchestrator runs `GuardrailEngine.validate()` before `execute()`; the core never imports `src/risk`). **Paused at the "simulator epoch green" checkpoint** before the deferred Alpaca adapter / formal BENCH-004 artifact.

**Code (no dev_graph types changed; the 24-type ontology covers everything):**
- `src/execution/{models,config,adapters,engine,runtime,__init__}.py` + `tests/execution/{test_execution_engine,test_execution_determinism,test_execution_guards}.py`; `pyproject.toml` += `"src/execution"` (wheel packages). Implementation note (contract refinements under INT-011 `experimental`): the broker boundary in code is the port's `fill()` method (avoids duplicating the portfolio/record logic across adapters); `execute()` takes the forwarded `direction` (the ADMIT record omits it) + an injected `ExecutionPort`; `instrument_price` is `float` (the snapshot/feature representation), not `Decimal`.
- **Verification:** 19 execution tests pass; **full suite 872 pass** (no regressions); `mypy --strict` + `ruff` **clean on `src/execution`** (the 2 remaining repo-wide mypy errors are pre-existing in `src/features/feature_builder/feature_builder.py`, an untouched file).

**Nodes Created (9):**
- **MOD-008 [[Execution]]** (module, active/tested) — realizes the re-grounded CAP-005, produces CAP-007 state; `module_path: src/execution`; depends_on MOD-007; provides INT-011.
- **FILE-024..028**: [[models.py (execution)]], [[config.py (execution)]], [[adapters.py]], [[engine.py (execution)]], [[runtime.py (execution)]] (all implemented; `module: [[Execution]]`). (`__init__.py` is boilerplate — no node, per §7.5.)
- **TEST-018..020**: [[test_execution_engine]] (unit), [[test_execution_determinism]] (regression — the BENCH-004 core), [[test_execution_guards]] (unit) — each `covers: [[Execution]], [[Execution API]]`.

**Changes to existing nodes (6):**
- **INT-011 [[Execution API]]**, **SCHEMA-014 [[Execution Record Schema]]**, **SCHEMA-015 [[Portfolio State Schema]]**: `planned/not-started → active/implemented`; `confidence inferred → confirmed`; `evidence += code`; populated `source_paths`/`related_files`/`related_tests` + `implemented_by`/`produced_by`/`consumed_by`/`validated_by`.
- **CAP-005 [[Order Management]]**: `implementation_status not-started → in-progress` (simulator tested; Alpaca + chain integration remain); `evidence += code`; `implemented_by → [[Execution]]`; `### Implemented By`/`### Validated By` added.
- **CAP-007 [[Position Tracking]]**: `not-started → in-progress`; `evidence += code`; `implemented_by → [[Execution]]`; `### Implemented By`/`### Validated By` added.
- **GATE-001 [[Trade Validation Gate]]**: `implementation_status in-progress → implemented` — **the dormant guardrail machinery is now wired** at the (paper) trade boundary by the [[Execution]] orchestrator (`validate()` before `execute()`); `updated → 2026-06-16`; `related_decisions += ADR-011`; `### Used By → [[Execution]]`; Open Question resolved.

**Module-consolidation note:** the plan named candidate MOD-008 (execution) + MOD-009 (portfolio); in code the portfolio state lives in the *same* `src/execution` package (`models.py`), so — mirroring MOD-007 (one module for the whole `paper_runtime` package) — it is modeled as **one module MOD-008**. MOD-009 is **not** created; CAP-007's portfolio state is produced by MOD-008. EVT-001 stays deferred (no event emitter built — avoid emitting into a vacuum).

**Lint (11 checks, touched nodes):** 1 frontmatter complete (file/test/module per-type extensions) ✓ · 2 enums valid (new files/tests `implemented`/`tested`/`confirmed`/`evidence [code]`; MOD-008 `active`/`tested`; INT-011/SCHEMA-014/015 `active`/`implemented`) ✓ · 3 no orphans — every new node ≥1 inbound (files ← MOD-008 `### Contains`; tests ← MOD-008 `### Validated By` + covered nodes; MOD-008 ← CAP-005/INT-011/index) and ≥1 outbound ✓ · 4 fresh (all 2026-06-16) ✓ · 5 wikilinks resolve — disambiguated `(execution)` file names; no plain-text dangling refs ✓ · 6 module `related_constraints` populated (MOD-008 → Canonical Ownership) ✓ · 7 module `related_tests` populated (MOD-008 → 3 tests; files carry tests) ✓ · 8 type-content aligned (module has Implementation Notes; files concise; tests have covers + Used By) ✓ · 9 no deprecated refs in typed sections (CAP-005 stays clean) ✓ · 10 canonical_id uniqueness — MOD-008 / FILE-024..028 / TEST-018..020 each once ✓ · 11 evidence-confidence coherence (confirmed nodes carry non-empty evidence) ✓.

**Metrics:** dev_graph content nodes 163 → 172 (+MOD-008, +FILE-024..028, +TEST-018..020); module 7→8, file 23→28, test 17→20; coverage 172/172; total files 176. `src/`: +1 package (`src/execution`, 6 modules), zero new runtime deps; `tests/`: +1 package (3 files, 19 tests). Re-sync Neo4j (`python sync_to_neo4j.py --clear`) — counts recorded after sync.

**Deferred / open (STEP 4–5):** the Alpaca-paper adapter (gate f, ADR-011 §5 — deferrable / parallel to epoch (b)); the formal **BENCH-004** golden artifact + run script (the determinism test is the core; the committed-artifact benchmark node is pending); full chain-orchestrator integration (re-deriving `instrument_price`/`direction` from the in-hand FeatureVector); continuous mark-to-market on no-fill snapshots; realized P&L on closes (v0 only opens LONGs). **Paused for operator review before STEP 4+.**

---

## [2026-06-16] fix | INT-011 contract-doc reconciliation (port seam = fill(), not execute())

**Doc-drift fix (no code, no graph-edge change).** [[Execution API]] (INT-011) still documented `execute()` as "the signature both adapters implement" — backwards for the node whose job is to describe the port. Reconciled the Definition to the STEP-2 code: **`execute()` is [[Execution]] (MOD-008)'s pure entry-point/core**, and the hexagonal **port seam the adapters implement is `ExecutionPort.fill()`** (the broker-specific method `execute()` dispatches to). Also corrected the signature sketch — `instrument_price: Decimal → float` (the snapshot/feature representation), added the forwarded `direction` param (the ADMIT record omits it) and the injected `port`; added `direction`/`port` to the Contract determinism tuple; trimmed the now-redundant Open-Questions caveat.

**Scope:** body prose only on one node — frontmatter, relationships, and `updated` (already 2026-06-16) unchanged; no Neo4j property or edge changes. Lint (touched node INT-011): 5 wikilinks resolve ✓ · 8 type-content aligned (Definition/Contract still accurate) ✓ · others unaffected. Re-synced Neo4j for currency (idempotent — 172 nodes / 1269 edges, unchanged).

---

## [2026-06-16] bench | Execution layer — STEP 4 (BENCH-004 byte-identical replay; ADR-011 gate (d) closed)

**Slice.** STEP 4 of the execution epoch per `EXECUTION_LAYER_IMPLEMENTATION_PLAN.md` §6: the committed-golden **BENCH-004** byte-identical sequence-replay benchmark over the green STEP-2 simulator core — the closing artifact for **ADR-011 §7 gate (d)** (execution-determinism replay requirement). A benchmark/verification slice only: **no `src/execution` logic or contract changed.** Mirrors the BENCH-003 idiom (deterministic harness → committed golden JSON → artifact-in-sync test). **Paused at the "simulator epoch green" checkpoint** before STEP 5 (Alpaca adapter, gate f). Precondition verified: INT-011 documents `fill()` as the port seam (the prior reconciliation), so STEP 4 proceeded.

**Code (no dev_graph types changed; no `src` change):**
- `benchmarks/execution/run_execution_bench.py` + committed golden `benchmarks/execution/artifacts/execution_bench.json` + `tests/execution/test_execution_bench.py` (15 tests). Determinism discipline: captured `guard_config` (ADR-011 gate c.4 — env-independent, fingerprinted into the replay key), no clock/network/randomness, canonical sorted-key JSON.
- **Results:** `all_replays_byte_identical = true` (real + synthetic-approve + synthetic-block). **Real sequence** grounded in the one consumable corpus snapshot (`952cc83a…`): one runtime ADMIT, `direction = AVOID` (RESTRICTIVE_RATES), `instrument_price = 4624.5` → a deterministic **no-fill** (non-LONG); re-presentation byte-identical. **Synthetic sequence**: `fill_distribution = {filled 1, no_fill 4}` (LONG fills at `100.05` = 5 bps slippage; AVOID/FLAT no-fill; duplicate LONG ⇒ idempotent **no-double-fill**); `guard_block_attribution = {SYN4_long_block: position_size_ok}`; `pinned_portfolio_state_hash = 847f714a…`.
- **Finding (not a defect):** both banked corpus snapshots (`952cc83a…`, `05c8369d…`) classify `RESTRICTIVE_RATES → AVOID` (non-LONG); `05c8369d…` lives only in the Mr-Ripley truth DB, not as a committed el_nino consumable. So no real ADMIT fills today — the real sequence evidences **replay determinism + stable portfolio state**; the fill + no-double-fill + guard-block paths are exercised by the synthetic sequence.
- **Verification:** 15 new tests pass; **full suite 887 pass** (was 872; no regressions); `mypy --strict` + `ruff` **clean on the new files** (the 2 repo-wide mypy errors remain pre-existing in the untouched `src/features/feature_builder/feature_builder.py`).

**Nodes Created (3):**
- **BENCH-004 [[Execution Layer Benchmark]]** (benchmark_result, active/implemented; `evidence [code, benchmark]`; `measures [replay_determinism, idempotency, fill_distribution, portfolio_state_hash, guard_block_attribution]`) — `### Depends On` [[Execution]] / [[Execution Record Schema]] / [[Portfolio State Schema]]; `### Validated By` [[test_execution_bench]]; `### Justified By` [[ADR - Execution Layer Planning]].
- **FILE-029 [[run_execution_bench.py]]** (file; `module: [[Execution]]`; the BENCH-004 harness).
- **TEST-021 [[test_execution_bench]]** (test, `test_type: benchmark`; `covers: [[Execution]], [[Execution Layer Benchmark]]`).

**Changes to existing nodes (4):**
- **MOD-008 [[Execution]]**: `related_files += [[run_execution_bench.py]]`; `related_tests += [[test_execution_bench]]`; `### Validated By += [[test_execution_bench]], [[Execution Layer Benchmark]]`; Implementation Notes + Open Questions updated (gate d closed, suite 887).
- **SCHEMA-014 [[Execution Record Schema]]** + **SCHEMA-015 [[Portfolio State Schema]]**: `validated_by += [[Execution Layer Benchmark]]`; `### Validated By += [[Execution Layer Benchmark]]`; stale "validated_by empty" Open Questions reconciled (gate d Closed).
- **ADR-011 [[ADR - Execution Layer Planning]]**: §7 **gate board reconciled** — gates **(a)–(e) Closed** with closing artifacts (a INT-011 · b FillModelConfig · c orchestrator guard-wiring/GATE-001 · d **BENCH-004** · e SCHEMA-015), **(f) deferred** (Alpaca, §5); Status section's stale "remain Open" line reconciled. Body/gate-board edit only — `status` stays `active`, `canonical_id`/`decision_status` unchanged; `updated` 2026-06-16.

**Lint (11 checks, touched nodes):** 1 frontmatter complete (BENCH-004 has `measures`; FILE-029 has `file_path`/`language`/`module`; TEST-021 has `test_path`/`test_type`/`covers`) ✓ · 2 enums valid (`benchmark_result`/`active`/`implemented`/`confirmed`; `test_type: benchmark`; `evidence [code]`/`[code,benchmark]`) ✓ · 3 no orphans — BENCH-004 ← MOD-008/SCHEMA-014/SCHEMA-015 `### Validated By` + index; FILE-029 ← MOD-008 + BENCH-004; TEST-021 ← MOD-008 + BENCH-004; each ≥1 outbound ✓ · 4 fresh (all 2026-06-16) ✓ · 5 wikilinks resolve (new `[[Execution Layer Benchmark]]`/`[[run_execution_bench.py]]`/`[[test_execution_bench]]` all created) ✓ · 6 module `related_constraints` (MOD-008 → Canonical Ownership) intact ✓ · 7 module `related_tests` (MOD-008 → 4 tests) ✓ · 8 type-content aligned (benchmark has Results; file has Implementation Notes; test has covers + Used By) ✓ · 9 no deprecated refs in typed sections ✓ · 10 canonical_id uniqueness — BENCH-004 / FILE-029 / TEST-021 each once ✓ · 11 evidence-confidence coherence (confirmed nodes carry non-empty evidence) ✓.

**Metrics:** dev_graph content nodes 172 → 175 (+BENCH-004, +FILE-029, +TEST-021); benchmark_result 3→4, file 28→29, test 20→21; coverage 175/175; total files 176→179. No new ontology type/enum; no `sync_to_neo4j.py` change. Re-sync Neo4j (`python dev_graph/sync_to_neo4j.py --clear`) — counts recorded after sync.

**Deferred / open (STEP 5):** the Alpaca-paper adapter (gate f, ADR-011 §5 — off the replay/benchmark path); full chain-orchestrator `run_once` integration; a LONG real-corpus snapshot (when epoch-(b) calibration shifts the regime→direction table) would let the real sequence exercise a fill. **Paused for operator review before STEP 5.**

---

## [2026-06-17] epoch | Epoch (b) calibration — empirical-readiness assessment + governance (ADR-012); ALL THREE TARGETS DEFER (no bump)

**Slice.** The calibration-governance step of epoch (b): decide whether the real snapshot corpus
(accumulating since 2026-06-11 per the 2026-06-11 operationalization entry) is large/diverse enough to
convert the provisional, domain-anchored regime thresholds, confidence weights, and regime→direction
table into empirically-grounded values. **Methodology + readiness gate only — NO `src/` change, NO
`*_version` bump, NO threshold/weight/direction value change, NO benchmark re-pin, NO new ontology
object beyond the governing ADR.** A config-version amendment was *not* performed because the corpus
fails the readiness gate. Paused-for-review boundary honored: nothing that changes a replay key was
touched.

### Step 1 — corpus sufficiency assessment (READ-ONLY; ran the real chain over every banked snapshot)

Enumerated both content-id-keyed sinks and ran `consume → build_features → classify → build_decision`
over every honestly-banked PIT snapshot (scratch harness; written nothing; reproduction recipe + the
verbatim verdict live in `EPOCH_B_CALIBRATION_RUNBOOK.md` §3).

- **N = 5** PASS-banked PIT snapshots in `Mr-Ripley/layer2_truth.db` (`engine gold-v3.3.0 / cfg 1.1.0`):
  `952cc83a` (2026-05-01, backfill anchor) · `05c8369d` (06-11) · `7d39aa8f` (06-13) · `e0e44caf`
  (06-14) · `c1fe5a02` (06-15). **1** is a committed el_nino consumable (the `latest_snapshot_pass.json`
  fixture); **4** are producer-only (Mr-Ripley truth DB + `runtime/snapshots/*.json` archives). Forward
  corpus = **4 trading days** (06-12 and 06-16 fail-closed no-bank days; 06-17 not yet run).
- **Regime distribution `{RESTRICTIVE_RATES: 5}` — 1/12 regimes.** Never observed: LIQUIDITY_STRESS,
  RISK_OFF, VOLATILE, REFLATION, DISINFLATION, CURVE_INVERSION, STRONG_USD, RISK_ON, LOW_VOL, NEUTRAL,
  INDETERMINATE. **Direction distribution `{AVOID: 5}` — 1/4 directions** (LONG/FLAT/WATCH never seen; a
  fill/LONG has never occurred). **Confidence** 0.397–0.571 (mean 0.520), all from `R04_restrictive_rates`;
  only competitor ever near is `R08_strong_usd`; **zero** staleness/revision/coverage penalty variation.
- The corpus is **monochromatic** (one regime, one direction, one deciding rule, no penalty variation) —
  the explicit do-not-calibrate condition. KA-010 already flags 5-day samples as not statistically
  significant; we have ~4 forward days.

### Step 2 — governance authored (always valid regardless of N)

- **ADR-012 [[ADR - Empirical Calibration Methodology]]** (decision_record, **draft** / not-started;
  `evidence [design, ADR, code, layer2]`; `confidence confirmed`). Records: **version-axis mapping**
  (regime thresholds → `taxonomy_version` per ADR-007; confidence weights + regime→direction table →
  `decision_policy_version` per ADR-008 §7 + the gold-config docstring; **never crossed**; a bump is a
  config amendment, never a `canonical_id` change/rebuild); the **empirical-readiness gate** (G0: N≥60
  forward PASS snapshots; G1 thresholds: both-sided boundary obs + ≥3 regimes + walk-forward holdout;
  G2 weights: real variation in every penalty dimension + ordinal-monotonicity holdout, no PnL/outcome
  fit, no SCHEMA-005 bleed; G3 direction table: per-cell regime observed + a forward gold-return
  evaluation harness beating the provisional cell out-of-sample per KA-010); the **method** (deterministic
  rule-based derivation + walk-forward, no ML/learned/online/history-dependent logic — ADR-005/007);
  **determinism/PIT preservation** (old versions stay byte-reproducible; re-pin affected goldens under
  the new version retaining the old; calibrate only on honestly-banked forward snapshots, never
  back-fabricate); and **Non-Goals** (no learned models, no live money, no schema/id change, no
  recalibration of a gate-failing target). Mirrors the ADR-006/009 governance-boundary idiom.
- **`EPOCH_B_CALIBRATION_RUNBOOK.md`** (repo root, non-dev_graph; corpus-runbook idiom) — operational
  companion: current pinned baseline + fingerprints, the §3 read-only assessment + reproduction harness,
  the §4 readiness gate, and the §5 recalibrate→validate→re-pin procedure (HARD PAUSE before any bump).

### Step 3 — calibration: DEFERRED (no gate passes)

| Target | Version axis | Gate | Verdict |
|---|---|---|---|
| Regime thresholds | `taxonomy_version` | G0 + G1 | **DEFER** — N=5 (<60); 1/12 regimes; cannot move a boundary never observed both sides of |
| Confidence weights | `decision_policy_version` | G0 + G2 | **DEFER** — zero staleness/revision/coverage variation to fit; ordinal score, not outcome-fittable |
| Regime→direction table | `decision_policy_version` | G0 + G3 | **DEFER** — 11/12 cells unexercised; no forward gold-return evaluation harness exists |

No value or version changed. `taxonomy_version` stays `1.0.0` (regime `decision_fingerprint`
`8ab0be8d…`); `decision_policy_version` stays `0.1.0` (gold `decision_policy_fingerprint` `be7e3192…`,
matching the BENCH-002 pin — no drift). BENCH-001/002 goldens untouched. FILE-013/FILE-016 config
nodes untouched (no `updated` bump).

### Changes to existing nodes (2 — inbound links only, no value/version change)

- **ADR-007 [[ADR - Deterministic Regime Taxonomy]]** + **ADR-008 [[ADR - Gold Decision Confidence
  Semantics]]**: each `related_decisions += [[ADR - Empirical Calibration Methodology]]` (forward link to
  the calibration methodology each ADR anticipated as the "expected v1 amendment" / "recalibration … is a
  governed bump"); `updated → 2026-06-17`. Frontmatter-only; no `decision_status`/`canonical_id`/body-value
  change; gives ADR-012 its inbound links.

### Lint (11 checks, touched nodes: ADR-012, ADR-007, ADR-008, index.md)

1 frontmatter complete (ADR-012 has `decision_id`/`decision_date`/`decision_status`; universal fields
present) ✓ · 2 enums valid (`decision_record`/`draft`/`not-started`/`confirmed`/`evidence
[design,ADR,code,layer2]`/`decision_status active`) ✓ · 3 no orphans — ADR-012 ← ADR-007 + ADR-008
`related_decisions` + index; ≥1 outbound (Justified By / Depends On / Constrains / Originates From /
Constrained By) ✓ · 4 fresh (2026-06-17) ✓ · 5 wikilinks resolve — all targets exist (config.py
regime/gold FILE-013/016, policy.py FILE-017, BENCH-001/002, KA-010/011, CON-001/003, ADR-005/006/007/008/009);
non-node runbook refs de-wikilinked to backticks ✓ · 6 n/a (ADR, not module) · 7 n/a · 8 type-content
aligned (ADR has Status/Context/Decision/Consequences) ✓ · 9 no deprecated refs in typed sections ✓ ·
10 canonical_id uniqueness — ADR-012 used once (next free after ADR-011) ✓ · 11 evidence-confidence
coherence (`confirmed` + non-empty evidence) ✓.

### Metrics

dev_graph content nodes 175 → 176 (+ADR-012); decision_record 11 → 12; total files 179 → 180; Originates
From edges 19 → 21 (ADR-012 → KA-010, KA-011); coverage 176/176. No new ontology type/enum; no schema
version change. Re-sync Neo4j (`python dev_graph/sync_to_neo4j.py --clear`) — counts recorded after sync.

### Deferred / next

Re-run the §3 assessment as the corpus grows (watch the regime distribution diversify away from
RESTRICTIVE_RATES). G0 (N≥60) is the first gate likely to come into reach (≈ a calendar quarter of
forward days); G1/G2/G3 additionally need regime/penalty diversity the macro tape must actually supply,
and G3 needs a forward gold-return evaluation harness to be built. **Stopped for operator review — no
`*_version` bump or value change was made, per the HARD PAUSE boundary.**

---

## [2026-06-17] session | Epoch (b) gate-G3 prerequisite — Gold Forward-Return Labeler (measurement only; G3 stays deferred)

**Slice.** Built the **forward-return labeling harness** ADR-012 gate G3 names as its prerequisite —
the deterministic tool that labels each banked gold decision with the gold return realized *after* it,
producing the per-regime outcome data G3 will eventually consume. The highest-leverage thing buildable
today (tractable independent of corpus size). **Measurement only: no decision-path edit, no config
change, no `*_version` bump, no direction-table change. G3 itself stays deferred** — the corpus is
still monochromatic. This is application code + a calibration-tool node set under ADR-012 (no new ADR).

### The non-negotiable — look-ahead containment (held, and adversarially verified)

Forward returns are computed from snapshots banked *after* a decision — legitimate for an outcome
label, poison on the decision path. The wall held: the harness lives under `benchmarks/` (not `src/`),
imports the chain **read-only** (the chain never imports it), calls `build_decision(fv, rc)` with **no**
future data, and never writes a return/label back into a snapshot/feature/regime/decision. A static
guard test (`test_decision_chain_does_not_import_the_labeler`) enforces it as a regression. An
independent adversarial review (general-purpose agent, 21 tool-uses) tried to break containment +
return-math + determinism + dedup and returned **CONTAINMENT: PASS / CORRECTNESS: PASS (0 issues)** —
it even monkeypatched the external corpus dir to prove the committed golden does not depend on the
Mr-Ripley repo. One fair hardening point it raised (unguarded non-positive entry price) was fixed
fail-closed (→ `no_price`), matching the ADR-003 posture.

### Node placement decision (NOT CAP-013)

Placed as a **standalone calibration tool governed by ADR-012**, not a realization of
[[Performance Scoring]] (CAP-013). CAP-013 is trade-log-driven *strategy* scoring feeding the
Supervisor/promotion (treasury) branch and its SCHEMA-005 scorecards — a bounded context ADR-004/ADR-008
keep **permanently separate** from the gold-decision branch. The labeler consumes the corpus (not trade
logs), produces no fills/scorecards, and serves the gold `decision_policy_version`/G3 calibration.
Folding it into CAP-013 would conflate the two contexts (CON-003). **CAP-013 stays `not-started`.**

### Code (application; benchmark idiom; no `src/` change)

- `benchmarks/calibration/run_forward_return_labels.py` — pure label/return-math core
  (`forward_return`, `select_exit`, `label_point`, `aggregate_by_regime_horizon`, `direction_correct`,
  `directional_pnl`, `_median`) + read-only corpus driver (`decision_points_from_corpus`, dedups by
  `snapshot_id`) + committed golden writer. Horizons 5/20/60 td-equiv (`CAL_PER_TD=1.4`); exit =
  nearest banked snapshot at-or-after `clock_ts + H` within `ceil(0.25·offset)` gap tolerance;
  statuses **realized / pending / no_exit_in_tolerance / no_price**. Per-label: forward return,
  `direction_correct` (LONG↔up, AVOID↔down, FLAT↔flat-band, WATCH→None), `directional_pnl`
  (LONG +r, AVOID −r, FLAT 0, WATCH None), `move_sign`.
- `benchmarks/calibration/artifacts/forward_return_labels.json` — committed golden (committed scope =
  el_nino consumables only, reproducible in CI; `--include-external` adds a stdout-only full-corpus
  diagnostic with the Mr-Ripley archives, never committed).
- `tests/calibration/test_forward_return_labels.py` — 19 tests.

### Results / evidence

- **Determinism + golden:** `build_report()` byte-identical; committed artifact in sync.
- **Synthetic validation** (the monochromatic real corpus can't exercise it): 6 regimes, all 4
  directions, all 3 statuses, **9 realized** labels with hand-verified returns/correctness
  (LONG-right/-wrong, AVOID-right/-wrong, FLAT-flat, WATCH-None; gap → no_exit_in_tolerance; long
  horizons → pending).
- **Real corpus today (honest, sparse):** committed scope dedups three JSONs (all id `952cc83a`) to
  **1** snapshot → all horizons **pending**, 0 realized. Full corpus (5 snapshots, `--include-external`)
  = all RESTRICTIVE_RATES/AVOID, all **pending** or **no_exit_in_tolerance** (the 2026-05-01 anchor's
  short horizons), **0 realized** — the four forward days cluster within 4 days, so no H≥5 forward
  return is realizable yet. The harness is ready to accumulate labels as the corpus grows.
- **Quality gates:** 19 new tests pass; **full suite 906 pass** (was 905; no regressions);
  `mypy --strict` + `ruff` clean on the new files (the 2 repo-wide mypy errors remain pre-existing in
  the untouched `src/features/feature_builder/feature_builder.py`).

### Nodes Created (4)

- **MOD-009 [[Gold Forward-Return Labeler]]** (module, active/tested; `evidence [code, design, ADR]`;
  `module_path benchmarks/calibration`) — `### Depends On` [[Gold Decision Builder]] / [[Market Regime
  Classifier]] / [[Feature Builder]] / [[Snapshot Consumer]] (read-only, downstream); `### Produces`
  [[Gold Forward-Return Label Set]]; `### Contains` [[run_forward_return_labels.py]]; `### Validated By`
  [[test_forward_return_labels]] + [[Gold Forward-Return Label Set]]; `### Justified By`
  [[ADR - Empirical Calibration Methodology]]. Body records containment + the NOT-CAP-013 separation.
- **FILE-030 [[run_forward_return_labels.py]]** (file; `module: [[Gold Forward-Return Labeler]]`).
- **TEST-022 [[test_forward_return_labels]]** (test, `test_type: benchmark`; `covers: [[Gold
  Forward-Return Labeler]], [[Gold Forward-Return Label Set]]`).
- **BENCH-005 [[Gold Forward-Return Label Set]]** (benchmark_result, active/implemented; `evidence
  [code, benchmark]`; `measures [forward_return, directional_pnl, hit_rate, regime_direction_correctness,
  horizon_coverage, realized_pending_status]`) — pins the committed golden; `### Justified By`
  [[ADR - Empirical Calibration Methodology]].

### Changes to existing nodes (1)

- **ADR-012 [[ADR - Empirical Calibration Methodology]]**: added §7 "G3 prerequisite — forward-return
  labeling harness (built 2026-06-17)" (the harness exists; G3 still deferred until per-regime coverage
  accrues; NOT CAP-013); G3 gate clause "the forward-return harness does not yet exist" reconciled to
  "the labeling harness now exists … the coverage it needs does not"; `### Constrains +=`
  [[Gold Forward-Return Labeler]], [[Gold Forward-Return Label Set]]. Body-only; `status` stays `draft`,
  `decision_status`/`canonical_id` unchanged; `updated` already 2026-06-17. (`EPOCH_B_CALIBRATION_RUNBOOK.md`
  §4 G3 / §7 status refreshed to point at the new harness — non-dev_graph doc.)

### Lint (11 checks, touched nodes: MOD-009, FILE-030, TEST-022, BENCH-005, ADR-012, index.md)

1 frontmatter complete (MOD-009 module ext; FILE-030 file_path/language/module; TEST-022 test_path/
test_type/covers; BENCH-005 measures) ✓ · 2 enums valid (module active/tested; file implemented; test
benchmark/tested; benchmark_result active/implemented; evidence subsets of the closed set) ✓ · 3 no
orphans — MOD-009 ← FILE-030/TEST-022/BENCH-005 + ADR-012 Constrains + index; FILE-030 ← MOD-009; TEST-022
← MOD-009/BENCH-005; BENCH-005 ← MOD-009/TEST-022/ADR-012; each ≥1 outbound ✓ · 4 fresh (2026-06-17) ✓ ·
5 wikilinks resolve — chain modules (MOD-003..006), config/benchmark/ADR/constraint targets all exist;
disambiguated file name `run_forward_return_labels.py` ✓ · 6 module `related_constraints` (MOD-009 →
Canonical Ownership) ✓ · 7 module `related_tests` (MOD-009 → test_forward_return_labels) ✓ · 8 type-content
aligned (module has Implementation Notes; file concise; test has covers + Used By; benchmark has measures
+ results) ✓ · 9 no deprecated refs in typed sections ✓ · 10 canonical_id uniqueness — MOD-009/FILE-030/
TEST-022/BENCH-005 each next-free, used once ✓ · 11 evidence-confidence coherence (confirmed + non-empty
evidence) ✓.

### Metrics

dev_graph content nodes 176 → 180 (+MOD-009, +FILE-030, +TEST-022, +BENCH-005); module 8→9, file 29→30,
test 21→22, benchmark_result 4→5; coverage 180/180; total files 180→184. No new ontology type/enum; no
schema version change; no `*_version` bump. Re-sync Neo4j (`python sync_to_neo4j.py --clear`) — counts
recorded after sync.

### Deferred / next

The labeler accumulates labels as the corpus grows; G3 stays deferred until per-regime coverage + a
walk-forward out-of-sample slice accrue (ADR-012 §3). When real ADMIT/LONG snapshots appear (a
diversifying tape), the real section will begin producing realized labels. **Stopped for operator
review — measurement tool only; no decision logic, config, or `*_version` changed.**

---

## [2026-06-18] writeback | Chain Orchestrator — end-to-end Layer-3 composition root (MOD-010)

Built the **full chain-orchestrator integration** the STEP-4 execution writeback explicitly deferred
(log 2026-06-16: *"full chain-orchestrator integration (re-deriving price/direction from the in-hand
FeatureVector)"*). A new `src/orchestration` module threads a banked snapshot through every
already-governed Layer-3 stage in one deterministic call — `consume → build_features → classify →
build_decision → evaluate → [GATE-001 guard] → execute → persist` — forwarding `packet.direction` and the
in-hand `FeatureVector.value("gold_price")` straight into `execute` (the ADR-011 **D1 in-hand path**) and
running the GATE-001 guard **in the orchestrator** before `execute` (ADR-009 §3 / ADR-011 gate c — the
orchestrator is the only cross-context importer, incl. `src/risk`). **Pure composition: no layer's logic,
no contract, and no `*_version` changed.** Governed by [[ADR - Paper-Trading Runtime Planning]] (ADR-009)
+ [[ADR - Execution Layer Planning]] (ADR-011); authors no new ADR / interface / schema.

### Application code created (not dev_graph nodes)

- `src/orchestration/`: `__init__.py`, `models.py` (`ChainResult` + `to_dict` + `ChainContractError`),
  `config.py` (captured `DEFAULT_OPERATIONAL_INPUT` + `DEFAULT_GUARD_CONFIG`), `engine.py` (pure
  `run_chain`), `runtime.py` (IO shell `run_once` + pure `run_sequence` + `find_latest_snapshot` + the
  `python -m orchestration.runtime` CLI).
- `benchmarks/orchestration/run_chain_bench.py` + committed golden `artifacts/chain_bench.json`.
- `tests/orchestration/`: `test_chain_engine.py` (12), `test_chain_determinism.py` (7),
  `test_chain_bench.py` (8) — **27 new tests**.
- `pyproject.toml` (+`src/orchestration` wheel package); `.gitignore` (+`runtime/` for CLI state);
  `CHAIN_ORCHESTRATOR_RUNBOOK.md` (the integration brief — data flow, full replay key, determinism
  guarantees, invocation, EOD hook documented-not-wired, follow-ups).

### Nodes Created (10)

**Module (1)** — `MOD-010` [[Chain Orchestrator]] (`module_path src/orchestration`; status active /
implementation_status tested; Depends On MOD-003..008 + MOD-001; Realizes [[Pipeline Pattern]]; Justified
By ADR-009 + ADR-011; Originates From [[Paper Trading Validation]]).

**File (5)** — all `module: [[Chain Orchestrator]]`, evidence [code]:
- `FILE-031` [[models.py (orchestration)]], `FILE-032` [[config.py (orchestration)]],
  `FILE-033` [[engine.py (orchestration)]], `FILE-034` [[runtime.py (orchestration)]],
  `FILE-035` [[run_chain_bench.py]] (the BENCH-006 harness; in `related_files`, not `Contains`).

**Test (3)** — evidence [code], implementation_status tested:
- `TEST-023` [[test_chain_engine]] (e2e), `TEST-024` [[test_chain_determinism]] (e2e),
  `TEST-025` [[test_chain_bench]] (benchmark) — each `covers [[Chain Orchestrator]]`.

**Benchmark (1)** — `BENCH-006` [[Chain Orchestrator Benchmark]] (measures = the full replay key + the
proof dimensions; committed golden `chain_bench.json`).

### Changes (existing nodes updated — 3)

- **MOD-008 [[Execution]]**: Open Question "full chain-orchestrator integration … deferred" → **closed**
  (now implemented by [[Chain Orchestrator]] / BENCH-006); `### Used By += [[Chain Orchestrator]]`;
  `updated 2026-06-18`. No logic/contract change.
- **PAT-004 [[Pipeline Pattern]]**: `realized_by_modules += [[Chain Orchestrator]]`; `### Realized By +=`;
  `updated 2026-06-18` (the orchestrator is the end-to-end pipeline).
- **WF-001 [[System Lifecycle]]**: prose note — the PaperTrading-state end-to-end run is operationalized
  by [[Chain Orchestrator]]; `### Used By += [[Chain Orchestrator]]`; `updated 2026-06-18`.
- **index.md**: Modules / Files / Tests / Benchmarks tables + header + Statistics.

### Full replay key (the union folded into BENCH-006 `measures`)

`source_snapshot_id` + `feature_schema_version` + `taxonomy_version`/`classifier_version`/
`classification_trace_version` + `decision_policy_version` (+fp) + `runtime_policy_version` (+fp) +
`execution_policy_version` (+fp) + `fill_model_version` (+fp) + **`guard_config_fingerprint`** +
**`operational_input_fingerprint`** + prior `RuntimeLedger`/`PortfolioState` `state_hash` ⇒ identical 5
records + new ledger + portfolio.

### Benchmark result (BENCH-006)

`all_replays_byte_identical = true`. Real sequence (the consumable corpus `952cc83a…` across 3 paths + 1
re-presentation): `verdict_distribution {ADMIT 1, REJECT 3}`, `fill_distribution {filled 0, no_fill 4}`.
First presentation ADMITs (`RESTRICTIVE_RATES → AVOID`, `packet_id gold-v0:5653d07a0b3949d5`, in-hand
`gold_price 4624.5`) — AVOID is non-LONG ⇒ deterministic **no-fill**; every re-presentation REJECTs on
`duplicate_ok` (no second admit, no double-fill). `pinned_ledger_state_hash fff4dcc3…`,
`pinned_portfolio_state_hash 2d19b9b5…` (empty portfolio). **Honest caveat (carried from BENCH-004):** the
monochromatic AVOID corpus proves end-to-end replay determinism + admission idempotency, **not** a real
fill — the fill path stays BENCH-004's synthetic execution sweep.

### Lint (11 checks, touched nodes: MOD-010, FILE-031..035, TEST-023..025, BENCH-006, MOD-008, PAT-004, WF-001, index.md)

1 frontmatter complete (MOD-010 module ext; FILE-031..035 file_path/language/module; TEST-023..025
test_path/test_type/covers; BENCH-006 measures) ✓ · 2 enums valid (module active/tested; files
implemented; tests e2e+benchmark/tested; benchmark_result active/implemented; evidence ⊆ closed set) ✓ ·
3 no orphans — MOD-010 ← FILE-031..035 (module) + TEST-023..025 (covers) + BENCH-006 + MOD-008 Used By +
PAT-004 Realized By + WF-001 Used By + index; each new node ≥1 outbound ✓ · 4 fresh (2026-06-18) ✓ ·
5 wikilinks resolve — composed modules (MOD-001, MOD-003..008), schemas, PAT-004, KA-010, WF-001, ADRs,
constraint all exist; disambiguated file names `(orchestration)` avoid Obsidian basename collisions ✓ ·
6 module `related_constraints` (MOD-010 → Canonical Ownership) ✓ · 7 module `related_tests` (MOD-010 →
test_chain_engine/determinism/bench) ✓ · 8 type-content aligned (module has Implementation Notes; files
concise w/ Depends On parent + Validated By; tests have covers + Used By; benchmark has measures +
Results + caveat) ✓ · 9 no deprecated refs in typed sections (CAP-004 referenced nowhere new) ✓ ·
10 canonical_id uniqueness — MOD-010 / FILE-031..035 / TEST-023..025 / BENCH-006 each next-free, used
once ✓ · 11 evidence-confidence coherence (confirmed + non-empty evidence on every new node) ✓.

### Metrics

dev_graph content nodes 180 → **190** (+MOD-010, +FILE-031..035, +TEST-023..025, +BENCH-006); module
9→10, file 30→35, test 22→25, benchmark_result 5→6; coverage 190/190; total files 184→194. Realizes
edges 36→37 (+MOD-010 → Pipeline Pattern); the index `Realizes edges` statistic, which had drifted from
the materialized graph (it read 31), is **corrected** to the true 37 (24 capability + 10 module + 3 file),
verified via the `sync_to_neo4j.py --dry-run` edge projection. No new ontology type/enum; no schema version change; **no
`*_version` bump; no contract / decision-path change**. Application: full suite **933 green** (906 prior
+ 27 new); `ruff` clean (src/tests/benchmarks); `mypy --strict` clean on `src/orchestration` (the only
2 mypy errors are pre-existing lambda-inference warnings in MOD-004 `feature_builder.py`, confirmed on
clean HEAD, unrelated to this slice). Re-sync Neo4j (`python dev_graph/sync_to_neo4j.py --clear`).

### Deferred / next (named follow-ups — NOT built here)

- **Live operational-status feed** behind the explicit `OperationalInput` seam (v0 is a configured
  captured default; ADR-009 Non-Goal).
- **Computed cooldown guard** (MOD-007's echoed `cooldown_ok` → computed from the ledger; its own slice —
  it changes an admission guard's semantics).
- **Scheduling** the daily run after the EOD snapshot (operator action; documented in
  `CHAIN_ORCHESTRATOR_RUNBOOK.md`, not wired).
- STEP-5 Alpaca paper adapter; the G1/G2/G3 calibration bumps (data-gated, ADR-012); the pre-existing
  MOD-004 `mypy` lambda annotations (a tiny, separate, behavior-neutral fix).

**Stopped for operator review — pure composition; no layer logic, contract, or `*_version` changed.
Scheduling is an operator action, not wired here.**

---

## [2026-06-18] schema+writeback | Computed Cooldown — runtime_policy_version 0.1.0 → 0.2.0 (MOD-007)

Lifted ADR-009's deferred **"computed cooldown guard (v0 echoes)"**: the L3 `cooldown_ok` is now
**computed from runtime state** (the gap, by the snapshot `as_of`, since the last ADMIT of a *different*
snapshot) instead of echoing the L2 snapshot flag. This **changes the accepted MOD-007 admission
baseline's behavior**, so it is a governed, **versioned** Config-Evolution change: `runtime_policy_version`
**0.1.0 → 0.2.0**, the affected goldens re-pinned, and old-version replay preserved (the version is in the
replay key). **Governance choice:** an **ADR-009 amendment** (not a new ADR) — it lifts that ADR's own
deferred Non-Goal within the same component/epoch, draws no new boundary. Deterministic only (sole time
source = the snapshot `as_of`; **never** wall-clock); fail-closed.

### Design (resolved + justified)

- **Replace, not additional** — the six-guard taxonomy has exactly one `cooldown_ok` slot; ADR-009 §6 framed
  the echo as a v0 placeholder for the future computed cooldown. The L2 snapshot `cooldown_ok` stays as
  forwarded `snapshot_guards` **provenance** (its §3 role), no longer echoed into the L3 outcome.
- **No SCHEMA-013 change** — the ledger already records each entry's `as_of`; only an additive read-accessor
  `RuntimeLedger.last_admit_as_of(exclude_self)` is added.
- **`duplicate_ok` evaluated FIRST** among required guards — an exact re-presentation attributes to
  idempotency (PRED-006), not cooldown (PRED-008); preserves every prior triggered-guard attribution.
- **Default `cooldown_window_hours = 20.0`** (sub-daily, so the ~24h snapshot cadence never self-blocks),
  `require_cooldown = True`. Fail-closed on missing/unparseable/negative-gap timing.

### Application code (not dev_graph nodes) — scoped to `src/gold/paper_runtime/`

- `config.py` — `+require_cooldown`, `+cooldown_window_hours`; `_RUNTIME_FIELDS` += both; version 0.1.0→0.2.0;
  fingerprint `ab798cae… → 47ca2649…`. `models.py` — `+RuntimeLedger.last_admit_as_of`. `predicates.py` —
  `cooldown_ok(packet, prior_ledger, config)` computed (`+_parse_as_of`), replacing the echo. `engine.py` —
  `_required_guards` duplicate-first + `require_cooldown`; calls `cooldown_ok` with ledger+config.
- Tests: `test_paper_runtime_guards` — echo tests split (data/freshness only) + **7 new computed-cooldown
  units** (no-prior / within-window / elapsed / exclude-self / only-admits / fail-closed-missing /
  out-of-order). `test_paper_runtime_determinism` — `_DEFAULT_FINGERPRINT` re-pinned to `47ca2649…`.
- Goldens re-pinned (all thread `evaluate`): **BENCH-003** (record_ids + version/fingerprint),
  **BENCH-004** execution (real ADMIT `record_id` → `execution_id` cascade), **BENCH-006** chain
  (replay_key `runtime_policy_version` + fingerprint). **Verdict distributions + triggered-guard
  attributions unchanged on every existing corpus** (all distinct-admit gaps ≥24h > the 20h window) —
  identity-only re-pins. Full suite **940 green** (933 + 7); `ruff` clean; `mypy --strict` clean on
  `src/gold/paper_runtime`.

### Nodes Created (1)

- `PRED-008` [[Cooldown OK]] — the computed-cooldown predicate (implemented_in `predicates.py`, validated_by
  `test_paper_runtime_guards`; Guards [[Gold Decision Gate]] + [[Runtime Admission Gate]]; Justified By ADR-009).

### Changes (existing nodes updated)

- **ADR-009** — `## Amendment — Computed Cooldown (v0.2.0)` section (the design, the bump, replay
  preservation, the no-new-ADR rationale); `updated 2026-06-18`.
- **MOD-007** — Definition (three computed guards now), config/predicates/engine Implementation Notes
  (v0.2.0, fingerprint, duplicate-first), Open Question (computed cooldown done; live feed still deferred);
  `updated 2026-06-18`.
- **GATE-003** Runtime Admission Gate — composes PRED-008; `Depends On += [[Cooldown OK]]`; "required guards"
  corrected (cooldown now required, duplicate-first); `updated`. **GATE-002** Gold Decision Gate —
  `Depends On += [[Cooldown OK]]`; `updated`.
- **FILE-019/020/021/022** (models/config/predicates/engine paper_runtime) — Implementation Notes + `updated`.
- **BENCH-003/004/006** nodes — Results re-pin notes (v0.2.0 version/fingerprint; distributions unchanged).
- **index.md** — Predicates table (+PRED-008) + Statistics (predicate 7→8; content nodes 190→191; files 194→195).

### Lint (11 checks, touched nodes: PRED-008, ADR-009, MOD-007, GATE-002/003, FILE-019..022, BENCH-003/004/006, index)

1 frontmatter complete (PRED-008 predicate ext; all enums) ✓ · 2 enums valid ✓ · 3 no orphans — PRED-008 ←
GATE-002/003 `Depends On` + MOD-007/ADR-009 body; ≥1 outbound (Guards → both gates) ✓ · 4 fresh
(2026-06-18) ✓ · 5 wikilinks resolve ([[Cooldown OK]], gates, ADR, test, constraint all exist) ✓ · 6/7
module constraint/test coverage unchanged (MOD-007 already populated) ✓ · 8 type-content aligned
(PRED-008 predicate scope + implemented_in; stale version strings corrected in MOD-007/GATE-003/BENCH
nodes) ✓ · 9 no deprecated refs ✓ · 10 canonical_id uniqueness — PRED-008 next-free, used once ✓ · 11
evidence-confidence coherence ✓.

### Metrics + version evolution

`runtime_policy_version 0.1.0 → 0.2.0`; `runtime_policy_fingerprint ab798cae…6f32 → 47ca2649…98cc8`
(`_RUNTIME_FIELDS` += cooldown_window_hours, require_cooldown). No schema/enum/ontology change; SCHEMA-012/013
unchanged; only MOD-007's `*_version` bumped (its own governed baseline). dev_graph content nodes 190 → **191**
(+PRED-008); predicate 7→8; total files 194→195; coverage 191/191. Re-sync Neo4j (`sync_to_neo4j.py --clear`).

### HARD PAUSE (per the follow-up prompt)

**Stopped for operator review BEFORE committing the `runtime_policy_version` bump** — it changes the
accepted baseline's record identities (verdicts/attributions unchanged). v0.1.0 echo behavior remains
reproducible at its version. Nothing committed.

---

## [2026-06-18] writeback | Live Operational-Status Feed — additive IO adapter (MOD-010 seam)

Lifted ADR-009's deferred **"live operational-status feed"**: a new `OperationalFeed` port +
deterministic `MarketCalendarFeed` produces a real `OperationalInput` for the live `run_once` path, behind
the explicit `OperationalInput` seam MOD-010 already left ready. **Purely additive IO — no pure-core
change, no `OperationalInput` schema change, no `*_version` bump.** Governed by ADR-009 (the guard + model)
+ ADR-011 §2 / gate f (the non-replayable-adapter quarantine).

### The non-negotiable: replay-path quarantine

The feed is read **only** on the live `run_once` path; the produced `OperationalInput` is **captured**
(persisted as a JSON artifact in the existing `load_operational` format), so any `run_sequence` replay
threads the captured value and **never** re-reads the feed (`run_sequence` has no feed parameter). No
clock/network on the replay path — exactly the ADR-011 §2 / gate-f boundary (live runs logged, not
replayed). The capture mechanism makes even a *non*-deterministic feed (the future Alpaca plug) replayable.

### Source choice (justified)

v0 = a **deterministic** US-equity trading-calendar feed for the GLD venue (`MarketCalendarFeed`): a
trading day is a non-holiday weekday ⇒ tradeable/venue_open; weekend / listed holiday / unparseable
`as_of` ⇒ `OperationalInput.closed()` (**fail-closed**). No network, no wall-clock, **no credentials** —
itself replay-safe. The holiday set is a deterministic v0 approximation, **not** a full NYSE calendar (the
live **Alpaca clock/calendar** plug's job — env-only creds per KA-008, never in repo/memory/node;
**deferred**, the seam is ready).

### Application code (not dev_graph nodes)

- `src/orchestration/operational_feed.py` (NEW) — `OperationalFeed` Protocol + `MarketCalendarFeed` +
  `persist_operational` (temp + `os.replace`) + `read_and_capture` (read once → capture → return).
- `src/orchestration/runtime.py` — `run_once` += `operational_feed` + `operational_capture_path` (IO-path
  read + capture); CLI += `--operational-feed` / `--operational-capture`. `run_sequence` **unchanged**
  (feed-free — the quarantine). `__init__.py` exports the feed.
- `tests/orchestration/test_operational_feed.py` (NEW, **10 tests**) — calendar open/closed/weekday-holiday
  (2026-12-25 Friday)/fail-closed; capture round-trip via `load_operational`; **capture freezes value
  independent of a later feed**; **`run_sequence` replay never reads the feed** (stub call-count stays 1);
  `run_once` live integration on the real (Friday/trading-day) fixture. Full suite **950 green** (940 + 10);
  `ruff` clean; `mypy --strict` clean on `src/orchestration`.

### Nodes Created (2)

- `FILE-036` [[operational_feed.py]] (module [[Chain Orchestrator]]); `TEST-026` [[test_operational_feed]]
  (covers MOD-010 + FILE-036).

### Changes (existing nodes updated)

- **ADR-009** — second amendment section `## Amendment — Live Operational Feed (additive IO adapter)` (the
  quarantine invariant, the source choice, KA-008 credential isolation for the deferred Alpaca plug,
  no-schema-change rationale).
- **MOD-010** — `related_files += operational_feed.py`, `related_tests += test_operational_feed`, `Contains`
  + `Validated By` updated, Open Question (live feed now implemented; Alpaca plug deferred).
- **MOD-007** — Open Question (live operational feed now implemented behind the seam).
- **FILE-034** runtime.py (orchestration) — Implementation Notes (the feed params + CLI flag + the
  quarantine).
- **index.md** — Files (+FILE-036) + Tests (+TEST-026) tables + Statistics (file 35→36, test 25→26, content
  nodes 191→193, total files 195→197) + header.

### Lint (11 checks, touched: FILE-036, TEST-026, ADR-009, MOD-010, MOD-007, FILE-034, index)

1 frontmatter complete (FILE-036 file ext; TEST-026 test ext) ✓ · 2 enums valid (file implemented; test
integration/tested) ✓ · 3 no orphans — FILE-036 ← MOD-010 (related_files + Contains) + TEST-026 + ADR-009
body; TEST-026 ← MOD-010 (related_tests) + FILE-036; each ≥1 outbound ✓ · 4 fresh (2026-06-18) ✓ · 5
wikilinks resolve ([[operational_feed.py]], [[test_operational_feed]], [[Chain Orchestrator]], ADRs, KA-008
all exist) ✓ · 6/7 MOD-010 constraint/test coverage already populated ✓ · 8 type-content aligned (file has
Implementation Notes + Constraints; test has covers + Used By) ✓ · 9 no deprecated refs ✓ · 10 canonical_id
uniqueness — FILE-036 / TEST-026 next-free, used once ✓ · 11 evidence-confidence coherence ✓.

### Metrics

dev_graph content nodes 191 → **193** (+FILE-036, +TEST-026); file 35→36, test 25→26; total files 195→197;
coverage 193/193. **No** schema/enum/ontology change; **no** `*_version` bump; **no** `OperationalInput`
contract change (purely additive IO). Re-sync Neo4j (`sync_to_neo4j.py --clear`).

### Stopped for operator review

**Built; nothing committed.** The live feed read is IO-path-only and captured for replay; the deterministic
calendar feed needs no credentials (the Alpaca live plug + its env/`.secrets` credential isolation is the
named deferred follow-up).

## 2026-06-18 writeback | Alpaca live plugs (ADR-011 gate f) + chain scheduling + ADR-012 readiness re-check

### Part 1 — Alpaca live plugs (behind existing ports; non-replayable; default-OFF)

- `src/orchestration/alpaca_clock_feed.py` (NEW, FILE-037) — `AlpacaClockFeed` implements the
  `OperationalFeed` port; reads Alpaca `/v2/calendar` (paper base URL only) to **close the v0
  holiday-calendar gap** (movable feasts / observed dates the fixed-date `MarketCalendarFeed` cannot
  model). Injected `AlpacaCalendarClient` Protocol + stdlib-only REST client + `clock_feed_from_env`
  factory. **Fail-closed** (missing/non-paper creds, API error, unparseable `as_of` ⇒ `closed()`); read
  on the live path only and captured/quarantined exactly like the deterministic feed (never re-read on
  replay). **Default-OFF**, not re-exported.
- `src/execution/alpaca_adapter.py` (NEW, FILE-038) — `AlpacaPaperAdapter` implements the INT-011
  `ExecutionPort` (`mode=alpaca_paper`, `replayable=False`); `fill()` submits a paper market BUY and
  echoes the paper fill. Injected `AlpacaPaperBroker` Protocol + `PaperOrderResult` + stdlib REST broker
  + `AlpacaExecutionError` + `paper_adapter_from_env` factory (refuses any non-paper base URL; fail-closed
  on missing creds). **Non-replayable quarantine** (never on `run_sequence`/benchmarks; simulator stays
  the hard-wired default port); **built-but-dormant** (engine calls `fill()` only for an approved LONG,
  none until calibration — ADR-011 §5). **Default-OFF**, not re-exported.
- `src/orchestration/runtime.py` — **additive** CLI flag `--operational-feed-source {calendar,alpaca}`
  (default `calendar`; prior behaviour unchanged); lazily wires the live clock feed on opt-in.
  `run_once`/`run_sequence` contracts **untouched**.
- `.gitignore` — added `.secrets` / `.secrets/` / `*.secrets` (KA-008 credential isolation).
- Tests: `tests/orchestration/test_alpaca_clock_feed.py` (TEST-027, 17) + `tests/execution/test_alpaca_adapter.py`
  (TEST-028, 20) — mocked clients, **no real network**; cover the holiday-gap closure, fail-closed paths,
  paper-only URL refusal (incl. spoofed URLs, below), and the replay/engine quarantine. **Full suite 986
  green** (was 950); `mypy --strict` + `ruff` clean on the new files (the 2 pre-existing MOD-004 lambda
  mypy warnings remain, unrelated).

### Adversarial review (5-dimension workflow) + hardening

A multi-agent adversarial review (paper-only/credentials, fail-closed, quarantine/determinism, holiday-gap
correctness, governance/writeback — each finding independently verified) returned **clean on four
dimensions** (fail-closed, quarantine/determinism, holiday-gap, governance) and found **one real defect**:
the paper-only credential boundary used a **substring** URL check (`_PAPER_HOST not in base_url`), which a
sub-/super-domain (`evil.paper-api.alpaca.markets`, `paper-api.alpaca.markets.evil.com`), a query/fragment
carrying the host, or a non-https URL could defeat (credential-exfil bypass of ADR-011 §3 / KA-008 /
PRED-005), and which also wrongly rejected a legitimate mixed-case host. **Hardened** both
`clock_feed_from_env` and `paper_adapter_from_env` to a parsed-hostname equality check
(`urlparse(base_url).hostname == "paper-api.alpaca.markets"` **and** `scheme == "https"`), added regression
tests (+6 each: 5 spoofed-URL params + 1 mixed-case accepted), and fixed a low test-stub nit
(`_StubCalendar` returned a duplicate date when `start == end`). Re-ran: `mypy --strict` + `ruff` clean,
**986 green**.

### Part 2 — chain scheduling (simulator path; ops tooling, no file nodes — mirrors Mr-Ripley)

- `scripts/daily_chain_run.ps1` (NEW) — runs the latest banked Mr-Ripley snapshot through MOD-010
  `run_once` on the **deterministic simulator** + operational calendar feed (captured), persisting the
  el_nino ledger + portfolio (idempotent). **Manually validated once** against scratch state: latest
  snapshot `c1fe5a02` (2026-06-15) → RESTRICTIVE_RATES/AVOID → ADMIT + no-fill, exit 0.
- `scripts/register_daily_chain_task.ps1` (NEW) — registers the recurring 23:45 task after the Mr-Ripley
  23:00 EOD job. **Parse-checked but NOT run — operator HARD-PAUSE.** Both scripts ASCII-only (PS 5.1
  reads UTF-8-no-BOM as CP1252).

### Part 3 — ADR-012 G1/G2/G3 readiness re-check (DEFER; no bump)

- Re-ran MOD-009 `run_forward_return_labels.py --include-external`. Corpus unchanged since 2026-06-17:
  N=5 (1 committed fixture + 4 Mr-Ripley archives, latest 2026-06-15), **monochromatic RESTRICTIVE_RATES
  / AVOID** (1/12 regimes, 1/4 directions), **0 realized labels**. ⇒ **G0 FAIL (N≪60); G1/G2/G3 DEFER.**
  **No `*_version` bump, no value/direction-table change, no benchmark re-pin** — the committed golden
  `forward_return_labels.json` is byte-identical (git diff empty). AVOID-objective + FLAT_BAND remain
  undefined in ADR-012 (a further precondition on any future G3 direction-table bump).

### dev_graph changes

- **NEW**: FILE-037 [[alpaca_clock_feed.py]] (→ MOD-010), FILE-038 [[alpaca_adapter.py]] (→ MOD-008),
  TEST-027 [[test_alpaca_clock_feed]], TEST-028 [[test_alpaca_adapter]].
- **ADR-011** — §7 gate **(f) CLOSED** (all six now closed); state + reconciliation lines updated to
  2026-06-18; `related_files`/`related_tests` + `evidence: code`.
- **ADR-009** — live-feed amendment extended (the Alpaca clock plug is now built, default-OFF; closes the
  holiday gap); `related_files`/`related_tests`; normative-nodes line.
- **MOD-008** — `related_files += alpaca_adapter.py`, `related_tests += test_alpaca_adapter`, Definition /
  Implementation Notes / Open Questions / Contains / Validated By updated (adapter now built default-OFF).
- **MOD-010** — `related_files += alpaca_clock_feed.py`, `related_tests += test_alpaca_clock_feed`,
  Implementation Notes (the clock plug + `--operational-feed-source` flag + scheduling scripts) / Open
  Questions (feed plug built; scheduling registration = HARD-PAUSE) / Contains / Validated By updated;
  suite 933→974.
- **INT-011** — second (default-OFF) implementor `AlpacaPaperAdapter` recorded; `related_files`; Open
  Questions updated; `updated` 2026-06-18.
- **FILE-026** (adapters.py) / **FILE-036** (operational_feed.py) — body + `related_files` cross-link the
  new sibling plugs; "deferred" → "built default-OFF".
- **index.md** — Files (+FILE-037/038) + Tests (+TEST-027/028) tables + header + Statistics (file 36→38,
  test 26→28, content nodes 193→197, total files 197→201, coverage 197/197) + dated entry.

### Lint (11 checks, touched: FILE-037/038, TEST-027/028, ADR-011, ADR-009, MOD-008, MOD-010, INT-011, FILE-026, FILE-036, index)

1 frontmatter complete (file/test domain fields present) ✓ · 2 enums valid (file implemented/implemented;
test unit&integration/tested; ADRs decision_record) ✓ · 3 no orphans — FILE-037 ← MOD-010 + ADR-009/011 +
FILE-036 + TEST-027; FILE-038 ← MOD-008 + ADR-011 + FILE-026 + TEST-028; tests ← their modules+files; each
≥1 outbound ✓ · 4 fresh (2026-06-18) ✓ · 5 wikilinks resolve ([[alpaca_clock_feed.py]],
[[alpaca_adapter.py]], [[test_alpaca_clock_feed]], [[test_alpaca_adapter]], [[Execution]],
[[Chain Orchestrator]], [[Execution API]], [[adapters.py]], [[operational_feed.py]], ADRs all exist) ✓ ·
6/7 MOD-008/010 constraint+test coverage populated ✓ · 8 type-content aligned (files have Implementation
Notes + Constraints; tests have covers + Used By; ADR-011 gate board updated) ✓ · 9 no deprecated refs ✓ ·
10 canonical_id uniqueness — FILE-037/038, TEST-027/028 next-free, used once ✓ · 11 evidence-confidence
coherence (all `confirmed` carry `evidence`) ✓.

### Metrics

dev_graph content nodes 193 → **197** (+FILE-037/038, +TEST-027/028); file 36→38, test 26→28; total files
197→201; coverage 197/197. **No** schema/enum/ontology change; **no** `*_version` bump; **no** contract
change (Part 1 additive plugs behind existing ports; Part 2 ops tooling; Part 3 DEFER). Re-sync Neo4j
(`sync_to_neo4j.py --clear`).

### Stopped for operator review (HARD PAUSE)

**Built + validated; nothing committed; nothing enabled.** Two HARD-PAUSE gates remain for the operator:
(a) **enabling the live Alpaca execution path** (the adapter ships dormant/default-OFF), and (b)
**registering the recurring scheduled task** (`register_daily_chain_task.ps1` is built + parse-checked but
not run). Part 3 is DEFER, so no calibration bump and no commit pause was reached.

## [2026-06-21] writeback | ADR-014 v2 — Operable Alpaca Paper Execution Adapter (design locks + audit folded, A8 resolved)

**Governance-only** revision of the **unaccepted** ADR-014 draft. `status` stays `draft`; `canonical_id`
ADR-014 unchanged; `supersedes`/`superseded_by` stay empty — an **in-place revision of an unaccepted
draft, not a supersession**. **No `src/` or `tests/` change** (the refactor is downstream:
`/prd-to-issues` → slices, after operator acceptance). No `wiki/**` / `raw/**` mutation (CON-001).

### Nodes Changed
- **ADR-014 renamed** `decisions/ADR-014 - Operable Alpaca Paper Execution Adapter v1.md` →
  `decisions/ADR - Operable Alpaca Paper Execution Adapter v1.md` (the conventional `ADR - <Title>`
  basename; nothing referenced the old prefixed name — grep-confirmed). `canonical_id` ADR-014 preserved;
  "v1" denotes the **adapter** version, not the document version.
- **ADR-014 Decision rewritten** to encode a six-round design grilling (Q1–Q6 locks) + the
  `app_audit.md` findings, split into **(i) contained shared changes (versioned)** — §5.1 source-pluggable
  `exec_ref_gld_price` (sim derived proxy `gold_price_proxy×oz_per_share` / live GLD mark; GLD-vs-GLD
  slippage; new `exec_price_source_version`; BENCH-004/006 re-pin), §5.2 daily-guard `as_of` threading
  (mislabeled-daily fix; `ExecutionEntry.as_of` SCHEMA-015 change; mirrors PRED-008), §5.3
  `assert port.replayable` + a separate live `(ledger_path, portfolio_path)` pair, §5.4 additive
  SCHEMA-014/015 fields — and **(ii) live-plug-only additions** — §6 the `operate_live` non-replayable
  entrypoint (fork-(b); `fill()` untouched), reconcile-then-act + broker=position-authority /
  local=lineage-authority + reconcile-heal entry-kind + **terminal-refuse-on-discrepancy** (no
  auto-flatten; refuse scopes to execution only), open-orders-aware in-flight ownership, settled-cash cap
  + fractionable, accumulate-only sim + live sell-fold, side-based adapter, and the
  QUEUED/PARTIAL/EXECUTION_UNCERTAIN/NO_ACTION state machine + typed errors + 429.
- **A8 resolved** (overrules `app_audit.md` blocker #1): the GLD-price fix is **el_niño-side, no hard
  Mr-Ripley predecessor**; the real-GLD-in-snapshot ingest is demoted to an optional, separately-tracked
  simulator-fidelity upgrade behind the same `exec_ref_gld_price` seam. Every "A8/B6 blocks on Mr-Ripley"
  statement corrected.
- **Enumerated-defects table** added — the audit's 12 ungoverned findings each owned with a scope +
  one-line rationale: **v1** (sync-fill raise, mislabeled daily guard, uncaught `HTTPError`,
  429/`Retry-After`, `GET /v2/account` status gate, audited Tier-2 kill switch, broker-traceability
  fields) / **deferred** (early-close, clock-feed TZ, audit actor field, GDPR/CCPA N-A note, rate limiter).
- **Frontmatter**: `updated` 2026-06-21; `evidence` keeps `[design, ADR, code]`; `source_paths +=
  app_audit.md`; `related_files += [[Runtime Ledger Schema]]`. status `draft`, decision_status `active`.
- **index.md** — added the ADR-014 Decisions row; Statistics `decision_record 13→14`, content nodes
  `210→211`, total files `214→215`, coverage `211/211`; header dated 2026-06-21 + revision note.

### Verification (two adversarial workflows, 8 agents)
- **Grounding** (5 agents) — verified every code/graph fact the locks reference against the real source
  (file:line + quotes): `_FILLED_STATUSES` sync-fill raise, unguarded order `urlopen`, parsed-hostname
  guard, `engine.py:95` `gold_price` forward, `gold_price` reserved/non-predicate in `taxonomy.py`,
  `oz_per_share`/`_apply_sell`/live `operate_live` all net-new, `build_guard_request` mislabeled inputs,
  PRED-008 `as_of` discipline, `replayable` pre-existing (assert net-new), SCHEMA-013/014/015 +
  BENCH-004/006 mapping, all wikilink targets resolve.
- **Review** (3 agents) — lock fidelity, audit-coverage+A8, code-accuracy+lint: all six locks **fully
  encoded**, all 12 findings **owned with scope+rationale**, A8 **fully resolved** (zero residual
  "Mr-Ripley first"), code citations accurate, frontmatter compliant. Six **nits** (no blockers) all
  applied: dropped a mis-encoded "Q2-class" tag, added `exec_ref_gld_price_ts`/`_basis` to the §5.4 schema
  delta, widened the `build_guard_request` line cite to `:78-101`, corrected "suite only stubs filled" →
  "stubs only `filled`/`rejected`, no async/4xx", clarified the kill-switch "pick one", and tightened the
  `source_record_id`/`guard_result` attribution.

### Lint (11 checks, touched: ADR-014, index.md)
1 frontmatter complete (decision_record domain fields present) ✓ · 2 enums valid (status draft;
implementation_status not-started; confidence confirmed; evidence ⊆ allowed) ✓ · 3 no orphans — ADR-014
links Execution/Chain Orchestrator/Paper-Trading Runtime/Gold Forward-Return Labeler + four justifying
ADRs + three constraints/KAs (≥1 outbound) ✓ · 4 fresh (updated 2026-06-21) ✓ · 5 wikilinks resolve (all
relationship + related_files/related_decisions targets exist — verified) ✓ · 6/7 a decision_record needs no
related_constraints/tests beyond those linked ✓ · 8 type-content aligned (Status/Context/Decision/
Alternatives/Consequences/Out-of-scope present) ✓ · 9 no deprecated refs ✓ · 10 canonical_id ADR-014 unique
✓ · 11 evidence-confidence coherent (`confirmed` carries `[design, ADR, code]`) ✓.

### Metrics
dev_graph content nodes 210 → **211** (ADR-014 now indexed; the node file pre-existed from the prior
session but was uncounted in index.md). **No** schema/enum/ontology change; **no** `*_version` bump (the
`exec_price_source_version` etc. are *proposed* in the draft, not applied to code); **no** contract change.
Re-sync Neo4j (`python sync_to_neo4j.py --clear`).

### Stopped for operator review (HARD PAUSE)
ADR-014 stays `status: draft` / `decision_status: active` — **operator acceptance is the checkpoint; it is
not auto-accepted.** On acceptance: `status: draft → active` (and the downstream `/prd-to-issues` slices
proceed under §5/§6). Pre-existing index-header drift (the 2026-06-18 "986 green" prose vs the later
ops-epoch Statistics) is noted but left untouched — out of scope for this governance revision.
