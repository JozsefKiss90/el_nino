---
type: test
canonical_id: TEST-041
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-25
updated: 2026-06-25
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_live_monitoring.py"
related_files:
  - "[[core.py (ops)]]"
  - "[[gated.py (ops)]]"
related_tests: []
related_constraints:
  - "[[No Wiki Mutation]]"
related_decisions:
  - "[[ADR - Operations Control Plane]]"
  - "[[ADR - Operable Alpaca Paper Execution Adapter v1]]"
test_path: "tests/ops/test_live_monitoring.py"
test_type: unit
covers:
  - "[[core.py (ops)]]"
  - "[[gated.py (ops)]]"
  - "[[Operations Control Plane]]"
required_for: []
---

# test_live_monitoring

## Definition

Headless unit tests (ISSUE-07, 24 tests) for the **LIVE read-model** in [[core.py (ops)]] (FILE-039) + the
governed Tier-3 **adopt** action in [[gated.py (ops)]] (FILE-042) — no Textual, no network.

## Purpose

Lock the live-monitoring invariants of ADR-013 (Tier-1 read-only) + ADR-014 (the `operate_live` live path):

- the live ledger/portfolio views read the **separate** `*.live` files and are **independent** of the SIM
  views (live empty when no live run; SIM panels unchanged);
- the live portfolio surfaces **realized P&L** (the REAL paper P&L), distinct from the accumulate-only SIM
  portfolio (a model number, NOT performance) — the SIM-vs-LIVE badging metadata is asserted correct;
- `reconcile_view` surfaces DISCREPANCY markers + the DERIVED `execution_refused`/`adoptable` state, and a
  foreign-order discrepancy is refused-but-not-adoptable (adopt heals POSITION discrepancies only);
- every live read is fail-closed (missing ⇒ empty; malformed ⇒ `error`, never raises);
- **no credential value** appears in any live read-model output (`to_dict` + render) with creds present;
- the **adopt-broker-position** action is append-only (preserves prior reconcile entries + executions,
  appends one `adopt:reconcile-adopt` + sets the local position), **precondition-gated** (REFUSES with
  nothing to adopt), clears the refuse, audits once, and never raises — and **carries the accumulated LIVE
  realized P&L forward** when adopting over a flat-but-realized position (a review-driven regression: adopt
  must not wipe the real-paper-P&L track record);
- the refuse banner is honest in the **multi-instrument mixed-discrepancy** case (does not claim adopt
  clears the refuse when a non-adoptable discrepancy remains).

## Constraints

Mocked only (no real Alpaca, no OS-task spawn, no Textual render); deterministic against fixture `*.live`
artefacts written under a tmp `runtime/chain`.

## Implementation Notes

Crafts live-portfolio fixtures (realized-P&L, unhealed unexplained-position discrepancy + pending order,
foreign-order discrepancy) at the derived `paths.live_*` siblings; asserts the badged `render_text_dashboard`
sections are distinct and never interleaved, and that an adopt heals the discrepancy so `reconcile_view` no
longer reports `execution_refused`/`adoptable`. The app-level adopt confirm-modal flow is covered by
[[test_ops_app]].

## Relationships

### Used By
- [[core.py (ops)]]
- [[gated.py (ops)]]
- [[Operations Control Plane]]

### Validated By
- [[ADR - Operations Control Plane]]

### Justified By
- [[ADR - Operations Control Plane]]
