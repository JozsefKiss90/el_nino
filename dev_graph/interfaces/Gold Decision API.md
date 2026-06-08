---
type: interface
canonical_id: INT-009
status: active
implementation_status: implemented
canonical: true
created: 2026-06-08
updated: 2026-06-08
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "GOLD_DECISIONPACKET_V0_BRIEF.md"
  - "src/gold/decision_builder/builder.py"
related_files:
  - "[[builder.py]]"
related_tests:
  - "[[test_decision_builder]]"
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
  - "[[ADR - Gold Decision Confidence Semantics]]"
interface_id: "gold-decision-api"
interface_version: "0.1.0"
parent_capability: "[[Gold Decision Generation]]"
input_schema: "[[Regime Classification Schema]]"
output_schema: "[[Gold DecisionPacket v0 Schema]]"
implemented_by:
  - "[[Gold Decision Builder]]"
stability: experimental
---

# Gold Decision API

## Definition

The boundary contract by which a consumer obtains a deterministic gold paper-trading decision for one snapshot:

```
build_decision(
    fv: FeatureVector,                       # SCHEMA-009 (coverage + citation)
    rc: RegimeClassification,                # SCHEMA-010 (primary input, via INT-007)
    guards: GuardRefs | None = None,         # optional L3 guard outcomes (ADR-006 §2/§6)
    config: DecisionPolicyConfig = DEFAULT,  # versioned confidence weights + direction table
    as_of: str | None = None,                # deterministic, caller-supplied; never wall-clock
) -> GoldDecisionPacket                       # SCHEMA-011
```

Primary input: SCHEMA-010 Regime Classification (the layer reasons over the regime label + provenance). SCHEMA-009 Feature Vector is the secondary input (for the confidence `coverage` term and the cited features). The packet is **paper_only** (instrument = gold/GLD proxy) — **not** a live trade signal, order, or broker instruction (ADR-006 §1, Non-Goals).

## Purpose

Make the Regime → Gold-decision seam an explicit, versioned contract so the (deferred) paper-trading runtime depends on a stable abstraction rather than re-deriving decision logic from raw features. It is the gold counterpart to INT-007 (Regime API), not the treasury INT-006 (Decision API).

## Architecture Role

Output interface of CAP-020 Gold Decision Generation, implemented (at the implementation step) by MOD-006 Gold Decision Builder. Pure call (no IO); the only side-channels are the injected, versioned `DecisionPolicyConfig` and the optional `guards` (themselves L3 outputs). The caller composes the full chain: `consume → build_features → classify → build_decision`.

## Contract

- **Determinism:** same `source_snapshot_id` + `source_feature_schema_version` + the regime version-triple + `decision_policy_version` + `configuration` ⇒ identical packet; `to_dict()` byte-identical (ADR-006 §3 / ADR-008 §8; `model_version` N/A for the rule-based v0).
- **Totality:** every `(fv, rc)` yields exactly one packet; the regime→direction table is total over all 12 `Regime` values.
- **Confidence:** the ADR-008 ordinal trust score (anchor = within-rule `rule_margin`; four discounts; NEUTRAL/INDETERMINATE floors); never a probability; never wired to SCHEMA-005 treasury calibration.
- **Provenance:** the packet carries `source_snapshot_id`, the echoed regime versions, the deciding `matched_rule_id`, and `cited_features` (read verbatim from the vector; only the 14 MOD-004 features).
- **Input boundary (ADR-006 §2):** consumes only SCHEMA-009 + SCHEMA-010 + optional L3 guard outputs — never raw SCHEMA-001, raw JSON, external APIs, hidden state, or history.
- **`as_of`** is an optional deterministic, caller-supplied string — never a wall-clock read.

## Error Modes

- INDETERMINATE regime (fail-closed upstream) → a packet with `direction = WATCH`, `confidence` at the defined minimum / `uncertainty` maxed (never a guessed stance).
- Invalid `DecisionPolicyConfig` (loaded via `from_mapping`/`load_config`) → raises a fail-closed `DecisionPolicyConfigError` at the boundary, before `build_decision` runs (mirrors `RegimeConfigError`).
- `guards = None` → `guard_refs` records the six-guard taxonomy as `null` (unevaluated); the packet is still produced (guards are advisory L3 context for v0).

## Stability

`experimental` / `interface_version: 0.1.0` — authored contract-first; implemented + tested when MOD-006 lands. May extend (not break) when the paper-trading runtime and the stateful L3 guards (`duplicate_ok`/`operational_ok`) are authored.

## Open Questions

- `implemented_by` → [[Gold Decision Builder]] (MOD-006), now authored and tested (`status: active` / `implemented`).
- The stateful L3 guards are deferred (ADR-006 Non-Goals); `guards` is optional in v0.

## Relationships

### Consumes
- [[Feature Vector Schema]]
- [[Regime Classification Schema]]

### Produces
- [[Gold DecisionPacket v0 Schema]]

### Implemented By
- [[Gold Decision Builder]]

### Validated By
- [[test_decision_builder]]

### Justified By
- [[ADR - Gold DecisionPacket v0 Planning]]
- [[ADR - Gold Decision Confidence Semantics]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Layer 2 Design Principles]]
