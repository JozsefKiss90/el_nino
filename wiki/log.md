# Wiki Log

Chronological record of wiki operations. Each entry uses format: `## [DATE] operation | details`

---

## [2026-05-09] init | Wiki structure created

Created initial wiki directory structure with 20 subdirectories:
concepts, systems, agents, strategies, execution, memory, risk, research, integrations, market_structure, backtesting, infrastructure, evaluation, observability, security, governance, workflows, patterns, sources, glossary

## [2026-05-09] init | CLAUDE.md maintenance schema created

Created wiki maintenance schema covering: ingestion workflow, canonicalization rules, naming conventions, redundancy prevention, lint workflow, update procedures, contradiction handling, graph maintenance.

## [2026-05-09] ingest | Batch ingestion of 8 source documents

### Sources processed:
1. `llm-wiki.md` — LLM Wiki persistent synthesis methodology
2. `raw/claude_stock_trader.md` — Claude Code + Alpaca stock trading
3. `raw/claude_opus_trader.md` — 24/7 Opus 4.6 trading with routines
4. `raw/claude_tradingview.md` — TradingView + BitGet crypto automation
5. `raw/claude_cowork_trader.md` — Claude Co-work crypto trading
6. `raw/Claude for Financial Services.md` — Anthropic financial services
7. `raw/ows-dev-squad.md` — Syndicate Squad architecture
8. `raw/build-spec.md` — Syndicate Squad build spec

### Pages created: 40
- 6 system pages
- 3 concept pages
- 3 strategy pages
- 2 execution pages
- 2 memory pages
- 2 risk pages
- 3 backtesting pages
- 4 agent pages
- 4 infrastructure pages
- 6 integration pages
- 2 security pages
- 2 governance pages
- 1 workflow page
- 1 research page
- 8 source pages
- index.md, log.md, CLAUDE.md

### Contradictions identified: None

### Architecture gaps identified:
- `/market_structure/` — empty, awaiting market microstructure research
- `/evaluation/` — empty, awaiting formal evaluation frameworks
- `/observability/` — empty, awaiting monitoring patterns
- `/patterns/` — empty, awaiting reusable pattern extraction
- `/glossary/` — pending formal glossary creation
- Reinforcement learning integration not yet covered
- Portfolio optimization not yet covered
- Compliance/regulatory frameworks not yet covered
- Multi-exchange portfolio management not yet covered

## [2026-05-15] ingest | Claude Alpaca Trader (3-level trading tutorial)

### Source processed:
- `raw/calude_alpaca_trader.md` — Three levels of Claude + Alpaca trading (basic setup, copy trading, Wheel Strategy)

### Pages created: 5
- `wiki/sources/SRC - Claude Alpaca Trader.md` — Source summary
- `wiki/concepts/Options Trading.md` — Calls, puts, premiums, strike, expiration
- `wiki/strategies/Wheel Strategy.md` — CSP → assignment → CC → repeat
- `wiki/strategies/Copy Trading Strategy.md` — Politician trade replication
- `wiki/integrations/Capital Trades Integration.md` — Congressional trade data service

### Pages updated: 8
- `wiki/risk/Guardrail Architecture.md` — "No options ever" clarified as per-strategy config, contradiction documented
- `wiki/execution/Stop-Loss Systems.md` — Floor ratcheting logic, 5-minute monitoring
- `wiki/execution/Position Sizing.md` — Ladder buying (scale-in) subsection
- `wiki/strategies/Paper Trading.md` — Custom balance accounts, strategy isolation
- `wiki/integrations/Alpaca API.md` — Custom paper balance, credential file persistence
- `wiki/systems/Claude-Assisted Trading Stack.md` — Capital Trades added to Data & Research
- `wiki/infrastructure/Claude Routines.md` — `/schedule` command, 5/15-minute intervals
- `wiki/systems/Architecture Overview.md` — Claude Desktop + Alpaca Beginner variant

### Index, log, glossary updated

### Contradictions identified: 1
- "No options ever" (SRC - Claude Opus Trader) vs. Wheel Strategy (SRC - Claude Alpaca Trader)
- Resolution: Per-strategy configurable guardrail, not universal constraint

### Architecture gaps identified:
- Options Greeks monitoring not yet covered
- Implied volatility analysis not yet covered
- Multi-politician portfolio diversification for copy trading
- Brokerage options approval level requirements

## [2026-05-15] governance | Metadata Migration Plan created

### Deliverables:
- `wiki/governance/Metadata Migration Plan.md` — 3-phase frontmatter rollout architecture
- `wiki/CLAUDE.md` — extended with 7 new governance sections (Frontmatter Governance, Metadata Lifecycle, Dataview Governance, MCP Compatibility, Metadata Anti-Entropy Rules, Metadata Lint Workflow)
- `wiki/index.md` — updated with new governance page and frontmatter coverage metric

