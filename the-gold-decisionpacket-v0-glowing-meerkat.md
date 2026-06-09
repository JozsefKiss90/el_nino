# Plan — Paper-Trading Runtime (Epoch a)

## Context

The Gold DecisionPacket v0 epoch is closed: `consume → build_features → classify → build_decision`
now produces a **pure, replay-safe** `GoldDecisionPacket` (SCHEMA-011). That packet carries a
six-guard `GuardRefs` block in which the two **stateful L3 guards** — `duplicate_ok` (PRED-006) and
`operational_ok` (PRED-007) — are deliberately left `None`, because computing them needs runtime
state that the pure builder must never touch (`GuardRefs` docstring; ADR-006 Non-Goals). ADR-006 also
explicitly defers the *"paper-trading runtime"* itself.

**This epoch un-defers exactly that runtime and nothing more.** It builds the first stateful Layer-3
component: a deterministic admission layer that consumes a packet + runtime state and computes the two
named guards, emitting an admission decision. It does **not** add live execution, a wall-clock
scheduler/daemon, broker/order routing, sizing, fills, or P&L — those stay deferred. DEBT-01 (a
NameError in the snapshot *publisher*) blocks epoch (b) real-corpus accumulation, **not** this consumer.

**Central tension & resolution.** Everything upstream is pure (only `consume()` does IO); the packet's
`packet_id` is a content hash over a 6-field version tuple that **excludes `guard_refs`**. A stateful
runtime must reconcile with that determinism discipline. Resolution (your confirmed choices):

1. **WRAP, not enrich-in-place.** The packet stays pure (`build_decision(guards=None)`); the runtime
   emits a **new** `RuntimeDecisionRecord` that references `packet_id` and carries the evaluated guard
   block + verdict. Filling the packet's guards in place would let one `packet_id` carry divergent
   content (collision) and violate ADR-004 §3.
2. **State is an explicit value, never ambient.** The core is a pure function
   `evaluate(packet, prior_ledger, operational_input, config) -> (record, new_ledger)`;
   the only IO (ledger load/persist, operational-input read) lives in a thin boundary shell — exactly
   like `consume()` / `load_config()`. This mirrors **KA-009 "Stateless Agent Architecture"**
   (Wake-Execute-Sleep, file-mediated continuity).
3. **ADR-first.** ADR-009 sets constraints + gates only; the contract/code freeze is a separate
   post-checkpoint slice (mirrors the ADR-006 → SCHEMA-011 rhythm).

This plan was hardened by an adversarial design review; the non-obvious correctness fixes (self-
describing ledger, once-ever dedup keyed on prior ADMIT, GATE-003 vs GATE-002, cut computed cooldown)
are folded in below.

---

## Recommended approach

### Slice 1 — ADR-009 (planning / governance only) → CHECKPOINT

Author `dev_graph/decisions/ADR - Paper-Trading Runtime Planning.md` (`canonical_id: ADR-009`,
`type: decision_record`), mirroring the ADR-006 section skeleton (Status / Context / Decision (numbered
constraints + Creation Gates) / Non-Goals / Alternatives / Consequences / Future Work / Relationships).
It **does not** freeze a schema or author code — it records the boundary, then a checkpoint pauses for
review. Key numbered constraints:

1. **Bounded context & separation** — net-new component, new canonical ids; consumes SCHEMA-011, emits
   SCHEMA-012; **not** the treasury branch (MOD-002/INT-006/SCHEMA-004; ADR-004), **not** live execution.
   Never mutates/re-hashes/re-emits a packet. **Distinct from CAP-008 Guardrail Enforcement** (Risk
   Control / SYS-003 — hard risk-limit *enforcement* via MOD-001 + PRED-001..005 + GATE-001): CAP-021 is
   runtime/operational *admission* of a gold decision in the Trading Engine (dedup + operational
   readiness). The two are **complementary, distinct layers — not duplicates**; a complete trade would
   pass both. CAP-021 must **not** link to, merge with, or supersede CAP-008; a `### Relationships` note
   records the complementarity **without coupling**.
2. **Wrap invariant** — the runtime MUST call `build_decision(guards=None)`; evaluated guards live only
   on the record. The `guards=` seam on `build_decision` is retained as forward-compat but is **not**
   the runtime's path.
