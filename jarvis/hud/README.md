# El Niño · JARVIS HUD (React + TypeScript)

The Stage-3 React refactor of the graph-grounded JARVIS console (`../frontend/jarvis.html`).
Structure is the payoff: a typed data layer, a **pure, unit-tested** question→answer router, hooks,
and components — same capability as the Stage-2 monolith, decomposed.

> Read-only consumer of the dev_graph (ADR-010): it reads the live Neo4j bridge or the offline
> `graph.json` projection; it never authors the graph.

## Layout

```
src/
  data/
    types.ts       TS interfaces mirroring the FastAPI Pydantic models (Node/Edge/Graph/Health)
    router.ts      PURE question -> Answer function (matched node + 1-hop neighborhood, cited)
    router.test.ts Vitest — fixture + real graph.json ("what depends on MOD-006" → cited answer)
    graph.ts       impure client: probe /api/health, load graph.json, live multi-hop neighbors
  hooks/
    useGraph        source detection + index + ask()
    useReactorState idle/listen/speak machine
    useClock, useCorpusCounter
    useSpeech       Web Speech (the always-available voice fallback)
    useVoiceBridge  Whisper/Piper client (Stage 5 backend)
    useClaudeUplink POST /ask client (Stage 4 backend)
  components/       Reactor, Caption, Console, ContextFeed, ConnectorArray, GraphView (cytoscape),
                    OperatorPanel, FlowStage, DriftTable
  pages/            MainHud, OpsDeck, SystemFlow (tab state)
  theme/ThemeContext  JARVIS / PIXEL via data-theme (CSS tokens unchanged from the console)
```

## Run

```bash
npm install
npm test          # Vitest — the pure router (the gate)
npm run dev       # http://localhost:5173  (/api proxies to the bridge on :8000; no CORS)
npm run build     # tsc + vite → dist/   (Stage 5 mounts dist on the bridge → single URL)
```

`public/graph.json` is the offline projection — never hand-edit it. A bare `python
../export_graph_json.py` (run from the repo root: `python jarvis/export_graph_json.py`) rewrites
**both** this copy and `../frontend/graph.json` from the dev_graph markdown. Better: run the one
re-projection command `jarvis/resync-devgraph.ps1` (Neo4j + both `graph.json`). See
`../CLAUDE.md` and `../PROJECTION_SYNC_PLAN.md`.

The HUD works **offline** (graph.json) with no server, and upgrades to **live** multi-hop traversal
when the bridge's `GET /health` passes. The connector chips reflect the active source.