### Architecture decisions:
- Universal schema: `type`, `domain`, `created`, `updated`, `status` (required on all pages)
- Closed enums for all classification fields (17 type values, 20 domain values)
- Domain-directory binding constraint enforced
- No frontmatter on structural files (index.md, log.md, CLAUDE.md)
- Source pages get extended schema: `source_file`, `source_type`, `date_ingested`
- Anti-entropy architecture: no freeform fields, append-only enums, flat YAML only

### Phase plan:
- Phase 1: 5 hub pages (Architecture Overview, Trading Engine Pipeline, Claude-Assisted Trading Stack, Agent Memory Architecture, Autonomous Trading Risk Model)
- Phase 2: 43 remaining canonical pages across all domains
- Phase 3: 9 source pages + observability dashboards + provenance queries

### Pages modified: 3
- `wiki/governance/Metadata Migration Plan.md` (created)
- `wiki/CLAUDE.md` (extended)
- `wiki/index.md` (updated)

## [2026-05-15] metadata | Phase 1 — Hub Page Metadata Foundation executed

### Frontmatter inserted on 5 hub pages:
- `wiki/systems/Architecture Overview.md` — type: system, domain: systems, confidence: confirmed
- `wiki/systems/Trading Engine Pipeline.md` — type: system, domain: systems, confidence: confirmed
- `wiki/systems/Claude-Assisted Trading Stack.md` — type: system, domain: systems, confidence: confirmed
- `wiki/memory/Agent Memory Architecture.md` — type: memory, domain: memory, confidence: confirmed
- `wiki/risk/Autonomous Trading Risk Model.md` — type: risk, domain: risk, confidence: confirmed

### Validation results:
- mcpvault `get_frontmatter`: 5/5 pass — all fields parsed (types, dates, arrays, enums)
- Rendering: 5/5 pass — frontmatter block before `# Title`, no content displacement
- Tags: `system` x3, `risk` x1 now visible via frontmatter; `tags: []` on Agent Memory produces no tag
- Domain-directory consistency: 5/5 match

### Dataview dashboard expanded:
- `wiki/observability/Graph Health Dashboard.md` — added 4 pilot queries (Metadata Coverage, Pages Missing Frontmatter, Confidence Distribution, Stale Pages)

### Phase 1 status: COMPLETE
- Frontmatter coverage: 5/58 canonical pages (8.6%)
- Schema validated against governance spec
- Ready for Phase 2 expansion

## [2026-05-15] metadata | Phase 2 — Canonical Page Expansion executed

### Rollout order (domain-by-domain):

**Batch 1 — Systems (3 pages):**
- Three-Layer Trading System — confidence: single-source
- LLM Failure Modes in Trading — confidence: confirmed
- Syndicate Squad Architecture — confidence: confirmed

**Batch 2 — Memory + Risk (2 pages):**
- Context Budget Engineering — confidence: confirmed
- Guardrail Architecture — confidence: confirmed, tags: [risk, contradiction]

**Batch 3 — Concepts (4) + Strategies (5) + Integrations (7) = 16 pages:**
- Concepts: VWAP (confirmed), EMA Crossover (confirmed), Relative Volume Filter (single-source), Options Trading (single-source)
- Strategies: VWAP Crossover Strategy (single-source), Signal Confirmation (confirmed), Paper Trading (confirmed), Wheel Strategy (single-source), Copy Trading Strategy (single-source)
- Integrations: Alpaca API (confirmed), TradingView Integration (confirmed), Exchange API Integration (confirmed), Perplexity API (single-source), MCP Architecture (confirmed), Webhook Architecture (confirmed), Capital Trades Integration (single-source)

**Batch 4 — Remaining domains (22 pages):**
- Execution (2): Position Sizing (confirmed), Stop-Loss Systems (confirmed)
- Agents (4): Supervisor Decision Engine (single-source), Multi-Agent Orchestration (confirmed), Stateless Agent Recovery (single-source), Agent Self-Verification (single-source)
- Backtesting (3): Walk-Forward Optimization (single-source), Overfitting Detection (single-source), Backtesting Methodology (single-source)
- Infrastructure (4): Claude Code (confirmed), Claude Co-work (single-source), Claude Routines (confirmed), Railway Deployment (single-source)
- Security (2): API Credential Isolation (confirmed), Environment Variable Management (confirmed)
- Governance (3): Trade Logging (confirmed), Treasury Policy System (confirmed), Metadata Migration Plan (inferred)
- Workflows (1): Office Action Loop (confirmed)
- Research (1): Research Ingestion Workflow (confirmed)
- Glossary (1): Glossary (inferred)
- Observability (1): Graph Health Dashboard (inferred)

### Validation results:
- mcpvault `get_frontmatter` spot-check: 8/8 pass across all batches
- Tag distribution: integration(7), system(6), agent(5), strategy(5), concept(4), infrastructure(4), risk(3), contradiction(2)
- Domain-directory consistency: 48/48 match
- All enum values within allowed sets

