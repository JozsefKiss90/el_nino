Architecture Review Addendum — Engineering Knowledge Graph Extension

---

Scope

This addendum extends the Dev Graph Ontology Redesign (audit_plan.md) with an assessment of whether the ontology should evolve into a complete Engineering Knowledge Graph. It evaluates seven proposed extensions against the criteria of architectural traceability, engineering reasoning, retrieval quality, explainability, maintainability, autonomous agent planning, and Graph-RAG precision.

The baseline proposal (audit_plan.md) is accepted in full. This addendum proposes only additive extensions that preserve backward compatibility.

---

0. Critical Review of the Current Ontology

The audit_plan proposal is architecturally sound. Its hierarchy (Architecture → System → Capability → Module → File) solves the five most damaging weaknesses of the original flat model: no hierarchy, no system boundaries, no interface contracts, no capabilities, and no runtime events. The 22-type ontology with 13 relationship types is well-structured and internally consistent.

Five gaps remain:

0.1 No "why" layer. The hierarchy models WHAT the system is (architecture), WHERE code lives (modules), and WHEN things happen (events), but not WHY the architecture is shaped this way. ADRs capture individual decisions ("we chose event-driven architecture") but not the foundational engineering knowledge that motivated them ("Event Sourcing is a pattern for..."). The chain from knowledge to implementation is broken at the top.

0.2 Pattern-blind. The proposal identifies pattern use implicitly — the Supervisor Office follows the Supervisor Pattern, the Risk Control system follows the Guardrail Pattern, the Trade Pipeline follows the Pipeline Pattern — but patterns are not first-class objects. When Claude encounters a new subsystem, there is no canonical reference defining which pattern applies and what its structural constraints are.

0.3 Weak upward traceability. The proposed relationships support strong downward traversal (Architecture → System → Capability → Module → File) and cross-cutting traversal (Constraints → Systems, Events → across boundaries). But upward traversal — "why does this module exist?" — requires reading wiki source pages (untyped prose), not following typed relationship edges. A developer or agent asking "justify this code" gets a narrative, not a traceable chain.

0.4 Uniform retrieval assumption. The proposal recommends capabilities as the primary retrieval entry point. This is correct for implementation tasks (~60% of sessions) but suboptimal for architecture questions, bug investigations, governance reviews, design reviews, and evolution planning — each of which has a natural entry point at a different abstraction level.

0.5 Implicit evidence model. The confidence field (confirmed, single-source, inferred, speculative) grades trust but not provenance. A confirmed node doesn't tell you WHETHER it was confirmed by running code, passing benchmarks, wiki synthesis from two sources, or external documentation. This matters for autonomous reasoning: confidence from benchmarks is more durable than confidence from wiki synthesis.

---

1. Knowledge Layer Review

1.1 The gap

The wiki answers "what do we know?" The dev_graph answers "what must we build?" Neither answers "why is the architecture shaped this way?"

Engineering knowledge — the abstract principles, methodologies, and external guidance that motivate architectural decisions — currently lives in three places:
- Wiki narrative pages (Architecture Overview, Syndicate Squad Architecture)
- Raw source documents (llm-wiki.md, ows-dev-squad.md)
- Implicit assumptions in ADRs

None of these are typed, linked, or retrievable as engineering knowledge.

Examples of unmodeled knowledge:
- Event Sourcing as a principle → motivates the event-driven architecture
- CQRS → shapes read/write separation in the Data Pipeline
- Supervisor Pattern methodology (from OWS Dev Squad) → shapes the Supervisor Office
- Office Action methodology → shapes the upgrade workflow
- Anthropic engineering guidance → shapes agent safety constraints
- Layer 2 design principles → shapes the snapshot-as-truth-layer architecture
- Guardrail philosophy → shapes the Risk Control system design

1.2 Ontology role

Knowledge assets sit ABOVE architecture in the abstraction hierarchy:

Knowledge Asset → (originates_from) → ADR → (shapes) → Architecture → System → Capability → Module → File

They are the conceptual foundations that make the architecture non-arbitrary. Without them, ADRs say "we decided X" but not "we decided X because principle Y and methodology Z."

1.3 Relationship to wiki

Knowledge assets are NOT wiki page duplicates. The wiki page "Syndicate Squad Architecture" is a 2000-word narrative synthesis. A knowledge asset "Supervisor Pattern" is a 200-word engineering-scoped reference that:
- Names the principle
- States its core structural constraints
- Links to wiki pages where it's discussed in full
- Links to ADRs it has influenced
- Links to systems/capabilities that implement it

Direction of reference: knowledge_asset → wiki pages (for full context), ADR → knowledge_asset (for justification), architecture → knowledge_asset (for foundation).

1.4 Relationship to ADRs

