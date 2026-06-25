# Claude Code prompt — draft ADR-011 (Execution / Portfolio Layer Planning)

Paste the block below into a Claude Code session rooted in the `el_nino` repo.

---

You are drafting a new Architecture Decision Record, **ADR-011**, that opens the **execution / portfolio layer epoch** for the El Niño trading engine. This is a **governance / architectural-boundary planning record only** — non-normative, no `src/` or `tests/` code, no frozen schema, and no module/interface/file/test/capability nodes. It mirrors the house style of ADR-006, ADR-009, and ADR-010. **Pause for my review when the ADR + writeback are done; do not start design or code.**

## Step 0 — read governance and ground yourself before writing

Read these first and obey them; do not write from memory:

1. `dev_graph/CLAUDE.md` — the operations manual. Follow the universal frontmatter schema, the decision_record extensions, the Node Template / ADR body sections, the Cross-Linking Protocol, and the end-of-session Writeback Checklist.
2. `dev_graph/index.md` — to **re-derive the next free canonical IDs** (do NOT assume; the log shows IDs must be re-derived each time) and to confirm the current node inventory.
3. The prior boundary ADRs to match structure and tone: `decisions/ADR - Gold DecisionPacket v0 Planning.md` (ADR-006, note its §8 Creation-Gate board), `decisions/ADR - Paper-Trading Runtime Planning.md` (ADR-009, note its Non-Goals), `decisions/ADR - JARVIS GraphRAG Integration.md` (ADR-010), and `decisions/ADR - Decision Layer Re-grounding.md` (ADR-004, the re-grounding precedent).
4. The nodes this epoch builds on: `modules/Paper-Trading Runtime.md` (MOD-007) and its files `engine.py`/`runtime.py` — **read the actual pure `evaluate()` / `run_sequence` vs IO `run_once` split**, because ADR-011's determinism boundary must mirror it. Also read `capabilities/Order Management.md` (CAP-005), `capabilities/Gold Decision Generation.md` (CAP-020), `gates/Trade Validation Gate.md` (GATE-001), the five guardrail predicates (PRED-001..005), and `knowledge_assets/Paper Trading Validation.md` (KA-010).

## Step 1 — author `decisions/ADR - Execution Layer Planning.md` (ADR-011)

Frontmatter: `type: decision_record`, `canonical_id: ADR-011`, `status: draft` (the governed stand-in for "Proposed" — promote to `active` on acceptance), `implementation_status: not-started`, `confidence: confirmed`, `evidence: [design, ADR]`, `created: 2026-06-16`, `updated: 2026-06-16`, `decision_status: active`, plus the required `related_decisions` / relationship arrays with resolvable wikilinks. Body sections must be **Status, Context, Decision, Alternatives Considered, Consequences** (required by lint check 8 / type-content alignment).

The ADR must record these decisions:

1. **Scope & epoch boundary.** ADR-011 governs the execution/portfolio layer — the sanctioned next epoch (per the 2026-06-09 audit baseline line). It answers *"under what constraints may an execution/portfolio contract be created?"* — it is NOT the contract itself. Permanently separate from the Supervisor treasury branch (ADR-004).

2. **The determinism boundary is the load-bearing invariant (the central decision).** Frame the directive *not* as "Alpaca vs offline" but as a **port/adapter (hexagonal) split**:
   - A **deterministic offline fill-simulator is the canonical, replay-safe core.** All tests, benchmarks, and replay run against it. It extends the existing replay key (`snapshot_id + feature/model/decision_policy versions + config`) to cover execution determinism (e.g., a fill-model version + seed/policy), so `inputs + versions ⇒ identical execution record`.
   - The **Alpaca Paper API is an optional, explicitly non-replayable live adapter**, quarantined behind the same execution interface at an **IO boundary shell**, exactly mirroring MOD-007's pure `evaluate()`/`run_sequence` core vs `run_once` IO shell. **Alpaca is never on the replay path** and never in benchmarks; live runs are logged, not replayed.
   - State this determinism boundary as a non-negotiable invariant.

