# PAPER-TRADING RUNTIME — FINAL AUDIT (epoch baseline)

**Date:** 2026-06-09 · **Scope:** Slice 2 — the Paper-Trading Runtime (the first stateful Layer-3
component), governed by ADR-009. **Status:** epoch baseline.

**Verdict: PASS · Readiness 97/100.** All 8 audit dimensions PASS. Zero critical or high-severity
findings survived adversarial scrutiny. Every pinned fact was independently reproduced by the lead.
The runtime is admission-only, deterministic, replay-safe, and bounded-context-clean; its honest
provisional caveats (single real snapshot, provisional config, deferred execution layer) are disclosed
consistently across the ADR, the nodes, and the code.

This is a **read-only** audit: no code, dev_graph node, or commit was authored during it. This document
is the only artifact produced.

---

## 1. Method

Mirrors the Gold v0 final-audit method:

1. **8 parallel read-only dimension auditors** (Explore agents), each returning verdict + score +
   file:line evidence + warnings + critical/high candidates.
2. **Adversarial verification** — every critical/high candidate routed to a skeptical verifier that
   defaults to *refuted unless clearly real*. **Outcome: 0 critical/high candidates surfaced**, so 0
   adversarial verifications were required. The single *low* candidate (D1) is dismissed in synthesis
   as a deployment concern, not a determinism defect.
3. **Lead synthesis with independent re-verification** — the lead re-ran the suite and reproduced the
   pinned facts directly (§2), not relying on auditor claims.

Scope audited: the Slice-2 node set (SCHEMA-012/013, INT-010, MOD-007, CAP-021, GATE-003, PRED-006/007,
BENCH-003, FILE-019..023, TEST-013..017) + the SCHEMA-011 v0.2.0 additive `snapshot_guards`/`as_of`
change.

---

## 2. Lead independent re-verification (pinned facts)

Reproduced directly by the lead (not delegated):

| Pinned fact | Result |
|---|---|
| `runtime_policy_fingerprint` (default config) | `ab798cae915c1617f26c2a2793d425280d495099e593579a2ba99e74e9e56f32` ✓ |
| SCHEMA-011 real-PASS `packet_id` (after the additive block) | `gold-v0:5653d07a0b3949d5` — unchanged ✓ |
| Runtime-built packet `guard_refs` | `== GuardRefs()` (all `None`, no enrich-back) ✓ |
| `run_sequence` twice | byte-identical records **and** identical ending ledger `state_hash` ✓ |
| Real-PASS packet verdict | `ADMIT` ✓ |
| BENCH-003 synthetic verdict distribution | `ADMIT 3 / HOLD 1 / REJECT 3` ✓ |
| BENCH-003 real sequence | `ADMIT → REJECT × 3`; idempotent re-presentation `REJECT`/`duplicate_ok`; `no_enrich_back=true`; byte-identical; artifact in sync ✓ |
| `pytest tests/gold/` | **81 passed** ✓ |
| Full suite (`pytest tests`) | **853 passed** ✓ |
| Core purity scan (AST/grep) | zero clock/RNG/IO in `evaluate`/`predicates`; the only IO outside `runtime.py` is `config.load_config` (a boundary loader, never on the decision path) ✓ |
| Import isolation scan | zero `src/risk`, `src/supervisor`/treasury, raw-snapshot, or SCHEMA-005 imports anywhere in `src/gold/paper_runtime/` ✓ |

All facts reproduced exactly. No discrepancy between the pinned claims and the shipped artifacts.

---

## 3. Per-dimension scorecard

| # | Dimension | Verdict | Score |
|---|-----------|---------|-------|
| D1 | Stateful replay determinism (the keystone) | **PASS** | 98 |
| D2 | Ledger integrity & self-description | **PASS** | 100 |
| D3 | Idempotency / dedup semantics | **PASS** | 98 |
| D4 | Wrap boundary & packet purity | **PASS** | 99 |
| D5 | ADR-009 compliance (rule-for-rule) | **PASS** | 98 |
| D6 | Bounded-context separation | **PASS** | 100 |
| D7 | Ontology & graph integrity | **PASS** | 100 |
| D8 | Honesty / no-overclaim | **PASS** | 92 |
| | **Dimension mean** | | **98.1** |

