---
type: decision_record
canonical_id: ADR-003
status: active
implementation_status: implemented
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - code
source_paths:
  - "wiki/risk/Guardrail Architecture.md"
  - "population_strategy.md"
related_files: []
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
  - "[[Frontmatter Required]]"
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Ontology Redesign]]"
decision_id: "ADR-003"
decision_date: 2026-06-06
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Implementation Substrate

## Status

Active — established by the first coding session (driven by [[Phase 5 Bootstrap Context]], CTX-002) that implemented the [[Guardrail Engine]] vertical slice.

## Context

The dev_graph reached implementation readiness (contracts INT-003 / SCHEMA-007 / SCHEMA-008 exist, MOD-001 planned) but the codebase had no substrate: no language, repo layout, dependency manager, test framework, typing or config policy were decided or governed. A module-implementation context pack would silently assume these. Per [[Phase 5 Bootstrap Context]], the first coding session must record the substrate decision before writing code.

## Decision

- **Language**: Python, `requires-python >= 3.10` (the interpreter available in the environment is 3.10.6; Alpaca + Anthropic SDKs and all wiki trading examples are Python). May be bumped later without breaking this ADR.
- **Package layout**: `src/` layout mirroring dev_graph `module_path` values. The Guardrail Engine module (MOD-001, `module_path: src/risk/guardrail_engine`) lives at `src/risk/guardrail_engine/`. Top-level importable packages under `src/` are domain-named (`risk`, later `supervisor`, etc.). Tests mirror under `tests/`.
- **Dependency manager**: `uv` (canonical), driven by a standard PEP 621 `pyproject.toml`. `pip` remains compatible since the manifest is tool-agnostic. The first slice has **zero runtime dependencies**.
- **Test framework**: `pytest` (v9 available). Imports resolve via `[tool.pytest.ini_options] pythonpath = ["src"]` — no install step required to run tests.
- **Typing policy**: full type hints on all public functions; `mypy --strict` is the gate (declared in `pyproject.toml`). `from __future__ import annotations` in every module.
- **Config policy**: guardrail hard limits load from environment variables and **fail closed** — a missing required limit raises `GuardrailConfigError` so the engine cannot be constructed (the system will not trade). No silent defaults for hard limits; the only safe default is `ALLOW_WITHDRAWALS=false`.
- **Schema/model representation**: stdlib `dataclasses` (frozen) for the first slice — dependency-free and trivially testable. `pydantic` (available) is reserved for later schemas that need richer runtime validation; not adopted now to keep the slice self-contained.
- **Lint/test commands**: `uv run pytest` (test), `uv run ruff check` (lint), `uv run mypy src` (type-check). No-uv fallback: `python -m pytest`. (ruff/mypy are dev-dependencies to be installed; this session ran `python -m pytest`.)

## Alternatives Considered

### Alternative 1: pydantic models from the start
**Deferred.** Adds a runtime dependency before it is needed; the first slice's validation is simple and fail-closed via plain dataclasses + explicit checks. Revisit when schemas require coercion/serialization.

### Alternative 2: flat layout (no `src/`)
**Rejected.** The dev_graph `module_path` fields already encode `src/...`; a src-layout keeps node paths and real paths identical and avoids import-shadowing during tests.

### Alternative 3: poetry as dependency manager
**Rejected.** `uv` is faster and the manifest stays standard PEP 621; no lock-in. poetry would also work against the same `pyproject.toml`.

## Consequences

### Positive
- Real, runnable, dependency-free first slice; tests pass under the available interpreter.
- dev_graph `module_path` / `schema_path` values map 1:1 to real files, so file nodes link cleanly.
- Fail-closed config encodes the Guardrail Philosophy at the substrate level.

### Negative
- Pinning to 3.10 (vs 3.12+) is a pragmatic concession to the available interpreter.
- ruff/mypy are declared but not yet installed, so lint/type gates are not enforced this session.

### Risks
- If the project later standardizes on pydantic, the dataclass models (SCHEMA-007/008 realization) will need migration — mitigated by the small surface (one `models.py`).

## Relationships

### Provides
- The implementation substrate for all Phase 5+ coding sessions

### Justified By
- [[ADR - Ontology Redesign]]

### Constrained By
- [[No Wiki Mutation]]
- [[Frontmatter Required]]
- [[Canonical Ownership]]

### Used By
- [[Guardrail Engine]]
- [[Phase 5 Bootstrap Context]]
