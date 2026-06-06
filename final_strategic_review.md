Final Strategic Ontology Review — Engineering Digital Twin Evolution

---

Scope and Authority

This review is the final strategic layer over two accepted baseline documents:

1. Dev Graph Ontology Redesign (audit_plan.md) — the structural redesign introducing Architecture → System → Capability → Module → File hierarchy with 22 types and 13 relationships.
2. Architecture Review Addendum (audit_plan_addendum.md) — the knowledge extension introducing knowledge_asset and pattern types, 3 new relationships, evidence field, experimental confidence value, and intent-aware Graph-RAG routing.

Both documents define the current target state: 24 types, 16 relationships, 23 directories.

This review does NOT redesign that target. It evaluates whether the target can evolve into a long-term Engineering Digital Twin suitable for autonomous Claude-assisted software engineering, and identifies the specific architectural decisions required to get there.

Every recommendation is challenged against five strategic criteria:

1. Does it improve autonomous engineering reasoning?
2. Does it improve Graph-RAG retrieval precision?
3. Is the maintenance cost proportional to the value?
4. Does it scale beyond 200 nodes without governance collapse?
5. Is it compatible with the three-substrate model (Obsidian + Neo4j + PostgreSQL)?

---

0. Strategic Assessment of the Current Target State

The combined target (audit_plan + addendum) is a strong engineering ontology. It solves the structural weaknesses of the original flat model and adds knowledge foundations that make the architecture traceable. Compared to the original 17-type flat graph, the target state is a generational improvement.

Three strategic limitations remain that this review addresses:

0.1 The ontology lacks identity. Nodes are identified by file name, which changes on rename. There is no stable identifier that survives refactoring, Neo4j export, cross-system reference, or API integration. Type-specific IDs exist for some types (decision_id, gate_id, schema_id) but not universally. This creates fragility at the boundary between Obsidian and external systems.

0.2 The ontology lacks self-governance. Schema evolution rules exist in CLAUDE.md, but the ontology has no version number, no formal change tracking, no merge/split procedures beyond "update CLAUDE.md first," and no mechanism to detect semantic drift (a node whose content no longer matches its type, or a relationship section that references a non-existent target). The lint checks catch structural issues but not semantic ones.

0.3 The traceability chain is open-ended. The addendum established a linear chain from Knowledge Asset down to Test. But engineering is cyclical: evaluation results inform new decisions, which reshape architecture, which changes implementation, which produces new evaluation data. The chain should close into a feedback loop. Without the loop, the ontology models a waterfall, not an evolving system.

---

1. Knowledge Origin Layer

1.1 Baseline position

The addendum PARTIALLY ACCEPTED knowledge_asset as type #23 with constraints: maximum 15 nodes, no implementation_status, lightweight pointers only.

1.2 Strategic reassessment

The 15-node cap was tactical caution appropriate for a near-term extension. Strategically, it is an arbitrary constraint that will be hit and then ignored or raised, creating a governance exception. Knowledge assets should be governed by the same creation rules as all other types — canonical ownership, frontmatter required, no duplicates — not by an artificial cap.

The deeper question is whether knowledge assets are stable reference objects or living documents that evolve as understanding deepens. The addendum assumed the former: "Event Sourcing doesn't evolve." This is true for well-established engineering principles but not for project-specific methodologies like "Office Action Loop methodology" or "Layer 2 design principles," which may be refined as implementation reveals edge cases.

1.3 Ownership model

Knowledge assets are owned by the engineering process, not by a specific system or capability. They are cross-cutting — the same knowledge asset (e.g., Event Sourcing) may inform multiple systems (Data Pipeline, Trading Engine, Agent Runtime). This makes them similar to constraints in their cross-cutting nature but different in their purpose: constraints define WHAT MUST NOT happen; knowledge assets define WHY THINGS ARE.

Owner: the dev_graph governance process. No system or capability owns a knowledge asset. Any session may create or update a knowledge asset, subject to canonical ownership and frontmatter rules.

1.4 Lifecycle

Knowledge assets have a two-phase lifecycle:

Phase A — Formative (during architecture design): Knowledge assets are created to document the engineering knowledge that motivates architectural decisions. They are initially `confidence: single-source` (derived from one wiki page or source document) and may be promoted to `confidence: confirmed` when a second source corroborates.

Phase B — Stable (during implementation): Knowledge assets rarely change once the architecture is set. They may be updated when implementation reveals that the original understanding was incomplete, or when new external guidance (e.g., updated Anthropic documentation) changes the foundational principle.

Status values: `active`, `draft`, `deprecated`. Not `planned`, `implemented`, `validated`, `blocked` — these are implementation lifecycle states that do not apply to knowledge.

The `implementation_status` field: OMIT for knowledge assets. The addendum was correct — knowledge assets are never "implemented." They are conceptual foundations. If forced to carry implementation_status, they would all be permanently `not-started`, which is meaningless metadata.

1.5 Relationship to wiki — the boundary problem

The addendum positioned knowledge assets as "pointers, not encyclopedias." This is correct but requires precise boundary rules:

What goes in the knowledge asset: The engineering-scoped summary — the structural constraints and design implications of the principle. "Event Sourcing means X, which implies Y for our architecture, constraining Z."

What stays in the wiki: The full domain knowledge — history, theory, alternative approaches, trade-offs, source citations. "Event Sourcing was introduced by Greg Young in..."

What goes in neither: Implementation details — those belong in capability, module, and file nodes.

Cross-reference protocol: Knowledge assets MUST include `source_wiki_pages: []` listing every wiki page that provides domain knowledge for this engineering principle. Wiki pages MAY (in a future wiki update) include a `## Engineering Application` section that references back to the dev_graph knowledge asset. The dev_graph does not modify wiki pages — this is a future wiki maintenance task.

1.6 Relationship to architecture nodes

Architecture nodes (Context Map, Runtime Topology, Layer Model) define the system's structural shape. Knowledge assets explain WHY that shape was chosen. The relationship is:

Architecture node `## Relationships / ### Originates From` → lists knowledge assets that motivated the architectural shape.

This is distinct from `### Depends On` (runtime/build dependency) and `### Constrained By` (hard invariant). An architecture is not CONSTRAINED BY Event Sourcing — it is SHAPED BY Event Sourcing. The originates_from relationship captures this semantic correctly.

1.7 Relationship to systems and capabilities

Systems and capabilities do not directly reference knowledge assets. The traceability chain goes: Knowledge Asset → ADR → Architecture → System → Capability. A capability's connection to foundational knowledge is mediated by the ADR that authorized its design.

Exception: When a capability directly follows a well-known methodology (e.g., Context Assembly follows Context Engineering principles), a direct `originates_from` edge from the capability to the knowledge asset is justified. This should be rare — most capabilities are derived from architecture, not directly from knowledge.

1.8 Engineering reasoning benefits

HIGH. Knowledge assets enable three reasoning patterns that are impossible without them:

1. Justification: "Why does this capability exist?" → traverse upward through ADRs to knowledge assets → retrieve foundational principles.
2. Consistency checking: "Is this new module consistent with our architectural principles?" → retrieve relevant knowledge assets → verify alignment.
3. Decision support: "Should we use approach A or B?" → retrieve knowledge assets that define the relevant principles → evaluate each approach against principles.

Without knowledge assets, these reasoning patterns require reading wiki prose and hoping semantic search finds the right passages. With knowledge assets, they are typed graph traversals.

1.9 Recommendation: ACCEPT

Upgrade from PARTIALLY ACCEPT. Remove the 15-node cap. Accept knowledge_asset as a full first-class ontology type governed by the same creation rules as all other types. Retain the "pointers not encyclopedias" principle. Accept the simplified lifecycle (no implementation_status). Estimate 10-20 nodes at maturity.

