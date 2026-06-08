---
type: pattern
canonical_id: PAT-011
status: active
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - code
source_paths:
  - "src/regime/regime_classifier/taxonomy.py"
related_files: []
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Deterministic Regime Taxonomy]]"
pattern_id: "regime-classification"
pattern_type: behavioral
instances:
  - "[[Market Regime Classification]]"
  - "[[Market Regime Classifier]]"
realized_by_capabilities:
  - "[[Market Regime Classification]]"
realized_by_modules:
  - "[[Market Regime Classifier]]"
related_knowledge:
  - "[[Regime Taxonomy]]"
---

# Regime Classification Pattern

## Definition

A behavioral pattern that interposes a deterministic **semantic abstraction** step between measurement and action:

```
Snapshot  →  Features  →  [Semantic abstraction: regime]  →  Decision  →  Execution
```

A priority-ordered rule table maps a feature vector to exactly one enumerated regime (first match wins), projecting `matched_rule_id → regime`, and the decision layer reasons over the regime rather than the raw features.

## Structural Constraints

1. The abstraction is a **pure function** of one feature vector + a versioned config (no history, state, clock, or randomness).
2. Rules are **priority-ordered and mutually exclusive** by first-match selection; an unconditional catch-all guarantees totality (exactly one label).
3. The label is a **projection of the matched rule** — selection is primary, the label is derived; rule provenance is carried.
4. **Fail closed**: a missing required input yields an explicit indeterminate terminal, never a guessed label.
5. Conflict/ambiguity is **metadata** (secondary/near matches), not additional labels.

## When to Apply

Apply whenever many downstream rules each re-derive "what kind of situation is this" from the same low-level signals. Lift that interpretation into one named, versioned, testable classifier so the decision layer consumes a stable label + provenance. Here: between MOD-004 (features) and the future Gold Decision Builder.

## Relationships

### Provides
- Structural guidance for a deterministic measurement → semantic-label → decision flow

### Realized By
- [[Market Regime Classification]]
- [[Market Regime Classifier]]

### Composes
- [[Pipeline Pattern]]

### Originates From
- [[Regime Taxonomy]]
