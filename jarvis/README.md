# JARVIS dev_graph stack

An **offline-first** way to make the El Niño `dev_graph` (the ~158-node engineering
knowledge graph) **traversable from a front end**, via Neo4j.

```
dev_graph/*.md  ──(../sync_to_neo4j.py)──►  Neo4j (bolt)  ◄──(read-only)──  FastAPI  ◄──(HTTP)──  graph explorer UI
   source of truth          MERGE on canonical_id        graph store      jarvis/backend         jarvis/frontend
```

Neo4j is **not** part of the trading runtime — it's a rebuildable mirror of the dev_graph
for traversal (dependency chains, impact, shortest path). The markdown stays canonical; you
can `--clear` and re-sync any time.

---

## Prerequisites
- Docker (for Neo4j; and optionally the API + UI containers), **or** local Neo4j + Python 3.12.
- Python with `neo4j` + `pyyaml` on the host for the one-time populate step.

## Offline quick start (recommended)

**1 — start Neo4j (with APOC):**
```bash
docker run -d --name elnino-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/elnino_dev \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v elnino_neo4j_data:/data \
  neo4j:5-community
```
Wait ~15s, then confirm the Neo4j Browser is up at <http://localhost:7474> (login `neo4j` / `elnino_dev`).

**2 — populate the graph from the dev_graph (one-time, repeatable):**
```bash
cd C:\Code\el_nino
# dry-run first — validates the parse offline, no DB needed (expect ~158 nodes / ~1106 edges):
python sync_to_neo4j.py --dry-run
# real sync:
set NEO4J_PASSWORD=elnino_dev   &&   python sync_to_neo4j.py --clear
```
> The exporter auto-scopes to `dev_graph/` whether it lives in `dev_graph/` or the repo root
> (override with the `DEV_GRAPH_DIR` env var). It prints node/edge counts by label at the end.

