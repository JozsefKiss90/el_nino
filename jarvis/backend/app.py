"""
JARVIS Graph API — read-only FastAPI service over the El Niño dev_graph in Neo4j.

Exposes the typed dev_graph (populated by ../sync_to_neo4j.py) for traversal from the
JARVIS front end: node lookup, neighbor expansion, label/text search, shortest path, and
seed subgraphs. Every query is READ-ONLY and parameterized:

  * the Neo4j session is opened in READ access mode (rejects writes at the driver),
  * a defensive keyword guard blocks any Cypher containing mutating clauses,
  * all user input flows through query parameters, never string interpolation.

Config via env (same vars as sync_to_neo4j.py / .mcp.json):
  NEO4J_URI (default bolt://localhost:7688), NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE.
For Neo4j Aura, set NEO4J_URI=neo4j+s://<dbid>.databases.neo4j.io and the Aura credentials —
nothing else changes.

Run:  uvicorn app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
import logging
import os
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pydantic import BaseModel

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DB = os.environ.get("NEO4J_DATABASE", "neo4j")

logger = logging.getLogger("jarvis")

# Defensive-in-depth ONLY — the primary enforcement is the driver's READ access mode in run_read().
# `apoc`/`call` are blocked because some procedures can mutate; the bridge uses none of them.
_FORBIDDEN = (
    "create", "merge", "delete", "set ", "remove", "drop",
    "detach", "call db.", "call apoc", "apoc.", "load csv", "foreach",
)

_driver: Any = None


def _guard(cypher: str) -> None:
    # Collapse whitespace first so multi-line / tab-obfuscated mutation clauses cannot slip past the
    # substring check. All bridge queries are static, parameterized templates — user input only ever
    # reaches Cypher as bound parameters, never as query text.
    low = re.sub(r"\s+", " ", cypher.lower())
    if any(tok in low for tok in _FORBIDDEN):
        raise HTTPException(status_code=400, detail="Only read queries are permitted.")


def run_read(cypher: str, **params: Any) -> list[dict]:
    """Execute a parameterized read query and return a list of record dicts."""
    _guard(cypher)
    if _driver is None:
        raise HTTPException(status_code=503, detail="Neo4j driver not initialized.")
    try:
        with _driver.session(database=NEO4J_DB, default_access_mode="READ") as session:
            # dict(record) preserves native Node/Relationship/Path objects (label- and
            # type-aware); record.data() would flatten them to primitives and lose labels.
            return [dict(r) for r in session.run(cypher, **params)]
    except (ServiceUnavailable, OSError) as exc:
        raise HTTPException(status_code=503, detail=f"Neo4j unavailable: {exc}") from exc
    except Neo4jError as exc:
        raise HTTPException(status_code=400, detail=f"Query error: {exc}") from exc


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _driver
    _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    yield
    if _driver is not None:
        _driver.close()


app = FastAPI(title="JARVIS Graph API", version="0.1.0", lifespan=lifespan)

# Local DevOps tool — read-only API, local-only. Permissive CORS so the static front end
# (file:// origin or a local static server) can call it. Tighten allow_origins for deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],  # POST for /ask (GraphRAG); reads only — see _guard
    allow_headers=["*"],
)

# --- Stage 4: GraphRAG (/ask) config ---
# The Claude model that explains a retrieved subgraph. Override with JARVIS_ASK_MODEL. Default to
# a current, fast model suitable for a low-latency RAG answer (Anthropic API Docs, API-002).
ASK_MODEL = os.environ.get("JARVIS_ASK_MODEL", "claude-sonnet-4-6")
ASK_MAX_TOKENS = int(os.environ.get("JARVIS_ASK_MAX_TOKENS", "1024"))
# graph.json carries the node summaries + evidence arrays that Neo4j does not store — it is the
# context corpus for /ask (same projection as Neo4j; never hand-edited — ADR-010 §4).
GRAPH_JSON_PATH = Path(
    os.environ.get("JARVIS_GRAPH_JSON", Path(__file__).resolve().parent.parent / "frontend" / "graph.json")
)
_CID_RE = re.compile(r"\b[A-Z]{2,6}-\d{1,4}\b")


# --- serialization helpers ---

def _node(n: Any) -> dict:
    """Neo4j node -> {id, labels, label, props}. `id` is the canonical_id (stable PK)."""
    labels = [lbl for lbl in n.labels if lbl != "DevGraph"]
    props = dict(n)
    return {
        "id": props.get("canonical_id"),
        "labels": labels,
        "label": labels[0] if labels else "DevGraph",
        "name": props.get("name"),
        "props": props,
    }


def _graph(records: list[dict], node_keys=("n",), path_key: str | None = None) -> dict:
    """Collapse records carrying nodes/relationships into a {nodes, edges} graph payload."""
    nodes: dict[str, dict] = {}
    edges: dict[tuple, dict] = {}

    def add_node(n):
        if n is None:
            return
        d = _node(n)
        if d["id"]:
            nodes[d["id"]] = d

    def add_rel(r):
        if r is None:
            return
        s = r.start_node.get("canonical_id")
        t = r.end_node.get("canonical_id")
        if s and t:
            add_node(r.start_node)
            add_node(r.end_node)
            edges[(s, r.type, t)] = {"source": s, "target": t, "type": r.type}

    for rec in records:
        for k in node_keys:
            if k in rec:
                add_node(rec[k])
        if path_key and path_key in rec and rec[path_key] is not None:
            p = rec[path_key]
            for n in p.nodes:
                add_node(n)
            for r in p.relationships:
                add_rel(r)
        if "rels" in rec and rec["rels"]:
            for r in rec["rels"]:
                add_rel(r)
        if "r" in rec and rec["r"] is not None:
            add_rel(rec["r"])

    return {"nodes": list(nodes.values()), "edges": list(edges.values())}


# --- response models (lightweight) ---

class Health(BaseModel):
    ok: bool
    neo4j: bool
    node_count: int = 0
    edge_count: int = 0
    detail: str = ""


# --- endpoints ---

@app.get("/health", response_model=Health)
def health() -> Health:
    """Liveness + Neo4j connectivity + graph size. The front end flips the connector chip
    to LIVE when this returns ok && neo4j."""
    try:
        rows = run_read(
            "MATCH (n:DevGraph) WITH count(n) AS nodes "
            "OPTIONAL MATCH (:DevGraph)-[r]->(:DevGraph) "
            "RETURN nodes, count(r) AS edges"
        )
        nc = rows[0]["nodes"] if rows else 0
        ec = rows[0]["edges"] if rows else 0
        return Health(ok=True, neo4j=True, node_count=nc, edge_count=ec)
    except HTTPException as exc:
        return Health(ok=True, neo4j=False, detail=str(exc.detail))


@app.get("/meta")
def meta() -> dict:
    """Label and relationship-type inventory with counts — drives the legend/filters."""
    labels = run_read(
        "MATCH (n:DevGraph) UNWIND labels(n) AS l "
        "WITH l WHERE l <> 'DevGraph' "
        "RETURN l AS label, count(*) AS count ORDER BY count DESC"
    )
    rels = run_read(
        "MATCH (:DevGraph)-[r]->(:DevGraph) "
        "RETURN type(r) AS type, count(*) AS count ORDER BY count DESC"
    )
    return {"labels": labels, "relationship_types": rels}


@app.get("/node/{cid}")
def node(cid: str) -> dict:
    """Full property bag for one node by canonical_id."""
    rows = run_read("MATCH (n:DevGraph {canonical_id: $cid}) RETURN n", cid=cid)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No node with canonical_id '{cid}'.")
    return _node(rows[0]["n"])


@app.get("/node/{cid}/neighbors")
def neighbors(
    cid: str,
    depth: int = Query(1, ge=1, le=3),
    direction: str = Query("both", pattern="^(out|in|both)$"),
    limit: int = Query(200, ge=1, le=2000),
) -> dict:
    """Expand the neighborhood around a node up to `depth` hops — the core traversal call."""
    arrow = {"out": "-[r]->", "in": "<-[r]-", "both": "-[r]-"}[direction]
    # depth is a validated int (1-3), safe to embed in the variable-length pattern.
    cypher = (
        f"MATCH (a:DevGraph {{canonical_id: $cid}}) "
        f"MATCH path = (a){arrow.replace('[r]', f'[*1..{depth}]')}(b:DevGraph) "
        f"RETURN path LIMIT $limit"
    )
    records = run_read(cypher, cid=cid, limit=limit)
    g = _graph(records, path_key="path")
    if not g["nodes"]:
        # node exists but is isolated → return at least the node itself
        g["nodes"] = [node(cid)]
    return g


@app.get("/search")
def search(
    q: str = Query("", min_length=0),
    label: str = Query("", description="optional label filter, e.g. Module"),
    limit: int = Query(50, ge=1, le=500),
) -> dict:
    """Case-insensitive search over canonical_id + name, optional label filter."""
    label_clause = f":{label}" if label.isalnum() else ""
    cypher = (
        f"MATCH (n{label_clause}:DevGraph) "
        "WHERE $q = '' OR toLower(n.name) CONTAINS toLower($q) "
        "OR toLower(n.canonical_id) CONTAINS toLower($q) "
        "RETURN n ORDER BY n.canonical_id LIMIT $limit"
    )
    rows = run_read(cypher, q=q, limit=limit)
    return {"nodes": [_node(r["n"]) for r in rows]}


@app.get("/path")
def shortest_path(
    source: str = Query(..., alias="from"),
    target: str = Query(..., alias="to"),
    max_hops: int = Query(6, ge=1, le=12),
) -> dict:
    """Shortest path between two nodes (undirected over typed edges)."""
    cypher = (
        "MATCH (a:DevGraph {canonical_id: $source}), (b:DevGraph {canonical_id: $target}) "
        f"MATCH path = shortestPath((a)-[*..{max_hops}]-(b)) "
        "RETURN path"
    )
    records = run_read(cypher, source=source, target=target)
    if not records or records[0].get("path") is None:
        raise HTTPException(status_code=404, detail="No path found within max_hops.")
    return _graph(records, path_key="path")


@app.get("/subgraph")
def subgraph(
    label: str = Query("", description="seed by label, e.g. System; empty = whole graph"),
    limit: int = Query(300, ge=1, le=3000),
) -> dict:
    """A seed view: nodes of `label` (or all) plus the edges among the returned set.
    Default (no label) returns the whole dev_graph capped at `limit`."""
    label_clause = f":{label}" if label.isalnum() else ""
    cypher = (
        f"MATCH (n{label_clause}:DevGraph) WITH n LIMIT $limit "
        "OPTIONAL MATCH (n)-[r]->(m:DevGraph) "
        "RETURN collect(DISTINCT n) AS seeds, collect(DISTINCT r) AS rels, "
        "collect(DISTINCT m) AS others"
    )
    records = run_read(cypher, limit=limit)
    if not records:
        return {"nodes": [], "edges": []}
    rec = records[0]
    flat = [{"n": n} for n in (rec.get("seeds") or [])]
    flat += [{"n": m} for m in (rec.get("others") or [])]
    flat.append({"rels": rec.get("rels") or []})
    return _graph(flat)


# --- Stage 4: GraphRAG /ask -----------------------------------------------------------------
# Pipeline: match a seed node from the question → pull its neighborhood (live Neo4j, graph.json
# fallback) → build a context block (summaries + edges + evidence-class) → ground Claude in ONLY
# that subgraph → return {answer, citations, subgraph}. Read-only: it never emits write Cypher
# and never proposes a graph edit (ADR-010 §1, §3).

_STOP = {
    "the", "a", "an", "what", "whats", "is", "are", "of", "on", "to", "do", "does", "depend",
    "depends", "with", "how", "why", "which", "and", "for", "in", "me", "tell", "about", "show",
    "that", "this", "it", "its", "by", "from", "node",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def _tokens(s: str) -> list[str]:
    return [t for t in _norm(s).split(" ") if len(t) > 1 and t not in _STOP]


@lru_cache(maxsize=1)
def _graph_doc() -> dict[str, dict]:
    """Load graph.json once → {canonical_id: node}. Empty dict if the projection is missing."""
    try:
        data = json.loads(GRAPH_JSON_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {n["id"]: n for n in data.get("nodes", []) if n.get("id")}


def _score(nq: str, toks: list[str], n: dict) -> int:
    """Mirror of the HUD router's scoreNode — same deterministic matcher, in Python."""
    nm = _norm(n.get("name", ""))
    idn = _norm(n.get("id", ""))
    idc = idn.replace(" ", "")
    sm = _norm(n.get("summary", ""))
    nm_tok = nm.split(" ")
    s = 0
    if idn and idn in nq:
        s += 20
    elif idc and idc in nq.replace(" ", ""):
        s += 18
    if nm and len(nm) > 2 and nm in nq:
        s += 14
    for t in toks:
        if t in nm_tok:
            s += 4
        elif t in nm:
            s += 2
        if t in sm:
            s += 1
    return s


