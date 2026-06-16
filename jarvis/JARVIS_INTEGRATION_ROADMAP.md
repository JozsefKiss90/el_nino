# JARVIS ↔ Neo4j ↔ MCP — Integration & Refactor Roadmap

**Date:** 2026-06-14
**Scope:** Connect the JARVIS console to the operational dev_graph (Neo4j + the read-only `neo4j` MCP),
replace its hardcoded keyword KB with graph-grounded answering, then refactor the monolith to React —
**capability first, refactor second.**
**Sequencing chosen:** ADR → bridge + `graph.json` → graph console on the *current* HTML → React refactor
→ GraphRAG (LLM uplink) → voice.

---

## Governing principles (baked into every stage)

1. **JARVIS is a read-only consumer of the dev_graph.** It *reads* the graph (Neo4j live, or `graph.json`
   offline); it never authors it. The dev_graph markdown stays canonical; Neo4j and `graph.json` are
   rebuildable projections (`sync_to_neo4j.py`). Same single-source-of-truth discipline that governed the
   whole project.
2. **Reuse what exists — don't rebuild.** `jarvis/backend/app.py` is *already* the live Cypher bridge.
   The voice bridge, `/ask`, and static serving fold into that **one** FastAPI app (one service, one URL).
   The cytoscape view in `jarvis/frontend/index.html` is the **graph-render building block** to embed —
   don't write a second renderer.
3. **Evidence-class is free.** The dev_graph's `confidence` (confirmed / single-source / inferred) and
   `evidence` arrays are already node properties in Neo4j and the markdown. Every answer annotates its
   claims with them ("this is single-source — be careful"). No new data required.
4. **Citations as governance.** Every graph-grounded answer cites the `canonical_id`s (and wiki pages) it
   drew from. Fail-closed applied to the assistant: no claim without a node.
5. **Offline + live duality behind one typed data layer.** `graph.json` (deterministic, no server) and the
   Neo4j bridge (live, multi-hop) are interchangeable sources; the UI degrades gracefully to offline.
6. **Typed end-to-end.** TS interfaces mirror the FastAPI Pydantic models (`Node`, `Edge`, `GraphResponse`)
   — the frontend analog of `mypy --strict`. The question→answer router is a **pure, unit-tested** function.
7. **Governance habit.** Each capability stage is introduced by (or cross-referenced to) an ADR and the
   dev_graph writeback; re-sync Neo4j when the dev_graph changes.

---

## Current state (what already exists — do not redo)

| Asset | Location | Status |
|---|---|---|
| Neo4j (158 nodes / 1106 edges) | Docker `elnino-neo4j`, bolt 7688 (host) → 7687 (container) | ✅ live, `restart: unless-stopped` |
| Read-only graph API | `jarvis/backend/app.py` | ✅ `/health /meta /node /neighbors /search /path /subgraph` |
| Cytoscape graph explorer | `jarvis/frontend/index.html` | ✅ standalone; the GraphView building block |
| `neo4j` MCP (read-only) | `.mcp.json` | ✅ connected; CLAUDE.md instructs proactive use |
| Exporter | `sync_to_neo4j.py` | ✅ scoped to `dev_graph/`, idempotent `--clear` |
| JARVIS console (target UI) | `jarvis/sources/el_nino_jarvis_interface (6).html` | 207 KB monolith; keyword KB; voice stubs (:8585); Neo4j chip |
| Voice bridge `voice_bridge.py` | — | ❌ **does not exist yet** (referenced by the HTML) |

The console currently answers from a **hardcoded keyword corpus**, not the graph. That is the gap Stage 2
closes.

---

## Stage 0 — ADR-010: JARVIS GraphRAG Integration (governance only)

**Goal:** Record the boundary before code, per the project's ADR discipline.
**Deliverable:** `dev_graph/decisions/ADR - JARVIS GraphRAG Integration.md` (canonical_id ADR-010; re-derive).
**Records:** read-only consumer boundary (principle 1); the bridge is the *existing* FastAPI app extended,
not a new server (2); answers carry evidence-class + citations (3,4); offline/live duality (5); Non-Goals
— writing to the graph, autonomous code generation, voice-driven *building* (all later/deferred).
**Gate:** ADR accepted; dev_graph writeback (this is a structural file change → re-sync Neo4j after).