> **Offline projection — regenerate `graph.json` alongside the Neo4j sync.** The JARVIS console can
> answer from a server-less `frontend/graph.json` when the bridge is down. It is the *same* projection
> as Neo4j (it reuses `sync_to_neo4j.py`'s parser — never hand-edit it). Regenerate it whenever the
> dev_graph markdown changes, right after `sync_to_neo4j.py --clear`:
> ```bash
> python jarvis/export_graph_json.py    # writes jarvis/frontend/graph.json (159 nodes / 1113 edges)
> ```

**3 — run the API:**
```bash
cd C:\Code\el_nino\jarvis\backend
pip install -r requirements.txt
set NEO4J_PASSWORD=elnino_dev   &&   uvicorn app:app --port 8000
```
Check <http://localhost:8000/health> → `{"ok":true,"neo4j":true,"node_count":158,...}` and the
interactive API docs at <http://localhost:8000/docs>.

**4 — open the explorer:**
- **Offline:** vendor cytoscape once so the UI needs no network:
  ```bash
  cd C:\Code\el_nino\jarvis\frontend && mkdir vendor
  curl -L -o vendor/cytoscape.min.js https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js
  ```
  then just open `jarvis/frontend/index.html` in Chrome/Edge.
- (If you skip vendoring, the page falls back to the CDN — fine when online.)

You'll see the whole dev_graph; **click any node to expand its neighbors**, search by id/name
(e.g. `MOD-006`, `regime`), and focus by type.

## Full stack via docker-compose (containerized)
```bash
cd C:\Code\el_nino\jarvis
copy .env.example .env          # adjust NEO4J_PASSWORD if you like
docker compose up -d neo4j      # DB first
# populate (host): set NEO4J_PASSWORD=<your value> && python ..\sync_to_neo4j.py --clear
docker compose up -d api frontend
# UI → http://localhost:8080 ,  API → http://localhost:8000/docs
```

---

## Wiring it into the JARVIS console
Your `el_nino_jarvis_interface.html` already lists *"Neo4j dev_graph · bolt://localhost:7687 ·
◐ LOCAL ONLY"* as a status chip. Drop this snippet in just before `</body>` to flip it **LIVE**
off the API health check and add a button that opens the explorer:

```html
<script>
(function(){
  var API = "http://localhost:8000", UI = "http://localhost:8080"; // or the file:// path to frontend/index.html
  fetch(API+"/health").then(r=>r.json()).then(h=>{
    // find the connector row whose text mentions Neo4j and update its status pill
    document.querySelectorAll(".cn").forEach(function(row){
      if(/neo4j/i.test(row.textContent)){
        var pill = row.querySelector("[class^='st-']") || row.lastElementChild;
        if(h.neo4j){ pill.textContent="● LIVE ("+h.node_count+" nodes)"; pill.className="st-on"; }
      }
    });
  }).catch(function(){});
  // optional: a console command / button to open the graph
  window.openDevGraph = function(){ window.open(UI, "_blank"); };
})();
</script>
```
This is intentionally non-invasive — it doesn't rewrite the 1,300-line console. A deeper
integration (an inline graph panel inside JARVIS using the same `/subgraph` + `/neighbors`
endpoints) is the natural follow-up once this is running.

---

## JARVIS GraphRAG console (Stages 1–5, ADR-010)

The `frontend/index.html` explorer is one face; the **JARVIS console** is the other — a voice-style
HUD that *answers from the graph*. It is a **read-only consumer** of the dev_graph (ADR-010): every
structural answer cites its `canonical_id` and evidence-class, and is grounded in a retrieved
subgraph (fail-closed — "not in the graph" rather than invent). Built in slices:

| Stage | Deliverable | What it adds |
|---|---|---|
| 1 | `export_graph_json.py` → `frontend/graph.json` | deterministic offline projection (reuses the `sync_to_neo4j.py` parser) |
| 2 | `frontend/jarvis.html` | graph-grounded answering on the current console + mini cytoscape view + LIVE chip |
| 3 | `hud/` (Vite + React + TS) | the monolith refactored — typed data layer, a **pure Vitest-tested router**, hooks, components |
| 4 | `POST /ask` on `backend/app.py` | GraphRAG over the Claude API — cited, evidence-annotated, read-only |
| 5 | `/voice/*` + static mount on the same app | Whisper/Piper voice (Web Speech fallback) + **single URL** |

### Run the React HUD

```bash
# 1) bridge (serves the graph API + /ask + /voice on :8000)
cd jarvis/backend && pip install -r requirements.txt
set NEO4J_PASSWORD=elnino_dev && uvicorn app:app --port 8000

# 2a) dev — Vite proxies /api → the bridge (hot reload)
cd jarvis/hud && npm install && npm test && npm run dev      # http://localhost:5173

# 2b) prod — one URL: build the HUD, the bridge mounts dist
cd jarvis/hud && npm run build
#   then reload http://127.0.0.1:8000/  → the whole HUD serves from the bridge
```

- **`/ask` needs `ANTHROPIC_API_KEY`** in the bridge env (model via `JARVIS_ASK_MODEL`, default
  `claude-sonnet-4-6`). Without it `/ask` returns 503 and the HUD falls back to the offline graph
  router — still cited, still graph-grounded.
- **Voice is optional.** `/voice/*` reports unavailable unless `faster-whisper` (STT) and a Piper
  binary + `.onnx` voice (`PIPER_BIN`/`PIPER_VOICE`) are installed; the HUD uses **Web Speech**
  (Chrome/Edge) otherwise.
- The Stage-2 `jarvis.html` works offline too — serve `frontend/` statically (or open it with the
  bridge up) and it answers from `graph.json`.

## Moving to Neo4j Aura (managed cloud) later
Aura is just a different connection string — **the exporter, API, and UI are unchanged**:
1. Create a free AuraDB; note its `neo4j+s://<dbid>.databases.neo4j.io` URI + password.
2. Set `NEO4J_URI` / `NEO4J_PASSWORD` (in `.env` or the API env) to the Aura values.
3. Re-run `python sync_to_neo4j.py --clear` against Aura to populate it.
4. Drop the `neo4j` service from compose; keep `api` + `frontend`.

## Notes & safety
- The API is **read-only**: sessions open in READ mode and a keyword guard rejects any
  mutating Cypher. CORS is open for local convenience — **tighten `allow_origins`** before
  exposing it beyond localhost.
- Re-sync any time: edit the dev_graph markdown, re-run `sync_to_neo4j.py --clear`. `MERGE`
  on `canonical_id` keeps it idempotent.
- The graph is data, not source — `neo4j_data` volume + `.env` are git-ignored.
