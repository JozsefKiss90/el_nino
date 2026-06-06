---
type: context_pack
canonical_id: CTX-002
status: draft
implementation_status: not-started
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: inferred
evidence:
  - design
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
  - "wiki/risk/Autonomous Trading Risk Model.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Ontology Redesign]]"
task_id: "phase5-bootstrap-001"
task_type: implementation
required_nodes:
  - "[[Guardrail Engine]]"
  - "[[Guardrail Enforcement]]"
  - "[[systems/Risk Control]]"
  - "[[Guardrail Pattern]]"
  - "[[Guardrail Philosophy]]"
  - "[[Risk Check API]]"
  - "[[Trade Validation Request Schema]]"
  - "[[Trade Validation Decision Schema]]"
  - "[[ADR - Ontology Redesign]]"
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
required_files: []
required_tests: []
required_docs:
  - "[[Alpaca API Docs]]"
  - "[[Anthropic API Docs]]"
admissibility_checked: true
---

# Phase 5 Bootstrap Context

## Definition

The context pack that prepares the FIRST real coding session. Its job is twofold: (1) establish the implementation substrate (language, repo layout, test framework, dependency tooling) by producing a substrate ADR, then (2) implement the inaugural module — the Guardrail Engine — against its now-existing contracts.

## Purpose

The dev_graph has reached implementation readiness (contracts exist for the first slice), but the codebase substrate is undecided and ungoverned. A module-specific pack would silently assume a repo layout and tech stack that no decision record sanctions. This pack makes that decision explicit before any code is written.

---

## Task

**Task ID**: phase5-bootstrap-001
**Task Type**: implementation
**Description**: Bootstrap the implementation substrate (produce ADR-003), then implement the Guardrail Engine module (MOD-001) realizing Guardrail Enforcement (CAP-008) against the Risk Check API (INT-003).

## Substrate Decision Agenda (produce ADR-003)

The first session MUST record an Architecture Decision Record (next free id ADR-003) covering:
- **Language**: Python is strongly implied (Alpaca + Anthropic SDKs; all wiki trading examples are Python).
- **Repo layout**: mirror the module nodes' `module_path` (e.g. `src/risk/guardrail_engine`, `src/supervisor/decision_engine`).
- **Test framework**: pytest (Python default; aligns with the planned `test_*.py` files).
- **Dependency tooling**: the one genuinely open choice (uv / poetry / pip-tools) — decide and record.

## Retrieved Nodes

- [[Guardrail Engine]]
- [[Guardrail Enforcement]]
- [[Guardrail Pattern]]
- [[Guardrail Philosophy]]
- [[systems/Risk Control]]
- [[Risk Check API]]
- [[Trade Validation Request Schema]]
- [[Trade Validation Decision Schema]]

## Canonical Nodes

All retrieved nodes are `canonical: true` and `status != deprecated`. Confirmed admissible below.

## Required Files

Created by this session (not pre-existing):
- `src/risk/guardrail_engine/guardrail_engine.py`
- `src/risk/guardrail_engine/predicates.py`

## Required Tests

Created by this session:
- `test_guardrail_engine.py`
- `test_predicates.py`

## Required Constraints

- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]

## Required API Docs

- [[Alpaca API Docs]] (account equity / portfolio state; freshness per [[API Documentation Policy]])
- [[Anthropic API Docs]] (agent runtime, if invoked)

## Relevant Decisions

- [[ADR - Ontology Redesign]] (justifies the ontology and contract layer)
- ADR-003 (to be produced by this session — implementation substrate)

## Deprecated / Excluded Notes

| Node | Failure Reason |
|---|---|
| (none) | All selected nodes passed all 9 admissibility checks |

## Admissibility Check

- Total nodes evaluated: 12
- Nodes admissible: 12
- Nodes excluded: 0
- All 9 checks from [[Admissibility Checks]] applied: [x] yes
- Check 9 note: MOD-001 `related_tests` is empty by design — tests are produced BY this session.

## Implementation Plan

1. Produce ADR-003 (substrate decision above).
2. Scaffold the repo per the decided layout; create the `src/risk/guardrail_engine` package.
3. Implement `predicates.py` (five hard-limit predicates) and `guardrail_engine.py` (`GuardrailEngine.validate()` short-circuit conjunction), consuming the Trade Validation Request Schema and producing the Trade Validation Decision Schema.
4. Write `test_predicates.py` and `test_guardrail_engine.py`.

## Validation Plan

1. Unit tests cover pass/fail boundary cases for every predicate.
2. Verify deterministic output for identical inputs.
3. Confirm no limit can be silently relaxed (missing config → BLOCK).

## Writeback Plan

Follow CLAUDE.md "End-of-Coding-Session Writeback Checklist":
1. Create file nodes for `guardrail_engine.py`, `predicates.py` (FILE-001, FILE-002).
2. Create test nodes (TEST-001, TEST-002); set `covers`.
3. Bump MOD-001 → status active, implementation_status in-progress/tested; add `code` to evidence; populate `related_files` / `related_tests`.
4. Bump CAP-008 implementation_status to in-progress.
5. Append a log.md entry; update index.md; run the 11 lint checks on touched nodes.

## Relationships

### Depends On
- [[Context Pack Assembly Rules]]
- [[Admissibility Checks]]
- [[Context Pack Template]]

### Provides
- Implementation context for the first coding session (substrate ADR + Guardrail Engine)

### Validated By
- [[Admissibility Checks]]

### Constrained By
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]