def _match_seed(question: str) -> dict | None:
    docs = _graph_doc()
    if not docs:
        return None
    nq, toks = _norm(question), _tokens(question)
    if not toks:
        return None
    best, best_score = None, 0
    for n in docs.values():
        sc = _score(nq, toks, n)
        if sc > best_score:
            best_score, best = sc, n
    return best if best_score >= 6 else None


def _neighborhood(cid: str) -> dict:
    """Seed + 1-hop neighborhood as {nodes, edges}, nodes enriched from graph.json. Tries the live
    bridge (the same /neighbors Cypher) first, then falls back to graph.json edges if Neo4j is down."""
    docs = _graph_doc()
    edges: list[dict] = []
    try:
        # pass every arg explicitly — calling the route fn directly bypasses FastAPI's Query
        # default resolution, so `direction` must not be left as its Query(...) sentinel.
        g = neighbors(cid, depth=1, direction="both", limit=120)  # live Neo4j (read-only)
        edges = g.get("edges", [])
    except HTTPException:
        edges = []
    if not edges:  # offline fallback — derive the neighborhood from graph.json's edge list
        edges = [e for e in _graph_doc_edges() if e.get("source") == cid or e.get("target") == cid]

    ids = {cid}
    for e in edges:
        ids.add(e["source"])
        ids.add(e["target"])
    nodes = [docs[i] for i in ids if i in docs]
    if cid in docs and cid not in {n["id"] for n in nodes}:
        nodes.append(docs[cid])
    return {"nodes": nodes, "edges": edges}


