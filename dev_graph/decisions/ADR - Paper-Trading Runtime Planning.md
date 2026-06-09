---
type: decision_record
canonical_id: ADR-009
status: active
implementation_status: not-started
canonical: true
created: 2026-06-09
updated: 2026-06-09
confidence: confirmed
evidence:
  - design
  - ADR
  - code
source_paths:
  - "ultimateplan.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Canonical Ownership]]"
related_decisions:
  - "[[ADR - Decision Layer Re-grounding]]"
  - "[[ADR - Gold DecisionPacket v0 Planning]]"
decision_id: "ADR-009"
decision_date: 2026-06-09
supersedes: []
superseded_by: []
decision_status: active
---

# ADR - Paper-Trading Runtime Planning

## Status

**Accepted** — authored 2026-06-09 (epoch (a) planning slice). This is a **governance and
architectural-boundary** record, mirroring [[ADR - Gold DecisionPacket v0 Planning]] (ADR-006). It does
**not** author, define, or freeze any schema, module, interface, gate, or code. It establishes the
constraints under which the deferred **paper-trading runtime** — un-deferred here — may be built
contract-first in a **separate, post-checkpoint implementation slice** (Slice 2). The Gold DecisionPacket
v0 epoch is closed (dev_graph log, 2026-06-08: each next epoch "needs its own planning ADR"); this is
that ADR for epoch (a).

## Context

