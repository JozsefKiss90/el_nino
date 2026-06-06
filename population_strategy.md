Dev Graph Population Strategy and Execution Roadmap

---

Authority

This document assumes the following as fixed and final:

- Dev Graph Ontology Redesign (audit_plan.md) — 22-type hierarchy
- Architecture Review Addendum (audit_plan_addendum.md) — knowledge_asset + pattern extensions
- Final Strategic Ontology Review (final_strategic_review.md) — canonical_id, governance, closed loop

Combined target state: 24 types, 17 relationships, 23 directories, 13 universal frontmatter fields, 11 lint checks, schema_version 2.2.0.

The ontology is structurally complete. This document defines how to populate it.

---

1. Population Principles

1.1 Just-in-time, never just-in-case

A node is created when engineering work REQUIRES it, not when someone imagines it might be useful. The audit_plan's object hierarchy (Section 5) defines the EVENTUAL shape of the graph. Nodes from that hierarchy are created only when a session needs them — for context assembly, implementation planning, or active coding.

Exception: Architecture and system nodes (Phases 1-2) are created proactively because they define the structural skeleton that all subsequent nodes reference. Without the skeleton, capability and module nodes have no parent context.

1.2 One engineering concept, one canonical node

Every engineering concept has exactly one canonical representation in the dev_graph. Before creating a node, search the dev_graph for existing coverage. If a concept is already represented, update the existing node. If two nodes overlap, merge them per the merge procedure (final_strategic_review.md Section 8.4).

1.3 No speculative nodes

A node must have substantive content — not just frontmatter and empty section headers. If the content would be entirely "TBD" or "to be determined during implementation," do not create the node. Wait until there is real content to write.

Test: Can the node provide useful context to a Claude coding session TODAY? If not, defer creation.

1.4 Wiki is knowledge, dev_graph is engineering

The wiki answers "what do we know about this concept?" The dev_graph answers "how do we build, validate, and govern this system?"

A wiki page describes Position Sizing as a trading concept — theory, formulas, trade-offs, failure modes, source references. A dev_graph module node describes Position Sizer as a code boundary — inputs, outputs, interfaces, dependencies, tests, constraints.

The wiki page continues to exist. The dev_graph node references it via source_paths. Neither duplicates the other.

Duplication test: If the dev_graph node would contain paragraphs copied from the wiki page, the boundary is wrong. The dev_graph node should contain ONLY engineering-specific content (architecture role, inputs/outputs, interface contracts, dependencies, test requirements) and reference the wiki for domain knowledge.

1.5 Every node has a creation trigger

No node is created ad hoc. Every creation must satisfy a defined trigger condition (Section 3). If no trigger condition is met, the node should not be created. This prevents ontology bloat from "while I'm at it" additions.

1.6 Source-driven creation

Every node's content must trace to an authoritative source:
- Wiki pages (for domain knowledge distilled into engineering artifacts)
- Source documents (for architectural decisions and methodology)
- Actual code (for implementation artifacts)
- Benchmark data (for performance measurements)
- External documentation (for API references)

If no source exists, the node is speculative and should not be created.

1.7 Governance-first

Before creating a node of a type not yet used in the dev_graph, verify:
1. The type exists in CLAUDE.md's allowed enum
2. The directory exists
3. The frontmatter extension schema is defined
4. The canonical_id prefix is assigned
5. The creation trigger (Section 3) is satisfied

If any governance prerequisite is missing, update governance first.

---

2. Population Sources — Canonical Source Matrix

Every ontology type has defined authoritative sources. A node's content MUST derive from these sources. Content from non-authoritative sources is treated as speculative.

| Type | Canonical Source(s) | What the Source Provides | What the Node Adds |
|------|--------------------|--------------------------|--------------------|
| knowledge_asset | Wiki concept/system pages, raw source docs, external docs | Domain knowledge, principles, methodologies | Engineering-scoped summary, ADR linkage, architectural implications |
| pattern | Observed repeated implementation structures across 2+ systems | Structural similarity in existing or planned implementations | Named pattern, structural constraints, realization references |
| architecture | Wiki Architecture Overview, Three-Layer Trading System, Trading Engine Pipeline, Claude-Assisted Trading Stack | Narrative system descriptions | Formal bounded context diagram, runtime topology, layer definitions |
| system | Audit_plan object hierarchy (Section 5), wiki systems pages | Bounded context definitions | Formal system boundary, upstream/downstream, contained capabilities |
| capability | Audit_plan object hierarchy, implementation planning sessions | Abstract behavior groupings | Formal capability definition, interface list, module list |
| interface | System boundary analysis, API documentation | Communication contracts between systems | Input schema, output schema, behavioral contract, error modes, stability rating |
| artifact_schema | Data shape definitions, Layer 2 specification, API contracts | Data structure requirements | Formal schema definition, validation rules, consumers, producers |
| module | Actual code or implementation plan | Code boundary definitions | Responsibility, dependencies, provided interfaces, file references |
| file | Source tree (repository) | Actual source file | File path, language, parent module, ownership |
| test | Test suite (repository) | Actual test file | Test path, test type, coverage targets |
| event | Runtime event flow analysis, interface definitions | Domain event specifications | Event ID, emitter, consumers, payload schema, triggers |
| workflow | Wiki workflow pages (Office Action Loop, Trade Pipeline), process definitions | Process step sequences | State machine definition, transition guards, trigger events |
| gate | Quality checkpoint definitions, governance requirements | Validation checkpoints | Gate scope, required artifacts, blocking behavior, predicate list |
| predicate | Constraint implementations, gate requirements | Boolean conditions | Predicate scope, implementation location, validation references |
| agent | Agent specifications, implementation plans | Autonomous actor definitions | Capabilities implemented, skills available, constraints |
| skill | Agent capability analysis | Individual agent tools | Skill scope, input/output, parent agent |
| decision_record | Architecture decisions made during development | Decision context and rationale | Status, context, decision, consequences, alternatives considered |
| constraint | Risk model requirements, hard invariants from governance | Rules that must not be violated | Invariant definition, scope, enforcement mechanism |
| governance | Governance policies, operational procedures | Process rules | Policy definition, scope, cadence |
| observability | Dashboard definitions, monitoring requirements | Observability specifications | Dataview queries, metric definitions |
| reference | External artifacts, wiki governance pointers | Pointer to external resource | Reference target, relevance, currency |
| api_doc_source | External API documentation (Alpaca, Anthropic) | API reference information | Provider, scope, freshness requirement, allowed tasks |
| benchmark_result | Performance measurement runs | Quantitative results | Measures, metrics, baseline comparisons |
| context_pack | Coding session context assembly | Assembled reading list | Task type, required nodes, admissibility results |