3. **`paper_only` / virtual-money safety posture.** Honors KA-010 (mandatory simulated validation before live), the pervasive `non_execution_notice`, and PRED-005 (withdrawals disabled). Alpaca **Paper** (virtual money) respects this. **Live-money trading is an explicit Non-Goal** at this epoch.

4. **Re-grounding (cite ADR-004 as precedent).** CAP-005 Order Management currently `Depends On` the deprecated Signal Generation, with a note that the paper-only gold successor does not feed Order Management. ADR-011 must specify the re-wiring of the live path: CAP-020 Gold Decision → MOD-007 runtime admission (ADMIT) → execution, and the wiring of **GATE-001 + PRED-001..005 into the actual trade pipeline** (GATE-001 is currently "not yet wired into a live trade pipeline — no order router yet"; this epoch is where the dormant guardrail machinery finally activates).

5. **Decouple from DEBT-01 and epoch (b) calibration.** DEBT-01 was resolved on 2026-06-11 (both legs closed). The execution epoch is independent of DEBT-01 and of real-corpus calibration. Record the sequencing caveat: build the offline-simulation core first; the live Alpaca adapter yields low-information results until decision logic is calibrated (regime thresholds / confidence weights / direction table are still provisional), so the Alpaca adapter may be deferred or run in parallel with epoch (b).

6. **Creation Gates** (an ADR-006-§8-style gate board) that must pass before any normative execution schema/module/interface may be authored — e.g.: execution interface contract defined; fill-simulation model specified and replay-keyed; guard-wiring (GATE-001/predicates) specified; execution-determinism replay requirement finalized; portfolio/position state model agreed; Alpaca-adapter boundary (auth/credential isolation per KA-008, non-replayable IO quarantine) specified.

7. **Candidate future objects — named as non-binding only, NOT reserved or created** (re-derive next free IDs from index.md, do not assume): an execution interface (next free INT id), execution/portfolio schema(s) (next free SCHEMA id, never reusing a deprecated id), execution + portfolio modules (next free MOD ids), the simulated-broker adapter and the Alpaca paper adapter, position/portfolio state, the fill model, and any execution events.

8. **Non-Goals** (extend ADR-009's list): live-money trading; real broker order routing beyond Alpaca paper; the wall-clock scheduler/daemon; multi-instrument (GLD only); learned/history-dependent logic; a second source of truth; persistence beyond the local ledger pattern.

Relationships to include: `### Originates From` → KA-010 (and KA-005 Guardrail Philosophy, KA-008 Agent Safety Principles where apt); `### Supersedes` n/a; `related_decisions` / `### ...` links → ADR-009, ADR-006, ADR-004, ADR-008. Every wikilink must resolve to an existing node.

## Step 2 — writeback (governance-only slice)

- Update `dev_graph/index.md`: add the ADR-011 row to the Decisions table; refresh Statistics (decision_record 10 → 11; total nodes; coverage) and the "Last updated" date.
- Append a `## [2026-06-16] decision | ADR-011 Execution Layer Planning` entry to `dev_graph/log.md` (Nodes Created / Changes / the directive-reframing rationale / Metrics / Deferred-open).
- Run the **11 lint checks** on the touched nodes (frontmatter, enums, orphan/≥1 inbound, stale, broken wikilinks, type-content alignment, deprecated refs, canonical_id uniqueness, evidence-confidence coherence; module checks n/a for an ADR) and report each as ✓.
- **Re-sync Neo4j** (`python dev_graph/sync_to_neo4j.py --clear`) — this slice changes the dev_graph. Note the new node/edge counts.

## Constraints

- MUST NOT modify `wiki/**` or `raw/**` (CON-001).
- `canonical_id` is immutable; no in-place reclassification.
- **No code** under `src/**` or `tests/**`; **no schema freeze**; no module/interface/capability/file/test nodes — this is a planning/boundary ADR only.
- When done, summarize what you wrote and **stop for my review** before any design or implementation.