3. **Input boundary** — the core consumes **only SCHEMA-011** (the `GoldDecisionPacket`) plus its own
   runtime state: the prior ledger (explicit), a versioned `OperationalInput`, and a versioned
   `RuntimePolicyConfig`. The snapshot-derived guards (`data_ok`/`freshness_ok`/`cooldown_ok`) and the
   deterministic `as_of` (= `snapshot.clock_ts`) are **forwarded through the packet** as explicit
   provenance, so the core never reads the raw SCHEMA-001 snapshot. SCHEMA-011 v0 does not yet carry a
   snapshot guard block, so a **small forward-compat additive change** — a `snapshot_guards` provenance
   block on the packet (distinct from `guard_refs`, which stays the L3-outcome block) + populating
   `as_of = snapshot.clock_ts` at build time, with a `packet_schema_version` bump — is settled in
   Slice 2. `snapshot_guards` is thereby a **named, deterministic, explicit input with a stated source
   (the packet)** — never an implicit echo. **Never** wall-clock/env/network/hidden cache inside the
   core. **Must not import `src/risk`** — general bounded-context hygiene (Risk Control vs Trading Engine;
   Context Map / CON-003), re-implementing the fail-closed verdict invariant rather than coupling the
   contexts (this is *not* ADR-004, which governs only the treasury/gold boundary).
4. **Stateful determinism / replay invariant** (the ADR core, reconciling ADR-004 §3 + ADR-006 §3):
   > Same (prior ledger + this snapshot's recorded inputs: packet identity, snapshot-guards digest,
   > `OperationalInput`, `as_of`) + same `runtime_policy_version`/`runtime_config`
   > ⇒ identical `RuntimeDecisionRecord` **and** identical new ledger state.
5. **Self-describing, append-only ledger** — each entry persists everything needed to reproduce its own
   decision (snapshot-guards digest + operational fingerprint + `as_of` + verdict + triggered guard);
   keyed by `source_snapshot_id`; never mutated/deleted; `seq = len(prior.entries)` so it continues
   across reload. The ledger **alone** is sufficient replay state.
6. **Guard separation & scope** — compute `duplicate_ok` (PRED-006, **once-ever**) + `operational_ok`
   (PRED-007); echo `data_ok`/`freshness_ok`/`cooldown_ok` from the packet's `snapshot_guards`
   provenance; `supervisor_ok = None`
   stub (no supervisor). Stateful guards are never added to MOD-004. **Computed cooldown is cut from
   v0** (Future Work).
7. **Policy fingerprinting** — `RuntimePolicyConfig` carries `runtime_policy_version` +
   `runtime_policy_fingerprint()` (SHA-256 over policy fields, version excluded); a silent edit fails a
   CI coherence test — identical idiom to `decision_policy_fingerprint`.
8. **Fail-closed verdict** — verdict ∈ {`ADMIT`,`HOLD`,`REJECT`}; non-ADMIT MUST name its triggering
   guard, ADMIT must not (mirrors `TradeValidationDecision.__post_init__`); `WATCH`/`INDETERMINATE`
   packets and any required-but-failed guard ⇒ non-ADMIT; record carries its own `paper_only` invariant.
9. **Creation Gates** — all already satisfied (pure packet exists; deterministic clock = `snapshot.clock_ts`;
   guard predicates named; config/fingerprint + pure-engine/IO-boundary patterns proven). No open gate,
   so the contract becomes authorable in Slice 2.

**Non-Goals (keep deferring):** wall-clock scheduler/daemon; live execution/broker/order routing;
sizing/fills/P&L; a *live* operational-status feed (v0 `OperationalInput` is an explicit versioned
artifact, not a venue probe); computed cooldown; multi-instrument; persistence beyond a local JSON ledger.

**Writeback for Slice 1:** create the ADR node; add to `dev_graph/index.md` Decisions table; append
`dev_graph/log.md`; back-link `related_decisions` on ADR-004/ADR-006; lint checks on touched nodes.

> **CHECKPOINT — pause for review.** Governance frozen, no code.

### Slice 2 — Contract-first implementation

**New node set** (canonical ids verified next-free against `index.md`):

