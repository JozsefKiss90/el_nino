# Claude Code prompts — two orchestrator follow-ups

Two **independent** slices; run them in separate sessions, either order. Prompt A (computed cooldown) is a deterministic behavior change to the accepted runtime baseline — it bumps a version and re-pins benchmarks, but adds no live surface. Prompt B (operational feed) adds a live, non-deterministic IO surface that must be quarantined off the replay path. If choosing an order, A is the lower-risk internal one; B is the determinism-boundary-sensitive one.

---

# Prompt A — computed cooldown guard

Paste into a fresh Claude Code session rooted in `el_nino`.

---

Lift ADR-009's deferred "**computed cooldown guard (v0 echoes)**" — make the L3 cooldown guard **computed from runtime state** (time since the last ADMIT) instead of echoing the snapshot's `cooldown_ok`. This **changes the accepted MOD-007 admission baseline's behavior**, so it is a governed, versioned change: it bumps `runtime_policy_version`, re-pins the affected golden benchmarks, and must preserve old-version replay. Deterministic only — the sole time source is the snapshot's `as_of`/`clock_ts`, **never** wall-clock. **HARD PAUSE for my review before committing the version bump.**

## Step 0 — read

1. `dev_graph/CLAUDE.md` — the Config/Schema Evolution + version-bump procedures, writeback checklist, 11 lint checks, Neo4j re-sync.
2. `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009) — the **six-guard taxonomy**, the `duplicate_ok`/`operational_ok` **computed-guard** pattern (mirror it), and the Non-Goal line that defers the computed cooldown (this slice lifts it).
3. The MOD-007 code (read; this is what changes): `src/gold/paper_runtime/` `engine.py` (`evaluate`), `predicates.py` (`duplicate_ok`/`operational_ok` — the computed-from-ledger idiom), `models.py` + the ledger (`RuntimeLedger` / SCHEMA-013 — confirm whether per-ADMIT `as_of`/timestamps are recorded; the cooldown needs the last ADMIT's time), `config.py` (`RuntimePolicyConfig` + `runtime_policy_fingerprint` + `runtime_policy_version`).
4. `benchmarks/.../run_paper_runtime_bench.py` (BENCH-003) and `benchmarks/orchestration/run_chain_bench.py` (BENCH-006) — both re-pin targets (the runtime is in the chain).

## Step 1 — resolve the design question, then build

**Resolve first (state the answer):** does the computed L3 cooldown **replace** the echoed `cooldown_ok`, or is it an **additional** L3 guard distinct from the L2 snapshot cooldown? Read the actual six-guard taxonomy + ADR-009 to decide. The likely shape: a computed L3 `cooldown_ok = (current as_of − last_ADMIT as_of) ≥ cooldown_window`, with the L2 snapshot guard handled per its existing role. Pick one and justify it against the taxonomy.

Then:

- Add a **versioned `cooldown_window`** (e.g., min gap between ADMITs, in a clock unit) to `RuntimePolicyConfig`; **bump `runtime_policy_version`** and update the fingerprint (this changes admission outputs → it is a replay-key axis change).
- Compute the guard in the **pure `evaluate()` core** from `prior_ledger` (the last ADMIT's `as_of`) + the current snapshot's `as_of` + the window. **Pure, no wall-clock.** Mirror the `duplicate_ok` computed-from-ledger pattern. **Fail-closed:** missing/ambiguous timing ⇒ `cooldown_ok = False` (block).
- If the ledger does not already record the last ADMIT's `as_of`, that is an **additive** capture to settle carefully (it touches SCHEMA-013) — flag it explicitly at the checkpoint.

## Step 2 — determinism + replay preservation

- **Old `runtime_policy_version` reproduces the echo behavior** (the version is in the replay key); the new version computes. Retain the old BENCH-003 golden as valid for the old version; **re-run + re-pin BENCH-003 and BENCH-006** under the new version.
- The change **alters admission verdicts** for some inputs (a second ADMIT inside the cooldown window now blocks). Exercise that explicitly with **synthetic** ledger sequences (the real corpus is sparse/AVOID and can't): cooldown-blocks-second-admit, cooldown-elapsed-allows, fail-closed-on-missing-timing — and assert byte-identical replay at the new version.
- `mypy --strict` + `ruff` clean; full prior suite green (expect intended golden changes only at the new version).

## Step 3 — governance + writeback

- This lifts an ADR-009 Non-Goal and changes the accepted baseline → **governance is required.** Assess: an **ADR-009 amendment** (record that cooldown is now computed, with the `runtime_policy_version` bump) vs. a thin new ADR. Likely the ADR-009 update + the bump logged per the Config Evolution procedure. State the choice.
- Update the MOD-007 node + its config/predicates/engine file nodes; if a new computed guard predicate warrants a node, create it (re-derive next-free `PRED-00x`); re-pin BENCH-003/006 nodes' artifacts; `index.md` + `log.md` (a Config-version-evolution entry); 11 lint checks; **Neo4j re-sync**.
- **HARD PAUSE before committing the `runtime_policy_version` bump** — it changes the accepted baseline's outputs.

## Constraints

- **Deterministic** — cooldown from explicit ledger state + the snapshot `as_of` only; **never wall-clock**; fail-closed; rule-based.
- **Preserve old-version replay** — never break reproducibility at the prior `runtime_policy_version`.
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids. Summarize what changed + the new vs old version behavior, and **stop for my review**.

---

# Prompt B — live operational-status feed

Paste into a fresh Claude Code session rooted in `el_nino`.

---

Lift ADR-009's deferred "**live operational-status feed**" — build the **IO adapter** that produces a real `OperationalInput` (tradeable / venue_open / halt / degraded) for the live (`run_once`) path, behind the explicit `OperationalInput` seam the orchestrator already left ready. **The live feed read happens ONLY on the IO path and is quarantined off the replay path — exactly the ADR-011 §2 determinism boundary the Alpaca adapter (gate f) uses.** The pure core is unchanged; the captured `OperationalInput` is **recorded so replay never re-reads the feed.** Pause for my review when built.

## The non-negotiable: replay-path quarantine

`run_sequence` / BENCH replay must **never** read the live feed. The feed is read once on the live `run_once` path, the resulting `OperationalInput` is **captured and recorded**, and any replay threads that captured value (run_sequence already takes explicit `OperationalInput`s). No clock/network on the replay path. The feed read is **logged, not replayed** — mirror ADR-011 §2 + the gate-f Alpaca boundary.

## Step 0 — read

1. `dev_graph/CLAUDE.md` — writeback checklist, 11 lint checks, Neo4j re-sync, §7.5 threshold.
2. `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009) — the `operational_ok` guard + the `OperationalInput` model + the "live operational feed" Non-Goal (this lifts it).
3. `decisions/ADR - Execution Layer Planning.md` (ADR-011 §2 + gate f) — the **non-replayable-adapter quarantine** + KA-008 credential isolation; this feed adapter follows the same boundary discipline.
4. The seam to fill: `src/orchestration/` `config.py` (`DEFAULT_OPERATIONAL_INPUT`) + `runtime.py` (how `run_once` threads it) and `src/gold/paper_runtime/models.py` (`OperationalInput` — the existing contract; **do not change it**).
5. `knowledge_assets/Agent Safety Principles.md` (KA-008) if the source needs credentials.