---

3. Population Triggers — When to Create Each Node Type

3.1 Knowledge Asset

Trigger: An engineering principle, methodology, or external guidance is referenced by TWO OR MORE architectural decisions (existing or planned), and no knowledge_asset node yet captures it.

Anti-trigger: A concept that is interesting but does not directly motivate any architectural decision. These belong in the wiki, not the dev_graph.

Examples:
- Event Sourcing: Referenced by event-driven architecture decisions AND data pipeline design → CREATE
- VWAP calculation method: A trading concept, not an engineering principle → DO NOT CREATE (stays in wiki)

Session action: When creating an ADR and you realize the decision is motivated by a principle not yet modeled, create the knowledge_asset node in the same session.

3.2 Pattern

Trigger: Two or more independent implementations (modules, capabilities, or systems) share the same structural approach, and naming the pattern would improve communication and design guidance.

Anti-trigger: A one-off implementation approach that is not reused. One-off approaches are implementation details, not patterns.

Examples:
- Guardrail Pattern: Used in Risk Control (Trade Validation Gate), Evaluation Loop (Promotion Gate), Supervisor Office (Treasury Approval Gate) → CREATE
- Specific stop-loss algorithm: Used only in Stop-Loss Manager → DO NOT CREATE

Session action: When implementing a second system that follows the same structure as an existing system, create the pattern node and add realizes edges to both.

3.3 Architecture

Trigger: Phase 1 of migration (proactive — these form the structural skeleton). Exactly 3 nodes: Context Map, Runtime Topology, Layer Model.

Anti-trigger: Additional architecture nodes beyond the canonical three. If a new architectural perspective is needed, evaluate whether it's a refinement of an existing node or genuinely new.

Session action: Created during the dedicated Phase 1 migration session.

3.4 System

Trigger: Phase 2 of migration (proactive — bounded contexts are structural). Exactly 6 systems as defined in audit_plan Section 5.

Anti-trigger: New systems should be extremely rare — they represent major architectural decisions. A new system requires an ADR.

Session action: Created during the dedicated Phase 2 migration session.

3.5 Capability

Trigger: Implementation planning begins for a cluster of related functionality within a system. A capability is created when you can answer: "What does this system need to be able to DO?" and the answer maps to a coherent group of future modules.

Anti-trigger: A capability that cannot be linked to at least one planned module. Abstract capabilities with no implementation path are speculative.

Examples:
- Signal Generation: Planning begins for the signal generation pipeline → CREATE
- "AI Reasoning": A vague capability with no concrete module plan → DO NOT CREATE

Session action: Created at the start of an implementation planning session, before module nodes.

3.6 Interface

Trigger: Two systems or capabilities need to communicate, and the contract between them must be defined before implementation. Interfaces are created BEFORE the modules that implement them.

Anti-trigger: An internal API within a single module. Internal APIs do not cross boundaries and do not warrant interface nodes.

Examples:
- Snapshot API: Data Pipeline → Trading Engine boundary → CREATE
- Internal helper function in Order Router: No boundary crossing → DO NOT CREATE

Session action: Created during capability planning or when a cross-system dependency is identified.

3.7 Module

Trigger: Code implementation begins for a specific code boundary. The module node is created WHEN the first file in the module is written, or when a detailed implementation plan is produced.

Anti-trigger: A module mentioned in the object hierarchy but with no implementation plan and no current coding need. It will be created when work begins.

Session action: Created at the start of a coding session that implements the module. The node is created BEFORE writing code, so it can be included in the context pack.

3.8 File

Trigger: A source file is created in the repository.

Anti-trigger: A planned file that does not yet exist. File nodes track ACTUAL files, not planned ones.

Session action: Created as part of the writeback step after a coding session (Context Pack Assembly Rules, Step 8: Writeback).

3.9 Test

Trigger: A test file is created in the repository.

Anti-trigger: Planned tests that do not yet exist. Test nodes track ACTUAL tests.

Session action: Created as part of the writeback step after a coding session.

3.10 Event

Trigger: An event-driven interaction is implemented in code. Events are created when the runtime event flow is being built, not speculatively.

Anti-trigger: Events listed in the object hierarchy but with no implementation timeline. They will be created when the event-driven architecture is implemented.

Session action: Created during coding sessions that implement event emission or consumption.

3.11 Artifact Schema

Trigger: A data shape is formally defined — either as a code artifact (JSON Schema, Pydantic model, protobuf) or as an interface contract component.

Anti-trigger: An informal data description in a wiki page. Wiki descriptions of data formats are knowledge, not engineering artifacts.

Session action: Created when defining an interface (the schema is part of the interface definition) or when implementing a module that produces/consumes structured data.

3.12 Workflow

Trigger: A multi-step process is formally defined with explicit states and transitions. The workflow exists as a state machine or pipeline definition, not as narrative prose.

Anti-trigger: A wiki description of a process ("the system does X then Y"). Wiki process descriptions are knowledge; dev_graph workflows are formal state machines.

Session action: Created during Phase 6 migration or when implementing workflow logic in code.

3.13 Gate

Trigger: A quality checkpoint is defined at a system or workflow boundary. The gate has specific artifacts it checks and specific predicates it evaluates.

Anti-trigger: An informal quality concern ("we should validate this"). Informal concerns become gates only when their predicates and blocking behavior are defined.

Session action: Created during Phase 6 migration or when implementing validation logic.

3.14 Predicate