### Phase 2 status: COMPLETE
- Frontmatter coverage: 48/48 canonical pages (100%)
- Source pages (9): awaiting Phase 3
- Structural files (3): excluded by design (index.md, log.md, CLAUDE.md)
- Confidence distribution: confirmed(28), single-source(17), inferred(3)
- Ready for Phase 3 (source pages + observability)

## [2026-05-15] metadata | Phase 3 — Source + Observability Layer executed

### 3A: Source page frontmatter (9 pages):
- SRC - LLM Wiki Methodology — source_type: methodology
- SRC - Claude Stock Trader — source_type: youtube_transcript
- SRC - Claude Opus Trader — source_type: youtube_transcript
- SRC - Claude TradingView Integration — source_type: youtube_transcript
- SRC - Claude Cowork Trader — source_type: youtube_transcript
- SRC - Claude for Financial Services — source_type: announcement
- SRC - OWS Dev Squad — source_type: architecture_doc
- SRC - Build Spec — source_type: product_spec
- SRC - Claude Alpaca Trader — source_type: youtube_transcript
- All include source_file, source_type, date_ingested + universal fields
- Prose metadata tables retained (no removal in this phase)

### 3B: Graph Health Dashboard expanded to full observability suite:
- 14 Dataview queries total (7 new):
  - Ontology Overview (domain distribution)
  - Type Distribution
  - Stub Tracking
  - Source Coverage (source_file, source_type, date_ingested)
  - Source Provenance (inbound link counts per source)
  - Contradiction Registry
  - Ingestion Timeline

### 3C: Schema lint — full vault:
- 57/57 pages pass schema validation
- Required fields: 57/57 present
- Type enum: 57/57 valid
- Domain enum: 57/57 valid
- Status enum: 57/57 valid
- Confidence enum: 57/57 valid where present
- Source-specific fields: 9/9 complete
- Domain-directory consistency: 57/57 match
- Data quality note: `raw/calude_alpaca_trader.md` filename has pre-existing typo (not a schema violation)

### Phase 3 status: COMPLETE

### Migration complete — final metrics:
- **Frontmatter coverage**: 57/57 pages (100%)
- **Structural files excluded**: 3 (index.md, log.md, CLAUDE.md)
- **Schema compliance**: 57/57 (100%)
- **Confidence distribution**: confirmed(28), single-source(26), inferred(3)
- **Observability queries**: 14
- **All 3 phases executed**: hub foundation → canonical expansion → source + observability

## [2026-05-15] governance | CLAUDE.md operational governance extension

### Context:
Post-migration governance extension. Vault completed metadata migration (57/57 pages, 100% compliance). CLAUDE.md extended from metadata governance spec into full semantic ontology operations manual.

### New governance sections appended to CLAUDE.md (8 sections):

1. **Continuous Ontology Operations** — per-session/weekly/monthly maintenance cadences, Green/Yellow/Red operational thresholds for 7 metrics, graph repair procedures (orphan, weak link, hub, density)
2. **MCP Operational Governance** — operation classification table for all mcpvault operations (safe-automated / constrained-automated / human-review-required / prohibited), 7 hard prohibitions, canonical ownership protection, MCP session logging requirements
3. **Semantic Retrieval Governance** — canonical precedence over embedding similarity, ambiguity handling (5% threshold), duplicate detection (85% creation / 80% periodic scan), false-positive mitigation, retrieval scope rules per query context
4. **Ontology Evolution Procedures** — change classification (minor/structural/breaking), enum append procedure, domain split/merge/deprecation procedures, migration logging requirements
5. **Observability Operations** — dashboard review cadence, per-metric remediation workflows for 10 metrics, 4-level escalation logic (Normal/Elevated/Critical/Structural), dashboard maintenance rules
6. **Semantic Confidence Lifecycle** — full state transition table (7 transitions), promotion/demotion rules, multi-source validation standards, stale confidence detection (60-day threshold), contradiction-triggered confidence review
7. **Schema Evolution Procedures** — 5 evolution principles, field addition (9-step), enum extension (4 constraints), field deprecation (6 rules), schema_version introduction conditions, backward compatibility rules
8. **Automated Maintenance Governance** — operation safety classification table, 3 MCP-assisted workflows (lint pass, cross-link enhancement, stale detection), 7 automation boundaries, 5 escalation triggers

### Graph Health Dashboard updated:
- Added Stale Confidence Dataview query (15th query)
- Added Known Distinct Pairs section for false-positive annotation

### Governance scope evolution:
- Before: metadata schema governance + migration operations
- After: full semantic ontology operations governance (continuous maintenance, MCP safety, retrieval governance, ontology evolution, observability operations, confidence lifecycle, schema evolution, automation boundaries)

### Files modified: 3
- `wiki/CLAUDE.md` — 8 new governance sections appended (~480 lines)
- `wiki/observability/Graph Health Dashboard.md` — stale confidence query + known distinct pairs
- `wiki/log.md` — this entry