## Step 1 — build the adapter (IO-boundary only)

- The pure core (`evaluate`/`run_chain`) keeps taking `OperationalInput` as an **explicit value** — unchanged. The new piece is an adapter that **reads** operational status at `run_once` time and **produces** that `OperationalInput`.
- **Pick the v0 source and justify it:** a deterministic market-hours/calendar computation for the GLD venue, and/or a live venue clock/calendar (e.g. Alpaca clock/calendar) if credentials exist. Keep it **pluggable** behind the seam. **Fail-closed:** feed unavailable / ambiguous ⇒ `tradeable = False` (no admission), never fail-open.
- **Capture + record** the produced `OperationalInput` so a replay reconstructs the exact operational decision byte-identically. Verify the runtime record / ledger captures enough to replay the `operational_ok` outcome without re-reading the feed; if not, settle the (additive) capture explicitly at the checkpoint.
- **Credential isolation (KA-008)** if the source needs keys — env / git-ignored `.secrets` only; never in the repo, a memory file, or a dev_graph node.

## Step 2 — validate

- Adapter with a **stubbed/injected feed** produces the correct `OperationalInput` for open / halted / degraded / closed states; **fail-closed** when the feed is unavailable.
- A **captured-vs-live** test proving the replay path uses the captured value and is **independent of the live feed** (mirror the execution layer's captured-`guard_config` env-independence test).
- `run_sequence` / BENCH paths never touch the feed (assert no live call on replay). `mypy --strict` + `ruff` clean; full prior suite green.

## Step 3 — governance + writeback

- Lifts the ADR-009 "live operational feed" Non-Goal; it is an **additive IO adapter** — no pure-core change, no `OperationalInput` schema change, no `*_version` bump. Governed by ADR-009 (the guard) + ADR-011 §2 (the non-replayable quarantine). Likely an **ADR-009 update note** + the adapter under existing contracts. State placement.
- Author the adapter file/test nodes (re-derive next-free `FILE-0xx`/`TEST-0xx`; a thin module node only if it warrants one); update the MOD-010/MOD-007 operational-seam Open Question; record that the feed is **non-replayable IO, captured for replay**. `index.md` + `log.md`; 11 lint checks; **Neo4j re-sync**.

## Constraints

- **Live feed read ONLY on the IO path, never on replay**; capture + record the `OperationalInput` for byte-identical replay; the feed read is logged, not replayed.
- **Fail-closed** (unavailable ⇒ not tradeable); **credential isolation** (KA-008); **no pure-core or `OperationalInput`-contract change**.
- No `wiki/**`/`raw/**` mutation (CON-001); canonical_id immutable; re-derive ids. Summarize the source choice, the quarantine/capture evidence, and the placement, and **stop for my review**.