Trigger: A boolean condition is formally defined as part of a gate or constraint. The predicate has a clear implementation location and a clear pass/fail definition.

Anti-trigger: An informal condition mentioned in a wiki page. Predicates are engineering artifacts with code implementations.

Session action: Created alongside the gate that checks them.

3.15 Agent

Trigger: An autonomous agent specification is produced with defined capabilities, skills, and constraints.

Anti-trigger: An informal mention of "the system could use an agent." Agent nodes require formal specifications.

Session action: Created during capability planning for systems that include agent actors.

3.16 Skill

Trigger: An agent's specific tool or capability is implemented.

Anti-trigger: A planned skill with no implementation path.

Session action: Created alongside agent implementation.

3.17 Decision Record (ADR)

Trigger: An architectural decision is made that affects system structure, capability design, or technology choice. Every significant "we chose X over Y" moment warrants an ADR.

Anti-trigger: Implementation details that don't affect architecture (e.g., "we used a list instead of a set"). These are code comments, not ADRs.

Session action: Created when the decision is made, during any session. ADRs are always timely — never backfilled weeks later.

3.18 Constraint

Trigger: A hard invariant is identified that MUST be enforced and that binds one or more systems, capabilities, or modules.

Anti-trigger: A soft preference or best practice. Constraints are hard rules, not suggestions.

Session action: Created when the invariant is identified, typically during risk analysis or governance review.

3.19 Governance, Observability, Reference, API Doc Source, Benchmark, Context Pack

These types are created as needed by their respective processes:
- Governance: When a new policy is established
- Observability: When a new dashboard is defined
- Reference: When a cross-graph pointer is needed
- API doc source: When a new external API is integrated
- Benchmark: When a repeatable performance measurement is conducted
- Context pack: On-demand at the start of each coding session

---

4. Population Order — Phased Roadmap

4.1 Strategic sequencing principle

Populate top-down along the containment hierarchy. Each layer provides context for the layer below. Populating modules before capabilities creates orphan nodes with no parent context. Populating capabilities before systems creates floating abstractions. Populating systems before architecture creates bounded contexts without structural grounding.

Exception: Knowledge assets and patterns are cross-cutting — they are populated alongside the layer they inform, not strictly before or after.

4.2 Phase 0: Governance Foundation

Timing: First dedicated session
Duration: Single session
Prerequisites: None

Deliverables:
1. Update CLAUDE.md with complete final ontology schema:
   - 24 type enum values
   - 17 relationship types
   - 23 directories
   - canonical_id universal field
   - evidence field with 7 values
   - confidence with 5 values
   - schema_version: "2.2.0"
   - Composes relationship definition
   - measures: [] for benchmark nodes
   - interface_version, schema_version for domain-specific nodes
   - Merge, split, deprecation procedures
   - Migration runbook template
   - Type-aware stale thresholds
   - 4 new lint checks
   - Closed-loop continuum documentation
   - 11-entry intent-aware routing table
2. Create 5 new empty directories: architecture/, systems/, capabilities/, interfaces/, events/
   (knowledge_assets/ and patterns/ also created)
3. Create ADR: "ADR - Ontology Redesign" (ADR-002)
4. Assign canonical_id to all 18 existing content nodes (GOV-001 through REF-003, etc.)
5. Update Neo4j Export Mapping with new types and canonical_id as primary key
6. Update Dev Graph Dashboard with new Dataview queries for new types
7. Log everything in log.md

Estimated node count after Phase 0: 19 (18 existing + 1 new ADR)

4.3 Phase 1: Architecture Skeleton + Knowledge Foundations

Timing: Second dedicated session
Duration: 1-2 sessions
Prerequisites: Phase 0 complete

Deliverables:
1. Architecture nodes (3):
   - Context Map (ARCH-001) — formal bounded context diagram showing 6 systems and their interactions
   - Runtime Topology (ARCH-002) — component interaction model with events, interfaces, data flows
   - Layer Model (ARCH-003) — formal L1 (data) → L2 (analysis) → L3 (execution) definition

2. Knowledge assets (8-12, co-created with architecture):
   - Event Sourcing (KA-001)
   - CQRS (KA-002)
   - Supervisor Pattern methodology (KA-003) — from OWS Dev Squad
   - Office Action methodology (KA-004) — from Syndicate Squad
   - Guardrail philosophy (KA-005) — defensive constraint design
   - Layer 2 design principles (KA-006) — snapshot-as-truth-layer
   - Context Engineering (KA-007) — token budget management
   - Agent Safety principles (KA-008) — from Anthropic guidance
   - Stateless Agent Architecture (KA-009) — file-based memory recovery
   - Paper Trading Validation (KA-010) — simulated validation before live
   Additional if warranted:
   - Walk-Forward Optimization methodology (KA-011)
   - Research Ingestion principles (KA-012)

3. Migrate existing Infrastructure Diagram to architecture/ (retype: reference → architecture)

Source for architecture nodes: Wiki pages Architecture Overview, Trading Engine Pipeline, Three-Layer Trading System, Claude-Assisted Trading Stack (read-only, referenced via source_paths).

Source for knowledge assets: Wiki concept pages, system pages, source documents (read-only).

Estimated node count after Phase 1: ~30-32

4.4 Phase 2: System Boundaries

Timing: Third dedicated session
Duration: 1 session
Prerequisites: Phase 1 complete

Deliverables:
1. System nodes (6):
   - Data Pipeline (SYS-001)
   - Trading Engine (SYS-002)
   - Risk Control (SYS-003)
   - Agent Runtime (SYS-004)
   - Evaluation Loop (SYS-005)
   - Supervisor Office (SYS-006)

2. System Lifecycle workflow (WF-001):
   Cold → Initialized → PaperTrading → Validated → Candidate → Production → Paused → Emergency → Archived

Each system node defines:
- Bounded context description
- Upstream/downstream system dependencies
- Contained capabilities (forward references to Phase 3)
- Source wiki pages

Estimated node count after Phase 2: ~38-40

4.5 Phase 3: Capabilities + Patterns

Timing: Fourth dedicated session (or spread across 2 sessions)
Duration: 2-3 sessions
Prerequisites: Phase 2 complete