---

## 4. Per-dimension findings

### D1 — Stateful replay determinism (keystone) · PASS 98
The pure core (`evaluate`) has **zero** clock/RNG/IO/hidden-state on the decision path; all temporal
input is `packet.as_of` (caller-forwarded, never wall-clock). `compute_record_id` binds
`prior_ledger.state_hash()` → a per-evaluation identity. IO is confined to `runtime.py`
(`load_ledger`/`persist_ledger`/`load_operational`); `run_sequence` threads the ledger purely in memory.
The replay invariant — *same (prior ledger + recorded inputs + `runtime_policy_version` + config) ⇒
identical record + identical new ledger* — holds, and the **ledger alone is sufficient replay state**.
Evidence: `engine.py:65-145`, `models.py:259-283` (record_id), `runtime.py:89-105` (pure driver),
TEST-015/016, BENCH-003 byte-identity.

### D2 — Ledger integrity & self-description · PASS 100
`RuntimeLedger`/`LedgerEntry` are frozen, append-only (`append` returns a NEW ledger), keyed by
`source_snapshot_id`, with `seq = len(prior.entries)` (continuity across reload). Each entry is
self-describing (snapshot-guards digest + operational fingerprint + `as_of` + verdict + triggered
guard), so a **cold reload reproduces identical decisions**. `state_hash()` is a canonical-JSON SHA-256;
`from_dict`/`to_dict` round-trip preserves it. Evidence: `models.py:141-244`, TEST-016
(`test_state_hash_stable_through_serialization`, `test_seq_continuity_across_persist_and_reload`,
`test_append_is_immutable_and_seq_is_length_derived`).

### D3 — Idempotency / dedup semantics · PASS 98
`duplicate_ok` (PRED-006) is **once-ever, keyed on a prior ADMIT** of that `source_snapshot_id`; a prior
HOLD/REJECT does not burn the snapshot (`has_admit` counts only `verdict == ADMIT`). `duplicate_ok` is
**always required** (not config-gated), so it cannot be bypassed. Re-presenting a previously-ADMITted
snapshot ⇒ `duplicate_ok=False` ⇒ REJECT. The semantic is correct: `source_snapshot_id` is a SHA-256
content hash, so this is **replay/re-presentation safety, not economic dedup**. Adversarial probe for a
double-admit path found none. Evidence: `models.py:203-212`, `predicates.py:26-30`, `engine.py:55-62`,
TEST-013/016, BENCH-003 idempotency block.

### D4 — Wrap boundary & packet purity · PASS 99
The runtime never mutates/re-hashes/re-emits the packet; `evaluate` reads packet fields but writes none;
guard outcomes live only on the record. Runtime-built packets carry `guard_refs == GuardRefs()`
(`no_enrich_back=true` on both benchmark sequences). The **SCHEMA-011 v0.2.0 change is genuinely
additive**: `snapshot_guards` is a separate block from `guard_refs`; `snapshot_guards`/`as_of` are
caller-forwarded (the builder never reads a snapshot); `compute_packet_id` digests only the 6-field
version tuple, so `packet_id` is unchanged; goldens were re-pinned; the log notes the block post-dates
the 94/100 gold audit. Evidence: `decision_builder/models.py:228-253` (packet_id excludes the block),
`test_decision_builder.py` (`test_snapshot_guards_forwarded_without_moving_packet_id`),
`test_e2e_pipeline.py:57-71`.

