---
type: test
canonical_id: TEST-030
status: implemented
implementation_status: tested
canonical: true
created: 2026-06-18
updated: 2026-06-18
confidence: confirmed
evidence:
  - code
source_paths:
  - "tests/ops/test_audit.py"
related_files:
  - "[[audit.py (ops)]]"
related_tests: []
related_constraints: []
related_decisions:
  - "[[ADR - Operations Control Plane]]"
test_path: "tests/ops/test_audit.py"
test_type: unit
covers:
  - "[[audit.py (ops)]]"
required_for: []
---

# test_ops_audit

## Definition

Headless unit tests for the append-only audit log [[audit.py (ops)]] (FILE-043) — 7 tests.

## Purpose

Lock the audit invariants: append + read round-trip; append-only (never truncates); tail by limit; the
file is **ASCII** even with non-ASCII in the result (`ensure_ascii`); absent file -> empty; malformed
lines skipped; the `line()` render format.

## Constraints

Deterministic clock injected; pure filesystem round-trip in `tmp_path`.

## Implementation Notes

Asserts the on-disk bytes are all `< 128` after writing a result containing `>=` / non-ASCII; verifies
the tail window and malformed-line resilience.

## Relationships

### Used By
- [[audit.py (ops)]]

### Justified By
- [[ADR - Operations Control Plane]]