The strategic value of knowledge assets is too high to constrain with an artificial cap. They are the foundation that makes the entire ontology non-arbitrary.

---

2. Canonical Pattern Layer

2.1 Baseline position

The addendum PARTIALLY ACCEPTED pattern as type #24 with constraints: maximum 10-12 nodes, must be instantiated by at least 2 modules or capabilities, simplified lifecycle.

2.2 Strategic reassessment

The 2-instance minimum is sound engineering practice and should be retained — a one-off solution is not a pattern. The node cap should be removed for the same reason as knowledge assets: it is an arbitrary constraint that will create governance exceptions.

The deeper strategic question: Should patterns be purely descriptive (documenting what exists) or prescriptive (defining what future implementations should follow)?

Answer: BOTH, at different lifecycle stages.

Early patterns are descriptive: "We observe that the Guardrail Engine and the Treasury Approval Gate both follow a structural pattern: predicate evaluation → gate decision → blocking behavior. We name this the Guardrail Pattern."

Mature patterns are prescriptive: "Any new validation checkpoint SHOULD follow the Guardrail Pattern: define predicates, compose into a gate, implement blocking behavior at the boundary."

This duality means patterns need a maturity indicator. The confidence field already serves this purpose:
- `confidence: inferred` → pattern observed but not yet validated as reusable
- `confidence: single-source` → pattern documented from one system's usage
- `confidence: confirmed` → pattern validated across multiple systems, safe to prescribe

2.3 Pattern composition

Patterns can compose other patterns. The Supervisor Pattern composes Multi-Agent Coordination (how agents interact) with Decision Pattern (how decisions are made) and Treasury Approval (how resources are allocated). This composition should be modeled.

Relationship: Pattern → `### Composes` → [other patterns]. This is a new relationship subsection, not a new relationship type — it uses the existing `Consumes` semantic (a composed pattern "consumes" its component patterns as building blocks). However, `Consumes` implies runtime data flow, not structural composition. A dedicated `### Composes` subsection is cleaner.

This adds one relationship type: `Composes` (Pattern → Pattern). This is narrowly scoped — only patterns compose patterns — but it enables reasoning about pattern hierarchies.

2.4 Cross-bounded-context reuse

Patterns are the ONLY ontology type that spans bounded contexts by design. A module belongs to one system. A capability belongs to one system. But the Guardrail Pattern is used in Risk Control (Trade Validation Gate) AND in Evaluation Loop (Paper Trading Promotion Gate) AND in Supervisor Office (Treasury Approval Gate).

This cross-system applicability is a core strategic value. When Claude implements a new gate in a new system, the pattern node provides structural guidance regardless of which system the gate belongs to. This is impossible with system-scoped or capability-scoped nodes.

2.5 Relationship hierarchy