| id | type | purpose |
|----|------|---------|
| SCHEMA-012 | artifact_schema | `RuntimeDecisionRecord` — packet ref + guard block + ADMIT/HOLD/REJECT verdict + runtime versions + ledger-state hashes |
| SCHEMA-013 | artifact_schema | `RuntimeLedger`/`LedgerEntry` — append-only, self-describing dedup state keyed by `source_snapshot_id` |
| MOD-007 | module | Paper-Trading Runtime — pure `evaluate()` + guard predicates + IO shell + replay driver |
| INT-010 | interface | Paper Runtime API — `evaluate(...) -> (record, new_ledger)` |
| CAP-021 | capability | Paper-Trade Admission, **`parent_system: [[Trading Engine]]` (SYS-002)**, downstream of CAP-020; `Originates From → [[Stateless Agent Architecture]]` (KA-009); complementary to but **distinct from CAP-008 Guardrail Enforcement** (SYS-003) — no link/merge/supersede, `### Relationships` records the complementarity only |
| GATE-003 | gate | Runtime Admission Gate — governs the **record** (blocking). **GATE-002 stays advisory** over the still-pure packet (promoting it would be blocking over an all-`None` packet) |
| PRED-006 / PRED-007 | predicate | implement: set `implemented_in`, `validated_by`, bump `not-started → tested` |
| FILE-019..023, TEST-013..016, BENCH-003 | file/test/benchmark | created at writeback |

Model the runtime as **SYSTEM(SYS-002) → CAPABILITY(CAP-021) → MODULE(MOD-007)** (the 24-type ontology
has no "runtime" type; this matches how stateful concerns are modeled). No new SYS node; no new wheel
package (it lives under the existing `src/gold` wheel entry).

**Source layout — `src/gold/paper_runtime/`** (peer of `decision_builder`; keeps the gold lineage cohesive):

```
src/gold/paper_runtime/
  __init__.py    # exports: evaluate, run_once, run_sequence, RuntimeDecisionRecord,
                 #          RuntimeLedger, RuntimePolicyConfig, OperationalInput, Verdict
  models.py      # SCHEMA-012 + SCHEMA-013 + OperationalInput + Verdict + GuardOutcome   (FILE-019)
  config.py      # RuntimePolicyConfig + runtime_policy_fingerprint + load_config         (FILE-020)
  predicates.py  # the guard predicates + ALL_GUARDS                                      (FILE-021)
  engine.py      # pure evaluate() — conjunction + verdict + ledger append               (FILE-022)
  runtime.py     # IO boundary shell (load/persist ledger, load operational) + run_once
                 #   + run_sequence (pure, in-memory replay driver)                       (FILE-023)
```

**Dataclasses (frozen, stdlib-only; `to_dict()` alphabetical keys, 6dp floats):**

- `Verdict(str, Enum)` = `ADMIT | HOLD | REJECT`.
- `GuardOutcome` = `(name: str, passed: bool | None, reason: str)` — **single source of truth**; derive the
  `GuardRefs`-shaped dict by reusing `_GUARD_NAMES` imported from `gold.decision_builder.models` (no
  second ordering). Avoids parallel flag/reason desync.
- `OperationalInput` — `instrument`, `tradeable`, `venue_open`, `halt`, `degraded`, `as_of`, `source_version`;
  `fingerprint()`; `from_dict`/`load` fail-closed, **default-closed** (absent/malformed ⇒ not tradeable).
- `LedgerEntry` — `source_snapshot_id`, `source_packet_id`, `as_of`, `verdict`, `triggered_guard`,
  `snapshot_guards_digest`, `operational_fingerprint`, `seq`. **Self-describing** (defect fix: the ledger
  alone reproduces every decision).
- `RuntimeLedger` — `ledger_schema_version`, `entries: tuple[LedgerEntry, ...]`; methods `empty()`,
  `has_admit(snapshot_id) -> bool` (prior **ADMIT** of that id — the dedup test), `append(entry)` →
  **new frozen ledger** (`seq = len(entries)`), `state_hash()` (SHA-256 over
  `json.dumps(to_dict(), sort_keys=True, separators=(",",":"))`), `to_dict`/`from_dict` fail-closed.
