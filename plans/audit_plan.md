Dev Graph Ontology Redesign                                      

  ---                                                                                                                                                                                                   
  1. Critique of Previous Expansion Proposal
                                                                                                                                                                                                        
  The previous proposal suffers from ten structural weaknesses:

  1.1 Document-centric design. The proposal maps wiki pages to dev_graph nodes almost 1:1. "System Architecture Boundary" is "Architecture Overview" with a different name. "Guardrail Engine" is
  "Guardrail Architecture" dressed as a module. This creates a typed shadow of the wiki, not an independent engineering ontology.

  1.2 No hierarchy. 37 flat nodes with no containment structure. A module has no formal relationship to the system it belongs to. The graph has no natural navigation path from general to specific.

  1.3 Missing abstractions. No interfaces (API contracts between boundaries), no events (runtime signals), no capabilities (abstract behaviors), no formal system boundaries. The proposal jumps
  straight from wiki concepts to implementation modules, skipping the architectural layers that make engineering ontologies useful.

  1.4 Redundancy within the proposal itself. Guardrail Engine (module) + Guardrail Gate (gate) + Position Size OK Predicate + Daily Loss Cap OK Predicate + Withdrawal Disabled Predicate all describe
  parts of risk validation, but without a unifying system or capability node. The graph has no concept of "these things belong together."

  1.5 Poor Graph-RAG retrieval. Flat structure means semantic search returns many loosely related nodes. For "implement execution engine," a flat graph returns the Execution Engine module but also
  Position Sizing Module, Stop-Loss Module, Guardrail Gate, Execution Gate, and several predicates — all at equal graph distance, with no way to scope retrieval to just the execution concern.

  1.6 Tight wiki coupling. Node names derive from wiki page names. If wiki pages are renamed or merged, dev_graph nodes would need corresponding updates. The dev_graph should be structurally
  independent of the wiki.

  1.7 No runtime model. The proposal describes what to build but not how components interact at runtime. There is no formal representation of data flow, event propagation, or inter-system
  communication.

  1.8 No interface contracts. Modules have no formal input/output contracts. It is unclear how the Snapshot Consumer connects to the Feature Builder, or what data format flows between them. The
  interfaces between modules are implicit and undocumented.

  1.9 Premature specificity without structure. Creating 37 nodes without a containment hierarchy means the graph will become unnavigable before it becomes useful. At 100+ nodes the flat model
  collapses entirely.

  1.10 Layer 2 as afterthought. The Layer 2 snapshot system — the deterministic truth layer — is treated as just another wiki concept to mirror, rather than as the foundational data contract that
  drives the entire pipeline. The proposal creates a "Layer 2 Snapshot Schema" node but doesn't model the architectural significance of L2 as a system boundary.

  ---
  2. New Ontology Proposal

  Design Principle

  The dev_graph becomes a semantic engineering graph with explicit hierarchy:

  Architecture → System → Capability → Module → File
                                     → Interface → Schema
                                     → Workflow → Event
                                                → Gate → Predicate

  Instead of mirroring wiki narratives, the dev_graph models engineering primitives that exist independently of how the wiki describes them.

  Type Hierarchy (22 types)

  Structural types — define what the system IS:

  ┌──────────────┬─────────────────────────────────────────────────────────────────────┬────────────────────────────┐
  │     Type     │                               Purpose                               │     Abstraction Level      │
  ├──────────────┼─────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ architecture │ Canonical engineering artifact (context map, topology, layer model) │ Highest — entire system    │
  ├──────────────┼─────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ system       │ Bounded context / major system boundary                             │ High — subsystem           │
  ├──────────────┼─────────────────────────────────────────────────────────────────────┼────────────────────────────┤
  │ capability   │ Abstract behavior a system provides                                 │ Mid-high — feature cluster │
  └──────────────┴─────────────────────────────────────────────────────────────────────┴────────────────────────────┘

  Implementation types — define HOW it's built:

  ┌───────────┬─────────────────────────────────────────────────┬───────────────────┐
  │   Type    │                     Purpose                     │ Abstraction Level │
  ├───────────┼─────────────────────────────────────────────────┼───────────────────┤
  │ module    │ Concrete implementation boundary (code package) │ Mid — code        │
  ├───────────┼─────────────────────────────────────────────────┼───────────────────┤
  │ interface │ API contract between systems/modules            │ Mid — contract    │
  ├───────────┼─────────────────────────────────────────────────┼───────────────────┤
  │ file      │ Individual source file                          │ Low — file        │
  ├───────────┼─────────────────────────────────────────────────┼───────────────────┤
  │ test      │ Test file or suite                              │ Low — file        │
  └───────────┴─────────────────────────────────────────────────┴───────────────────┘

  Behavioral types — define WHEN/HOW things happen:

  ┌──────────┬─────────────────────────────────────────┬───────────────────┐
  │   Type   │                 Purpose                 │ Abstraction Level │
  ├──────────┼─────────────────────────────────────────┼───────────────────┤
  │ workflow │ Multi-step process, state machine       │ Mid — process     │
  ├──────────┼─────────────────────────────────────────┼───────────────────┤
  │ event    │ Domain event (boundary-crossing signal) │ Mid — signal      │
  └──────────┴─────────────────────────────────────────┴───────────────────┘

  Data types — define WHAT data looks like:

  ┌─────────────────┬───────────────────────┬───────────────────┐
  │      Type       │        Purpose        │ Abstraction Level │
  ├─────────────────┼───────────────────────┼───────────────────┤
  │ artifact_schema │ Data shape definition │ Mid — contract    │
  └─────────────────┴───────────────────────┴───────────────────┘

  Quality types — define WHAT MUST be true:

  ┌───────────┬────────────────────────────────┬───────────────────┐
  │   Type    │            Purpose             │ Abstraction Level │
  ├───────────┼────────────────────────────────┼───────────────────┤
  │ gate      │ Quality checkpoint at boundary │ Mid — validation  │
  ├───────────┼────────────────────────────────┼───────────────────┤
  │ predicate │ Boolean condition              │ Low — check       │
  └───────────┴────────────────────────────────┴───────────────────┘

  Agent types — define WHO does the work:

  ┌───────┬────────────────────────────────┬───────────────────┐
  │ Type  │            Purpose             │ Abstraction Level │
  ├───────┼────────────────────────────────┼───────────────────┤
  │ agent │ Autonomous agent specification │ Mid — actor       │
  ├───────┼────────────────────────────────┼───────────────────┤
  │ skill │ Agent capability               │ Low — tool        │
  └───────┴────────────────────────────────┴───────────────────┘

  Meta types — governance infrastructure:

  ┌──────────────────┬──────────────────────────────┐
  │       Type       │           Purpose            │
  ├──────────────────┼──────────────────────────────┤
  │ decision_record  │ Architecture Decision Record │
  ├──────────────────┼──────────────────────────────┤
  │ constraint       │ Hard invariant               │
  ├──────────────────┼──────────────────────────────┤
  │ governance       │ Policy document              │
  ├──────────────────┼──────────────────────────────┤
  │ reference        │ Pointer to external artifact │
  ├──────────────────┼──────────────────────────────┤
  │ api_doc_source   │ API documentation reference  │
  ├──────────────────┼──────────────────────────────┤
  │ context_pack     │ Assembled context for coding │
  ├──────────────────┼──────────────────────────────┤
  │ observability    │ Dashboard / monitoring       │
  ├──────────────────┼──────────────────────────────┤
  │ benchmark_result │ Performance measurement      │
  └──────────────────┴──────────────────────────────┘

  New types (5 additions to existing 17):
  - system — not equivalent to module. A system is a bounded context containing multiple capabilities; a module is a single code boundary.
  - capability — not equivalent to module. A capability defines WHAT the system can do; a module defines HOW it does it. A capability may be implemented by multiple modules.
  - architecture — not equivalent to governance. Governance defines rules; architecture defines structure.
  - interface — not equivalent to artifact_schema. A schema defines data shape; an interface defines behavioral contract including input schema, output schema, invariants, and error modes.
  - event — not equivalent to workflow. A workflow defines a process; an event is a signal that crosses system boundaries. Events trigger workflows; workflows emit events.

  ---
  3. New Top-Level Directory Structure

  /dev_graph
    /architecture       — context maps, runtime topology, layer models
    /systems            — bounded contexts (6 systems)
    /capabilities       — abstract capabilities (~20)
    /interfaces         — API contracts between boundaries
    /events             — domain events (boundary-crossing signals)
    /modules            — implementation modules (code boundaries)
    /schemas            — data shape definitions
    /workflows          — process definitions, state machines
    /files              — source file nodes
    /tests              — test nodes
    /gates              — quality checkpoints
    /predicates         — boolean conditions
    /agents             — agent specifications
    /skills             — agent capabilities
    /decisions          — ADRs
    /constraints        — hard invariants
    /api_docs           — API documentation sources
    /context_packs      — assembled context for coding
    /observability      — dashboards and monitoring
    /governance         — governance policies
    /benchmarks         — performance records

  21 directories (16 existing + 5 new). The existing 16 are unchanged. Five new directories are added.

  Domain-by-domain justification for new directories

  architecture/

  - Purpose: Canonical engineering artifacts that define the system's structural shape. Not wiki summaries — formal diagrams and models that serve as the root context for any engineering session.
  - Ontology role: Root level. Architecture nodes are the starting point for understanding the entire system. A Context Map shows bounded contexts and their relationships. A Runtime Topology shows
  component interactions. A Layer Model defines the architectural layers.
  - Distinction from wiki: Wiki's "Architecture Overview" is a narrative synthesis that explains the system to humans. An Architecture Context Map is a formal engineering artifact that defines system
  boundaries for machines. The wiki describes; the dev_graph defines.
  - Interaction with existing nodes: Architecture nodes contain (reference) all System nodes. System nodes reference their position in the Architecture. Every engineering session can start by reading
  the Context Map to understand scope.
  - Long-term maintainability: Very low churn. Architecture changes are rare and significant. 3-4 nodes maximum, each updated only on major structural decisions.
  - Graph-RAG benefits: HIGH. When Claude starts a coding session, the Context Map provides immediate structural context: "This module belongs to the Execution System, which communicates with the Risk
   System via the Risk Check Interface." This eliminates guesswork about where code fits.
  - Implementation cost: Low. 3 initial nodes: Context Map, Runtime Topology, Layer Model.
  - Decision: ACCEPT. The Infrastructure Diagram (existing root-level reference node) would migrate here and be refactored into formal architecture artifacts.

  systems/

  - Purpose: Bounded contexts — the major system boundaries within the product.
  - Ontology role: Primary decomposition level. Systems are the largest grouping of implementation artifacts. Each system owns a set of capabilities, which own modules.
  - Distinction from wiki: Wiki has 6 pages in systems/ that are narrative descriptions mixing architecture, implementation, and knowledge synthesis. Dev_graph system nodes define formal bounded
  contexts with explicit inputs, outputs, upstream/downstream dependencies, and contained capabilities.
  - Interaction with existing nodes: System nodes contain Capability nodes. Capability nodes contain Module nodes. Constraints bind to Systems. Decisions affect Systems.
  - Long-term maintainability: Low churn. System boundaries change only on major architectural decisions. ~6 initial nodes.
  - Graph-RAG benefits: HIGH. Systems provide scope filtering. When working on execution code, Claude can scope to "Execution System" and retrieve only relevant capabilities, modules, interfaces, and
  tests. This eliminates cross-concern noise.
  - Implementation cost: Low. 6 system nodes, each with clear bounded context definition.
  - Decision: ACCEPT. Systems are the primary navigation entry point after architecture.

  capabilities/

  - Purpose: Abstract behaviors that systems provide. The bridge between "what the system does" and "how it's implemented."
  - Ontology role: Intermediate grouping between Systems and Modules. A capability defines a coherent cluster of related functionality.
  - Distinction from wiki: Wiki doesn't have capability as a concept. Capabilities are pure engineering abstractions derived from analyzing what the system needs to do. "Signal Generation" is a
  capability — not a wiki page, not a module, but a named behavior.
  - Interaction with existing nodes: Capabilities belong to Systems. Modules implement Capabilities. Agents implement Capabilities. Interfaces are defined at the Capability level.
  - Long-term maintainability: Medium churn. Capabilities change when product scope changes, but they're more stable than modules. ~20 initial nodes.
  - Graph-RAG benefits: MEDIUM-HIGH. Capabilities answer "I need to implement signal generation" — they scope retrieval to the right cluster of modules, interfaces, and schemas without being so
  specific that you miss dependencies.
  - Implementation cost: Medium. ~20 capability nodes, each requiring careful decomposition.
  - Decision: ACCEPT. Without capabilities, the system → module hierarchy has only two levels. With 40+ eventual modules, an intermediate grouping is essential for navigability. The alternative — a
  capability field on module nodes — loses the ability to formally define what a capability IS, what its interface IS, and what it contains.

  interfaces/

  - Purpose: Stable API contracts between system boundaries and between capabilities.
  - Ontology role: Define the contracts that modules must implement. Interfaces are MORE than schemas — they include behavioral specifications, invariants, and error modes.
  - Distinction from wiki: Wiki has no interface concept. Interfaces are pure engineering artifacts that emerge from system decomposition.
  - Interaction with existing nodes: Capabilities define Interfaces. Modules implement Interfaces. Interfaces reference Schemas (for input/output data shapes). Interfaces are more stable than modules
  — changing an interface is a breaking change; changing a module's internals is not.
  - Long-term maintainability: LOW churn. Interfaces change less than modules by design. That's their purpose — they provide stability at boundaries. ~8-12 initial nodes.
  - Graph-RAG benefits: HIGH. When implementing a module, Claude needs to know what interface it must satisfy. Interfaces answer "what does this module need to accept and return?" without coupling to
  implementation details. When two teams (or two Claude sessions) work on different sides of an interface, the interface node is the contract they agree on.
  - Implementation cost: Medium. ~8-12 interface nodes, each defining input schema, output schema, behavioral contract, and error modes.
  - Decision: ACCEPT. Interfaces provide the stability guarantees that make independent module development possible. Without them, module dependencies are implicit and fragile.

  events/

  - Purpose: Domain events that flow between system boundaries at runtime.
  - Ontology role: Represent runtime behavior — what HAPPENS in the system, as distinct from what EXISTS.
  - Distinction from wiki: Wiki describes processes narratively. Events are individual signals that trigger downstream behavior. The wiki says "the trading engine generates a signal and validates it."
   Events say "SignalGenerated flows from Signal System to Risk System, triggering the TradeValidation workflow."
  - Interaction with existing nodes: Modules emit Events. Workflows are triggered by Events. Events carry Schemas as payloads. Events cross System boundaries.
  - Long-term maintainability: Medium churn. Adding events is easy (new signals). Removing events is hard (consumers may depend on them). ~15-20 eventual nodes.
  - Graph-RAG benefits: MEDIUM. Events answer "what happens when X?" — a common query pattern. "What happens when a stop loss triggers?" → StopTriggered event → consumed by Trade Logger, Position
  Manager, Evaluation System. This runtime view is absent from the current ontology. However, events are less commonly the STARTING point for implementation tasks than capabilities or modules.
  - Implementation cost: Medium. ~15-20 event nodes eventually, but Phase 4+ priority — created as the event-driven architecture is implemented, not speculatively.
  - Decision: ACCEPT the type in the ontology. Create events as the system is built, not upfront. The architecture IS event-driven (market data events, trade lifecycle events, supervisor intervention
  events). Modeling events explicitly enables event-sourcing patterns, replay, and observability — all of which the Syndicate Squad already uses.

  Rejected domain: states/

  - Purpose (proposed): Represent system lifecycle states and state machines explicitly.
  - Why rejected: State machines are already representable as Workflow nodes. The Office Action Loop is a workflow that IS a state machine. System lifecycle states (Cold, Initialized, PaperTrading,
  Validated, Candidate, Production, Paused, Emergency, Archived) should be modeled as a "System Lifecycle" workflow. Transition guards are Predicates. Adding a dedicated states/ type would create
  ambiguity about where state machine information lives — in workflows or in states? One concept, one place.
  - Alternative: Create a canonical "System Lifecycle" workflow node with formal state definitions and transitions. Transition guards reference Predicate nodes.

  ---
  4. Canonical Ownership Rules (Updated)

  1. Each system boundary has ONE canonical system node. Systems are bounded contexts — their boundaries are decided once and defended.
  2. Each capability has ONE canonical capability node, owned by exactly one system. A capability cannot span systems — if it does, it's either two capabilities or the system boundary is wrong.
  3. Each module has ONE canonical module node, implementing one primary capability. A module may contribute to adjacent capabilities via interfaces, but it belongs to one capability.
  4. Each interface has ONE canonical interface node, defined at the boundary of one capability. The capability that PROVIDES the interface owns the interface node.
  5. Each event is globally unique by event_id. Events are owned by the system that emits them.
  6. Each schema is globally unique by schema_id. Schemas are owned by the interface or module that defines them.
  7. Architecture nodes are singletons per architecture_type (one Context Map, one Runtime Topology, one Layer Model).
  8. Wiki concepts are NEVER duplicated. Dev_graph nodes reference wiki pages via source_paths for domain knowledge context. The dev_graph does not re-describe what the wiki already explains — it
  defines engineering artifacts that the wiki does not contain.
  9. Normalization rule: When multiple wiki pages describe the same implementation concern, they converge to ONE canonical dev_graph node. The dev_graph node references ALL relevant wiki pages in
  source_paths, but it defines the engineering reality, not the wiki's multiple perspectives.
  10. Direction of reference: Wiki pages may (eventually) reference dev_graph nodes for implementation status. Dev_graph nodes reference wiki pages for domain knowledge. Neither duplicates the other.

  ---
  5. Object Hierarchy

  Formal containment graph

  Architecture (Context Map, Runtime Topology, Layer Model)
  │
  ├── System: Data Pipeline
  │   ├── Capability: Market Scanning
  │   │   ├── Module: Market Scanner
  │   │   ├── Interface: Market Data API
  │   │   └── Schema: Watchlist Schema
  │   ├── Capability: Feature Engineering
  │   │   ├── Module: Feature Builder
  │   │   ├── Interface: Feature API
  │   │   └── Schema: Feature Vector Schema
  │   └── Capability: Snapshot Assembly
  │       ├── Module: Snapshot Builder
  │       ├── Interface: Snapshot API
  │       ├── Schema: Layer 2 Snapshot Schema
  │       └── Event: SnapshotCreated
  │
  ├── System: Trading Engine
  │   ├── Capability: Signal Generation
  │   │   ├── Module: Signal Generator
  │   │   ├── Schema: Signal Schema
  │   │   └── Event: SignalGenerated
  │   ├── Capability: Order Management
  │   │   ├── Module: Order Router
  │   │   ├── Module: Position Sizer
  │   │   ├── Interface: Execution API
  │   │   ├── Schema: Order Schema
  │   │   ├── Event: OrderPlaced
  │   │   └── Event: OrderFilled
  │   ├── Capability: Stop-Loss Management
  │   │   ├── Module: Stop-Loss Manager
  │   │   ├── Schema: Stop Config Schema
  │   │   └── Event: StopTriggered
  │   └── Capability: Position Tracking
  │       ├── Module: Position Manager
  │       ├── Event: PositionOpened
  │       └── Event: TradeClosed
  │
  ├── System: Risk Control
  │   ├── Capability: Guardrail Enforcement
  │   │   ├── Module: Guardrail Engine
  │   │   ├── Interface: Risk Check API
  │   │   ├── Gate: Trade Validation Gate
  │   │   ├── Predicate: Position Size OK
  │   │   ├── Predicate: Daily Loss Cap OK
  │   │   ├── Predicate: Withdrawal Disabled
  │   │   ├── Event: TradeApproved
  │   │   └── Event: TradeBlocked
  │   └── Capability: Exposure Tracking
  │       └── Module: Exposure Tracker
  │
  ├── System: Agent Runtime
  │   ├── Capability: State Persistence
  │   │   ├── Module: Memory Store
  │   │   ├── Interface: Memory API
  │   │   └── Schema: Memory File Schema
  │   ├── Capability: Context Assembly
  │   │   └── Module: Context Assembler
  │   └── Capability: Trade Logging
  │       ├── Module: Trade Logger
  │       ├── Interface: Trade Log API
  │       ├── Schema: Trade Log Schema
  │       └── Event: TradeLogged
  │
  ├── System: Evaluation Loop
  │   ├── Capability: Performance Scoring
  │   │   ├── Module: Scorecard Generator
  │   │   ├── Schema: Evaluation Scorecard Schema
  │   │   └── Event: EvaluationCompleted
  │   ├── Capability: Promotion Validation
  │   │   ├── Gate: Paper Trading Promotion Gate
  │   │   ├── Predicate: Promotable Scorecard
  │   │   ├── Predicate: Paper Trading Mode
  │   │   └── Event: PromotionDecided
  │   └── Workflow: System Lifecycle
  │       (Cold → Initialized → PaperTrading → Validated →
  │        Candidate → Production → Paused → Emergency → Archived)
  │
  ├── System: Supervisor Office
  │   ├── Capability: Decision Making
  │   │   ├── Module: Decision Engine
  │   │   ├── Interface: Decision API
  │   │   ├── Schema: Decision Packet Schema
  │   │   ├── Agent: Supervisor Agent
  │   │   ├── Predicate: Budget Available
  │   │   └── Event: UpgradeDecided
  │   ├── Capability: Treasury Management
  │   │   ├── Module: Treasury Manager
  │   │   ├── Schema: Treasury Policy Schema
  │   │   ├── Gate: Treasury Approval Gate
  │   │   └── Constraint: Treasury Burn Rule
  │   ├── Capability: Upgrade Evaluation
  │   │   ├── Module: Upgrade Simulator
  │   │   ├── Module: Evolution Engine
  │   │   └── Agent: Evaluator Agent
  │   ├── Capability: Team Orchestration
  │   │   └── Module: Action Orchestrator
  │   ├── Workflow: Office Action Loop
  │   │   (baseline_live → diagnosis_signed → upgrade_approved →
  │   │    evaluation_complete | evaluation_rejected)
  │   └── Workflow: Paper Trading Work Cycle
  │       (watching → scan_ready → proposal_ready → verification_pending →
  │        execution_live → position_open → position_closed → scoring_ready)
  │
  └── Workflow: Trade Pipeline
      (Research → Signal → Validation → Execution → Journaling →
       Evaluation → Refinement)

  Cross-cutting relationships

  Constraints → bind to Systems, Capabilities, Modules
  Gates → guard Workflow transitions
  Predicates → checked by Gates
  Decisions → affect Systems, Capabilities (lifecycle)
  Agents → implement Capabilities
  Events → cross System boundaries
  Interfaces → define contracts between Systems

  ---
  6. Relationship Model

  Structural relationships (new)

  ┌──────────────┬─────────────────────────────────────────┬──────────────────────────────────────────┐
  │ Relationship │                Semantics                │                 Example                  │
  ├──────────────┼─────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Contains     │ Hierarchical ownership (parent → child) │ System → Capability, Capability → Module │
  ├──────────────┼─────────────────────────────────────────┼──────────────────────────────────────────┤
  │ Implements   │ Realization of abstract contract        │ Module → Interface, Agent → Capability   │
  └──────────────┴─────────────────────────────────────────┴──────────────────────────────────────────┘

  Existing relationships (retained)

  ┌────────────────┬────────────────────────────────┬──────────────────────────────────┐
  │  Relationship  │           Semantics            │             Example              │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Depends On     │ Runtime or build dependency    │ Module A → Module B              │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Provides       │ What this node makes available │ Module → Interface               │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Validated By   │ What tests/gates verify this   │ Module → Test, Capability → Gate │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Constrained By │ What invariants bind this      │ System → Constraint              │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Supersedes     │ Temporal replacement           │ Decision v2 → Decision v1        │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Used By        │ Reverse dependency             │ Schema → Module                  │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Produces       │ Output generation              │ Module → Schema, Module → Event  │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────┤
  │ Consumes       │ Input consumption              │ Module → Schema, Module → Event  │
  └────────────────┴────────────────────────────────┴──────────────────────────────────┘

  Behavioral relationships (new)

  ┌──────────────┬─────────────────────────────┬────────────────────────────────────────┐
  │ Relationship │          Semantics          │                Example                 │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Emits        │ Event production at runtime │ Module → Event                         │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Triggered By │ Event consumption           │ Workflow → Event                       │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Guards       │ Quality check on transition │ Gate → Workflow step, Predicate → Gate │
  └──────────────┴─────────────────────────────┴────────────────────────────────────────┘

  Total: 13 relationship types (8 existing + 5 new).

  Frontmatter extensions for new types

  System nodes add:
  system_id: <string>
  bounded_context: <string>
  contains_capabilities: []
  upstream_systems: []
  downstream_systems: []

  Capability nodes add:
  capability_id: <string>
  parent_system: <wikilink>
  implemented_by: []
  interfaces: []

  Architecture nodes add:
  architecture_type: context_map|runtime_topology|layer_model
  scope: <string>

  Interface nodes add:
  interface_id: <string>
  parent_capability: <wikilink>
  input_schema: <wikilink or null>
  output_schema: <wikilink or null>
  implemented_by: []
  stability: stable|evolving|experimental

  Event nodes add:
  event_id: <string>
  emitted_by: <wikilink>
  consumed_by: []
  triggers: []
  payload_schema: <wikilink or null>

  ---
  7. Migration Strategy

  Phase 0: Ontology Update (governance-first)

  Update CLAUDE.md with:
  - 5 new type enum values
  - 5 new directories
  - 5 new frontmatter extension schemas
  - 5 new relationship types
  - Updated Object Hierarchy documentation
  - New ADR documenting the redesign

  Create new ADR: "ADR - Ontology Redesign" documenting WHY the flat model was insufficient and WHAT the hierarchy provides.

  No content nodes created. Only governance changes.

  Phase 1: Architecture Layer (3 nodes)

  ┌──────────────────┬──────────────┬──────────────────────────────────────────────────────────────────────────────┐
  │       Node       │     Type     │                                   Content                                    │
  ├──────────────────┼──────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Context Map      │ architecture │ Formal bounded context diagram — 6 systems and their interactions            │
  ├──────────────────┼──────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Runtime Topology │ architecture │ Component interaction model — events, interfaces, data flows                 │
  ├──────────────────┼──────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Layer Model      │ architecture │ Formal definition of L1 (data) → L2 (analysis) → L3 (execution) architecture │
  └──────────────────┴──────────────┴──────────────────────────────────────────────────────────────────────────────┘

  Migrate existing Infrastructure Diagram node to architecture/ (retype from reference to architecture).

  Source_paths reference: Architecture Overview, Trading Engine Pipeline, Three-Layer Trading System, Claude-Assisted Trading Stack.

  Phase 2: Systems (6 nodes) + System Lifecycle workflow (1 node)

  ┌──────────────────┬─────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────┐
  │      System      │                             Bounded Context                             │                                         Source Wiki Pages                                         │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Data Pipeline    │ Market data ingestion, feature engineering, snapshot assembly           │ Three-Layer Trading System (L1-L2), Trading Engine Pipeline (Stage 1-2)                           │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Trading Engine   │ Signal generation, order management, position tracking, stop management │ Trading Engine Pipeline (Stage 2-4), Three-Layer Trading System (L3), Position Sizing, Stop-Loss  │
  │                  │                                                                         │ Systems                                                                                           │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Risk Control     │ Guardrail enforcement, exposure tracking, circuit breaking              │ Guardrail Architecture, Autonomous Trading Risk Model                                             │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Agent Runtime    │ State persistence, context assembly, trade logging                      │ Agent Memory Architecture, Context Budget Engineering, Trade Logging                              │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Evaluation Loop  │ Performance scoring, promotion validation, regime detection             │ Paper Trading (scoring), Walk-Forward Optimization, Backtesting Methodology                       │
  ├──────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Supervisor       │ Decision making, treasury management, upgrade evaluation, team          │ Supervisor Decision Engine, Syndicate Squad Architecture, Office Action Loop, Treasury Policy     │
  │ Office           │ orchestration                                                           │ System                                                                                            │
  └──────────────────┴─────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────┘

  System Lifecycle workflow: Cold → Initialized → PaperTrading → Validated → Candidate → Production → Paused → Emergency → Archived.

  Phase 3: Capabilities (~20 nodes)

  Approximately 3-4 capabilities per system. See Object Hierarchy in Section 5 for the full list.

  Each capability node defines:
  - What the system can do (not how)
  - What interface it exposes
  - What modules implement it
  - What wiki pages provide domain knowledge

  Phase 4: Interfaces + Key Schemas (~12-15 nodes)

  Priority interfaces:
  1. Snapshot API (Data Pipeline → Trading Engine)
  2. Execution API (Trading Engine → Broker)
  3. Risk Check API (Risk Control → Trading Engine)
  4. Memory API (Agent Runtime → all systems)
  5. Trade Log API (Agent Runtime → all systems)
  6. Decision API (Supervisor Office → Trading Engine)
  7. Evaluation API (Evaluation Loop → Supervisor Office)
  8. Treasury API (Supervisor Office → internal)

  Priority schemas:
  1. Layer 2 Snapshot Schema
  2. Order Schema
  3. Trade Log Schema
  4. Decision Packet Schema
  5. Evaluation Scorecard Schema
  6. Treasury Policy Schema

  Phase 5: Modules under capabilities (ongoing)

  Create module nodes as implementation work begins. Each module:
  - Belongs to exactly one capability
  - Implements specific interfaces
  - References source files (when they exist)
  - References tests (when they exist)

  Phase 6: Gates, Predicates, Workflows (ongoing)

  Create as implementation demands. Priority:
  1. Trade Validation Gate (Risk Control)
  2. Paper Trading Promotion Gate (Evaluation Loop)
  3. Treasury Approval Gate (Supervisor Office)
  4. Key predicates: Position Size OK, Daily Loss Cap OK, Withdrawal Disabled, Promotable Scorecard
  5. Workflows: Trade Pipeline, Office Action Loop, Paper Trading Work Cycle

  Phase 7: Events (when event-driven architecture is implemented)

  Create event nodes when runtime event flows are being implemented. Not before. Event definitions emerge from code, not from speculation.

  Phase 8: Files, Tests (when code exists)

  File and test nodes are created as actual source files are written. These are the leaf level of the ontology.

  ---
  8. Backward Compatibility Strategy

  Zero breakage. The existing 18 content nodes (governance, reference, constraint, decision_record, api_doc_source, context_pack, observability) are all meta-types. None of them are system,
  capability, architecture, interface, or event. The schema evolution is purely additive.

  Specific compatibility guarantees:

  1. Existing Dataview queries on Dev Graph Dashboard continue to work. They filter on existing types (WHERE type = "governance" etc.) and are unaffected by new type values.
  2. Existing frontmatter is unchanged. The 11 universal fields remain identical. New fields are type-specific extensions that only apply to new types.
  3. Existing relationships are unchanged. The 8 existing relationship section names are retained. New relationship sections are additive.
  4. Existing CLAUDE.md governance is extended, not rewritten. The enum tables get new values appended. The frontmatter governance section gets new type-specific extension blocks.
  5. Existing constraints (No Wiki Mutation, Frontmatter Required, Canonical Ownership) apply identically to all new types.
  6. Infrastructure Diagram migrates from root-level reference to architecture/ with type architecture. This is the only existing node that changes, and it's a retype + directory move — content is
  preserved.

  ---
  9. Risk Assessment

  ┌──────────────────────────────────────────────────┬──────────┬────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                       Risk                       │ Severity │ Likelihood │                                                      Mitigation                                                      │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Over-engineering: 22 types and 21 directories    │ Medium   │ Medium     │ Only create nodes when they have substantive content. Empty directories cost nothing. Mark speculative nodes as      │
  │ for a system with no code yet                    │          │            │ confidence: inferred, implementation_status: not-started.                                                            │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Ontology complexity: Developers and Claude need  │ Medium   │ Low        │ CLAUDE.md contains clear hierarchy documentation with the Object Hierarchy diagram. Context Map provides visual      │
  │ to understand the hierarchy                      │          │            │ orientation. The hierarchy IS the documentation.                                                                     │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Premature abstraction: Defining capabilities and │ Medium   │ Medium     │ Capabilities and interfaces are refined as implementation reveals reality. The ontology is designed to evolve: nodes │
  │  interfaces before code exists                   │          │            │  can be split, merged, or reclassified. Start with ~20 capabilities, expect 10% to be wrong.                         │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Maintenance burden: More types = more governance │ Low      │ Low        │ Hierarchy means changes are scoped. Modifying a module doesn't affect its parent capability or system. Adding a      │
  │                                                  │          │            │ module doesn't require updating architecture. The hierarchy REDUCES cascading maintenance.                           │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Ontology drift: Dev_graph diverges from actual   │ Medium   │ Medium     │ Context pack assembly (Phase 5+) continuously validates dev_graph against codebase reality. Stale node detection     │
  │ implementation                                   │          │            │ (30-day) catches drift. Monthly ontology audit catches structural divergence.                                        │
  ├──────────────────────────────────────────────────┼──────────┼────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Graph-RAG confusion: Too many abstraction levels │ Low      │ Low        │ Context pack assembly can start at ANY level. Simple tasks start at module. Complex tasks start at capability or     │
  │  confuse retrieval                               │          │            │ system. The hierarchy supports multi-resolution retrieval, not forced full-depth traversal.                          │
  └──────────────────────────────────────────────────┴──────────┴────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ---
  10. Recommended Implementation Order

  ┌───────────┬───────┬───────────────────────────────────────┬─────────────────────────────────────────────────────────────────┐
  │ Priority  │ Phase │                 Nodes                 │                            Rationale                            │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Immediate │ 0     │ CLAUDE.md update, ADR, log.md         │ Governance-first. No content nodes without ontology definition. │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Next      │ 1     │ 3 architecture nodes                  │ Structural root. Everything references architecture.            │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Then      │ 2     │ 6 system nodes + 1 lifecycle workflow │ System boundaries define everything else.                       │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Then      │ 3     │ ~20 capability nodes                  │ Capabilities organize implementation scope.                     │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Then      │ 4     │ ~12-15 interfaces + schemas           │ Contracts before code.                                          │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Then      │ 5     │ Modules (ongoing)                     │ Implementation boundaries created as coding begins.             │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Then      │ 6     │ Gates, predicates, workflows          │ Quality infrastructure.                                         │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Deferred  │ 7     │ Events                                │ Created when event-driven architecture is implemented.          │
  ├───────────┼───────┼───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ Deferred  │ 8     │ Files, tests                          │ Created when source code exists.                                │
  └───────────┴───────┴───────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘

  ---
  Normalization Strategy Summary

  ┌──────────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                          Wiki Concepts (multiple perspectives)                           │                               Dev Graph (one canonical representation)                               │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Architecture Overview + Trading Engine Pipeline + Three-Layer Trading System +           │ Architecture: Context Map + Runtime Topology + Layer Model                                           │
  │ Claude-Assisted Trading Stack                                                            │                                                                                                      │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Guardrail Architecture + Autonomous Trading Risk Model                                   │ System: Risk Control → Capability: Guardrail Enforcement → Module: Guardrail Engine + Gate +         │
  │                                                                                          │ Predicates                                                                                           │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Supervisor Decision Engine + Syndicate Squad Architecture + Office Action Loop +         │ System: Supervisor Office → 4 Capabilities → Modules + Agent + Workflows                             │
  │ Treasury Policy System                                                                   │                                                                                                      │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Trade Logging + Trading Engine Pipeline (Stage 5)                                        │ Capability: Trade Logging → Module: Trade Logger + Interface: Trade Log API + Schema: Trade Log      │
  │                                                                                          │ Schema                                                                                               │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Position Sizing + Stop-Loss Systems + Trading Engine Pipeline (Stage 3-4)                │ System: Trading Engine → Capability: Order Management + Capability: Stop-Loss Management → Modules   │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Paper Trading + Autonomous Trading Risk Model (phased risk)                              │ System: Evaluation Loop → Capability: Promotion Validation → Gate: Paper Trading Promotion Gate +    │
  │                                                                                          │ Workflow: System Lifecycle                                                                           │
  ├──────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Three-Layer Trading System (L2) + Trading Engine Pipeline (Stage 1-2)                    │ System: Data Pipeline → Capability: Snapshot Assembly → Interface: Snapshot API + Schema: Layer 2    │
  │                                                                                          │ Snapshot Schema                                                                                      │
  └──────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────┘

  The wiki retains all perspectives. The dev_graph normalizes to one engineering truth per concept.

  ---
  Layer 2 Integration Design

  Layer 2 (the Strategy Engine / deterministic analysis layer) becomes a first-class ontology source rather than a wiki mirror:

  System: Data Pipeline
    └── Capability: Snapshot Assembly
         ├── Module: Snapshot Builder (creates L2 snapshots)
         ├── Interface: Snapshot API (contract for snapshot consumers)
         ├── Schema: Layer 2 Snapshot Schema (canonical data shape)
         └── Event: SnapshotCreated (signals downstream consumers)

  The Layer 2 Snapshot Schema becomes the foundational data contract of the entire system. Everything downstream (signal generation, execution, risk validation) consumes snapshots. This makes the
  schema a high-stability interface node, not just a data definition.

  The architectural implication: schema changes to L2 snapshots are breaking changes that cascade through the entire pipeline. The dev_graph models this explicitly through interface dependencies,
  which the flat proposal did not.

  ---
  Graph-RAG Retrieval Design

  Primary entry point: Capabilities, with Systems as scope filter.

  Retrieval flow for a coding task:

  1. Parse task → identify target capability
     "implement stop-loss monitoring"
     → Capability: Stop-Loss Management (in System: Trading Engine)

  2. Retrieve capability node
     → Module: Stop-Loss Manager
     → Interface: (none yet — stop-loss is internal to Trading Engine)
     → Schema: Stop Config Schema
     → Wiki source: Stop-Loss Systems page

  3. Expand to dependent modules
     → Module: Position Manager (same system, related capability)
     → Interface: Execution API (broker communication)

  4. Expand cross-cutting concerns
     → Gate: Trade Validation Gate (Risk Control system)
     → Predicate: Position Size OK
     → Constraint: Treasury Burn Rule (if applicable)
     → Event: StopTriggered (emitted), TradeClosed (downstream)

  5. Ground in code reality
     → File nodes (when code exists)
     → Test nodes (when tests exist)

  6. Attach documentation
     → API docs: Alpaca API Docs (broker integration)
     → Wiki: Stop-Loss Systems, Position Sizing (domain knowledge)

  Why capabilities, not systems, as entry point:
  - Systems are too broad. "Implement something in the Trading Engine" gives you all of signal generation, order management, stop-loss management, and position tracking.
  - Capabilities are the right granularity. "Implement Stop-Loss Management" gives you exactly the modules, interfaces, schemas, and tests you need.
  - Modules are too narrow. Starting from a specific module misses dependencies and cross-cutting concerns.

  Why this is better than flat retrieval:
  - Flat retrieval: semantic search returns "Stop-Loss Module, Stop-Loss Systems wiki page, Position Sizing Module, Guardrail Engine, Execution Engine, several predicates" — all at equal relevance, no
   hierarchy.
  - Hierarchical retrieval: start at Capability → get contained modules → expand to interfaces/schemas → expand cross-system to gates/predicates. Each step is intentional and scoped.

  ---
  This redesign is complete. Ready for your review before any mutations to the dev graph.