ADRs capture SPECIFIC decisions. Knowledge assets capture GENERAL principles. An ADR may cite multiple knowledge assets; a knowledge asset may be cited by multiple ADRs. This is a many-to-many relationship via the `originates_from` edge.

Example:
- ADR "Use Event-Driven Architecture" → originates_from → Knowledge Asset "Event Sourcing"
- ADR "Use Event-Driven Architecture" → originates_from → Knowledge Asset "CQRS"
- Knowledge Asset "Supervisor Pattern" → cited_by → ADR "Supervisor Office Design"
- Knowledge Asset "Supervisor Pattern" → cited_by → ADR "Office Action Loop Design"

1.5 Relationship to capabilities

Capabilities define WHAT the system can do. Knowledge assets explain WHY the capability is designed the way it is. This is not a structural relationship but an explanatory one — useful for Graph-RAG but not for containment navigation.

1.6 Graph-RAG benefits

HIGH for research and architecture questions. When Claude is asked "why is the trading engine event-driven?", current retrieval returns wiki prose and hopes semantic search finds the right passages. With knowledge assets, retrieval follows: "event-driven" → Knowledge Asset "Event Sourcing" → links to ADRs and architecture nodes → complete justification chain.

MEDIUM for implementation tasks. Most coding sessions don't need to trace all the way to foundational principles. But when a developer questions an architectural choice mid-implementation, knowledge assets provide instant justification without wiki page reading.

1.7 Maintenance cost

VERY LOW. Knowledge assets represent foundational concepts that change rarely — Event Sourcing doesn't evolve, the Supervisor Pattern methodology doesn't change session to session. Estimated 10-15 nodes total, each updated perhaps once per quarter.

1.8 Frontmatter extension

```yaml
knowledge_id: <string>
knowledge_type: principle|methodology|guidance|pattern_theory
source_wiki_pages: []
informs_decisions: []
informs_architecture: []
external_references: []
```

1.9 Recommendation: PARTIALLY ACCEPT

Accept `knowledge_asset` as type #23 with its own directory `knowledge_assets/`. Accept the `originates_from` relationship (ADR → Knowledge Asset).

Constraints:
- Maximum 15 knowledge asset nodes at bootstrap. If a knowledge asset cannot be linked to at least one ADR, it does not warrant a node.
- Knowledge assets are POINTERS, not encyclopedias. Brief engineering-scoped summaries only. Full knowledge lives in the wiki.
- Knowledge assets do NOT have `implementation_status` (they are never "implemented" — they are conceptual foundations).
- Add to Phase 1 or Phase 2 of migration, since they provide root context for architecture nodes.

---

2. Pattern Library Review

2.1 The gap

The wiki has an empty `patterns/` domain (declared in the domain enum but no files exist). The dev_graph does not model patterns. The audit_plan identifies pattern use implicitly — Supervisor Pattern, Pipeline Pattern, Guardrail Pattern — but treats them as emergent properties of the hierarchy rather than first-class objects.

2.2 What patterns are NOT

Patterns are not systems. A system is an instance (Trading Engine); a pattern is reusable across instances (Pipeline Pattern).
Patterns are not workflows. A workflow defines sequential steps (Trade Pipeline); a pattern defines a structural template (Pipeline Pattern, which the Trade Pipeline follows).
Patterns are not modules. A module is a code boundary (Order Router); a pattern is an architectural blueprint.
Patterns are not capabilities. A capability defines WHAT (Signal Generation); a pattern defines a proven HOW (Event Sourcing Pattern for signal propagation).

2.3 Candidate patterns

From the audit_plan's object hierarchy, the following patterns are implicitly present:

| Pattern | Where It Appears | Instances |
|---------|-----------------|-----------|
| Supervisor Pattern | Supervisor Office system | Decision Engine, Agent orchestration |
| Guardrail Pattern | Risk Control system | Trade Validation Gate, all predicates |
| Evaluation Loop Pattern | Evaluation Loop system | Scorecard → Promotion cycle |
| Pipeline Pattern | Trade Pipeline workflow | Research → Signal → Validation → Execution → Journaling |
| Event Sourcing Pattern | Events throughout | SnapshotCreated, SignalGenerated, OrderPlaced, etc. |
| Context Assembly Pattern | Agent Runtime system | Context Assembler module |
| Treasury Approval Pattern | Supervisor Office | Treasury Approval Gate + Budget Available predicate |
| Promotion Pattern | Evaluation Loop | Paper Trading Promotion Gate + lifecycle transitions |
| CQRS Pattern | Data Pipeline + Trading Engine | Snapshot read model vs. trading write model |
| Multi-Agent Coordination | Supervisor Office | Supervisor Agent + Evaluator Agent orchestration |

2.4 Ontology relationships