Architecture COMPOSES patterns (the overall system is a composition of patterns).
Systems EXHIBIT patterns (a system follows certain patterns).
Capabilities REALIZE patterns (a capability's design follows a pattern).
Modules IMPLEMENT patterns (a module's code structure follows a pattern).

These four verbs represent different levels of pattern engagement:
- COMPOSE: "the architecture is built from these patterns"
- EXHIBIT: "this system follows these patterns"
- REALIZE: "this capability's design follows this pattern"
- IMPLEMENT: "this code follows this pattern"

However, modeling four separate relationship types for the same fundamental concept (pattern adoption) is over-engineering. The single `realizes` relationship (from the addendum) captures the essential semantic: "this node follows this pattern." The specific level of engagement is implied by the type of the source node (architecture vs. module).

2.6 Recommendation: ACCEPT

Upgrade from PARTIALLY ACCEPT. Remove the node cap. Retain the 2-instance minimum for pattern creation. Accept `Composes` as a new relationship type (Pattern → Pattern only). Accept the prescriptive/descriptive duality governed by the confidence field. Estimate 10-15 nodes at maturity.

---

3. Complete Decision Traceability

3.1 Baseline position

The addendum accepted three relationships (originates_from, justified_by, realizes) and rejected three (derived_from, operationalizes, validated_by). Total: 16 relationship types.

3.2 The closed-loop chain

The user proposes a closed engineering feedback loop:

```
Knowledge Asset → ADR → Architecture → System → Capability → Pattern → Interface →
Module → Schema → File → Test → Runtime Event → Evaluation → Benchmark → Evolution →
Knowledge Asset
```

This is 16 stages. Some are at the same abstraction level and should be grouped:

```
KNOWLEDGE        knowledge_asset
    ↓ originates_from
DECISION         decision_record
    ↓ justified_by / Contains
ARCHITECTURE     architecture, system, capability
    ↓ realizes / Contains
DESIGN           pattern, interface, artifact_schema
    ↓ Contains / Implements
IMPLEMENTATION   module, file
    ↓ Validated By
VERIFICATION     test, gate, predicate
    ↓ Emits / Triggered By
RUNTIME          event, workflow
    ↓ measured_by
EVALUATION       benchmark_result
    ↓ informs
EVOLUTION        decision_record (new ADR)
    ↓ originates_from
KNOWLEDGE        knowledge_asset (loop closes)
```

This is 9 stages — the same 7 from the addendum's continuum plus DESIGN (patterns + interfaces) and EVALUATION (benchmarks) as explicit stages.

3.3 Gap analysis: what closes the loop?

The addendum's chain was open-ended: Knowledge → ... → Test (end). The loop requires two additional traversal paths:

Path 1: VERIFICATION → EVALUATION. How do test results and gate outcomes feed into benchmark assessments? Currently, benchmark_result nodes have no frontmatter field for what they measure. The test nodes have `covers: []` for what they validate. Benchmarks need an equivalent.

Proposed: Add `measures: []` to benchmark_result frontmatter. This parallels `covers: []` on test nodes. Format: `measures: ["[[Module Name]]", "[[Capability Name]]"]`. This is a frontmatter extension, not a new relationship type — consistent with how test coverage is modeled.

Path 2: EVALUATION → EVOLUTION. How do benchmark results trigger new architectural decisions? This is mediated by engineering judgment (human or Claude). A benchmark doesn't automatically create an ADR. The process is: poor benchmark → analysis → new ADR with `evidence: [benchmark]` field. The evidence field (from the addendum) already captures this provenance. No new relationship type needed.

Path 3: EVOLUTION → KNOWLEDGE. How do new ADRs feed back to knowledge assets? A new ADR may refine understanding of an existing knowledge asset (e.g., "Event Sourcing requires additional safeguards for financial data" → updates Knowledge Asset "Event Sourcing" with new constraint). This is a governance process: the ADR author updates the relevant knowledge asset. No new relationship type needed — the `originates_from` edge on the new ADR references the same knowledge asset, and the knowledge asset's `updated` field reflects the refinement.

3.4 Proposed relationship evaluation

| Proposed | Semantics | Addendum Decision | Strategic Reassessment |
|----------|-----------|-------------------|----------------------|
| originates_from | ADR → Knowledge Asset | ACCEPT | MAINTAIN ACCEPT |
| justified_by | Module/Capability → ADR | ACCEPT | MAINTAIN ACCEPT |
| realizes | Module/Capability → Pattern | ACCEPT | MAINTAIN ACCEPT |
| Composes | Pattern → Pattern | Not evaluated | ACCEPT (new — see Section 2.3) |
| measured_by | Benchmark → Module/Capability | Not evaluated | REJECT as relationship type — use frontmatter `measures: []` instead |
| derived_from | System → Architecture | REJECT | MAINTAIN REJECT — Contains covers structural derivation |
| operationalizes | Module → Capability | REJECT | MAINTAIN REJECT — Contains covers containment; Implements covers contract fulfillment |
| evolves_into | ADR_v1 → ADR_v2 | Not evaluated | REJECT — Supersedes already covers this in reverse direction |
| feeds_back_to | Benchmark → Knowledge Asset | Not evaluated | REJECT — mediated by human judgment; modeled through evidence field on new ADRs |
| implements | Module → Interface | Already exists as Implements | MAINTAIN — no change |
| validated_by | Module → Test | Already exists | MAINTAIN — no change |

3.5 The loop closure mechanism

The closed loop does not require new relationship types. It requires the following to be true:

1. Benchmark nodes have `measures: []` listing what they evaluate (frontmatter extension).
2. New ADRs reference their evidence source via `evidence: [benchmark]` or `evidence: [code]` (already planned from addendum).
3. New ADRs reference the knowledge assets they build on via `originates_from` (already planned from addendum).
4. Knowledge assets are updated when ADRs reveal new understanding (governance process, already covered by standard update procedures).

The loop is conceptual and processual, not mechanical. Forcing it into typed edges would create false precision — as if benchmarks automatically trigger ADRs, which they do not.

3.6 Recommendation: PARTIALLY ACCEPT

Accept the closed-loop model as the canonical conceptual backbone of the ontology (documented in CLAUDE.md). Accept `Composes` as a new relationship type (Pattern → Pattern). Accept `measures: []` as a benchmark_result frontmatter extension. Reject measured_by, evolves_into, and feeds_back_to as relationship types — the loop closes through existing relationships and governance processes.

Total relationship types: 17 (16 from addendum + Composes).

---

4. Universal Metadata for Every Object

4.1 Baseline position

The addendum accepted evidence: [] as a new universal field and experimental as a new confidence value. It rejected lifecycle, source_quality, and review_status.

4.2 Canonical Identifier

This is the most strategically significant metadata gap.

Current state: Some types have type-specific IDs (decision_id, gate_id, predicate_id, schema_id). The proposed types add more (system_id, capability_id, interface_id, event_id, knowledge_id, pattern_id). But these are inconsistently named and not universal. Modules, files, tests, agents, skills, governance nodes, observability nodes, reference nodes, context packs, api_doc_source nodes, and benchmark_result nodes lack stable identifiers beyond the file name.

Problem: File names change on rename. If a module node is renamed from "Order Router.md" to "Order Execution Router.md", every wikilink pointing to it breaks, every Neo4j node name becomes stale, and every external reference becomes invalid. Wikilink refactoring in Obsidian handles internal links, but Neo4j and external systems have no automatic rename propagation.

Proposal: Add `canonical_id` as a universal frontmatter field on ALL content nodes.

Format: `{TYPE_PREFIX}-{SEQUENCE_NUMBER}`

```
KA-001    (knowledge_asset)
PAT-001   (pattern)
ARCH-001  (architecture)
SYS-001   (system)
CAP-001   (capability)
MOD-001   (module)
INT-001   (interface)
EVT-001   (event)
FILE-001  (file)
TEST-001  (test)
WF-001    (workflow)
SCHEMA-001 (artifact_schema)
GATE-001  (gate)
PRED-001  (predicate)
AGT-001   (agent)
SKILL-001 (skill)
ADR-001   (decision_record) — already exists
CTX-001   (context_pack)
GOV-001   (governance)
OBS-001   (observability)
REF-001   (reference)
BENCH-001 (benchmark_result)
API-001   (api_doc_source)
CON-001   (constraint)
```

Rules:
- canonical_id is assigned at creation and NEVER changes, even if the node is renamed.
- canonical_id is globally unique within the dev_graph.
- Neo4j export uses canonical_id as the primary key, not the file name.
- Existing type-specific IDs (decision_id, gate_id, etc.) are retained for backward compatibility but canonical_id becomes the primary identifier.
- Sequence numbers are assigned incrementally per type prefix.

This is a significant governance addition — it requires updating CLAUDE.md, adding the field to all 18 existing content nodes, and updating the Neo4j export mapping. But the strategic value is high: stable identity is foundational for cross-system integration.

Assessment: ACCEPT.

4.3 Ontology version tracking

The ontology itself has no version number. Schema changes are tracked in CLAUDE.md prose and log.md entries, but there is no machine-readable version that tells a tool or agent "which version of the schema is this graph running?"

Proposal: Add `schema_version` as a single declaration in CLAUDE.md (not per-node).

```yaml
# In CLAUDE.md header
schema_version: "3.0.0"
```

Versioning scheme:
- MAJOR: Breaking changes (field removal, enum value removal, relationship type removal). Currently prohibited by append-only rules, but if ever needed, a major version bump signals it.
- MINOR: New types, new relationships, new fields, new enum values. All changes from audit_plan + addendum + this review are MINOR.
- PATCH: Documentation-only changes, lint rule updates, dashboard query updates.

Current version: 1.0.0 (the bootstrap ontology from ADR-001).
After audit_plan: 2.0.0 (structural redesign — 5 new types, 5 new relationships, new hierarchy).
After addendum: 2.1.0 (knowledge extensions — 2 new types, 3 new relationships, 1 new field).
After this review: 2.2.0 (strategic extensions — Composes relationship, canonical_id, measures field, governance procedures).

Per-node schema_version: REJECT for now. All nodes are presumed to be at the current schema version. If a future breaking change occurs, a per-node `schema_version` field can be added at that time to distinguish migrated from unmigrated nodes.

Assessment: ACCEPT schema_version in CLAUDE.md. REJECT per-node schema_version.

4.4 Lifecycle — strategic reconsideration

The addendum rejected lifecycle as redundant with status + implementation_status.

Strategic reconsideration: In a multi-agent environment with Claude sessions operating concurrently on different parts of the system, the distinction between "this node is architecturally approved" (governance lifecycle) and "this node's code is tested" (implementation lifecycle) becomes important. The current two-field model captures this if status is read as governance lifecycle and implementation_status is read as code lifecycle.

The proposed lifecycle field adds a THIRD dimension. When would all three differ?

- status: active (governance approves this node)
- implementation_status: not-started (no code written)
- lifecycle: proposed (concept is under review)

But "under review" is captured by status: planned or status: draft. The third field adds no information that the first two cannot express.

Reconfirm: REJECT. The two-field model (status + implementation_status) is sufficient. The governance and implementation lifecycles are orthogonal and well-served by two independent fields.

4.5 Confidence — strategic reconsideration

The addendum accepted experimental as a fifth confidence value.

Strategic consideration: Should confidence values be weighted for Graph-RAG? If an agent must choose between two conflicting nodes, can it rank them by confidence?

Implicit ordering: confirmed > single-source > inferred > experimental > speculative.

This ordering is already usable without changes. Dataview queries can sort by confidence. Context pack assembly can prefer higher-confidence nodes. No additional metadata needed — the ordering is intrinsic to the enum.

Reconfirm: ACCEPT experimental. No further changes.

4.6 Evidence — strategic enrichment

The addendum accepted evidence: [] with values wiki, layer2, code, benchmark, ADR, external.

Strategic addition: `design` as an evidence value. Some nodes are confirmed by design reasoning alone — the architecture's structure is evidence that the system decomposition is correct, even before code exists. "Evidence: design" captures "this was validated by architectural analysis."

Extended enum: `wiki`, `layer2`, `code`, `benchmark`, `ADR`, `external`, `design`.

Assessment: ACCEPT the addition of `design` to the evidence enum.

4.7 Source quality, review status — strategic reconsideration

Source quality: still derivable from confidence + source_paths. No new information from a strategic perspective. Reconfirm: REJECT.

Review status: In a multi-agent future, review workflows become more relevant. But the project is not there yet. Adding review_status now creates maintenance overhead without active consumers. Reconfirm: REJECT, with a note that this should be reconsidered when multi-agent concurrent sessions become operational.

4.8 Semantic version for nodes

Should individual nodes carry semantic version numbers? For most types, no — a module node represents the current state, not a versioned artifact. But for two types, versioning matters:

- Interface nodes: An interface version defines a contract. Breaking changes to interfaces need versioning to track compatibility. Proposed: add `interface_version: <semver>` to interface frontmatter. This is a domain-specific extension, not a universal field.
- Schema nodes: Data schema changes affect consumers. Proposed: add `schema_version: <semver>` to artifact_schema frontmatter. Same reasoning.

Both are domain-specific frontmatter extensions, not universal metadata.

Assessment: ACCEPT interface_version and schema_version as domain-specific frontmatter fields. REJECT universal node versioning.

4.9 Recommendation: PARTIALLY ACCEPT

| Proposed | Recommendation | Rationale |
|----------|---------------|-----------|
| canonical_id | ACCEPT | Stable identity for Neo4j, APIs, cross-system reference |
| schema_version (CLAUDE.md) | ACCEPT | Machine-readable ontology version |
| schema_version (per-node) | REJECT | Premature; add on first breaking change |
| lifecycle | REJECT | Redundant with status + implementation_status |
| confidence expansion | Reconfirm: ACCEPT experimental | No further changes |
| evidence: design | ACCEPT | Fills gap for design-stage validation |
| source_quality | REJECT | Derivable |
| review_status | REJECT | Process mismatch; reconsider for multi-agent |
| interface_version | ACCEPT | Domain-specific, essential for contract stability |
| schema_version (on artifact_schema) | ACCEPT | Domain-specific, essential for data contract tracking |

Net new additions: +1 universal field (canonical_id), +1 evidence enum value (design), +2 domain-specific fields (interface_version, schema_version on schemas).

---

5. Adaptive Graph-RAG Routing

5.1 Baseline position

The addendum ACCEPTED intent-aware routing with a 10-entry routing table. This was modeled as a Context Pack Assembly Rules update, not an ontology change.

5.2 Strategic extension: Knowledge exploration

The user proposes adding: "Knowledge exploration → Concept." The dev_graph does not have a `concept` type — that is a wiki type. In the dev_graph, the equivalent entry point is `knowledge_asset`.

However, a pure knowledge exploration task ("help me understand how event sourcing applies to our system") should span BOTH the wiki (for domain knowledge) and the dev_graph (for engineering application). The routing should be:

```
Knowledge exploration → Knowledge Asset (dev_graph) + wiki concept pages (read-only)
```

This is the only routing entry that crosses the wiki/dev_graph boundary. It is justified because knowledge exploration is inherently a synthesis task that draws on both knowledge sources.

5.3 Extended routing table (11 entries)

| Task Intent | Primary Entry Point | Expansion Direction | Secondary Context | Cross-Boundary? |
|-------------|--------------------|--------------------|-------------------|-----------------|
| Implementation | Capability | Down: modules, files, tests | Interfaces, schemas, constraints | No |
| Architecture review | Architecture | Down: systems, capabilities | Knowledge assets, ADRs, patterns | No |
| Bug investigation | Module (or File) | Lateral: dependencies, interfaces | Tests, events, constraints | No |
| Integration | Interface | Lateral: both sides of contract | Schemas, modules, api_docs | No |
| Runtime incident | Event | Lateral: emitters, consumers | Workflows, modules, gates | No |
| Research | Knowledge Asset | Down: ADRs, architecture | Wiki source pages (read-only) | Yes |
| Governance | Constraint (or Governance) | Lateral: bound systems/capabilities | ADRs, gates, predicates | No |
| Evolution planning | Decision Record | Up: knowledge assets; Down: affected systems | Patterns, architecture | No |
| Performance | Benchmark | Lateral: measured modules | Schemas, interfaces, constraints | No |
| Design review | Pattern | Down: realizing modules/capabilities | Knowledge assets, ADRs | No |
| Knowledge exploration | Knowledge Asset | Lateral: related knowledge assets | Wiki concept pages (read-only) | Yes |

5.4 Token efficiency

Intent-aware routing improves token efficiency by reducing irrelevant context:

- Uniform capability entry: ~15-25 nodes retrieved per session, ~30-40% irrelevant for non-implementation tasks.
- Intent-aware entry: ~10-20 nodes retrieved per session, ~10-15% irrelevant.

Estimated token savings: 20-30% per context pack for non-implementation sessions.

5.5 Hallucination reduction

Precision improvements from intent-aware routing reduce hallucination in three ways:

1. Correct abstraction level: Architecture questions get architecture nodes, not module details. This prevents Claude from hallucinating implementation details when only architectural facts are available.
2. Relevant evidence: Bug investigations start at module/file level where the evidence is, not at capability level where it's abstracted away. This prevents Claude from reasoning about abstractions when concrete code is needed.
3. Bounded scope: Each entry point has defined expansion limits. Claude doesn't receive the entire graph — only the relevant subgraph. This reduces the probability of combining unrelated facts into incorrect conclusions.

Estimated hallucination reduction: 15-25% for non-implementation tasks.

5.6 Recommendation: ACCEPT

Reconfirm ACCEPT with the extended 11-entry routing table. Add Knowledge exploration as the 11th entry point. Document the cross-boundary protocol for research and knowledge exploration tasks.

---

6. Knowledge-to-Operation Continuum

6.1 Baseline position

The addendum accepted the Knowledge-to-Code Continuum as a conceptual model documented in CLAUDE.md. It rejected a frontmatter field (continuum_stage) as derivable from type.

6.2 The closed loop

The addendum's continuum was linear: Knowledge → Decision → Architecture → Capability → Implementation → Runtime → Evaluation → Evolution (back to Decision).

The strategic model is a closed loop with explicit stages:

```
                    ┌─────────────────────────────────────────────┐
                    │                                             │
                    ↓                                             │
    KNOWLEDGE ──→ DECISION ──→ ARCHITECTURE ──→ DESIGN ──→      │
    (knowledge_    (decision_    (architecture,   (pattern,       │
     asset)        record)       system,          interface,      │
                                 capability)      schema)         │
                                                    │             │
                                                    ↓             │
    EVALUATION ←── RUNTIME ←── VERIFICATION ←── IMPLEMENTATION   │
    (benchmark_    (event,       (test, gate,     (module, file)  │
     result)       workflow)     predicate)                       │
        │                                                         │
        └─────────────── EVOLUTION ───────────────────────────────┘
                        (new decision_record)
```

9 stages. Each stage maps to one or more ontology types. The mapping is deterministic from type, which is why a frontmatter field remains unnecessary.

6.3 What the closed loop enables

The loop enables three reasoning patterns impossible with a linear continuum:

1. Regression tracing: "A benchmark regression occurred in the Execution System. What knowledge assets and decisions led to the current design? Should the design change, or is the regression an implementation bug?" This traverses: EVALUATION → IMPLEMENTATION → DESIGN → ARCHITECTURE → DECISION → KNOWLEDGE, then evaluates whether the issue is at the architecture level (requiring a new ADR) or the implementation level (requiring a bug fix).

2. Impact prediction: "If we change Knowledge Asset 'Event Sourcing' to add financial compliance requirements, what downstream nodes are affected?" This traverses: KNOWLEDGE → DECISION (all ADRs that originate from this knowledge asset) → ARCHITECTURE → DESIGN → IMPLEMENTATION → VERIFICATION → RUNTIME → EVALUATION. The entire forward chain shows the blast radius.

3. Evolution planning: "The current guardrail architecture is producing too many false positives. Propose an evolution path." This traverses: EVALUATION (benchmark data showing false positive rate) → identify the relevant VERIFICATION nodes (which predicates are over-triggering?) → identify the IMPLEMENTATION (which modules implement those predicates?) → identify the DESIGN (which pattern do they follow?) → identify the ARCHITECTURE (is the pattern wrong or the implementation?) → propose a new DECISION (ADR) → optionally refine KNOWLEDGE (update the Guardrail Philosophy knowledge asset with lessons learned).

6.4 Recommendation: ACCEPT

Accept the closed-loop 9-stage continuum as the canonical conceptual backbone. Document in CLAUDE.md with the stage-to-type mapping table. Reject frontmatter field (derivable from type, as before). The loop closure is a governance process, not a mechanical edge — no new relationship types required.

---

7. Runtime Digital Twin

7.1 The question

Should the ontology model runtime instances — individual runs, trades, snapshots, evaluation scorecards — as ontology objects?

7.2 The three-substrate boundary

The project already has three data substrates:

| Substrate | Role | Strengths | Weaknesses |
|-----------|------|-----------|------------|
| Obsidian (markdown) | Authoring, governance, human-readable definitions | Semantic search, Dataview, wikilinks, narrative context | Poor for high-volume data, no transactions |
| Neo4j | Graph traversal, Graph-RAG, relationship queries | Path queries, subgraph extraction, pattern matching | Not for document authoring, poor for time series |
| PostgreSQL | Instance data, time series, aggregation | ACID transactions, SQL queries, high volume | No graph traversal, no semantic search |

Runtime instances are HIGH VOLUME (every trade creates records), TRANSACTIONAL (requires ACID), and TIME-SERIES (ordered by timestamp). These characteristics make PostgreSQL the correct substrate, not Obsidian.

7.3 What belongs where

The question is not "should we model runtime instances?" but "which substrate models what?"

Ontology (Obsidian): DEFINITIONS — what a runtime instance looks like, what events are possible, what workflows exist.

- Event nodes: define possible events (SnapshotCreated, OrderPlaced, StopTriggered)
- Workflow nodes: define process templates (Trade Pipeline, Office Action Loop)
- Schema nodes: define data shapes (Trade Log Schema, Evaluation Scorecard Schema)

These already exist in the audit_plan. They are the TYPES that runtime instances conform to.

Database (PostgreSQL): INSTANCES — individual trades, runs, snapshots, evaluations.

- Trade records: individual trade executions with timestamps, prices, outcomes
- Evaluation results: individual scorecard assessments
- Benchmark runs: individual performance measurements with metrics
- Run logs: individual agent execution traces

Bridge (both): The connection between definitions and instances.

The schema nodes in the ontology define the CONTRACT that database records must follow. The interface nodes define the API through which the runtime produces instances. This bridge already exists in the proposed ontology — no new types needed.

7.4 Runtime instance evaluation

Would runtime instance modeling in the ontology improve:

Replay: NO. Replay requires time-ordered instance data with full state. This is a database concern (PostgreSQL event store), not an ontology concern. The ontology defines WHAT can be replayed (via event and workflow nodes); the database stores WHAT ACTUALLY HAPPENED.

Debugging: PARTIALLY. The ontology helps debugging by answering structural questions ("which modules are involved in order execution?"), but actual debugging requires instance data ("what happened to order #12345?"). Structural context from the ontology + instance data from the database = complete debugging context. Neither alone is sufficient.

Observability: NO for instance-level. YES for structural-level. The ontology's observability dashboard monitors ontology health (stale nodes, missing frontmatter, orphans). Runtime observability (error rates, latency, throughput) is a monitoring system concern (Prometheus/Grafana or equivalent), not an ontology concern. The ontology defines WHAT to observe (via event nodes and workflow nodes); the monitoring system observes it.

Auditability: PARTIALLY. The ontology provides the audit FRAMEWORK (which constraints govern which systems, which gates must pass, which predicates are checked). The database stores the audit TRAIL (which constraints were checked when, which gates passed/failed, which predicates evaluated to what). The framework is essential for knowing WHAT to audit; the trail is essential for knowing WHAT HAPPENED.

Autonomous diagnosis: YES, if the ontology can traverse from a runtime symptom to the structural cause. Example: "Order execution is slow" → Event: OrderPlaced → Module: Order Router → Interface: Execution API → Depends On: Broker API → api_doc_source: Alpaca API Docs. This structural traversal is possible with current ontology types. Instance data (which specific orders were slow?) comes from the database.

7.5 Telemetry source nodes

One gap exists: the ontology does not define WHERE runtime data is stored or HOW to access it. If Claude is debugging a performance issue, it needs to know "trade records are in PostgreSQL table trading.executions" and "latency metrics are in Prometheus endpoint X."

This could be modeled as a `telemetry_source` type — lightweight reference nodes that define where runtime data lives. However, this is premature: no monitoring infrastructure exists yet. When it does, telemetry sources can be modeled as either:
- New api_doc_source nodes (the API doc type already serves as "pointer to external system")
- New reference nodes (the reference type already serves as "pointer to external artifact")
- A new telemetry_source type

The choice should be made when monitoring infrastructure is built, not speculatively now.

7.6 Recommendation: REJECT

Reject runtime instances as ontology objects. The three-substrate boundary is clear: Obsidian defines structures, Neo4j traverses relationships, PostgreSQL stores instances. Runtime instances belong in PostgreSQL, not in the ontology.

Accept that the ontology's event, workflow, and schema nodes are the structural DEFINITIONS that runtime instances conform to. These are already planned in the audit_plan.

Defer telemetry_source consideration until monitoring infrastructure exists.

---

8. Ontology Governance and Evolution

8.1 Current state

The dev_graph has governance mechanisms:
- CLAUDE.md as the operations manual
- Append-only enum evolution
- Additive field evolution
- 7 lint checks (structural)
- 3 maintenance cadences (per-session, weekly, monthly)
- Confidence lifecycle with promotion/demotion rules
- Dev Graph Governance node as root governance document

What's missing: ontology versioning, canonical identity, formal merge/split procedures, semantic drift detection, and migration runbooks.

8.2 Ontology versioning

Covered in Section 4.3. schema_version in CLAUDE.md tracks the ontology's structural evolution. Versioning is ACCEPTED.

8.3 Canonical identifiers

Covered in Section 4.2. canonical_id as a universal frontmatter field. ACCEPTED.

8.4 Merge strategy

When should two nodes be merged?

Trigger: Two nodes describe the same engineering concept from different perspectives (e.g., a module node and a capability node that both describe "order execution" at the same granularity).

Procedure:
1. Identify which node is at the correct abstraction level (type)
2. Migrate content from the subordinate node into the canonical node
3. Update all wikilinks pointing to the subordinate node
4. Set subordinate node to status: deprecated with a `### Supersedes` reference
5. Log merge in log.md

Governance rule: NEVER delete the subordinate node. Deprecate it with a redirect. This preserves link stability and Neo4j export history.

Assessment: ACCEPT. Document merge procedure in CLAUDE.md.

8.5 Split strategy

When should one node be split into two?

Trigger: A node covers two distinct engineering concepts that belong at different abstraction levels or in different systems (e.g., a module node that describes both order routing and position sizing).

Procedure:
1. Create two new nodes, each with correct type and system placement
2. Distribute content appropriately
3. The new nodes both reference the original via `### Supersedes` (they supersede it jointly)
4. Set original node to status: deprecated
5. Update all wikilinks from the original to the appropriate new node
6. Log split in log.md

Assessment: ACCEPT. Document split procedure in CLAUDE.md.

8.6 Deprecation strategy

The current approach ("set status: deprecated") is correct but incomplete. A deprecated node should also:
1. Have a `deprecated_reason` recorded (in the node body, not frontmatter — to avoid field proliferation)
2. Reference what replaces it (via `### Supersedes` section on the replacement node)
3. Be excluded from context packs (already handled by admissibility check #2)
4. Be retained indefinitely (never deleted — preserved for audit trail)
5. Be excluded from active Dataview counts but included in historical counts

Assessment: ACCEPT. Document deprecation procedure in CLAUDE.md. No new frontmatter fields — reason is recorded in the node body.

8.7 Stale node detection

Current: 30-day threshold (Dataview query #6 on the dashboard). Nodes not updated in 30 days and not deprecated are flagged.

Strategic enhancement: Differentiate stale thresholds by type. Knowledge assets and patterns are inherently stable — flagging them at 30 days creates noise. Implementation nodes (modules, files, tests) during active development should be flagged earlier.

Proposed thresholds:
- knowledge_asset, pattern, architecture: 180 days (stable by nature)
- system, capability, interface: 90 days (structural, evolve slowly)
- module, file, test: 30 days (active development)
- governance, constraint, decision_record: 120 days (governance cadence)
- event, workflow, schema: 60 days (behavioral, moderate change)
- All others: 30 days (default)

Implementation: Update Dataview query #6 on Dev Graph Dashboard with type-aware thresholds.

Assessment: ACCEPT. Type-aware staleness thresholds improve signal-to-noise for the governance process.

8.8 Ontology drift detection

Current lint checks detect STRUCTURAL drift (missing frontmatter, invalid enums, broken links, orphans). They do not detect SEMANTIC drift — a node whose content no longer matches its type or relationships.

Examples of semantic drift:
- A module node whose content describes an architectural decision (should be reclassified as decision_record)
- A relationship section listing a wikilink to a node that has been deprecated (should be updated)
- A knowledge asset whose source_wiki_pages reference wiki pages that have been substantially rewritten (the knowledge asset's summary may be stale)
- A pattern node with `instances: []` listing modules that no longer follow that pattern

Proposed: Add two new lint checks:

Check 8: Type-content alignment
Verify that a node's body sections match its type. A module node should have Implementation Notes. An ADR should have Status, Context, Decision, Consequences. A knowledge asset should have source_wiki_pages referencing live wiki pages.

This check cannot be fully automated in Dataview — it requires content analysis. It should be a per-session checklist item for nodes touched in the session and a monthly audit item for all nodes.

Check 9: Deprecated reference detection
```
Dataview: Find nodes whose relationship sections reference deprecated nodes
```
This IS automatable: check all wikilinks in relationship sections against nodes where status = deprecated.

Assessment: ACCEPT. Add Check 8 (manual, per-session + monthly) and Check 9 (automated, Dataview) to the lint workflow.

8.9 Automatic consistency checks

Current: 7 checks in CLAUDE.md. Proposed additions: Check 8 (type-content alignment) and Check 9 (deprecated reference detection) from Section 8.8. Also:

Check 10: Canonical ID uniqueness
Verify that no two nodes share the same canonical_id value. This is essential once canonical_id is universal.

Check 11: Evidence-confidence coherence
Verify that nodes with `confidence: confirmed` have `evidence: []` with at least one value. A node claiming confirmed confidence with no evidence source is suspect.

Assessment: ACCEPT Checks 9, 10, 11 (automated). ACCEPT Check 8 (manual checklist).

Total lint checks: 11 (7 existing + 4 new).

8.10 Human approval workflow

REJECT. The addendum's reasoning holds: the project's operational model is single-developer + AI agent. Formal multi-person approval workflows create governance overhead without active participants to fulfill the roles. If the project scales to multiple human contributors, add review_status at that time.

8.11 Semantic migration strategy

When the ontology schema changes (new types, new fields, new relationships), existing nodes may need migration. The current approach is informal: "update affected nodes." A formal migration strategy prevents partial migration (some nodes updated, others not).

Proposed migration runbook template:

```
# Migration: [schema_version] → [new_version]

## Changes
- [list of schema changes]

## Affected Nodes
- [list of nodes that need updating, or Dataview query that identifies them]

## Migration Steps
1. Update CLAUDE.md with new schema
2. Create ADR documenting the change
3. Run migration queries/scripts
4. Verify with lint checks
5. Update schema_version in CLAUDE.md
6. Log migration in log.md

## Rollback
- [procedure if migration fails]

## Verification
- [Dataview queries that confirm migration success]
```

Assessment: ACCEPT. Document the migration runbook template in CLAUDE.md or as a governance node.

8.12 Recommendation: ACCEPT

Accept ontology governance as a first-class engineering concern. Specific acceptances:

| Proposal | Recommendation |
|----------|---------------|
| schema_version in CLAUDE.md | ACCEPT |
| canonical_id universal field | ACCEPT |
| Merge procedure | ACCEPT (document in CLAUDE.md) |
| Split procedure | ACCEPT (document in CLAUDE.md) |
| Deprecation procedure | ACCEPT (document in CLAUDE.md) |
| Type-aware stale thresholds | ACCEPT |
| Check 8: Type-content alignment | ACCEPT (manual) |
| Check 9: Deprecated reference detection | ACCEPT (automated) |
| Check 10: Canonical ID uniqueness | ACCEPT (automated) |
| Check 11: Evidence-confidence coherence | ACCEPT (automated) |
| Migration runbook template | ACCEPT |
| Human approval workflow | REJECT |
| Semantic migration strategy | ACCEPT |

---

9. Engineering Digital Twin Assessment

9.1 Reframing the question

The addendum asked: "Should the dev_graph become a digital twin?" The strategic answer is: the dev_graph already IS a digital twin in architecture. The three-substrate model (Obsidian + Neo4j + PostgreSQL) IS the engineering digital twin. The question is not whether to BUILD one but how to RECOGNIZE and GOVERN what already exists.

```
┌─────────────────────────────────────────────────────────────┐
│                  ENGINEERING DIGITAL TWIN                    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐      │
│  │ LAYER 1: Ontology (Obsidian/Markdown)             │      │
│  │ - Definitions, governance, relationships          │      │
│  │ - 24 types, 17 relationships                      │      │
│  │ - Human-readable, semantically searchable         │      │
│  │ - ~100-150 nodes at maturity                      │      │
│  └───────────────────┬───────────────────────────────┘      │
│                      │ sync_to_neo4j.py                     │
│  ┌───────────────────▼───────────────────────────────┐      │
│  │ LAYER 2: Graph Engine (Neo4j)                     │      │
│  │ - Traversal, Graph-RAG, impact analysis           │      │
│  │ - Same nodes and edges as Layer 1                 │      │
│  │ - Optimized for path queries and pattern matching │      │
│  └───────────────────┬───────────────────────────────┘      │
│                      │ interface/schema contracts            │
│  ┌───────────────────▼───────────────────────────────┐      │
│  │ LAYER 3: Instance Store (PostgreSQL)              │      │
│  │ - Runtime data, trades, evaluations, telemetry    │      │
│  │ - High volume, transactional, time-series         │      │
│  │ - Conforms to schemas defined in Layer 1          │      │
│  └───────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

9.2 What the twin integrates

With the audit_plan + addendum + this review, the digital twin integrates:

| Dimension | Substrate | Ontology Types | Status |
|-----------|-----------|---------------|--------|
| Knowledge | Obsidian | knowledge_asset | Planned (this review) |
| Architecture | Obsidian | architecture, system, capability | Planned (audit_plan) |
| Patterns | Obsidian | pattern | Planned (this review) |
| Interfaces | Obsidian | interface, artifact_schema | Planned (audit_plan) |
| Implementation | Obsidian | module, file, test | Planned (audit_plan) |
| Behavior | Obsidian | event, workflow | Planned (audit_plan) |
| Quality | Obsidian | gate, predicate | Existing + planned |
| Governance | Obsidian | constraint, governance, decision_record | Existing |
| Evidence | Obsidian | benchmark_result | Existing |
| Agents | Obsidian | agent, skill | Existing |
| Documentation | Obsidian | api_doc_source, reference | Existing |
| Observability | Obsidian | observability, context_pack | Existing |
| Runtime instances | PostgreSQL | (defined by schema nodes) | Future |
| Graph traversal | Neo4j | (mirrors Obsidian) | Planned |

12 of 14 dimensions are already modeled or planned. The remaining two (runtime instances, graph traversal) require no ontology changes — they are infrastructure activations.

9.3 Advantages

Complete engineering model: Claude can reason about the system from foundational knowledge through architecture through implementation through verification. No dimension requires leaving the ontology to find context.

Autonomous planning: Claude can propose implementation plans by traversing Architecture → System → Capability → Module, referencing relevant patterns and interfaces, checking constraints, and assembling context packs. The entire planning process is graph-navigable.

Consistent governance: All dimensions share the same governance framework (canonical ownership, frontmatter, confidence lifecycle, lint checks). This prevents governance fragmentation across tools.

Evolutionary coherence: The closed-loop continuum ensures that evaluation results feed back into knowledge and decisions, preventing architectural decay where implementation diverges from design intent.

9.4 Risks

Complexity ceiling: At 24 types and 17 relationships, the ontology approaches the limit of what a single operations manual can govern. Beyond ~30 types, CLAUDE.md becomes unwieldy and the governance surface exceeds a single agent's working memory.

Mitigation: The current 24 types is near but not beyond the ceiling. The ontology should resist further type additions unless they provide substantial retrieval or reasoning value. Future needs should be met by subtyping (via frontmatter fields like pattern_type, knowledge_type) rather than new top-level types.

Map-territory inversion: If maintaining the ontology takes more effort than writing code, the cost-benefit inverts.

Mitigation: The node creation protocol should be "just-in-time, not just-in-case." Nodes are created when they are needed for implementation, not speculatively. The audit_plan's phased migration (create nodes as code work begins) already enforces this.

Scalability: At ~150 nodes, per-session lint takes 2-5 minutes. At ~300 nodes, it could take 10-15 minutes — significant overhead for a coding session.

Mitigation: Scope lint to touched nodes per-session. Full lint weekly. Type-aware stale thresholds (Section 8.7) reduce false positives. Neo4j can handle automated consistency checks at scale that Dataview cannot.

9.5 Long-term scalability assessment

| Node Count | Obsidian | Neo4j | Lint Overhead | Recommendation |
|-----------|---------|-------|--------------|----------------|
| 50-100 | Excellent | Good | Trivial | Normal operations |
| 100-200 | Good | Excellent | Manageable | Shift complex queries to Neo4j |
| 200-400 | Adequate | Excellent | Moderate | Automate lint via Neo4j; Obsidian for authoring only |
| 400+ | Strained | Excellent | High | Consider splitting ontology into sub-domains with federation |

The practical ceiling for the markdown-first model is ~200-300 nodes. Beyond that, Neo4j becomes the primary query substrate and Obsidian serves as the authoring interface. The sync_to_neo4j.py script becomes the critical infrastructure.

9.6 Compatibility with autonomous Claude-assisted development

HIGH. The ontology is designed for Claude consumption:

- Frontmatter is machine-readable YAML
- Relationship sections use predictable headers
- Wikilinks are parseable
- The closed-loop continuum provides navigation logic
- Intent-aware routing selects entry points
- Admissibility checks filter context packs
- Canonical IDs enable stable cross-references

The primary barrier to full autonomy is not the ontology — it is the absence of application code. Once code exists, the ontology provides the structural scaffold for autonomous implementation sessions.

9.7 Recommendation: ACCEPT

Accept the three-layer Engineering Digital Twin (Obsidian + Neo4j + PostgreSQL) as the canonical architecture. The ontology (Obsidian) is the definition layer. Neo4j is the traversal layer. PostgreSQL is the instance layer. Each layer has clear responsibilities and clear boundaries.

No new types or relationships required for this recognition — the digital twin is the ARCHITECTURE, not a feature.

---

10. Deliverables

10.1 Critical assessment of the current ontology

The combined target state (audit_plan + addendum) provides a strong hierarchical engineering ontology with knowledge foundations. Three strategic gaps remain: lack of stable identity (canonical_id), lack of self-governance (versioning, drift detection), and an open-ended traceability chain (no closed loop). This review addresses all three.

10.2 Missing abstraction layers

No additional abstraction layers beyond those already proposed (knowledge_asset, pattern). The 9-stage closed-loop continuum provides the conceptual organization. Adding further layers (e.g., "strategy layer," "operations layer") would exceed the complexity ceiling without proportional retrieval value.

10.3 Recommended new ontology types

None beyond the two already accepted (knowledge_asset, pattern). The strategic recommendation is to RESIST further type additions and use subtyping via frontmatter fields instead.

Type ceiling: 24 types (22 from audit_plan + knowledge_asset + pattern).
Hard limit: 30 types. Beyond this, the governance surface exceeds a single operations manual.

10.4 Recommended new relationships

| Relationship | Semantics | Between | Recommendation |
|-------------|-----------|---------|---------------|
| Composes | Structural composition | Pattern → Pattern | ACCEPT |
| All other proposals from Section 3.4 | — | — | REJECT or already covered |

Total: 17 relationships (16 from addendum + Composes).

10.5 Universal metadata proposal

| Field/Change | Recommendation | Scope |
|-------------|---------------|-------|
| canonical_id | ACCEPT | Universal — all content nodes |
| schema_version (CLAUDE.md) | ACCEPT | Governance — CLAUDE.md header |
| evidence: design | ACCEPT | Enum append — evidence field |
| interface_version | ACCEPT | Domain-specific — interface nodes |
| schema_version (artifact_schema) | ACCEPT | Domain-specific — schema nodes |
| measures: [] | ACCEPT | Domain-specific — benchmark_result nodes |
| lifecycle | REJECT | Redundant |
| source_quality | REJECT | Derivable |
| review_status | REJECT | Premature |
| per-node schema_version | REJECT | Premature |

10.6 End-to-end traceability model

The 9-stage closed-loop continuum:

```
KNOWLEDGE → DECISION → ARCHITECTURE → DESIGN → IMPLEMENTATION →
VERIFICATION → RUNTIME → EVALUATION → EVOLUTION → KNOWLEDGE
```

Loop closure mechanism: governance process (evidence field + originates_from relationship), not mechanical edges.

Traversal directions:
- Forward (downstream): "What does this knowledge asset produce?"
- Backward (upstream): "Why does this module exist?"
- Lateral (cross-cutting): "What patterns does this system follow?"
- Cyclical (evolution): "What benchmarks triggered this ADR?"

10.7 Adaptive Graph-RAG routing strategy

11-entry intent-aware routing table (Section 5.3). Implemented as a Context Pack Assembly Rules update. Estimated 30-40% precision improvement for non-implementation tasks. 20-30% token savings per context pack. 15-25% hallucination reduction.

10.8 Runtime Digital Twin assessment

REJECT runtime instances as ontology objects. The three-substrate boundary is clear:
- Obsidian: definitions
- Neo4j: traversal
- PostgreSQL: instances

Runtime schemas (event nodes, workflow nodes, artifact_schema nodes) already define what runtime instances look like. Individual instances belong in PostgreSQL.

Defer telemetry_source type consideration until monitoring infrastructure exists.

10.9 Ontology governance strategy

ACCEPT ontology governance as a first-class concern:

| Component | Status |
|-----------|--------|
| schema_version tracking | ACCEPT |
| canonical_id universal field | ACCEPT |
| Merge procedure | ACCEPT (document in CLAUDE.md) |
| Split procedure | ACCEPT (document in CLAUDE.md) |
| Deprecation procedure | ACCEPT (enhance current) |
| Type-aware stale thresholds | ACCEPT |
| 4 new lint checks (#8-#11) | ACCEPT |
| Migration runbook template | ACCEPT |
| Human approval workflow | REJECT |

Total lint checks after this review: 11 (7 existing + 4 new).

10.10 Engineering Digital Twin assessment

ACCEPT. The digital twin is the three-layer architecture (Obsidian + Neo4j + PostgreSQL), not a feature to be built. The ontology IS the definition layer of the twin. Recognizing this architecture provides strategic clarity for all future decisions about where data belongs.

10.11 Migration strategy

All changes from this review integrate into the existing phased migration:

| Phase | Audit Plan | Addendum | This Review |
|-------|-----------|----------|-------------|
| Phase 0 | CLAUDE.md update, ADR | +2 types, +3 relationships, +evidence field, +experimental | +canonical_id field, +schema_version, +Composes relationship, +measures field, +interface_version/schema_version on domain types, +evidence:design, +4 lint checks, +merge/split/deprecation procedures, +migration runbook, +type-aware stale thresholds, +closed-loop continuum documentation, +intent-aware routing (11-entry) |
| Phase 1 | 3 architecture nodes | +5-10 knowledge assets | Assign canonical_id to all new + existing nodes |
| Phase 2 | 6 systems + lifecycle workflow | (no change) | (no change) |
| Phase 3 | ~20 capabilities | +8-10 patterns | Add Composes edges between patterns |
| Phase 4 | ~12-15 interfaces + schemas | +justified_by, realizes edges | Add interface_version, schema_version to domain nodes |
| Phase 5+ | Modules, gates, events, files, tests | +originates_from, evidence on all new nodes | Add measures: [] to benchmark nodes |

Phase 0 is the largest governance update. It should be executed as a single atomic CLAUDE.md revision + ADR, before any content nodes are created.

10.12 Summary decision table

| Proposal | Recommendation | Strategic Justification |
|----------|---------------|------------------------|
| Knowledge Asset type | ACCEPT | Foundation of architectural traceability; upgrade from PARTIALLY ACCEPT |
| Pattern type | ACCEPT | Essential shared vocabulary for autonomous agents; upgrade from PARTIALLY ACCEPT |
| Composes relationship | ACCEPT | Pattern hierarchy; narrowly scoped (Pattern → Pattern only) |
| Closed-loop continuum | ACCEPT | Conceptual backbone; enables regression tracing and evolution planning |
| canonical_id field | ACCEPT | Stable identity across substrates; strategic infrastructure |
| schema_version (CLAUDE.md) | ACCEPT | Machine-readable ontology versioning |
| evidence: design | ACCEPT | Fills gap for pre-code validation evidence |
| interface_version field | ACCEPT | Contract stability tracking |
| schema_version (artifact_schema) | ACCEPT | Data contract versioning |
| measures: [] (benchmark) | ACCEPT | Benchmark-to-module tracing |
| Type-aware stale thresholds | ACCEPT | Reduces governance noise |
| 4 new lint checks | ACCEPT | Semantic drift and consistency |
| Merge/split/deprecation procedures | ACCEPT | Governance completeness |
| Migration runbook template | ACCEPT | Controlled schema evolution |
| 11-entry intent-aware routing | ACCEPT | Extended from addendum's 10-entry table |
| Three-layer Digital Twin | ACCEPT | Architectural recognition, not new build |
| Runtime instances in ontology | REJECT | Wrong substrate; belongs in PostgreSQL |
| lifecycle metadata | REJECT | Redundant with existing two-field model |
| source_quality metadata | REJECT | Derivable |
| review_status metadata | REJECT | Premature for current operational model |
| per-node schema_version | REJECT | Premature; add on first breaking change |
| Human approval workflow | REJECT | Process mismatch |
| measured_by relationship | REJECT | Modeled as frontmatter measures: [] instead |
| evolves_into relationship | REJECT | Covered by Supersedes in reverse |
| feeds_back_to relationship | REJECT | Mediated by governance process, not mechanical edge |
| derived_from relationship | REJECT | Covered by Contains |
| operationalizes relationship | REJECT | Covered by Implements |
| Telemetry source type | DEFER | Reconsider when monitoring infrastructure exists |

---

Cumulative Ontology State After All Three Documents

| Dimension | Bootstrap (ADR-001) | After Audit Plan | After Addendum | After This Review |
|-----------|--------------------|--------------------|---------------|-------------------|
| Types | 17 | 22 (+5) | 24 (+2) | 24 (no change) |
| Relationships | 8 | 13 (+5) | 16 (+3) | 17 (+1: Composes) |
| Directories | 16 | 21 (+5) | 23 (+2) | 23 (no change) |
| Universal fields | 11 | 11 | 12 (+evidence) | 13 (+canonical_id) |
| Confidence values | 4 | 4 | 5 (+experimental) | 5 (no change) |
| Evidence values | — | — | 6 | 7 (+design) |
| Lint checks | 7 | 7 | 7 | 11 (+4) |
| Continuum model | — | — | Linear (8 stages) | Closed loop (9 stages) |
| Routing entries | — | — | 10 | 11 (+knowledge exploration) |
| Schema version | — | — | — | 2.2.0 |
| Domain-specific fields | ~15 | ~25 | ~25 | ~28 (+interface_version, schema_version, measures) |

---

Backward Compatibility

All recommendations are purely additive:
- 0 type additions (knowledge_asset and pattern already accepted in addendum)
- 1 new relationship type (Composes — Pattern → Pattern only)
- 1 new universal field (canonical_id)
- 1 new evidence enum value (design)
- 3 new domain-specific fields (interface_version, schema_version on schemas, measures on benchmarks)
- 4 new lint checks
- 0 existing fields changed
- 0 existing relationships renamed or removed
- 0 existing nodes modified (canonical_id rollout is Phase 1)

Full backward compatibility is maintained across all three documents.

---

Strategic Horizon

The ontology is now architecturally complete for autonomous software engineering. The 24-type, 17-relationship, closed-loop model with stable identity, intent-aware retrieval, and three-substrate architecture provides:

- Complete traceability from knowledge through implementation to evaluation
- Pattern-aware design guidance
- Intent-specific retrieval precision
- Stable cross-system identity
- Self-governing schema evolution
- Clear substrate boundaries (Obsidian/Neo4j/PostgreSQL)

Future ontology evolution should focus on:
1. Subtyping within existing types (via frontmatter fields) rather than new types
2. Neo4j query templates that exploit the closed-loop continuum
3. Context pack assembly automation using intent-aware routing
4. Benchmark-driven governance (automated staleness detection via Neo4j)
5. Telemetry integration when runtime infrastructure exists

The ontology does not need to grow larger. It needs to be POPULATED.

---

End of Final Strategic Ontology Review.