> **Claude Code prompt — Stage 0**
> ```
> Read dev_graph/CLAUDE.md (the operations manual) and the existing ADR chain (ADR-001..009) for
> format. Author ADR-010 "JARVIS GraphRAG Integration" as a governance/boundary record (mirror
> ADR-006/ADR-009 structure). It authors no app code. Record: (1) JARVIS is a READ-ONLY consumer of
> the dev_graph — reads Neo4j (live) or graph.json (offline), never writes; markdown stays canonical.
> (2) The bridge is jarvis/backend/app.py EXTENDED (graph + future /ask + future /voice + static
> serving) — not a separate voice_bridge.py. (3) Every graph-grounded answer cites canonical_ids and
> carries the node's `confidence` evidence-class. (4) Offline graph.json and live Neo4j are
> interchangeable sources. Non-Goals: writing to the graph; autonomous code generation; voice-driven
> app-building (deferred). Then run the dev_graph writeback (index.md + log.md + 11 lint checks) and,
> because this changed the dev_graph, re-sync: `python sync_to_neo4j.py --clear`. Pause at a checkpoint
> for review before any app code.
> ```

---

## Stage 1 — `graph.json` exporter + bridge confirmation (offline seed)

**Goal:** A deterministic offline projection of the graph for the console + mini-view, and confirm the
live bridge covers the console's needs.
**Deliverables:**
- `jarvis/export_graph_json.py` — reuses `sync_to_neo4j.py`'s markdown parser to emit `graph.json`:
  `{ nodes: [{id, label, name, summary, confidence, evidence, status}], edges: [{source, type, target}] }`,
  where `summary` = first sentence of the node's `## Definition`. Deterministic, no server.
- Confirm `jarvis/backend/app.py` exposes everything the console needs (`/search`, `/node`, `/neighbors`,
  `/subgraph`); add a `/summary/{id}` only if the markdown summary isn't already serializable.
**Gate:** `python jarvis/export_graph_json.py` produces a valid `graph.json` (158 nodes); `/health` green.

> **Claude Code prompt — Stage 1**
> ```
> Create jarvis/export_graph_json.py. Reuse the markdown parsing from sync_to_neo4j.py (frontmatter +
> relationship sections) so node/edge extraction stays identical and DRY. For each dev_graph node emit
> {id: canonical_id, label, name, summary, confidence, evidence, status}; summary = the first sentence
> of the node's "## Definition" section (fall back to name). Emit edges as {source, type, target} using
> the same canonical_id resolution as the exporter (skip the same 5 unresolved edges). Write
> jarvis/frontend/graph.json. Keep it pure/deterministic (no DB needed — it reads the markdown, same as
> --dry-run). Add a one-line note to jarvis/README.md on regenerating graph.json alongside the Neo4j
> sync. Do NOT modify the trading code or the dev_graph nodes.
> ```

---

## Stage 2 — Graph-driven console on the *current* HTML (the capability win)

**Goal:** Replace the keyword KB with graph traversal **on the existing JARVIS HTML** — answer from the
graph, render a mini local graph next to the answer, flip the Neo4j chip LIVE. Capability-first: value
before the refactor.
**Deliverables (in a copy of `jarvis/sources/...html`, e.g. `jarvis/frontend/jarvis.html`):**
- A `graphAnswer(question)` path: match a node (live `/search`, or `graph.json` fuzzy match offline) →
  pull its neighborhood (`/neighbors` or `graph.json`) → compose an answer from the node `summary` + its
  edges, **annotated with the node's evidence-class and citing its `canonical_id`**.
- A **mini graph view** beside the answer — reuse the cytoscape setup from `frontend/index.html` (the
  matched node + 1-hop neighborhood).
- **Source toggle:** live bridge if `/health` passes, else `graph.json` offline (principle 5). Flip the
  "Neo4j dev_graph" connector chip to ● LIVE off `/health`.
**Gate:** ask "what depends on the Gold Decision Builder?" in the console → correct graph-derived answer
with citations + mini-view, both online (bridge) and offline (graph.json).