Should modules IMPLEMENT patterns? YES. A module's `## Relationships` section should include `### Realizes` with pattern references. This tells Claude "this module follows the Guardrail Pattern — here are the structural constraints."

Should capabilities REALIZE patterns? YES, but at a higher level. A capability like "Guardrail Enforcement" realizes the "Guardrail Pattern." This is useful for architecture-level reasoning.

Should architecture COMPOSE patterns? YES. The Context Map (architecture node) should reference the patterns that shape the overall topology. "The system composes the Pipeline Pattern (data flow), Supervisor Pattern (governance), and Event Sourcing Pattern (state management)."

2.5 Lifecycle

Patterns have a simpler lifecycle than implementation nodes:
- `status`: active, deprecated (not planned, implemented, validated — patterns are not implemented, they are referenced)
- No `implementation_status` field (patterns are never "implemented" — modules implement patterns)
- `confidence`: confirmed, single-source, inferred (not speculative — if a pattern is speculative, it shouldn't be modeled)

2.6 Graph-RAG benefits

MEDIUM-HIGH for design reviews and new subsystem implementation. When Claude needs to implement a new capability, knowing which pattern to follow provides structural guidance that's more actionable than wiki prose. "Implement this following the Guardrail Pattern" is more precise than "look at how risk control works."

MEDIUM for ongoing coding. Most coding sessions work within established patterns and don't need to reference the pattern definition. But when architectural questions arise, patterns provide quick answers.

2.7 Maintenance cost

LOW. Patterns are extremely stable — the Supervisor Pattern doesn't change. ~10 pattern nodes, each updated rarely. The main maintenance cost is ensuring that new modules correctly reference the patterns they follow.

2.8 Frontmatter extension

```yaml
pattern_id: <string>
pattern_type: structural|behavioral|governance|coordination
instances: []
realized_by_capabilities: []
realized_by_modules: []
related_knowledge: []
```

2.9 Recommendation: PARTIALLY ACCEPT

Accept `pattern` as type #24 with its own directory `patterns/`. Accept the `realizes` relationship (Module/Capability → Pattern).

Constraints:
- Maximum 10-12 pattern nodes at bootstrap. A pattern must be instantiated by at least 2 modules or capabilities to warrant a node. One-off solutions are not patterns.
- Patterns are REFERENCE nodes with simplified lifecycle (no `implementation_status`).
- Patterns link DOWN to implementations and UP to knowledge assets.
- Add to Phase 3 (alongside capabilities), since capabilities reference patterns.
- Patterns live in the dev_graph, not the wiki. The wiki's empty `patterns/` domain is for TRADING patterns (strategy patterns). Engineering patterns belong in the dev_graph.

---

3. Engineering Traceability

3.1 The gap

The audit_plan establishes a structural hierarchy (Contains, Implements) and behavioral relationships (Emits, Triggered By, Guards) on top of the 8 existing relationship types. Total: 13 relationship types.

Missing: explicit traceability edges that answer "why does this exist?" upward and "how is this validated?" downward across the full chain.

3.2 The traceability chain

With knowledge assets and patterns added, the full chain becomes:

```
Knowledge Asset        (WHY — foundational principle)
    ↓ originates_from
Decision Record        (WHEN — specific decision point)
    ↓ justified_by
Architecture           (WHAT — structural shape)
    ↓ Contains
System                 (WHERE — bounded context)
    ↓ Contains
Capability             (WHAT — abstract behavior)
    ↓ Contains / Implements
Module                 (HOW — code boundary)
    ↓ Contains
File                   (HOW — source code)
    ↓ Validated By
Test                   (PROOF — verification)
```

Cross-cutting:
```
Pattern ←── realizes ──→ Module/Capability
Constraint ←── Constrained By ──→ System/Capability/Module
Interface ←── Implements ──→ Module
Event ←── Emits / Triggered By ──→ Module/Workflow
Gate ←── Guards ──→ Workflow
```

3.3 Proposed new relationship types

Evaluate each against the three criteria: (a) no semantic overlap with existing relationships, (b) answers a question that existing relationships cannot, (c) maintenance cost is justified by retrieval value.

| Proposed | Semantics | Overlap? | Question Answered | Recommendation |
|----------|-----------|----------|-------------------|----------------|
| originates_from | ADR → Knowledge Asset | None | "What principle motivated this decision?" | ACCEPT |
| justified_by | Module/Capability → ADR | Partial with `related_decisions` frontmatter | "Which decision authorized this code?" | ACCEPT (stronger than frontmatter array) |
| realizes | Module/Capability → Pattern | None | "Which pattern does this follow?" | ACCEPT |
| derived_from | System → Architecture | Overlaps with `Contains` | "Which architecture defines this system?" | REJECT — use Contains |
| operationalizes | Module → Capability | Overlaps with `Implements` | "Which capability does this make real?" | REJECT — use Implements |
| validated_by | (already exists) | Exact duplicate | — | Already in ontology |

3.4 Traceability queries enabled

With 3 new relationship types, Claude can answer:

Forward (why → what → how → proof):
- "Why does the Guardrail Engine exist?"
  → Guardrail Engine → justified_by → ADR "Risk Control Design" → originates_from → Knowledge Asset "Guardrail Philosophy"

Reverse (proof → how → what → why):
- "What principle is this test validating?"
  → test_guardrail_engine → Validated By → Guardrail Engine → justified_by → ADR → originates_from → Knowledge Asset

Pattern discovery:
- "What else follows the Supervisor Pattern?"
  → Pattern "Supervisor Pattern" → realized_by → [Decision Engine, Action Orchestrator, Supervisor Agent]

3.5 Recommendation: PARTIALLY ACCEPT

Accept 3 new relationship types: `originates_from`, `justified_by`, `realizes`.
Reject 3 proposed types: `derived_from`, `operationalizes`, `validated_by` (redundant).

Total relationship types: 16 (13 from audit_plan + 3 new).

Each new relationship is modeled as a `### Relationship_Name` subsection in the `## Relationships` section of affected nodes, consistent with the existing convention.

---

4. Universal Object Metadata

4.1 Current state

The dev_graph universal schema has 11 fields: type, status (7 values), implementation_status (7 values), canonical, created, updated, confidence (4 values), source_paths, related_files, related_tests, related_constraints, related_decisions.

The proposal evaluates 5 new universal metadata dimensions.

4.2 Lifecycle field

**Proposed**: lifecycle: draft → proposed → approved → implemented → validated → deprecated → archived

**Assessment**: REJECT.

The existing `status` (7 values: active, planned, implemented, validated, deprecated, blocked, draft) and `implementation_status` (7 values) already cover this entire lifecycle. The proposed lifecycle enum maps directly:
- draft → status: draft
- proposed → status: planned
- approved → status: active
- implemented → implementation_status: implemented
- validated → implementation_status: validated
- deprecated → status: deprecated
- archived → status: deprecated + implementation_status: deprecated

Adding a third lifecycle dimension creates semantic overlap and governance confusion. Which field is authoritative when `status: active` but `lifecycle: proposed`? The current two-field model (status for ontology lifecycle, implementation_status for code lifecycle) is cleaner.

4.3 Confidence expansion

**Proposed**: canonical, validated, inferred, experimental, deprecated

**Assessment**: REJECT as expansion. ACCEPT `experimental` as an append to the existing enum.

Current confidence enum (confirmed, single-source, inferred, speculative) is well-calibrated and operationally proven. The proposed values overlap heavily:
- canonical → already a boolean field (`canonical: true`)
- validated → ≈ confirmed
- inferred → identical
- experimental → genuinely new — captures nodes that are hypothetical engineering artifacts not yet grounded in sources
- deprecated → already in `status` enum

Append `experimental` to confidence enum: `confirmed`, `single-source`, `inferred`, `speculative`, `experimental`.

4.4 Evidence field

**Proposed**: evidence: wiki, layer2, code, benchmark, ADR, external

**Assessment**: ACCEPT as a new universal field.

This fills gap 0.5 (implicit evidence model). Currently, `confidence: confirmed` tells you HOW MUCH to trust a node but not WHY. Evidence provenance answers:
- Is this confirmed because two wiki sources agree? (evidence: wiki — volatile, may change on re-synthesis)
- Is this confirmed because code passes tests? (evidence: code — durable)
- Is this confirmed because benchmarks prove it? (evidence: benchmark — strong)
- Is this confirmed because an external API doc says so? (evidence: external — authoritative)

This improves autonomous reasoning. Claude can weight evidence types differently: code > benchmark > ADR > wiki > layer2 > external (for architecture decisions). For API integration tasks: external > code > wiki.

Implementation:
```yaml
evidence: []  # array of evidence types; allows multiple
```

Allowed values: `wiki`, `layer2`, `code`, `benchmark`, `ADR`, `external`

Default: `[]` (no evidence recorded — legacy nodes).

Maintenance cost: LOW. Set once at creation, updated when evidence basis changes. No cascading effects.

4.5 Source quality field

**Proposed**: source_quality: primary, secondary, derived

**Assessment**: REJECT.

Source quality is derivable from existing fields:
- primary = confidence: confirmed + multiple source_paths
- secondary = confidence: single-source + one source_path
- derived = confidence: inferred + no direct source_paths

Adding a field that can be computed from existing fields creates maintenance burden (two fields must stay synchronized) without adding information.

4.6 Review status field

**Proposed**: review_status: pending, reviewed, approved

**Assessment**: REJECT.

This implies a multi-person review workflow that doesn't match the project's operational model. The dev_graph is maintained by Claude sessions with user oversight. "Review" happens in real-time during the session. A formal review_status field would require:
- Someone to set it to "pending" on every change
- Someone to advance it to "reviewed" / "approved"
- Governance around what happens to nodes that are "pending" too long

This overhead is disproportionate to the value. If formal review becomes necessary later, it can be added as an enum append.

4.7 Recommendation: PARTIALLY ACCEPT

| Proposed | Recommendation | Rationale |
|----------|---------------|-----------|
| lifecycle | REJECT | Redundant with status + implementation_status |
| confidence expansion | ACCEPT `experimental` only | One new enum value, no restructuring |
| evidence | ACCEPT | New universal field, fills provenance gap |
| source_quality | REJECT | Derivable from existing fields |
| review_status | REJECT | Process mismatch, premature |

Net changes: +1 universal field (`evidence: []`), +1 enum value (`experimental` appended to confidence).

---

5. Adaptive Graph-RAG Entry Points

5.1 Current assumption

The audit_plan recommends capabilities as the primary retrieval entry point with systems as scope filter. This is correct for the dominant use case (implementation tasks) but assumes all sessions have the same retrieval needs.

5.2 Intent-aware routing

Different task intents have different natural entry points. The ontology already SUPPORTS multiple entry points — the Context Pack Assembly Rules just need to USE them.

Proposed routing table:

| Task Intent | Primary Entry Point | Expansion Direction | Secondary Context |
|-------------|--------------------|--------------------|-------------------|
| Implementation task | Capability | Down: modules, files, tests | Interfaces, schemas, constraints |
| Architecture question | Architecture | Down: systems, capabilities | Knowledge assets, ADRs |
| Bug investigation | Module (or File) | Lateral: dependencies, interfaces | Tests, events, constraints |
| Integration task | Interface | Lateral: both sides of contract | Schemas, modules, api_docs |
| Runtime incident | Event | Lateral: emitters, consumers | Workflows, modules, gates |
| Research question | Knowledge Asset | Down: ADRs, architecture | Wiki source pages |
| Governance question | Constraint (or Governance) | Lateral: bound systems/capabilities | ADRs, gates, predicates |
| Evolution planning | Decision Record | Up: knowledge assets; Down: affected systems | Patterns, architecture |
| Performance tuning | Benchmark | Lateral: measured modules | Schemas, interfaces, constraints |
| Design review | Pattern | Down: realizing modules/capabilities | Knowledge assets, ADRs |

5.3 Intent classification

Intent can be classified from the task description using keyword and structure analysis:

```
if task contains "implement", "build", "create", "add feature"  → implementation
if task contains "why", "architecture", "design rationale"       → architecture question
if task contains "bug", "fix", "error", "broken", "failing"      → bug investigation
if task contains "integrate", "connect", "API", "endpoint"       → integration
if task contains "incident", "crash", "timeout", "runtime"       → runtime incident
if task contains "research", "explore", "understand", "compare"  → research
if task contains "constraint", "policy", "rule", "governance"    → governance
if task contains "evolve", "migrate", "upgrade", "deprecate"     → evolution planning
if task contains "performance", "latency", "throughput", "speed" → performance tuning
if task contains "review", "pattern", "approach", "design"       → design review
```

Fallback: capability entry point (current default).

5.4 Expansion depth rules

Not all entry points need the same traversal depth:

- Implementation: 3 hops down (capability → module → file → test), 1 hop lateral (interfaces, constraints)
- Architecture question: 1 hop up (knowledge assets), 2 hops down (systems, capabilities)
- Bug investigation: 2 hops lateral (dependencies, interfaces), 1 hop down (files, tests)
- Design review: 2 hops down (capabilities, modules), 1 hop up (knowledge assets)

Maximum context pack size remains governed by token budget (< 50% of context window).

5.5 Impact on retrieval precision

Estimated improvement from intent-aware routing vs. uniform capability entry:

| Task Type | Current Precision (capability-only) | Estimated Precision (intent-aware) |
|-----------|------------------------------------|------------------------------------|
| Implementation | HIGH (correct entry point) | HIGH (unchanged) |
| Architecture question | LOW (too deep, misses context) | HIGH (starts at architecture) |
| Bug investigation | MEDIUM (right area, wrong granularity) | HIGH (starts at module/file) |
| Integration task | MEDIUM (misses interface contracts) | HIGH (starts at interface) |
| Research question | LOW (implementation-focused) | HIGH (starts at knowledge) |
| Design review | LOW (no pattern awareness) | HIGH (starts at pattern) |

Overall precision improvement: estimated 30-40% for non-implementation tasks.

5.6 Recommendation: ACCEPT

Accept intent-aware routing as an update to Context Pack Assembly Rules. This requires NO ontology changes — the types and relationships already exist. The change is purely in the retrieval strategy.

Add a new Step 1.5 ("Intent Classification") to the Context Pack Assembly Rules between Step 1 (Parse Task Request) and Step 2 (Semantic Retrieval). The routing table becomes a governance artifact in the assembly rules.

---

6. Knowledge-to-Code Continuum

6.1 The continuum

The proposed lifecycle stages map directly to ontology types:

```
Knowledge        → knowledge_asset
    ↓
Decision         → decision_record
    ↓
Architecture     → architecture
    ↓
Capability       → capability
    ↓
Implementation   → module, file
    ↓
Runtime          → event, workflow
    ↓
Evaluation       → benchmark_result, gate
    ↓
Evolution        → decision_record (loops back to Decision)
```

6.2 Assessment

The continuum is ALREADY implicit in the proposed ontology. Making it explicit has two possible forms:

Option A: Add a `continuum_stage` frontmatter field to all nodes.
Option B: Document the continuum as a conceptual model in CLAUDE.md without adding metadata.

Option A adds a field that is fully derivable from `type`. Every `knowledge_asset` is at stage `knowledge`. Every `module` is at stage `implementation`. A field that can be computed from an existing field violates the anti-entropy rule: "No duplicate semantics — do not create fields that overlap existing fields."

Option B provides the conceptual framework without metadata overhead.

6.3 The cycle

The continuum is not linear — it cycles. Evolution (ADRs about changing the system) feeds back to Decision, which feeds Architecture. This cycle is already modeled by the `supersedes` relationship on ADRs. A new ADR that supersedes an old one represents an evolution cycle completing.

The cycle also connects Evaluation → Evolution: benchmark results that reveal performance problems trigger new ADRs. This is modeled by: benchmark_result → (informs) → decision_record.

6.4 Recommendation: ACCEPT as conceptual model, REJECT as frontmatter field

Document the Knowledge-to-Code Continuum in CLAUDE.md as the conceptual backbone of the ontology. Include the type-to-stage mapping table. Use it to guide retrieval (see Section 5 routing) and to explain the ontology's design rationale.

Do NOT add a `continuum_stage` field — it is derivable from `type` and would violate anti-entropy.

---

7. Engineering Digital Twin

7.1 Definition

An Engineering Digital Twin is a model that represents the complete engineering state of a system across all dimensions: knowledge, architecture, implementation, runtime, governance, evolution, evidence, and validation.

7.2 Current state

The dev_graph IS already an embryonic digital twin. With the audit_plan proposal, it covers:
- Architecture (3 nodes)
- Implementation (systems, capabilities, modules, files)
- Quality (gates, predicates, tests)
- Governance (constraints, governance policies)
- Evolution (ADRs)
- Evidence (benchmarks)
- Runtime (events, workflows)
- Documentation (api_docs, context_packs, observability)

With this addendum's proposed extensions, it additionally covers:
- Knowledge (knowledge_assets)
- Patterns (reusable architectural solutions)

7.3 What a full twin would add

Beyond the audit_plan + this addendum, a FULL Engineering Digital Twin would also model:
- Runtime telemetry (live performance metrics, error rates, latency)
- Production incidents (incident reports, root cause analysis)
- Deployment state (which version is deployed where)
- Team/agent state (who/what is working on what)
- Cost model (infrastructure costs, API costs per component)
- Security posture (vulnerability state, credential rotation status)

7.4 Assessment

Advantages:
- COMPLETE model enables Claude to reason about the entire engineering lifecycle
- Every question ("why does this exist?", "what happens at runtime?", "how well does this perform?", "what's the security posture?") is answerable from the graph
- Enables truly autonomous planning: Claude can propose changes with full context of cost, risk, performance, and governance implications

Disadvantages:
- NO APPLICATION CODE EXISTS YET. Modeling runtime telemetry for a system with no runtime is speculative metadata about speculative metadata.
- Complexity scales combinatorially. 25+ types × 16+ relationships × 22+ directories creates a governance surface that exceeds the value for a pre-code project.
- Obsidian/markdown works well up to ~200-300 nodes. A full twin could reach 500+ nodes, at which point maintenance cadences (per-session lint) become expensive.
- The map risks becoming larger than the territory. If the dev_graph takes more effort to maintain than the code it describes, the cost-benefit inverts.

Scalability estimate:
| Scope | Node Count | Maintainability | Value |
|-------|-----------|-----------------|-------|
| Current (18 nodes) | 18 | Trivial | Moderate — governance only |
| Audit plan (Phase 1-4) | ~50-60 | Manageable | High — architecture + implementation |
| Audit plan (full, Phase 1-8) | ~80-120 | Moderate effort | High — complete implementation model |
| + This addendum | ~100-140 | Moderate effort | Very high — knowledge + patterns + traceability |
| Full digital twin | ~200-400 | Significant effort | Marginal improvement over addendum |

7.5 Compatibility with autonomous development

The proposed ontology (audit_plan + addendum) provides ~90% of the autonomous reasoning value of a full digital twin at ~40% of the complexity. The remaining 10% (runtime telemetry, deployment state, cost model) becomes valuable only when:
1. Application code exists and runs
2. Production deployments occur
3. Cost optimization is a concern

These are Phase 3-4 concerns in the organic growth model below.

7.6 Organic growth model

The digital twin should evolve in phases tied to project maturity:

Phase 1 — Knowledge + Architecture Model (NOW)
- Knowledge assets, patterns, architecture nodes, ADRs
- Answers: why does this exist? what pattern does it follow?
- Prerequisites: none

Phase 2 — Implementation Model (WHEN CODE BEGINS)
- Systems, capabilities, modules, files, tests, interfaces, schemas
- Answers: where is the code? what are the contracts? what tests exist?
- Prerequisites: first code written

Phase 3 — Runtime Model (WHEN CODE RUNS)
- Events, workflows, runtime telemetry nodes
- Answers: what happens at runtime? where are the bottlenecks?
- Prerequisites: running application, observable metrics

Phase 4 — Evaluation + Evolution Model (WHEN METRICS EXIST)
- Benchmarks, evaluation scorecards, promotion decisions
- Answers: how well does this perform? should we change the architecture?
- Prerequisites: production data, performance baselines

Each phase activates ontology types that are already defined but dormant. No schema changes needed between phases — only node creation.

7.7 Recommendation: PARTIALLY ACCEPT

Accept the concept of an Engineering Digital Twin as the long-term aspiration for the dev_graph. Accept Phases 1-2 for immediate implementation. Defer Phases 3-4 until code exists and runtime data is available.

Do NOT add runtime telemetry, deployment state, cost model, or incident tracking types at this time. These can be added as enum appends when the project matures, preserving backward compatibility.

---

8. Deliverables — Consolidated Recommendations

8.1 Critical review of the current ontology

The audit_plan proposal is ACCEPTED as the baseline. It correctly identifies and solves the five most critical weaknesses of the flat model. The 22-type hierarchy with 13 relationship types provides a sound engineering ontology for implementation tracking.

Five gaps identified (Sections 0.1-0.5) motivate the extensions below.

8.2 Missing ontology layers

Two additional layers are recommended:

| Layer | Abstraction | Purpose | Position in Hierarchy |
|-------|------------|---------|----------------------|
| Knowledge Assets | Highest (above architecture) | WHY the architecture exists | Root conceptual layer |
| Patterns | Cross-cutting (parallel to capabilities) | Proven structural solutions | Referenced by modules/capabilities |

8.3 Proposed new ontology types

| Type | Directory | Recommendation | Rationale |
|------|-----------|---------------|-----------|
| knowledge_asset | knowledge_assets/ | PARTIALLY ACCEPT | Fills the "why" gap; lightweight pointers, not duplicates |
| pattern | patterns/ | PARTIALLY ACCEPT | Fills the pattern gap; reference nodes with simplified lifecycle |

Total type count: 24 (22 from audit_plan + 2 new).
Total directory count: 23 (21 from audit_plan + 2 new).

Both types are additive — zero impact on existing nodes, queries, or governance.

8.4 New relationship types

| Relationship | Semantics | Between | Recommendation |
|-------------|-----------|---------|---------------|
| originates_from | Conceptual foundation | ADR → Knowledge Asset | ACCEPT |
| justified_by | Decision authorization | Module/Capability → ADR | ACCEPT |
| realizes | Pattern implementation | Module/Capability → Pattern | ACCEPT |
| derived_from | Architectural derivation | System → Architecture | REJECT (use Contains) |
| operationalizes | Capability realization | Module → Capability | REJECT (use Implements) |
| validated_by | Validation link | (already exists) | REJECT (already in ontology) |

Total relationship count: 16 (13 from audit_plan + 3 new).

8.5 Universal metadata proposal

| Proposed Field/Change | Recommendation | Rationale |
|----------------------|---------------|-----------|
| lifecycle enum | REJECT | Redundant with status + implementation_status |
| confidence: experimental | ACCEPT (enum append) | Fills gap for speculative engineering artifacts |
| evidence: [] | ACCEPT (new universal field) | Provenance tracking for confidence claims |
| source_quality | REJECT | Derivable from existing fields |
| review_status | REJECT | Process mismatch for single-developer + AI model |

Net additions: 1 new universal field (`evidence`), 1 new confidence enum value (`experimental`).

8.6 Traceability model

PARTIALLY ACCEPT. The traceability chain becomes fully traversable with the 3 accepted relationship types:

```
Knowledge Asset ←─ originates_from ─ ADR ←─ justified_by ─ Capability/Module
                                       │
                                       ├─ shapes → Architecture
                                       └─ Contains → System → Capability → Module → File
                                                                              │
Pattern ←────────── realizes ──────────────────────────────────────────────────┘
                                                                              │
                                                                    Validated By → Test
```

No new types required — traceability is achieved through new relationships on existing types.

8.7 Adaptive Graph-RAG routing model

ACCEPT. Intent-aware retrieval routing using a 10-entry routing table. Implementation is a Context Pack Assembly Rules update, not an ontology change.

Key changes to assembly protocol:
- New Step 1.5: Intent Classification (between Parse Task and Semantic Retrieval)
- Routing table maps 10 task intents to primary entry points
- Expansion depth rules per intent type
- Fallback to capability entry point for unclassifiable tasks

Estimated precision improvement: 30-40% for non-implementation tasks.

8.8 Engineering Digital Twin assessment

PARTIALLY ACCEPT as long-term aspiration. The audit_plan + this addendum together create ~90% of the value of a full digital twin at ~40% of the complexity. Full twin (runtime telemetry, deployment state, cost model, incident tracking) is deferred until application code exists and produces runtime data.

Organic growth model: 4 phases tied to project maturity, each activating dormant ontology types without schema changes.

8.9 Migration strategy

All proposed extensions integrate into the existing audit_plan migration phases:

| Phase | Audit Plan | Addendum Extension |
|-------|-----------|-------------------|
| Phase 0 | CLAUDE.md update, ADR | + 2 new type enums, 2 new directories, 3 new relationship types, evidence field, experimental confidence value |
| Phase 1 | 3 architecture nodes | + 5-10 knowledge asset nodes (co-created with architecture for immediate traceability) |
| Phase 2 | 6 system nodes + lifecycle workflow | No addendum changes |
| Phase 3 | ~20 capability nodes | + 8-10 pattern nodes (co-created with capabilities that realize them) |
| Phase 4 | ~12-15 interfaces + schemas | + justified_by edges on all new modules, realizes edges on pattern-following modules |
| Phase 5-8 | Modules, gates, events, files, tests | + originates_from edges on new ADRs, evidence field on all new nodes |

Total additional nodes from addendum: ~15-20 (knowledge assets + patterns).
Total additional migration effort: ~15% increase over audit_plan alone.

8.10 Summary decision table

| Extension | Recommendation | Impact | Migration Phase |
|-----------|---------------|--------|----------------|
| Knowledge Asset type | PARTIALLY ACCEPT | +1 type, +1 directory, +10-15 nodes | Phase 0 (schema) + Phase 1 (nodes) |
| Pattern type | PARTIALLY ACCEPT | +1 type, +1 directory, +8-10 nodes | Phase 0 (schema) + Phase 3 (nodes) |
| originates_from relationship | ACCEPT | +1 relationship type | Phase 0 |
| justified_by relationship | ACCEPT | +1 relationship type | Phase 0 |
| realizes relationship | ACCEPT | +1 relationship type | Phase 0 |
| derived_from relationship | REJECT | — | — |
| operationalizes relationship | REJECT | — | — |
| lifecycle metadata | REJECT | — | — |
| confidence: experimental | ACCEPT | +1 enum value | Phase 0 |
| evidence field | ACCEPT | +1 universal field | Phase 0 |
| source_quality metadata | REJECT | — | — |
| review_status metadata | REJECT | — | — |
| Adaptive Graph-RAG routing | ACCEPT | Assembly Rules update | Phase 0 |
| Knowledge-to-Code Continuum | ACCEPT (documentation only) | CLAUDE.md conceptual model | Phase 0 |
| Engineering Digital Twin | PARTIALLY ACCEPT | Long-term aspiration, phases 1-2 now | Organic |

---

Backward Compatibility

All recommendations are purely additive:
- 2 new type enum values appended (knowledge_asset, pattern)
- 1 new confidence enum value appended (experimental)
- 1 new universal frontmatter field (evidence: [])
- 3 new relationship section types (originates_from, justified_by, realizes)
- 2 new directories (knowledge_assets/, patterns/)
- 0 existing nodes modified
- 0 existing queries affected
- 0 existing relationships renamed or removed
- 0 existing frontmatter fields changed

The addendum preserves full backward compatibility with the audit_plan proposal, which preserves full backward compatibility with the current dev_graph.

---

End of Architecture Review Addendum.