@lru_cache(maxsize=1)
def _graph_doc_edges() -> list[dict]:
    try:
        data = json.loads(GRAPH_JSON_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data.get("edges", [])


def _context_block(subgraph: dict) -> str:
    lines = ["NODES:"]
    for n in subgraph["nodes"]:
        ev = ", ".join(n.get("evidence", []) or []) or "unstated"
        lines.append(
            f'[{n["id"]}] {n.get("label", "")} "{n.get("name", "")}" — '
            f'confidence: {n.get("confidence", "unstated")}; evidence: {ev}'
        )
        if n.get("summary"):
            lines.append(f"  summary: {n['summary']}")
    lines.append("EDGES:")
    for e in subgraph["edges"]:
        lines.append(f'{e["source"]} -[{e["type"]}]-> {e["target"]}')
    return "\n".join(lines)


_ASK_SYSTEM = (
    "You are JARVIS, a read-only analyst over the El Niño engineering dev_graph. Answer ONLY from "
    "the SUBGRAPH supplied in the user message. Rules, in order of priority:\n"
    "1. Ground every claim in the subgraph. If the subgraph does not contain the answer, reply "
    "exactly 'That is not in the graph.' and stop — never invent nodes, edges, or facts.\n"
    "2. Cite the canonical_id(s) you used inline, e.g. [MOD-006].\n"
    "3. Label each claim with the source node's evidence-class (its confidence) in parentheses, "
    "e.g. (confirmed) or (single-source).\n"
    "4. Be concise and precise; prefer the node summaries and the typed edges. Do not propose "
    "changes to the graph — you only read it."
)


def _claude_answer(question: str, context: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured — /ask offline (use the graph fallback).")
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="anthropic SDK not installed — /ask offline.") from exc
    client = Anthropic(api_key=key)
    user = f"SUBGRAPH:\n{context}\n\nQUESTION: {question}"
    try:
        msg = client.messages.create(
            model=ASK_MODEL,
            max_tokens=ASK_MAX_TOKENS,
            system=_ASK_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:  # noqa: BLE001 — any SDK/transport error → generic 502 (detail server-side only)
        logger.warning("Claude API call failed: %s", exc)
        raise HTTPException(status_code=502, detail="Claude API error — /ask offline (use the graph fallback).") from exc
    return "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", None) == "text").strip()


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    """GraphRAG: explain a question grounded ONLY in a retrieved dev_graph subgraph, cited and
    evidence-annotated. 503 when no Claude key is configured (the UI keeps the offline graph
    answering as the no-API fallback)."""
    question = (req.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required.")
    if len(question) > 8000:  # bound input — avoid runaway retrieval / Claude token cost
        raise HTTPException(status_code=400, detail="question too long (max 8000 chars).")

    seed = _match_seed(question)
    if seed is None:
        # Fail-closed: nothing in the graph matched — do not call the LLM, do not invent.
        return {
            "answer": "That is not in the graph. Ask about a dev_graph node by name or canonical_id "
                      "(e.g. \"what depends on the Gold Decision Builder?\" or \"ADR-010\").",
            "citations": [],
            "subgraph": {"nodes": [], "edges": []},
            "model": None,
        }

    subgraph = _neighborhood(seed["id"])
    context = _context_block(subgraph)
    answer = _claude_answer(question, context)

    # Citations = canonical_ids Claude cited that actually exist in the supplied subgraph (seed first).
    present = {n["id"] for n in subgraph["nodes"]}
    cited = [seed["id"]] if seed["id"] in present else []
    for cid in _CID_RE.findall(answer):
        if cid in present and cid not in cited:
            cited.append(cid)

    return {"answer": answer, "citations": cited, "subgraph": subgraph, "model": ASK_MODEL}


# --- Stage 5: voice router (Whisper STT + Piper TTS) -----------------------------------------
# Folded into THIS app — there is no separate voice_bridge.py (ADR-010 §2: one service, one URL).
# Whisper/Piper are OPTIONAL local deps; when absent the endpoints report unavailable and the UI
# falls back to Web Speech (which already works in Chrome/Edge). Voice is input/output only — it
# never drives graph mutation or app-building (ADR-010 Non-Goals).

WHISPER_MODEL = os.environ.get("JARVIS_WHISPER_MODEL", "base.en")
PIPER_BIN = os.environ.get("PIPER_BIN", "piper")
PIPER_VOICE = os.environ.get("PIPER_VOICE", "")  # path to a .onnx Piper voice model


def _whisper_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("faster_whisper") is not None


def _piper_available() -> bool:
    import shutil
    return bool(PIPER_VOICE) and (shutil.which(PIPER_BIN) is not None or Path(PIPER_BIN).exists())


@lru_cache(maxsize=1)
def _whisper_model() -> Any:
    """Lazily load the Whisper model on first STT call (heavy — not on /voice/health)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        return WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    except Exception:  # noqa: BLE001 — any model-load failure → unavailable, fall back to Web Speech
        return None


@app.get("/voice/health")
def voice_health() -> dict:
    stt, tts = _whisper_available(), _piper_available()
    return {
        "ok": stt or tts,
        "stt": stt,
        "tts": tts,
        "whisper_model": WHISPER_MODEL if stt else None,
        "detail": "" if (stt or tts) else "Whisper/Piper not installed — the UI uses Web Speech.",
    }


@app.post("/voice/stt")
async def voice_stt(audio: UploadFile = File(...)) -> dict:
    """Transcribe uploaded audio via local Whisper. 503 when Whisper is unavailable."""
    model = _whisper_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Whisper STT not available — use Web Speech.")
    import tempfile
    data = await audio.read()
    suffix = Path(audio.filename or "clip.webm").suffix or ".webm"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(data)
        tmp.close()
        segments, _info = model.transcribe(tmp.name)
        text = " ".join(seg.text for seg in segments).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Whisper STT failed: %s", exc)
        raise HTTPException(status_code=502, detail="STT transcription failed — check server logs.") from exc
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    return {"text": text}


class TtsRequest(BaseModel):
    text: str


@app.post("/voice/tts")
def voice_tts(req: TtsRequest) -> Response:
    """Synthesize speech via local Piper. 503 when Piper/voice model is not configured."""
    if not _piper_available():
        raise HTTPException(status_code=503, detail="Piper TTS not available — use Web Speech.")
    if len(req.text or "") > 10000:  # bound input passed to the synth subprocess
        raise HTTPException(status_code=400, detail="text too long for TTS (max 10000 chars).")
    import subprocess
    import tempfile
    out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    out.close()
    try:
        proc = subprocess.run(
            [PIPER_BIN, "--model", PIPER_VOICE, "--output_file", out.name],
            input=(req.text or "").encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        if proc.returncode != 0:
            logger.warning("Piper TTS failed (rc=%s): %s", proc.returncode, proc.stderr.decode(errors="ignore")[:500])
            raise HTTPException(status_code=502, detail="TTS synthesis failed — check server logs.")
        audio = Path(out.name).read_bytes()
    finally:
        try:
            os.unlink(out.name)
        except OSError:
            pass
    return Response(content=audio, media_type="audio/wav")


def _info() -> dict:
    return {
        "service": "JARVIS Graph API",
        "neo4j_uri": NEO4J_URI,
        "endpoints": ["/health", "/meta", "/node/{cid}", "/node/{cid}/neighbors", "/search",
                      "/path", "/subgraph", "/ask", "/voice/health", "/voice/stt", "/voice/tts", "/docs"],
        "ask_model": ASK_MODEL,
    }


@app.get("/info")
def info() -> dict:
    return _info()


# --- Stage 5: single-URL serving --------------------------------------------------------------
# When the React HUD has been built (jarvis/hud/dist), mount it as static so the whole thing serves
# from ONE url (e.g. http://127.0.0.1:8000/). The mount is added LAST so every API route above wins;
# StaticFiles(html=True) serves index.html at "/" and the bundled assets + graph.json beneath it.
# ORDER IS CRITICAL: any API route added AFTER this mount would be shadowed (html=True also serves
# index.html on unknown paths). StaticFiles confines reads to STATIC_DIR (no path traversal).
# In dev (no dist) the API root returns the endpoint index instead.
STATIC_DIR = Path(os.environ.get("JARVIS_STATIC_DIR", Path(__file__).resolve().parent.parent / "hud" / "dist"))

if STATIC_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="hud")
else:
    @app.get("/")
    def root() -> dict:
        return _info()