### D5 — ADR-009 compliance (rule-for-rule) · PASS 98
All nine constraints satisfied. Fail-closed verdict enforced in `evaluate` **and**
`RuntimeDecisionRecord.__post_init__` (ADMIT ⇔ `triggered_guard is None`). `supervisor_ok` is an explicit
`None` stub, never in `_required_guards`. Computed cooldown is cut (`cooldown_ok` echo-only).
`runtime_policy_fingerprint` excludes only the version; an un-versioned policy edit breaks the pinned
TEST-015. **The INDETERMINATE→WATCH composition is complete and enforced at three independent levels:**
(1) `GoldDecisionPacket.__post_init__` rejects INDETERMINATE with non-WATCH direction; (2)
`DecisionPolicyConfig.__post_init__` forces INDETERMINATE→WATCH in the direction table (total over all
regimes); (3) the engine's direction-only HOLD check (`packet.direction is Direction.WATCH`) therefore
catches every INDETERMINATE packet — **no INDETERMINATE packet can slip to ADMIT**.

### D6 — Bounded-context separation · PASS 100
AST/import scan over all of `src/gold/paper_runtime/*.py`: the only external import is
`gold.decision_builder.models`. **Zero** `risk.*`, `supervisor.*`/treasury, raw-snapshot, or SCHEMA-005
imports. The risk-guardrail predicate/verdict pattern is **mirrored, not imported**. In the graph,
CAP-021 carries **no typed relationship edge** to CAP-004 (deprecated Signal Generation), CAP-008
(Guardrail Enforcement), Order Management, or the treasury branch — the CAP-008 complementarity is
**prose only** ("recorded without a coupling edge, per ADR-009"). The export dry-run confirms no edge
from CAP-021 to those nodes.

### D7 — Ontology & graph integrity · PASS 100
All 17 new nodes are schema_version-2.2.0 compliant: valid universal frontmatter, closed-enum values,
correct type-prefixed **unique** canonical_ids, correct type-directory binding, required body sections,
and ≥1 inbound link (no orphans). The convergence wiring resolves: SCHEMA-011 `consumed_by` → MOD-007,
CAP-020 `Used By` → CAP-021, KA-009 `informs_decisions` → ADR-009, GATE-003 → PRED-006/007,
PRED-006/007 `implemented_in`/`validated_by` updated. Export dry-run: **158 nodes / 1106 relationships /
5 skips** — the 5 are the pre-existing legitimate Infrastructure-Diagram / Supervisor-Office skips;
**zero new broken links or orphans**. Index Statistics (158) consistent.