The Layer-3 analysis path `SCHEMA-001 → consume → build_features → classify → build_decision` now
produces a pure, replay-safe [[Gold DecisionPacket v0 Schema]] (SCHEMA-011). That packet carries a
six-guard `GuardRefs` block in which the two **stateful L3 guards** — [[Duplicate OK]] (PRED-006) and
[[Operational OK]] (PRED-007) — are deliberately left `None`, because computing them needs runtime state
the pure builder must never touch ([[ADR - Decision Layer Re-grounding]] §"Gold DecisionPacket Design
Constraints"; ADR-006 Non-Goals). ADR-006 also explicitly deferred the **paper-trading runtime** itself.

This ADR answers a deliberately narrow question:

> **Under what governance constraints may the first stateful Layer-3 component — the paper-trading
> runtime — be built, so that it computes the two stateful guards without breaking the determinism and
> bounded-context discipline the pure layers established?**

The runtime is the first stateful component in the Layer-3 lineage. [[Stateless Agent Architecture]]
(KA-009) — Wake-Execute-Sleep, file-mediated continuity — is the governing precedent for *how* state is
held: as an explicit, persisted value, never ambient process memory.

The central tension: the packet's `packet_id` is a content hash over a 6-field version tuple that
**excludes `guard_refs`** (`compute_packet_id`, `builder.py`). A stateful consumer must reconcile with
that — it must never let runtime state leak into the pure packet, yet it must record the stateful guard
outcomes somewhere replay-safe.

## Decision

The following constraints bind the future paper-trading runtime. They are invariants of record; the
contract and code authored in Slice 2 must satisfy them.

### 1. Bounded context & permanent separation
The paper-trading runtime is a **net-new, permanently separate** component with **new canonical
identifiers**. It consumes the pure `GoldDecisionPacket` (SCHEMA-011) and emits a **new** decision
record (a future SCHEMA). It is **not** the Supervisor treasury branch ([[Decision Engine]]/[[Decision
API]]/[[Decision Packet Schema]] — ADR-004), **not** live execution, **not** an order/broker/fill. It
**never** mutates, re-hashes, or re-emits a `GoldDecisionPacket`.

It is also distinct from [[Guardrail Enforcement]] (CAP-008, Risk Control / SYS-003 — hard risk-limit
*enforcement* via [[Guardrail Engine]] (MOD-001) + PRED-001..005 + [[Trade Validation Gate]] (GATE-001)).
The runtime is runtime/operational **admission** of a gold decision in the Trading Engine (dedup +
operational readiness). The two are **complementary, distinct layers — not duplicates**; a complete
trade would pass both. The future admission capability must **not** link to, merge with, or supersede
CAP-008 (see Relationships note).

### 2. Wrap, never enrich-in-place (the packet stays pure)
The runtime MUST call `build_decision` with `guards=None`. It MUST NOT pass a filled `GuardRefs` into
`build_decision`: because `compute_packet_id()` excludes `guard_refs`, doing so would make one
`packet_id` carry divergent `to_dict()` content across runtime states — breaking "`packet_id` ⇒ identical
content" and ADR-004 §3 (the packet must never depend on runtime state). All evaluated guard outcomes
live on the **new wrapping record**, never on the packet. The `guards=` parameter on `build_decision` is
retained as forward-compat, but is documented as **not** the runtime's enrichment path.

### 3. Input boundary
The runtime **core** consumes **only SCHEMA-011** (the `GoldDecisionPacket`) plus its own runtime state:
the prior ledger (explicit), a versioned operational-readiness input, and a versioned runtime-policy
config. The snapshot-derived guards (`data_ok`/`freshness_ok`/`cooldown_ok`) and the deterministic
`as_of` (= the snapshot's `clock_ts`) are **forwarded through the packet** as explicit provenance, so the
core never reads the raw SCHEMA-001 snapshot. SCHEMA-011 v0 does not yet carry a snapshot-guard block, so
a **small forward-compat additive change** — a `snapshot_guards` provenance block on the packet (distinct
from `guard_refs`, which stays the L3-outcome block) plus populating `as_of = snapshot.clock_ts` at build
time, with a `packet_schema_version` bump — is settled in Slice 2. The forwarded `snapshot_guards` is
thereby a **named, deterministic, explicit input with a stated source (the packet)** — never an implicit
echo. The core MUST NEVER read wall-clock, environment, network, or hidden caches.

The core MUST NOT import `src/risk`: this is **general bounded-context hygiene** (the Risk Control ↔
Trading Engine boundary defined in the [[Context Map]] (ARCH-001); cf. [[Canonical Ownership]], CON-003),
re-implementing the fail-closed verdict invariant rather than coupling the contexts. (This is *not*
ADR-004, which governs only the treasury/gold boundary.)

### 4. Stateful determinism / replay invariant (reconciling ADR-004 §3 and ADR-006 §3)
ADR-004 §3 / ADR-006 §3 keep the *packet* pure (preserved by §2). This ADR adds a **runtime-level**
invariant for the new record:

> Same (prior ledger state + this snapshot's recorded inputs: packet identity, snapshot-guards digest,
> operational input, `as_of`) + same `runtime_policy_version` + same runtime config
> ⇒ identical decision record **and** identical new ledger state.

State is **not** hidden: it is an **explicit function argument** (the prior ledger) and an **explicit
return value** (the new ledger). The core `evaluate()` is a pure function; the only IO (ledger
load/persist, operational-input read) lives in a thin boundary shell — exactly as `consume()` and the
gold `load_config()` confine IO to the edge.

### 5. Self-describing, append-only ledger
The ledger is an append-only, deterministically-serialized artifact carrying a ledger schema version.
Each entry persists everything needed to reproduce **its own** decision — the snapshot-guards digest, the
operational fingerprint, `as_of`, the verdict, and the triggering guard — keyed by `source_snapshot_id`,
with `seq = len(prior.entries)` so it continues across reload. No entry is ever mutated or deleted. The
ledger **alone** is sufficient replay state; replaying the same snapshot sequence from the same starting
ledger yields a byte-identical ending ledger.

### 6. Guard separation & scope
v0 **computes** exactly the two named stateful guards — `duplicate_ok` (PRED-006, **once-ever**: a prior
**ADMIT** of that `source_snapshot_id` fails it; a prior HOLD/REJECT does not count) and `operational_ok`
(PRED-007) — and **echoes** `data_ok`/`freshness_ok`/`cooldown_ok` from the packet's forwarded
`snapshot_guards`. `supervisor_ok` stays an **explicit `None` stub** (no supervisor exists; never silently
`True`). A **computed** cooldown is **cut from v0** (Future Work). Stateful guards are never added to
MOD-004 [[Feature Builder]].

### 7. No schema freeze (this slice)
This ADR does **not** define or freeze the runtime contract. The normative artifacts are future,
dedicated nodes with **new canonical_ids**, authored contract-first in Slice 2. Likely-next-free ids are
named as **non-binding candidates** only — `SCHEMA-012` (decision record), `SCHEMA-013` (ledger),
`MOD-007`, `INT-010`, `CAP-021`, `GATE-003`, `BENCH-003` — with formal assignment at the moment each node
is authored.

### 8. Policy fingerprinting & fail-closed verdict
The runtime-policy config carries a `runtime_policy_version` + a `runtime_policy_fingerprint()` (SHA-256
over the policy-defining fields, version excluded), mirroring `decision_policy_fingerprint`; a silent edit
without a version bump changes the fingerprint and fails a CI coherence test. The record's verdict ∈
{`ADMIT`, `HOLD`, `REJECT`}: a non-ADMIT verdict MUST name its triggering guard and an ADMIT must not
(mirroring `TradeValidationDecision.__post_init__`, by pattern, not import); `WATCH`/`INDETERMINATE`
packets and any required-but-failed guard fail closed to non-ADMIT. The record carries its own
`paper_only` invariant.

### 9. Creation Gates
The normative runtime contract may be authored in Slice 2 only after ALL of the following hold — all are
already satisfied:

- a. **Pure replay-stable packet exists** — [[Gold DecisionPacket v0 Schema]] (SCHEMA-011) is active,
  tested, byte-identical on replay. ✅ **Closed** (2026-06-08).
- b. **Deterministic time source exists** — `snapshot.clock_ts`/`clock_date`, read from the snapshot JSON,
  never computed. ✅ **Closed**.
- c. **Guard predicates named & snapshot guards available** — [[Duplicate OK]]/[[Operational OK]]
  (PRED-006/007); `data_ok`/`freshness_ok`/`cooldown_ok` on `Snapshot.guards`. ✅ **Closed**.
- d. **Config/fingerprint pattern proven** — `DecisionPolicyConfig` + `decision_policy_fingerprint`. ✅
  **Closed**.
- e. **Pure-engine + IO-boundary-shell pattern proven** — [[Guardrail Engine]] (MOD-001) +
  [[Snapshot Consumer]] (MOD-003) `consume()`. ✅ **Closed**.

**All five gates pass.** Unlike ADR-006, no gate is *open*, so the contract becomes authorable in Slice 2
after the checkpoint review of this ADR.

## Illustrative Field Sketch (non-normative)

> **Illustrative, provisional, non-normative — not a schema.** It exists only to give the constraints a
> concrete referent; the normative SCHEMA nodes (Slice 2) are the single source of truth once authored.

A future runtime decision record *might* carry: `record_id` (deterministic, binding `packet_id` +
`runtime_policy_fingerprint` + `as_of` + operational fingerprint + snapshot-guards digest + prior-ledger
state hash), `source_packet_id`, `source_snapshot_id`, `verdict` (`ADMIT`/`HOLD`/`REJECT`),
`triggered_guard`, `reason`, the six guard outcomes, `runtime_policy_version`, `as_of`, the prior/new
ledger state hashes, `non_execution_notice`, `constraints`. A ledger entry *might* carry:
`source_snapshot_id`, `source_packet_id`, `as_of`, `verdict`, `triggered_guard`, `snapshot_guards_digest`,
`operational_fingerprint`, `seq`.

## Non-Goals (explicitly deferred)

This ADR and the runtime slice it plans explicitly defer:
- a wall-clock-triggered scheduler / cron / long-running daemon;
- live execution, broker integration, order routing;
- position sizing, fills, P&L accounting;
- a **live** operational-status feed (v0 operational input is an explicit, versioned, file/caller-supplied
  artifact — not a venue probe);
- a **computed** cooldown guard (v0 echoes the snapshot's `cooldown_ok`);
- multi-instrument support; persistence backends beyond a local JSON ledger;
- the **normative SCHEMA nodes, runtime module, L3 guard implementations, gate, and all code** (Slice 2).

No execution, order, broker, position, fill, or P&L nodes are created in this slice.

## Alternatives Considered

- **Enrich the packet in place** (fill `guard_refs` via `build_decision(guards=...)`). **Rejected** —
  `packet_id` excludes `guard_refs`, so one id would carry divergent content across runtime states,
  breaking ADR-004 §3 / ADR-006 §3.
- **Long-running daemon holding the ledger in memory.** **Rejected** — violates KA-009 (Wake-Execute-
  Sleep, file-mediated continuity) and hides state; replay would depend on process lifetime.
- **Wrap with a new record + stateless invocation, ledger as explicit in/out.** **Chosen** — the packet
  stays pure; runtime state is an explicit argument and return value; replay is byte-identical from the
  ledger alone.
- **Author the runtime contract inside this ADR (a single combined epoch).** **Rejected** — keeps this
  ADR a boundary record; the contract/code is a separate reviewable slice after the checkpoint, mirroring
  the ADR-006 → SCHEMA-011 rhythm.

## Consequences

### Positive
- Establishes the runtime's boundary, input rules, and a stateful replay invariant **before** any
  contract is frozen — extending the determinism discipline to the first stateful layer.
- Keeps the pure planning packet pure and the Supervisor treasury branch permanently separate; keeps
  Risk Control (CAP-008) and gold admission (the new capability) distinct but complementary.
- Gives a clear, gated path to the normative nodes (Creation Gates all pass), so authoring is justified.

### Negative / Trade-offs
- A small forward-compat additive change to the frozen SCHEMA-011 packet (a `snapshot_guards` provenance
  block + populated `as_of`, with a `packet_schema_version` bump and re-pinned goldens) is incurred in
  Slice 2.
- The concrete runtime contract remains unwritten until Slice 2; downstream work waits on the checkpoint.

### Risks
- Hidden-state / wall-clock leak in the core (mitigated by §2/§3, the IO-boundary shell, and a
  byte-identical replay test).
- `operational_input` non-determinism if it ever became a live probe (mitigated by keeping it an explicit
  versioned artifact, default-closed, with its fingerprint persisted into the ledger).

## Future Work

When this ADR is accepted at the checkpoint, Slice 2 authors — contract-first, with new canonical_ids —
the runtime decision-record schema, the ledger schema, the runtime module, the runtime interface, the
admission capability, and the runtime admission gate; **implements** [[Duplicate OK]]/[[Operational OK]];
and adds the determinism/idempotency tests + a sequence-replay benchmark. The runtime decision record is
governed by a new blocking gate; [[Gold Decision Gate]] (GATE-002) stays **advisory** over the still-pure
packet (promoting it would be blocking over an all-`None` packet). Later epochs may add a computed
cooldown and a live operational-status feed under their own amendments.

## Relationships

### Depends On
- [[Gold DecisionPacket v0 Schema]]
- [[Gold Decision Builder]]
- [[Snapshot Consumer]]

### Justified By
- [[ADR - Decision Layer Re-grounding]]
- [[ADR - Gold DecisionPacket v0 Planning]]

### Constrained By
- [[Canonical Ownership]]

### Originates From
- [[Stateless Agent Architecture]]

**Complementarity note (no coupling edge):** the future Paper-Trade Admission capability (Slice 2) is
*complementary to but distinct from* [[Guardrail Enforcement]] (CAP-008, Risk Control): CAP-008 enforces
hard risk limits; the gold runtime admits a decision on dedup + operational readiness. A complete trade
passes both. The admission capability must **not** link to, merge with, or supersede CAP-008. This is
recorded here deliberately **without** a typed relationship edge, to avoid implying coupling across the
Risk Control ↔ Trading Engine boundary ([[Context Map]], ARCH-001).