- `RuntimePolicyConfig` — `require_operational: bool = True`, `require_snapshot_guards: bool = True`,
  `runtime_policy_version`; `runtime_policy_fingerprint()` over the policy fields (version excluded), exact
  `DecisionPolicyConfig` idiom; `from_mapping`/`load_config` fail-closed; `DEFAULT_RUNTIME_POLICY_CONFIG`.
- `RuntimeDecisionRecord` (SCHEMA-012) — `record_id` (`paper-v0:` + SHA-256 over `packet_id` +
  `runtime_policy_fingerprint` + `as_of` + `operational_fingerprint` + `snapshot_guards_digest` +
  `prior_ledger.state_hash()`), `record_schema_version`, `source_packet_id`, `source_snapshot_id`,
  `verdict`, `triggered_guard`, `reason`, `guard_outcomes: tuple[GuardOutcome, ...]`,
  `runtime_policy_version`, `as_of`, `prior_ledger_state_hash`, `new_ledger_state_hash`,
  `non_execution_notice`, `constraints`. `__post_init__`: ADMIT ⇔ `triggered_guard is None`; paper-only.

**Guard predicates** (mirror `PredicateResult = tuple[bool, str]`):

```
GuardResult = tuple[bool | None, str]
duplicate_ok(packet, prior_ledger) -> GuardResult        # PRED-006: pass iff NOT prior_ledger.has_admit(packet.source_snapshot_id)
operational_ok(packet, op, config) -> GuardResult        # PRED-007: pass iff tradeable & venue_open & not halt & not degraded
data_ok(packet) -> GuardResult                           # echo packet.snapshot_guards.data_ok
freshness_ok(packet) -> GuardResult                      # echo packet.snapshot_guards.freshness_ok
cooldown_ok(packet) -> GuardResult                       # echo packet.snapshot_guards.cooldown_ok (computed cooldown deferred)
# supervisor_ok -> explicit None stub (no supervisor)
```

`evaluate()` runs the guards as a short-circuit conjunction (first failure names the guard), applies
fail-closed rules (WATCH/INDETERMINATE ⇒ HOLD; required-but-failed guard ⇒ REJECT), appends exactly one
`LedgerEntry` (carrying its verdict), and returns `(record, new_ledger)` — **no IO**. `run_once()` is the
IO entry (load ledger → `evaluate` → persist atomically); `run_sequence()` threads the ledger over an
ordered list in memory (the determinism/BENCH-003 vehicle, no IO).

**Tests (`tests/gold/`) + benchmark:**

- TEST-013 `test_paper_runtime_guards.py` — each guard unit (duplicate pass-on-unseen / fail-on-prior-ADMIT;
  operational pass/halt/degraded/default-closed-on-absent; data/freshness/cooldown echo).
- TEST-014 `test_paper_runtime_engine.py` — conjunction order + short-circuit; fail-closed verdict
  (`__post_init__`); WATCH/INDETERMINATE ⇒ HOLD; triggered_guard = first failure.
- TEST-015 `test_paper_runtime_determinism.py` — byte-identical `record.to_dict()` across two `evaluate()`
  runs from the same prior ledger; `runtime_policy_fingerprint` coherence (pinned hash).
- TEST-016 `test_paper_runtime_ledger.py` — `run_sequence` twice ⇒ identical records **and** identical
  ending `state_hash`; re-presented snapshot ⇒ `duplicate_ok=False` / non-ADMIT; append-only; `seq`
  continuity across reload; a halted op mid-sequence ⇒ REJECT with the ledger still advancing.
- BENCH-003 `benchmarks/gold/run_paper_runtime_bench.py` + `artifacts/paper_runtime_bench.json` — replay a
  deterministic snapshot **sequence** (reuse `consume→build_features→classify→build_decision(guards=None)`
  + fixed `OperationalInput` fixtures) through `run_sequence` twice; assert byte-identical records +
  ending ledger; re-present the first snapshot to demonstrate idempotency. Report carries
  `benchmark_id`, `runtime_policy_version`, `runtime_policy_fingerprint`, `ending_ledger_state_hash`; a
  committed-artifact-in-sync test mirrors `test_gold_bench.py`.