### D8 — Honesty / no-overclaim · PASS 92
The slice is **admission-only**: no execution, sizing, fills, P&L, or order routing is claimed or
implemented. Every deferral is disclosed consistently — ADR-009 Non-Goals, the node Open
Questions/Constraints, and the code/docstrings (`_NON_EXECUTION_NOTICE`, `supervisor_ok` stub reason,
`cooldown_ok` "computed cooldown deferred", the bench's "one underlying snapshot replayed — honest,
deterministic" note, the "provisional v0" config comment). The single deduction is a documentation
precision nit (§6, TD-1), not an overclaim.

---

## 5. Adversarial verification outcome

**0 critical/high candidates surfaced across all 8 dimensions → 0 adversarial verifications run.** The
only candidate flagged at any severity was **low** (D1): "`run_once` performs IO that could be
non-deterministic if the ledger file is concurrently modified by another process." **Dismissed in
synthesis**: the runtime is a single-invocation, file-mediated component (KA-009 Wake-Execute-Sleep);
concurrent ledger writes are a deployment-level concern orthogonal to the ledger's own determinism. The
pure core and the ledger are deterministic; an external race is not a determinism defect of this slice.
Recorded as TD-2 for the future runtime driver.

---

## 6. Warnings (minor; no verdict impact)

- **Forward-compat:** the SCHEMA-011 v0.2.0 `snapshot_guards` block is additive — a pre-v0.2.0 reader of
  a v0.2.0 packet would see an unexpected field. Controlled (goldens re-pinned, `packet_id` stable); no
  in-repo consumer is affected.
- **`prior_ledger_state_hash` threads into `record_id`** — upstream ledger corruption would silently
  change `record_id`. Mitigated: `load_ledger` validates `from_dict` fail-closed (malformed ⇒ raise).
- **Dedup is string-equality on a SHA-256 `source_snapshot_id`** — a hash collision would miss a true
  duplicate; cryptographically infeasible at this scope.
- **`cooldown_ok` is echoed, not computed** (deferred per ADR-009 §6) — the runtime is not a complete
  implementation of every conceivable L3 guard, by design.
- **Real benchmark corpus is one snapshot** (the three real paths are content-identical) — disclosed;
  the synthetic sequence supplies the full verdict distribution.

---

## 7. Technical debt (tracked, not blocking)

- **TD-1 (doc precision, low):** MOD-007 §Constraints and ADR-009 §2 say "the runtime **calls**
  `build_decision(guards=None)`." Strictly, the runtime consumes a **pre-built** packet by reference; it
  is the *chain orchestrator* (test/bench/future driver) that calls `build_decision(guards=None, ...)`.
  Behavior is correct and the no-enrich-back property is proven; only the wording conflates "the
  runtime" with "the runtime's chain". Fix: reword to "the runtime's chain builds the packet with
  `guards=None`; the runtime never enriches it." (Cosmetic — defer to the next dev_graph touch.)
- **TD-2 (future runtime driver, low):** when a real long-running/scheduled driver wraps `run_once`,
  add ledger write-locking or single-writer guarantees (concurrency is out of scope for v0's
  file-mediated single invocation).
- **DEBT-01 (pre-existing, carried):** the `snapshot_publisher.py` producer fix blocks epoch (b)
  real-corpus accumulation, not this consumer.

---

## 8. Honesty assessment (synthesis)

The artifacts do **not** overclaim. The runtime is a deterministic **admission** layer: it decides
ADMIT/HOLD/REJECT over a paper decision and records it — it does not execute, size, fill, or account for
P&L, and it says so in code, nodes, and the ADR. The provisional surfaces (the regime/confidence/
direction policy upstream, the runtime require-flag policy, the single real snapshot) are flagged as
provisional/domain-anchored and calibration-deferred. `supervisor_ok` and computed cooldown are
explicit, disclosed stubs/deferrals. There is no hidden state, no wall-clock, and no cross-context
coupling.

---

## 9. Remaining work for a fully-validated runtime (FUTURE epochs — not gaps in this baseline)

These are correctly **out of scope** for the admission runtime and deferred by ADR-009 Non-Goals; they
are future epochs, not defects of this slice:

1. **Execution / portfolio layer** — turning an ADMIT into a (paper) position: sizing, fills, P&L
   accounting, position tracking, exits. A net-new bounded context downstream of CAP-021, with its own
   planning ADR.
2. **Real-corpus calibration (epoch b)** — accumulate real snapshots (unblocked by fixing DEBT-01) to
   move the regime thresholds, confidence weights, direction table, **and** the runtime require-flags
   from domain-anchored/provisional to empirically calibrated (a governed version bump, not a rebuild).
3. **Computed cooldown guard** — a `clock_date`-windowed cooldown (currently echoed), with its own
   policy field + fingerprint + off-by-one tests.
4. **Live operational-status feed** — replace the explicit, file/caller-supplied `OperationalInput` with
   a real venue/health probe (must preserve replay by recording the captured operational state).
5. **Supervisor integration** — flip `supervisor_ok` from a `None` stub to a computed guard when a
   supervisor exists.
6. **Scheduler / driver + multi-instrument** — a wall-clock-triggered driver over a snapshot stream
   (with the TD-2 concurrency guarantees) and instrument generalization beyond GLD.

---

## 10. Conclusion

The Paper-Trading Runtime epoch is **accepted as the baseline at PASS / 97 readiness**. The keystone
risk for the project's first stateful component — replay determinism under explicit state — is
airtight, independently reproduced, and proven by 50 runtime tests + BENCH-003. Bounded-context
separation and packet purity are clean at the AST and graph levels. The lone actionable item is a
cosmetic documentation precision nit (TD-1). No code, node, or commit was changed by this audit.