Deliverables:
1. Capability nodes (~20, per audit_plan object hierarchy):

   Data Pipeline:
   - Market Scanning (CAP-001)
   - Feature Engineering (CAP-002)
   - Snapshot Assembly (CAP-003)

   Trading Engine:
   - Signal Generation (CAP-004)
   - Order Management (CAP-005)
   - Stop-Loss Management (CAP-006)
   - Position Tracking (CAP-007)

   Risk Control:
   - Guardrail Enforcement (CAP-008)
   - Exposure Tracking (CAP-009)

   Agent Runtime:
   - State Persistence (CAP-010)
   - Context Assembly (CAP-011)
   - Trade Logging (CAP-012)

   Evaluation Loop:
   - Performance Scoring (CAP-013)
   - Promotion Validation (CAP-014)

   Supervisor Office:
   - Decision Making (CAP-015)
   - Treasury Management (CAP-016)
   - Upgrade Evaluation (CAP-017)
   - Team Orchestration (CAP-018)

2. Pattern nodes (8-10):
   - Supervisor Pattern (PAT-001) — from KA-003
   - Guardrail Pattern (PAT-002) — from KA-005
   - Evaluation Loop Pattern (PAT-003) — from KA-010
   - Pipeline Pattern (PAT-004) — from KA-001 (Event Sourcing)
   - Event Sourcing Pattern (PAT-005) — from KA-001
   - Context Assembly Pattern (PAT-006) — from KA-007
   - Treasury Approval Pattern (PAT-007) — from KA-004
   - Promotion Pattern (PAT-008) — from KA-010
   - CQRS Pattern (PAT-009) — from KA-002
   - Multi-Agent Coordination Pattern (PAT-010) — from KA-003

3. Add realizes edges: each capability references the pattern(s) it follows.
4. Add Composes edges between patterns where applicable (e.g., Supervisor Pattern Composes Multi-Agent Coordination + Treasury Approval).

Estimated node count after Phase 3: ~68-72

4.6 Phase 4: Interfaces + Schemas

Timing: When implementation planning begins for cross-system communication
Duration: 2-3 sessions (can be spread across early development)
Prerequisites: Phase 3 complete for the relevant systems

Deliverables:
1. Priority interfaces (8):
   - Snapshot API (INT-001) — Data Pipeline → Trading Engine
   - Execution API (INT-002) — Trading Engine → Broker
   - Risk Check API (INT-003) — Risk Control → Trading Engine
   - Memory API (INT-004) — Agent Runtime → all systems
   - Trade Log API (INT-005) — Agent Runtime → all systems
   - Decision API (INT-006) — Supervisor Office → Trading Engine
   - Evaluation API (INT-007) — Evaluation Loop → Supervisor Office
   - Treasury API (INT-008) — Supervisor Office → internal

2. Priority schemas (6):
   - Layer 2 Snapshot Schema (SCHEMA-001)
   - Order Schema (SCHEMA-002)
   - Trade Log Schema (SCHEMA-003)
   - Decision Packet Schema (SCHEMA-004)
   - Evaluation Scorecard Schema (SCHEMA-005)
   - Treasury Policy Schema (SCHEMA-006)

Estimated node count after Phase 4: ~82-86

4.7 Phase 5: Implementation Nodes (ongoing)

Timing: During active development, continuously
Duration: Ongoing — the life of the project
Prerequisites: Relevant capability and interface nodes exist

Module, file, test, and agent nodes are created during coding sessions following the triggers defined in Section 3. This phase never "completes" — it grows with the codebase.

Cadence:
- Module node: created at the START of a coding session
- File and test nodes: created at the END of a coding session (writeback)
- Agent and skill nodes: created during agent implementation sessions

4.8 Phase 6: Quality Infrastructure (ongoing)

Timing: When validation logic is implemented
Duration: Ongoing
Prerequisites: Relevant module nodes exist

Gate, predicate, and workflow nodes are created when quality checkpoints and process definitions are implemented.

Priority order:
1. Trade Validation Gate + its predicates (Risk Control)
2. Paper Trading Promotion Gate + its predicates (Evaluation Loop)
3. Treasury Approval Gate + its predicate (Supervisor Office)
4. Trade Pipeline workflow
5. Office Action Loop workflow
6. Paper Trading Work Cycle workflow

4.9 Phase 7: Events (when event-driven architecture is implemented)

Timing: When runtime event flows are coded
Duration: Ongoing
Prerequisites: Relevant module nodes exist and emit/consume events

Event nodes are created ONLY when the event is implemented in code. Not before.

4.10 Phase 8: Benchmarks + Evaluation (when metrics exist)

Timing: When the system produces measurable performance data
Duration: Ongoing
Prerequisites: Running system with observable metrics

Benchmark nodes capture repeatable performance measurements. They reference the modules they measure (via measures: []).

---

5. Existing Wiki Migration Strategy

5.1 Migration principle

Wiki pages are NEVER moved to the dev_graph. They remain in the wiki as canonical knowledge. The dev_graph creates NEW engineering nodes that REFERENCE wiki pages via source_paths. This is extraction, not migration.

5.2 Wiki page classification

Every wiki page falls into one of three categories:

Category A — Produces dev_graph node(s): The wiki page contains engineering content that should be extracted into a formal engineering artifact.

Category B — Remains wiki-only: The wiki page contains domain knowledge that serves the dev_graph as context (via source_paths) but does not warrant its own node.

Category C — Already represented: The wiki page's engineering content is already captured by an existing or planned dev_graph node.

5.3 Complete wiki page mapping