> **Claude Code prompt — Stage 2**
> ```
> Work on a copy of "jarvis/sources/el_nino_jarvis_interface (6).html" saved as jarvis/frontend/jarvis.html
> (leave the original untouched). Replace the hardcoded keyword-KB answering with graph-grounded
> answering, WITHOUT yet refactoring to React:
> 1. Add a data layer that loads from EITHER the live bridge (http://localhost:8000: /search, /node,
>    /neighbors) when GET /health is ok, OR ./graph.json offline otherwise. Show which source is active.
> 2. On a question: find the best-matching node (name/canonical_id/summary), fetch its 1-hop
>    neighborhood, and compose the answer from the node summary + its edges. Prepend the node's
>    evidence-class (confidence) and cite its canonical_id, e.g. "[MOD-006 · single-source]".
> 3. Render a mini local graph next to the answer by reusing the cytoscape setup from
>    jarvis/frontend/index.html (matched node + neighbors; click to expand).
> 4. Flip the "Neo4j dev_graph" connector chip to LIVE based on /health.
> Keep it read-only (never write to the graph). Keep the existing visual theme and voice stubs intact.
> Verify both modes: bridge up, and bridge down (offline graph.json).
> ```

---

## Stage 3 — React refactor (Vite + React + TypeScript)

**Goal:** Decompose the monolith now that the graph capability is proven. Structure = the real payoff.
**Deliverables (`jarvis/hud/`):** `npm create vite@latest` (react-ts). Layers:
- **data/** `snapshot.ts`, `graph.ts` (the Stage-1/2 client + types), **`router.ts` as a PURE function**
  (question→answer) — unit-tested with **Vitest** (mirrors the 853-test culture).
- **hooks/** `useGraph`, `useReactorState`, `useClock`, `useCorpusCounter`, `useSpeech` (Web Speech),
  `useVoiceBridge` (built but last).
- **components/** `<Reactor> <Caption> <Console> <ContextFeed> <ConnectorArray> <OperatorPanel>
  <FlowStage> <DriftTable> <GraphView>` (cytoscape); pages `MainHud / OpsDeck / SystemFlow`.
- Transfer the **CSS-token theme unchanged**; JARVIS/PIXEL via a `ThemeContext` setting `data-theme`.
- `vite.config.ts` proxies `/api` → the bridge (no CORS in dev).
**Migration order:** scaffold → CSS tokens → data/router + tests → components bottom-up → voice hooks last.
**Gate:** Vitest green on `router.ts`; `npm run build` → `dist`; parity with the Stage-2 console.

> **Claude Code prompt — Stage 3**
> ```
> Scaffold jarvis/hud with `npm create vite@latest jarvis/hud -- --template react-ts`. Migrate the
> Stage-2 jarvis.html into it, in this order:
> 1. Copy the CSS-variable theme verbatim into a global stylesheet; JARVIS/PIXEL via a ThemeContext that
>    sets data-theme (CSS tokens unchanged).
> 2. data/: types.ts (Node/Edge/GraphResponse mirroring the FastAPI Pydantic models), graph.ts (the
>    bridge+graph.json client), router.ts as a PURE function (question -> answer object). Write Vitest
>    tests for router.ts (e.g. "what depends on MOD-006" -> expected node + citation).
> 3. hooks/: useReactorState (idle/listen/speak machine), useClock, useCorpusCounter, useGraph; leave
>    useSpeech/useVoiceBridge as stubs for last.
> 4. components/ bottom-up: Reactor, Caption, GraphView (reuse cytoscape), Console, ContextFeed,
>    ConnectorArray, OperatorPanel, FlowStage, DriftTable; pages MainHud/OpsDeck/SystemFlow via tab state.
> 5. vite.config.ts: proxy /api -> http://localhost:8000 (the bridge).
> Verify: Vitest passes; `npm run build` succeeds; the running app matches Stage-2 behavior. Do voice last.
> ```

---

## Stage 4 — LLM uplink = GraphRAG (`/ask`)

**Goal:** Wire the reserved LLM slot: query → subgraph context → Claude API → explained, **cited**,
evidence-annotated answer.
**Deliverables:**
- `POST /ask` on the bridge: retrieve a subgraph (keyword/semantic match + neighborhood) → build context
  from node summaries + edges + **evidence-class** → call the Claude API → return answer + the
  `canonical_id` citations + per-claim evidence labels. Read-only; never proposes graph writes.
- React `useClaudeUplink` hook; conversation history becomes React state (not DOM append).
**Gate:** a multi-hop question ("what connects the Paper Runtime to the risk guardrails?") returns a
graph-explained answer citing the nodes/edges it traversed, with evidence-class on each claim.

> **Claude Code prompt — Stage 4**
> ```
> Add POST /ask to jarvis/backend/app.py (the same bridge). Pipeline: (1) from the question, find seed
> nodes (reuse /search) and pull their neighborhood (reuse the /neighbors Cypher) to assemble a
> subgraph; (2) build a context block = each node's summary + its edges + its confidence/evidence; (3)
> call the Claude API (key from env ANTHROPIC_API_KEY) with a system prompt that REQUIRES the answer to
> (a) be grounded only in the supplied subgraph, (b) cite the canonical_ids it used, (c) label each
> claim with the source node's evidence-class, (d) say "not in the graph" rather than invent. Return
> {answer, citations:[canonical_id], subgraph}. Read-only — the endpoint must never emit write Cypher.
> In jarvis/hud add a useClaudeUplink hook and render the conversation + the returned subgraph in
> GraphView, with citations clickable to open the node. Keep the offline path (Stage 2 graph answering)
> as the no-API fallback.
> ```

---

## Stage 5 — Voice bridge (Whisper/Piper) + single-URL serving

**Goal:** Build the voice bridge the HTML already expects, fold it into the one service, ship one URL.
**Deliverables:**
- `/voice/health`, `/voice/stt` (Whisper), `/voice/tts` (Piper) on the **same** FastAPI app (replacing the
  imagined separate `voice_bridge.py`). Web Speech stays the fallback.
- Production: FastAPI mounts the React `dist` as static → single URL (e.g. `http://127.0.0.1:8000/`).
**Gate:** mic → Whisper transcript → graph/`/ask` answer → Piper TTS, end to end; Web Speech still works if
the bridge is down.

> **Claude Code prompt — Stage 5**
> ```
> Extend jarvis/backend/app.py with a voice router: GET /voice/health, POST /voice/stt (accept audio,
> return {text} via local Whisper), POST /voice/tts (accept {text}, return audio via Piper). This
> REPLACES the separate voice_bridge.py the HTML imagined — one service. Wire jarvis/hud's useVoiceBridge
> to these (health-poll, /stt, /tts), keeping useSpeech (Web Speech) as the automatic fallback when
> /voice/health fails. Finally, mount the built React dist as StaticFiles on the same app so the whole
> thing serves from one URL. Verify the full loop: speak -> transcript -> graph/ask answer -> spoken
> reply; and confirm graceful fallback to Web Speech when the bridge is offline.
> ```

---

## Sequence & dependencies

```
Stage 0  ADR-010 (governance)
   │
Stage 1  graph.json exporter + bridge confirm ──────────────┐ (offline seed + live bridge ready)
   │                                                          │
Stage 2  graph console on CURRENT html  ◄── reuses bridge + graph.json + cytoscape
   │     (THE capability win — graph answers, citations, evidence-class, mini-view)
   │
Stage 3  React refactor (data+tests / hooks / components / pages)  ◄── GraphView built React-native
   │
Stage 4  /ask = GraphRAG (Claude API, cited, evidence-annotated)  ◄── conversation = React state
   │
Stage 5  voice bridge (Whisper/Piper) + single-URL serving  ◄── last, most delicate
```

**Cross-cutting:** after any stage that changes the dev_graph (only Stage 0 does), re-sync Neo4j. The
bridge, `graph.json`, and the cytoscape view are reused across stages — built once, not twice.

## Risks & notes
- **Two front ends exist:** `frontend/index.html` (cytoscape explorer — the GraphView building block) and
  the `sources/...html` JARVIS console (the target UI). Stage 2 works on a copy of the console; the
  explorer feeds the `<GraphView>` component. Don't fork a third.
- **Don't let JARVIS become a second source of truth.** `graph.json` and Neo4j are projections; regenerate
  them from the markdown — never hand-edit. (The producer-drift lesson, again.)
- **Voice is genuinely last** — Web Speech already works in Chrome/Edge, so Stages 2–4 ship without the
  Whisper/Piper bridge; treat it as an enhancement, not a blocker.
- **Evidence-class + citations are the governance payoff** — they make JARVIS fail-closed about its own
  claims, the same discipline the engine holds for trades.
