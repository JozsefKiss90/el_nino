---
type: pattern
canonical_id: PAT-008
status: active
canonical: true
created: 2026-06-06
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
  - wiki
source_paths:
  - "wiki/strategies/Paper Trading.md"
  - "wiki/systems/Syndicate Squad Architecture.md"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Ontology Redesign]]"
pattern_id: "promotion"
pattern_type: governance
instances:
  - "[[Promotion Validation]]"
realized_by_capabilities:
  - "[[Promotion Validation]]"
realized_by_modules: []
related_knowledge:
  - "[[Paper Trading Validation]]"
---

# Promotion Pattern

## Definition

A quantitative gate that controls promotion from a safe environment (paper trading) to a live environment (production). Promotion requires measurable evidence meeting defined thresholds — not subjective judgment.

## Structural Constraints

1. Quantitative thresholds defined before evaluation begins (not post-hoc)
2. Multiple metrics evaluated — not a single pass/fail score
3. No regressions allowed — improvement in some metrics cannot mask decline in others
4. Statistical significance assessed — short samples are flagged, not promoted
5. Human approval required after quantitative gate passes (defense in depth)

## When to Apply

Apply at lifecycle transitions where increased autonomy or risk exposure is granted: PaperTrading → Validated, Candidate → Production.

## Relationships

### Provides
- Structural guidance for evidence-based lifecycle promotion

### Realized By
- [[Promotion Validation]]

### Originates From
- [[Paper Trading Validation]]