**Writeback (Slice 2):** create the nodes above; bump MOD-007/CAP-021; update the **SCHEMA-011** node for
the additive `snapshot_guards` provenance block + `packet_schema_version` bump (and re-pin the
`test_e2e_pipeline` / `gold_bench` goldens), then wire its `consumed_by → [[Paper-Trading Runtime]]`;
update PRED-006/007 + GATE-003; `CAP-020 Used By → CAP-021`; `index.md` + `log.md`; all 11 lint checks on
touched nodes (esp. check 9 — CAP-021 must **not** link to or supersede deprecated CAP-004, **CAP-008
Guardrail Enforcement**, or Order Management).

---

## Reuse map (do not reinvent)

- `src/gold/decision_builder/config.py` — copy the `*_version` + `*_fingerprint()` idiom
  (`sorted(_FIELDS)`, `json.dumps(..., separators=(",",":"))`, version excluded) + fail-closed
  `from_mapping`/`load_config` for `RuntimePolicyConfig`.
- `src/risk/guardrail_engine/{predicates,guardrail_engine}.py` — mirror the pure-predicate
  `(…) -> (passed, reason)` shape, the short-circuit conjunction, and the `TradeValidationDecision`
  fail-closed `__post_init__`. **Pattern only — never import** (bounded-context hygiene: Risk Control vs
  Trading Engine; Context Map / CON-003 — not ADR-004).
- `src/snapshot/snapshot_consumer/{consumer,models.py}` — `data_ok`/`freshness_ok`/`cooldown_ok`
  originate from `Snapshot.guards` (forwarded onto the packet's `snapshot_guards` block at build time,
  Slice 2); `clock_ts` is the deterministic time source (forwarded as the packet's `as_of`); mirror
  `consume()`'s absence-returns-empty vs malformed-raises split for `load_ledger`.
- `src/gold/decision_builder/models.py` — import `_GUARD_NAMES` for the guard ordering; `build_decision`
  line 80 (`guards if guards is not None else GuardRefs()`) confirms the runtime must call with `guards=None`.
- `benchmarks/gold/run_gold_bench.py` + `tests/gold/test_e2e_pipeline.py` — the replay-harness +
  committed-artifact + `json.dumps(..., sort_keys=True)` determinism pattern BENCH-003 / TEST-015/016 mirror.

## Top risks & mitigations

- **Hidden-state/wall-clock leak in the core** → all IO confined to `runtime.py`; `as_of` threaded from
  `snapshot.clock_ts`; determinism test runs `evaluate()`/`run_sequence` (no IO) twice; assert the packet
  built inside the runtime has `guard_refs == GuardRefs()` (proves no enrich-back).
- **Ledger not self-describing** (the review's key defect) → `LedgerEntry` stores the snapshot-guards
  digest + operational fingerprint + `as_of`, so a cold replay reproduces `operational_ok`/`data_ok`.
- **Idempotency ambiguity** → dedup is **once-ever**, keyed on a prior **ADMIT** of that `source_snapshot_id`
  (`has_admit`); a prior HOLD/REJECT does not count as "already produced a packet"; no window param.
- **GATE-002 promotion** → do **not** flip GATE-002 (it governs the all-`None` packet); GATE-003 governs the
  record. Record `__post_init__` is the real fail-closed surface.
- **`OperationalInput` determinism** → explicit versioned artifact, default-closed, fingerprint persisted
  into the ledger; a live feed stays a Non-Goal.

## Verification

1. `python -m pytest tests/ -q` — full suite green (prior 53 + 719 regime + gold + new TEST-013..016).
2. `python -m mypy --strict src` and `python -m ruff check src tests` — clean on `src/gold/paper_runtime`.
3. `python benchmarks/gold/run_paper_runtime_bench.py` — prints `all_replays_byte_identical=True`; the
   committed `artifacts/paper_runtime_bench.json` matches `build_report()` (in-sync test passes).
4. Determinism proof: `run_sequence` twice yields byte-identical records + identical
   `ending_ledger_state_hash`; re-presented snapshot is flagged `duplicate_ok=False`.
5. Fingerprint coherence: editing a `RuntimePolicyConfig` field without bumping `runtime_policy_version`
   changes `runtime_policy_fingerprint()` and fails TEST-015.
6. dev_graph: all 11 lint checks pass on touched nodes; gate-board/index/log updated.
