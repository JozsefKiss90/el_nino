# JARVIS Operations Manual

This file governs work under `jarvis/`. The `jarvis/` stack is the **read-only front end** over the
El Niño `dev_graph` — a graph explorer plus a GraphRAG console (ADR-010). It does not own data; it
**projects and displays** the dev_graph. Read `dev_graph/CLAUDE.md` first — it is authoritative for
anything that touches `dev_graph/**`; this file governs only the `jarvis/` consumer.

---

## Prime directive — JARVIS is a read-only consumer (ADR-010)

1. The dev_graph **markdown is canonical**. Neo4j and every `graph.json` are **rebuildable
   projections** of it. **Never hand-edit a projection** — regenerate it from the markdown.
2. JARVIS **reads** the graph (live Neo4j bridge, or offline `graph.json`); it **never authors** it.
   The backend issues no write Cypher (`backend/app.py` opens sessions in READ mode + a keyword
   guard), and the UI proposes no graph edits.
3. **Do not let JARVIS become a second source of truth.** If a number or structure belongs to the
   dev_graph, derive it from a projection — do not retype it into a component.

---

## The projection chain (know this before changing anything)

```
dev_graph/*.md  ──sync_to_neo4j.py --clear──►  Neo4j (bolt :7688)   ◄─read─ backend/app.py (live)
   (canonical)  ──export_graph_json.py──────►  frontend/graph.json  ◄─read─ frontend/index.html
                                            └─►  hud/public/graph.json ◄─read─ hud (Vite) ─build─► dist/graph.json
```

Four projections, all rebuilt from the **one** markdown source:

| # | Projection | Built by | Consumed by |
|---|---|---|---|
| 1 | Neo4j | `sync_to_neo4j.py --clear` (repo root) | `backend/app.py` live endpoints, `neo4j` MCP |
| 2 | `frontend/graph.json` | `export_graph_json.py` | `frontend/index.html` explorer, `backend` `/ask` corpus |
| 3 | `hud/public/graph.json` | `export_graph_json.py` (both paths in one run) | the React HUD router/index |
| 4 | `hud/dist/graph.json` | `npm run build` (bakes `public/`) | the served single-URL HUD |

**Critical nuance:** the HUD's node index and the backend `/ask` seed matcher both read
`graph.json`, **not** Neo4j — even in live mode (`hud/src/hooks/useGraph.ts` builds its index from
`graph.json`; only the rendered subgraph swaps to live Neo4j). So **re-syncing Neo4j alone does not
refresh the HUD.** A stale `graph.json` degrades answering against a fresh Neo4j. Always rebuild
**both** projections together.

---

## When the dev_graph changes — re-project EVERYTHING (one command)

After any change to `dev_graph/**`, run the single re-projection command rather than the steps
piecemeal (a half-run leaves Neo4j and `graph.json` on different versions of the markdown):

```powershell
powershell -ExecutionPolicy Bypass -File C:\Code\el_nino\jarvis\resync-devgraph.ps1
```

It runs, fail-fast: `sync_to_neo4j.py --dry-run` → `sync_to_neo4j.py --clear` →
`export_graph_json.py` (writes **both** `graph.json` paths) and prints node/edge counts.
This is the same action as `dev_graph/CLAUDE.md` writeback **step 10** — prefer this script.

If you changed the HUD and want the served bundle current too: `cd jarvis/hud; npm run build`
(re-bakes `dist/graph.json`). `start.ps1` builds once if `dist/` is missing but **does not**
re-project — it assumes the projections are already current.

> A `pre-commit` hook enforces this: `jarvis/hooks/pre-commit` fails the commit when a staged
> `dev_graph/**.md` change leaves either `graph.json` copy stale (it never touches Neo4j — DB-free).
> Install it once per clone: `sh jarvis/hooks/install.sh`. Bypass (discouraged): `git commit
> --no-verify`. When it fires, run `resync-devgraph.ps1` and `git add` the regenerated `graph.json`.

---

## Component contract — two classes, one boundary

| Class | Files | Rule |
|---|---|---|
| **Graph-driven** | `data/graph.ts`, `hooks/useGraph`, `data/router.ts`, `components/GraphView`, `components/main/KnowledgeGraph` | Must read `graph.json` / the live bridge. Never hardcode node/edge data here. |
| **Presentation constants** (curated narrative) | `data/snapshot.ts` (SNAPSHOT/SERIES/ORBITS/VITALS), `ops/Architecture.tsx`, `ops/The12PivotalPoints.tsx`, epoch/roadmap panels | Deliberately static editorial content, tagged `SNAPSHOT-DRIVEN`. Market data (SERIES/ORBITS) refreshes on a separate pass. |

**Rule for the boundary:** anything in a presentation constant that is *graph-derivable* (node/edge
counts, ADR range, the vitals module list) should be read from `graph.json.meta` rather than retyped,
so it cannot drift. Pure narrative (the 12 Pivotal Points, the epoch story) stays static. See
`PROJECTION_SYNC_PLAN.md` Rec 4.

---

## Backend safety invariants (do not weaken)

- Sessions open in `default_access_mode="READ"`; `_guard()` rejects any mutating Cypher token. Keep
  both — driver-level enforcement *and* the keyword guard (defense in depth).
- User input reaches Cypher **only as bound parameters**, never string-interpolated. The only embedded
  values are validated ints (hop depth) and `isalnum()`-checked label names.
- `/ask` is fail-closed: no seed match → "That is not in the graph.", never an LLM call, never an
  invented node. The static-mount block at the bottom of `app.py` must stay **last** (it shadows
  unknown paths with `index.html`).
- CORS is `*` for local convenience — **tighten `allow_origins`** before exposing beyond localhost.

---

## Pointers

- Architecture & rationale: `JARVIS_INTEGRATION_ROADMAP.md` (Stages 0–5), ADR-010 in
  `dev_graph/decisions/`.
- Run instructions: `README.md` (offline explorer + full HUD), `hud/README.md` (the React app).
- The sync-hardening plan this manual references: `PROJECTION_SYNC_PLAN.md`.
- The producer (Layer-2 truth) is a **separate repo** (`C:\Code\Mr-Ripley`) with its own
  constitution — out of scope here.
