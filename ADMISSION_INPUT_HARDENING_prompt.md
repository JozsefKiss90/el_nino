# Claude Code prompt — admission-input hardening (computed cooldown + live operational feed)

Paste the block below into a fresh Claude Code session rooted in `el_nino`.

---

Run one governed slice that lifts **two** deferred ADR-009 Non-Goals for the admission layer: **(A) the computed cooldown guard** and **(B) the live operational-status feed**. They are sequenced as two cleanly-separated sub-steps and must **not** entangle: **A** is a deterministic core behavior change that owns the single `runtime_policy_version` bump; **B** is an additive, non-replayable IO adapter behind the existing `OperationalInput` seam that bumps nothing and is quarantined off the replay path. Do A first, then B, then **one** combined benchmark re-pin + writeback. **HARD PAUSE for my review before committing the version bump**, and a final pause when the whole slice is built.

Two invariants govern the whole slice:
- **Cooldown is deterministic** — computed from the ledger's last-ADMIT `as_of` vs. the current snapshot's `as_of` + a versioned window; **never wall-clock**.
- **The operational feed never touches the replay path** — read once on the live `run_once` path, the resulting `OperationalInput` captured + recorded so replay threads the captured value (ADR-011 §2 / gate-f quarantine). No clock/network on replay.

## Step 0 — read

1. `dev_graph/CLAUDE.md` — Config/Schema Evolution + version-bump procedures, writeback checklist, 11 lint checks, Neo4j re-sync, §7.5 threshold.
2. `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009) — the **six-guard taxonomy**, the `duplicate_ok`/`operational_ok` **computed-from-ledger** pattern (mirror it for cooldown), the `operational_ok` guard + `OperationalInput` model, and the **two Non-Goal lines** this slice lifts (computed cooldown; live operational feed).
3. `decisions/ADR - Execution Layer Planning.md` (ADR-011 §2 + gate f) — the **non-replayable-adapter quarantine** + KA-008 credential isolation; sub-step B follows this boundary exactly.
4. The code that changes / is composed: `src/gold/paper_runtime/` `engine.py` (`evaluate`), `predicates.py` (`duplicate_ok`/`operational_ok`), `models.py` + `RuntimeLedger`/SCHEMA-013 (does it record per-ADMIT `as_of`?), `config.py` (`RuntimePolicyConfig` + fingerprint + `runtime_policy_version`); the orchestrator `src/orchestration/` `config.py` (`DEFAULT_OPERATIONAL_INPUT`) + `runtime.py` (how `run_once` threads it).
5. `benchmarks/.../run_paper_runtime_bench.py` (BENCH-003) + `benchmarks/orchestration/run_chain_bench.py` (BENCH-006) — the re-pin targets. `knowledge_assets/Agent Safety Principles.md` (KA-008) if the feed needs credentials.

## Step 1 — Sub-step A: computed cooldown guard (deterministic; owns the version bump)

**Resolve first (state the answer):** does the computed L3 cooldown **replace** the echoed `cooldown_ok` or sit **alongside** the L2 snapshot guard? Decide against the actual six-guard taxonomy; the likely shape is a computed L3 `cooldown_ok = (current as_of − last_ADMIT as_of) ≥ cooldown_window`.

- Add a **versioned `cooldown_window`** to `RuntimePolicyConfig`; **bump `runtime_policy_version`** + update the fingerprint (admission outputs change → replay-key axis change).
- Compute it in the **pure `evaluate()` core** from `prior_ledger` (last ADMIT `as_of`) + the snapshot `as_of` + the window, mirroring `duplicate_ok`. **Pure, no wall-clock. Fail-closed** (missing/ambiguous timing ⇒ block).
- If the ledger doesn't record the last ADMIT's `as_of`, that additive capture (touches SCHEMA-013) is a checkpoint item — flag it.

## Step 2 — Sub-step B: live operational-status feed (additive IO adapter; bumps nothing)

- The pure core keeps taking `OperationalInput` as an **explicit value — unchanged contract, no `*_version` bump.** The new piece is an adapter that **reads** operational status (tradeable / venue_open / halt / degraded) at `run_once` time and **produces** that `OperationalInput`.
- **Pick + justify the v0 source** (deterministic market-hours/calendar for the GLD venue, and/or a live venue clock/calendar if creds exist); keep it **pluggable**. **Fail-closed:** unavailable/ambiguous ⇒ `tradeable = False`.
- **Capture + record** the produced `OperationalInput` so replay reconstructs the `operational_ok` outcome byte-identically without re-reading the feed; if the record/ledger doesn't capture enough, flag the additive capture. **Credential isolation (KA-008)** if keyed (env/`.secrets` only).
- The feed read is **live-path only, logged not replayed**; `run_sequence`/BENCH never call it.

## Step 3 — combined determinism + replay (one pass)

- **One** `runtime_policy_version` bump (from A); the feed (B) bumps nothing. Retain old-version goldens (valid for the prior version); **re-run + re-pin BENCH-003 and BENCH-006 once** under the new version, capturing both the new cooldown behavior and the captured operational input.
- Make the golden diff **interpretable**: the benchmark should report the cooldown-driven verdict changes and the captured-operational provenance as **distinct** axes so a reviewer can tell A's effect from B's.
- Tests: **A** — synthetic ledger sequences (cooldown blocks a second ADMIT inside the window; elapsed window allows; fail-closed on missing timing) with byte-identical replay at the new version. **B** — adapter with an injected feed yields correct `OperationalInput` across open/halt/degraded/closed; fail-closed when unavailable; a **captured-vs-live** test proving replay independence from the feed (mirror the execution `guard_config` env-independence test); assert no live call on the replay path.
- `mypy --strict` + `ruff` clean; full prior suite green (only the intended golden changes, at the new version).

## Step 4 — governance + writeback (combined)

- One **ADR-009 amendment** covering **both** lifted Non-Goals + the `runtime_policy_version` bump (state whether cooldown replaced or augmented the echo, and the feed's non-replayable quarantine). Log per the Config Evolution procedure.
- Update the MOD-007 node + its engine/predicates/config file nodes; create a computed-cooldown predicate node if warranted (re-derive next-free `PRED-0xx`); author the feed adapter file/test nodes (re-derive `FILE-0xx`/`TEST-0xx`; a thin module node only if it warrants one); update the MOD-010/MOD-007 operational-seam Open Question; re-pin the BENCH-003/006 node artifacts; `index.md` + `log.md` (one Config-version-evolution entry covering both sub-steps); 11 lint checks; **Neo4j re-sync**.

## Checkpoints + constraints

- **HARD PAUSE before committing the `runtime_policy_version` bump** (it changes the accepted baseline's outputs); final pause when the slice is built.
- **Keep A and B separated** — the feed read must never enter the cooldown computation or any pure core; cooldown logic must never depend on the live feed.
- **Deterministic** — cooldown from explicit ledger state + snapshot `as_of`, never wall-clock; **preserve old-version replay**; fail-closed throughout; rule-based.
- **Feed quarantine** — live read only on the IO path, captured for replay, logged not replayed; **credential isolation**; no pure-core or `OperationalInput`-contract change.
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids. Summarize A's old-vs-new behavior, B's source + quarantine/capture evidence, and the node placements, and **stop for my review**.