Systems (6 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Architecture Overview | A | Context Map, Runtime Topology | architecture | 1 |
| Trading Engine Pipeline | A | Trade Pipeline workflow; feeds architecture nodes | workflow, architecture | 1, 6 |
| Three-Layer Trading System | A | Layer Model architecture; Layer 2 knowledge asset | architecture, knowledge_asset | 1 |
| Claude-Assisted Trading Stack | A | Context Map (technology layer) | architecture | 1 |
| LLM Failure Modes in Trading | B | Remains wiki — risk knowledge, not engineering artifact | — | — |
| Syndicate Squad Architecture | A | System: Supervisor Office; Knowledge Asset: Supervisor Pattern | system, knowledge_asset | 1, 2 |

Concepts (4 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| VWAP | B | Remains wiki — trading concept, not engineering principle | — | — |
| EMA Crossover | B | Remains wiki — trading concept | — | — |
| Relative Volume Filter | B | Remains wiki — trading concept | — | — |
| Options Trading | B | Remains wiki — trading concept | — | — |

Strategies (5 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| VWAP Crossover Strategy | B | Remains wiki — trading strategy, not engineering | — | — |
| Signal Confirmation | B | Remains wiki — trading methodology | — | — |
| Paper Trading | A | Knowledge Asset: Paper Trading Validation; feeds Capability: Promotion Validation | knowledge_asset | 1 |
| Wheel Strategy | B | Remains wiki — options strategy | — | — |
| Copy Trading Strategy | B | Remains wiki — trading strategy | — | — |

Execution (2 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Position Sizing | C | Feeds Capability: Order Management → Module: Position Sizer | capability, module | 3, 5 |
| Stop-Loss Systems | C | Feeds Capability: Stop-Loss Management → Module: Stop-Loss Manager | capability, module | 3, 5 |

Memory (2 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Agent Memory Architecture | A | Knowledge Asset: Stateless Agent Architecture; System: Agent Runtime | knowledge_asset, system | 1, 2 |
| Context Budget Engineering | A | Knowledge Asset: Context Engineering; Capability: Context Assembly | knowledge_asset, capability | 1, 3 |

Risk (2 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Autonomous Trading Risk Model | A | System: Risk Control; feeds constraint and predicate nodes | system, constraint, predicate | 2, 6 |
| Guardrail Architecture | A | Knowledge Asset: Guardrail Philosophy; Pattern: Guardrail Pattern; Capability: Guardrail Enforcement | knowledge_asset, pattern, capability | 1, 3 |

Backtesting (3 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Walk-Forward Optimization | A | Knowledge Asset: Walk-Forward Optimization methodology | knowledge_asset | 1 |
| Overfitting Detection | B | Remains wiki — methodology knowledge | — | — |
| Backtesting Methodology | B | Remains wiki — methodology knowledge (feeds knowledge asset if warranted) | — | — |

Agents (4 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Supervisor Decision Engine | A | Capability: Decision Making; Agent: Supervisor Agent | capability, agent | 3, 5 |
| Multi-Agent Orchestration | A | Pattern: Multi-Agent Coordination; Knowledge Asset source | pattern, knowledge_asset | 1, 3 |
| Stateless Agent Recovery | C | Feeds Knowledge Asset: Stateless Agent Architecture | knowledge_asset | 1 |
| Agent Self-Verification | B | Remains wiki — AI capability description | — | — |

Infrastructure (4 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Claude Code | B | Remains wiki — tooling description, not engineering artifact | — | — |
| Claude Routines | B | Remains wiki — tooling description | — | — |
| Claude Co-work | B | Remains wiki — tooling description | — | — |
| Railway Deployment | B | Remains wiki — deployment platform description | — | — |

Integrations (7 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Alpaca API | C | Already represented → api_doc_source: Alpaca API Docs | — | existing |
| TradingView Integration | B | Remains wiki — integration description (potential future interface node) | — | — |
| Exchange API Integration | B | Remains wiki — integration description | — | — |
| Perplexity API | B | Remains wiki — tooling description | — | — |
| MCP Architecture | A | Knowledge Asset: Context Engineering (MCP as integration pattern) | knowledge_asset | 1 |
| Webhook Architecture | B | Remains wiki — integration pattern description | — | — |
| Capital Trades Integration | B | Remains wiki — data source description | — | — |

Security (2 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| API Credential Isolation | A | Constraint: API Credential Isolation (hard invariant) | constraint | 2 |
| Environment Variable Management | B | Remains wiki — operational procedure | — | — |

Governance (3 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Trade Logging | C | Feeds Capability: Trade Logging → Module: Trade Logger | capability, module | 3, 5 |
| Treasury Policy System | A | Capability: Treasury Management; Constraint: Treasury Burn Rule; Schema: Treasury Policy Schema | capability, constraint, schema | 3, 4 |
| Metadata Migration Plan | C | Already represented → REF - Wiki Metadata Migration Plan | — | existing |

Workflows (1 page):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Office Action Loop | A | Workflow: Office Action Loop; Knowledge Asset: Office Action methodology | workflow, knowledge_asset | 1, 6 |

Research (1 page):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Research Ingestion Workflow | B | Remains wiki — methodology (potential knowledge asset if principle is reused) | — | — |

Sources (9 pages):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| All SRC - pages | B | Remain wiki — knowledge provenance. Referenced via source_paths on dev_graph nodes. | — | — |

Glossary (1 page):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Glossary | B | Remains wiki — term definitions | — | — |

Observability (1 page):

| Wiki Page | Category | Dev_graph Extraction | Type(s) | Phase |
|-----------|----------|---------------------|---------|-------|
| Graph Health Dashboard | C | Already represented → REF - Wiki Graph Health Dashboard | — | existing |

5.4 Migration summary

| Category | Count | Action |
|----------|-------|--------|
| A — Produces dev_graph nodes | 18 pages | Extract engineering artifacts into dev_graph nodes |
| B — Remains wiki-only | 29 pages | No action; referenced via source_paths when relevant |
| C — Already represented | 10 pages | No action; existing dev_graph nodes or planned nodes cover the content |
| Total | 57 pages | |

5.5 Migration rules

1. NEVER copy wiki prose into dev_graph nodes. Extract engineering content only.
2. ALWAYS add the wiki page to the dev_graph node's source_paths.
3. A single wiki page may produce MULTIPLE dev_graph nodes (e.g., Guardrail Architecture → knowledge_asset + pattern + capability).
4. MULTIPLE wiki pages may feed a SINGLE dev_graph node (e.g., Architecture Overview + Trading Engine Pipeline + Three-Layer Trading System → Context Map architecture node).
5. Do NOT create a dev_graph node for every wiki page. Only Category A pages produce nodes.
6. Review each wiki page's "Architecture Role" and "Implementation Notes" sections. If these sections contain content that isn't in the dev_graph, that content should be extracted. If they contain only general knowledge, the page remains wiki-only.
7. After extraction, the wiki page is NOT modified. The dev_graph references the wiki; the wiki is unaware of the dev_graph.

---

6. Layer 2 Integration Strategy

6.1 What is Layer 2

Layer 2 is the Strategy Engine / deterministic analysis layer in the Three-Layer Trading System. It produces snapshots — point-in-time analytical assessments that serve as the single source of truth for the execution layer (Layer 3).

6.2 Layer 2 objects and their ontology classification

| Layer 2 Object | Ontology Classification | Ontology Type | Rationale |
|----------------|------------------------|---------------|-----------|
| Layer 2 design principles | Knowledge origin | knowledge_asset (KA-006) | WHY snapshots exist and why they are deterministic |
| Snapshot data contract | Interface contract | interface (INT-001: Snapshot API) | HOW systems communicate snapshot data |
| Snapshot data shape | Data definition | artifact_schema (SCHEMA-001) | WHAT a snapshot contains |
| Snapshot assembly process | Abstract behavior | capability (CAP-003: Snapshot Assembly) | WHAT the system does |
| Snapshot builder | Code boundary | module (when code exists) | HOW snapshots are built |
| Individual snapshots | Runtime instance | PostgreSQL record | NOT an ontology object — high volume |
| Snapshot validation | Quality check | gate + predicate (when implemented) | WHAT must be true |
| Snapshot creation signal | Runtime event | event (EVT: SnapshotCreated) | WHEN it happens |

6.3 Boundary rules

What becomes an ontology node:
- The design principle (knowledge_asset): created in Phase 1
- The communication contract (interface): created in Phase 4
- The data shape (schema): created in Phase 4
- The assembly capability (capability): created in Phase 3
- The builder module (module): created in Phase 5 when code is written
- The creation event (event): created in Phase 7 when event flow is implemented

What remains runtime data:
- Individual snapshot records → PostgreSQL
- Snapshot metadata (timestamp, version) → database columns
- Snapshot content (indicators, scores, signals) → database JSON columns
- Snapshot history (all snapshots for a symbol) → database time series

What remains wiki knowledge:
- Three-Layer Trading System page → knowledge synthesis
- Trading Engine Pipeline page → process narrative

6.4 The Layer 2 Snapshot Schema as foundational data contract

The Layer 2 Snapshot Schema (SCHEMA-001) is the most important schema in the ontology. Everything downstream (signal generation, execution, risk validation) consumes snapshots. Changes to this schema are breaking changes that cascade through the entire pipeline.

Governance:
- The schema node MUST have `schema_version` (domain-specific field)
- Changes require an ADR
- The schema is the primary consumer of the Snapshot API interface
- All downstream modules that consume snapshots MUST list SCHEMA-001 in their Consumes relationship section

---

7. Code-Driven Population Strategy

7.1 Principle

Every significant code artifact should have a corresponding dev_graph node. "Significant" means: a code boundary that warrants independent tracking, testing, or governance. Individual utility functions do not warrant nodes. Packages, modules, and test suites do.

7.2 Automated triggers during coding sessions

When a coding session creates or modifies code, the following dev_graph actions are triggered:

| Code Action | Dev_graph Action | Node Type | Trigger |
|-------------|-----------------|-----------|---------|
| Create new Python package | Create module node | module | Package init + at least one substantive file |
| Create new source file | Create file node | file | File created in repository |
| Create new test file | Create test node | test | Test file created in repository |
| Define new API endpoint | Create or update interface node | interface | Endpoint defined with input/output contract |
| Define new data class/schema | Create schema node | artifact_schema | Formal data shape defined (Pydantic, dataclass, JSON Schema) |
| Add new event emission | Create event node | event | Event emitted across system boundary |
| Add new validation gate | Create gate node | gate | Validation checkpoint with predicates |
| Run performance benchmark | Create benchmark node | benchmark_result | Repeatable measurement with quantitative results |
| Make architecture decision | Create ADR | decision_record | Significant "we chose X over Y" decision |
| Discover constraint | Create constraint node | constraint | Hard invariant identified |

7.3 Session writeback protocol

At the end of every coding session that creates or modifies code:

1. Identify all new/modified files
2. For each new file: create file node (if substantive) or update parent module node
3. For each new test: create test node
4. Update implementation_status on affected module/capability nodes
5. Update the evidence field on affected nodes (evidence: [code])
6. Log session in dev_graph/log.md
7. Run lint checks on touched nodes

7.4 Automation opportunities

Near-term (manual with guidance): Claude follows the writeback protocol above at the end of each session. The protocol is documented in Context Pack Assembly Rules (writeback section).

Medium-term (semi-automated): A post-session script scans the repository for new/modified files and proposes dev_graph node creation. Claude reviews and approves.

Long-term (automated): A CI/CD hook on repository pushes triggers dev_graph node creation for new files. Module-level and above nodes still require manual creation (they represent design decisions, not just file existence).

7.5 The file node threshold

Not every source file needs a file node. Threshold rules:

CREATE a file node when:
- The file is a primary implementation file (e.g., order_router.py)
- The file defines a public API
- The file is a test file
- The file is a schema definition file
- The file is a configuration file that affects system behavior

DO NOT create a file node when:
- The file is a boilerplate file (__init__.py with only imports)
- The file is auto-generated
- The file is a utility with no public interface
- The file is a third-party vendored dependency

---

8. Continuous Maintenance Strategy

8.1 Per-coding-session (every session that modifies dev_graph)

Duration: 5-10 minutes at session end
Scope: Nodes touched in the session

| Check | Action |
|-------|--------|
| Writeback | Create/update file and test nodes for new/modified code |
| Lint (touched nodes) | Run all 11 lint checks on nodes created or modified in this session |
| Status update | Update implementation_status on affected nodes |
| Evidence update | Add evidence types to nodes whose basis changed |
| Log entry | Append timestamped session summary to dev_graph/log.md |
| Orphan check | Verify new nodes have >=1 inbound wikilink |

8.2 Weekly (every 7 days)

Duration: 15-30 minutes
Scope: All dev_graph nodes
Trigger: First session of the week

| Check | Action |
|-------|--------|
| Full lint | Run all 11 lint checks across all nodes |
| Dashboard review | Review Dev Graph Dashboard — check stale, orphan, blocked, deprecated counts |
| Type distribution | Verify type distribution matches expectations (no single type dominates unexpectedly) |
| Confidence audit | Check for nodes with stale confidence (confidence not reviewed in >60 days per type threshold) |
| Cross-reference | Verify wikilinks to wiki pages still resolve (wiki pages not renamed or deleted) |
| Neo4j sync | If Neo4j is active, run sync_to_neo4j.py |

8.3 Monthly (first session of each month)

Duration: 30-60 minutes
Scope: Full ontology audit
Trigger: First session of the calendar month

| Check | Action |
|-------|--------|
| Ontology audit | Review type distribution, relationship density, orphan rate, duplicate rate |
| API doc freshness | Check api_doc_source nodes for freshness (external docs may have updated) |
| Constraint review | Review all constraint nodes — are they still relevant? Any new constraints needed? |
| Schema drift | Check 3-5 random nodes for type-content alignment (lint check 8) |
| Pattern review | Are any patterns underused? Are new patterns emerging from recent implementations? |
| Knowledge asset review | Are knowledge assets still accurate? Any new principles worth capturing? |
| KPI measurement | Calculate population metrics (Section 9) and record in log.md |

8.4 Quarterly (every 3 months)

Duration: 1-2 hours
Scope: Strategic review
Trigger: Every 3 months

| Check | Action |
|-------|--------|
| Architecture alignment | Does the dev_graph still accurately represent the system architecture? Have architectural decisions been made that aren't reflected? |
| Capability completeness | For each system, are all active capabilities represented? |
| Traceability check | Select 3 random modules and trace them up to knowledge assets. Is the chain complete? |
| Population progress | Compare actual node counts to the roadmap expectations. Is population on track? |
| Stopping rule check | Is the ontology growing too fast? Is the maintenance burden proportional to the value? |
| Schema version review | Should the schema version be bumped? Any breaking changes needed? |

8.5 Annual (once per year)

Duration: Half day
Scope: Full strategic review
Trigger: Annually

| Check | Action |
|-------|--------|
| Full traceability audit | Trace every module to its knowledge asset origin. Identify gaps. |
| Ontology health assessment | Is the ontology still serving its purpose? Is Graph-RAG retrieval effective? |
| Maintenance cost assessment | How much time is spent on ontology maintenance vs. value delivered? |
| Technology review | Is Obsidian/markdown still the right substrate? Should more weight shift to Neo4j? |
| Schema evolution review | Any structural changes needed for the next year? |

---

9. Population Metrics — Governance KPIs

9.1 Coverage metrics

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| Architecture coverage | Architecture nodes / expected architecture nodes (3) | 100% after Phase 1 | Count of architecture type nodes |
| System coverage | System nodes / expected system nodes (6) | 100% after Phase 2 | Count of system type nodes |
| Capability coverage | Capability nodes / expected capability nodes (~20) | 100% after Phase 3 | Count of capability type nodes |
| Interface coverage | Interface nodes / cross-system boundaries (~8) | 100% after Phase 4 | Count of interface type nodes |
| Module coverage | Module nodes / code packages in repository | Grows with code | Module count / package count |
| File coverage | File nodes / significant source files | Grows with code | File node count / source file count (excl. boilerplate) |
| Test coverage (ontology) | Module nodes with related_tests populated / total module nodes | >80% | Dataview query |
| Knowledge coverage | Knowledge assets / identified engineering principles | >80% after Phase 1 | Count of knowledge_asset nodes vs. identified principles |
| Pattern coverage | Pattern nodes / identified reusable patterns | >80% after Phase 3 | Count of pattern nodes vs. observed patterns |
| ADR linkage | Capabilities with justified_by edges / total capabilities | >90% | Dataview query |

9.2 Quality metrics

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| Orphan rate | Nodes with 0 inbound links / total nodes | <5% | Dashboard query #7 |
| Stale rate | Nodes past stale threshold / total nodes | <10% | Dashboard query #6 (type-aware) |
| Duplicate rate | Known duplicates / total nodes | 0% | Manual audit |
| Frontmatter completeness | Nodes with all required fields / total nodes | 100% | Dashboard query #2 |
| Canonical ID coverage | Nodes with canonical_id / total nodes | 100% | Dataview query |
| Evidence coverage | Nodes with evidence: [] populated / total nodes (excl. legacy) | >70% | Dataview query |
| Constraint coverage | Module/file nodes with related_constraints / total module+file nodes | >80% | Dashboard query #8 |

9.3 Structural metrics

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| Graph density | Total wikilinks / total nodes | >5 (same as wiki) | Obsidian graph stats |
| Traceability completeness | Modules traceable to knowledge assets (full chain) / total modules | >80% | Manual or Neo4j query |
| Pattern reuse | Modules/capabilities with realizes edges / total modules+capabilities | >40% | Dataview query |
| Connectivity | Average inbound + outbound links per node | >4 | Obsidian graph stats |
| Hub saturation | Architecture/system/governance nodes with >10 inbound links | All hub nodes | Dataview query |

9.4 Operational metrics

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| Context pack efficiency | Average nodes in context pack / total nodes retrieved before filtering | >60% | Session logs |
| Retrieval precision | Nodes used by session / nodes in context pack | >70% | Session logs |
| Maintenance time | Minutes spent on lint/maintenance per session | <10 min | Self-reported |
| Population velocity | New content nodes per week (rolling 4-week average) | Track only | Log analysis |

9.5 Recommended dashboard

Extend the existing Dev Graph Dashboard with the following additional Dataview queries:

```
## 13. Canonical ID Coverage
Dataview: TABLE type, canonical_id FROM "dev_graph"
WHERE type != null AND (canonical_id = null OR canonical_id = "")

## 14. Evidence Coverage
Dataview: TABLE type, evidence FROM "dev_graph"
WHERE type != null AND (evidence = null OR length(evidence) = 0)
SORT type ASC

## 15. Pattern Realization Coverage
Dataview: TABLE type, file.name FROM "dev_graph"
WHERE (type = "module" OR type = "capability")
AND NOT contains(file.content, "### Realizes")

## 16. Traceability Gaps (Capabilities without justified_by)
Dataview: TABLE file.name, type FROM "dev_graph"
WHERE type = "capability"
AND NOT contains(file.content, "### Justified By")

## 17. Population Progress
Dataview: TABLE length(rows) AS Count FROM "dev_graph"
WHERE type != null
GROUP BY type
SORT length(rows) DESC
```

---

10. Population Stopping Rules

10.1 The stopping principle

The dev_graph should represent exactly the engineering knowledge needed for autonomous Claude-assisted development. Not more, not less. Every node must earn its existence by providing retrieval value to coding sessions.

10.2 When a concept should NOT become a dev_graph node

| Condition | Action | Rationale |
|-----------|--------|-----------|
| The concept is domain knowledge with no engineering implication | Stays in wiki | Knowledge concepts (VWAP, EMA) inform trading, not engineering |
| The concept is a one-off implementation detail | Code comment or inline docs | Not reused, not referenced, not worth the governance overhead |
| The concept duplicates an existing node | Update existing node | Canonical ownership — one concept, one node |
| The concept is speculative with no implementation timeline | Do not create | No speculative nodes — wait for a trigger |
| The concept describes HOW a tool works, not how WE use it | Stays in wiki | Claude Code, Railway, Alpaca are tools; our engineering is in how we use them |
| The concept's content would be entirely "TBD" | Do not create | No empty nodes — wait for substantive content |
| The concept has no relationship to any other dev_graph node | Do not create | Orphan nodes reduce retrieval quality |
| The concept is already fully expressed by its parent node | Do not create | Avoid unnecessary hierarchy depth |

10.3 Over-modeling detection signals

The ontology is over-modeled when any of the following is true:

| Signal | Threshold | Response |
|--------|-----------|----------|
| Node count grows faster than code | >3 nodes per source file | Audit: are nodes providing value or just tracking artifacts? |
| Maintenance time exceeds coding time | >30% of session on ontology | Reduce maintenance scope; shift lint to weekly |
| Orphan rate exceeds target | >10% of nodes have 0 inbound links | Stop creating nodes; focus on connecting existing ones |
| Context packs retrieve <50% useful nodes | Precision <50% | Audit node quality; prune or merge low-value nodes |
| Stale rate exceeds target | >20% of nodes past stale threshold | Batch deprecation sweep; reduce population velocity |
| More governance nodes than content nodes | governance type count > implementation type count | Stop adding governance; focus on content |

10.4 Ontology size targets

| Phase | Expected Node Count | Max Acceptable | If Exceeded |
|-------|--------------------|--------------------|-------------|
| Phase 0 (governance) | ~19 | 25 | Governance bloat — consolidate |
| Phase 1 (architecture + knowledge) | ~30-32 | 40 | Knowledge asset proliferation — enforce trigger rules |
| Phase 2 (systems) | ~38-40 | 45 | System over-decomposition — merge similar systems |
| Phase 3 (capabilities + patterns) | ~68-72 | 85 | Capability granularity too fine — merge related capabilities |
| Phase 4 (interfaces + schemas) | ~82-86 | 100 | Interface over-specification — are internal APIs being modeled? |
| Phase 5+ (ongoing) | Grows with code | 200 | Consider shifting complex queries to Neo4j |
| Hard ceiling | — | 300 | Ontology federation or substrate migration review |

10.5 Annual stopping rule review

Once per year, answer these questions:

1. If we deleted every node created in the last 12 months, would Claude's coding sessions be measurably worse?
2. Are there nodes that no context pack has referenced in the last 6 months?
3. Is the dev_graph helping Claude write better code, or is it consuming attention that should go to writing code?

If the answer to #1 is "no," the ontology has stopped providing value and should be frozen. If #2 identifies unused nodes, they should be deprecated. If #3 reveals attention drain, reduce maintenance cadence and simplify the population protocol.

---

11. Recommended Implementation Order — Executive Summary

| Step | Phase | Duration | Nodes Created | Cumulative |
|------|-------|----------|---------------|------------|
| 1 | Phase 0: Governance update | 1 session | 1 (ADR-002) | ~19 |
| 2 | Phase 1: Architecture + Knowledge | 1-2 sessions | ~12-14 | ~31-33 |
| 3 | Phase 2: System boundaries | 1 session | ~7 | ~38-40 |
| 4 | Phase 3: Capabilities + Patterns | 2-3 sessions | ~28-30 | ~68-72 |
| 5 | Phase 4: Interfaces + Schemas | 2-3 sessions | ~14 | ~82-86 |
| 6 | Phase 5+: Implementation (ongoing) | Continuous | Grows with code | ~100-200 |
| 7 | Phase 6: Quality infrastructure | As needed | ~10-15 | ~110-215 |
| 8 | Phase 7: Events | When event architecture is built | ~15-20 | ~125-235 |
| 9 | Phase 8: Benchmarks | When metrics exist | ~5-10 | ~130-245 |

Critical path: Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5+

Phases 6-8 are ongoing and parallel to Phase 5+ implementation work. They do not block each other.

The first four phases (0-3) constitute the structural skeleton — approximately 70 nodes that define the full architectural context for all future development. These should be completed in 5-8 dedicated sessions before significant coding begins. Phase 4 can overlap with early Phase 5 coding.

After Phase 4, population is entirely code-driven — nodes are created as code is written, following the triggers and writeback protocol defined in this document. There are no more "dedicated ontology sessions." The ontology grows organically alongside the codebase.

---

End of Dev Graph Population Strategy and Execution Roadmap.
