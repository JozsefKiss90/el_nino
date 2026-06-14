"""
JARVIS Graph API — read-only FastAPI service over the El Niño dev_graph in Neo4j.

Exposes the typed dev_graph (populated by ../sync_to_neo4j.py) for traversal from the
JARVIS front end: node lookup, neighbor expansion, label/text search, shortest path, and
seed subgraphs. Every query is READ-ONLY and parameterized:

  * the Neo4j session is opened in READ access mode (rejects writes at the driver),
  * a defensive keyword guard blocks any Cypher containing mutating clauses,
  * all user input flows through query parameters, never string interpolation.

Config via env (same vars as sync_to_neo4j.py / .mcp.json):
  NEO4J_URI (default bolt://localhost:7687), NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE.
For Neo4j Aura, set NEO4J_URI=neo4j+s://<dbid>.databases.neo4j.io and the Aura credentials —
nothing else changes.

Run:  uvicorn app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pydantic import BaseModel

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DB = os.environ.get("NEO4J_DATABASE", "neo4j")

# Defensive: even though sessions run in READ mode, reject any clause that could mutate.
_FORBIDDEN = (
    "create", "merge", "delete", "set ", "remove", "drop",
    "detach", "call db.", "load csv", "foreach",
)

_driver: Any = None


def _guard(cypher: str) -> None:
    low = cypher.lower()
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
    allow_methods=["GET"],
    allow_headers=["*"],
)


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


@app.get("/")
def root() -> dict:
    return {
        "service": "JARVIS Graph API",
        "neo4j_uri": NEO4J_URI,
        "endpoints": ["/health", "/meta", "/node/{cid}", "/node/{cid}/neighbors",
                      "/search", "/path", "/subgraph", "/docs"],
    }
