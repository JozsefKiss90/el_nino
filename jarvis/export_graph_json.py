"""
graph.json exporter — a deterministic, server-less projection of the dev_graph.

For node and edge extraction this reuses the SAME markdown parser as ``sync_to_neo4j.py``
(frontmatter + relationship-section extraction + canonical_id edge resolution), so the
node/edge sets stay identical and DRY: ``graph.json`` and Neo4j are two projections of the
one canonical source (the dev_graph markdown), never hand-edited (ADR-010 §4). The first
sentence of ``## Definition`` (the ``summary`` field) is a novel extraction added here for the
console — ``sync_to_neo4j.py`` does not parse body prose.

For each dev_graph node it emits::

    {id, label, name, summary, confidence, evidence, status}

where ``summary`` is the first sentence of the node's ``## Definition`` section
(falling back to the node name). Edges are ``{source, type, target}`` using the same
canonical_id resolution as the Neo4j exporter, so the same 5 unresolved edges are
skipped and the resolved-edge set matches the live graph.

It contacts no database — it reads the markdown exactly as ``sync_to_neo4j.py
--dry-run`` does. Output: ``jarvis/frontend/graph.json``.

Usage:
    python jarvis/export_graph_json.py            # writes jarvis/frontend/graph.json
    python jarvis/export_graph_json.py --stdout   # print to stdout instead
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Reuse the canonical parser. export_graph_json.py lives in jarvis/; sync_to_neo4j.py
# is at the repo root — put the repo root on sys.path so the import resolves regardless
# of the current working directory. sync_to_neo4j.DEV_GRAPH_DIR is anchored to that
# module's own location, so it still points at <repo>/dev_graph.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import sync_to_neo4j as sync  # noqa: E402  (path set above)

OUTPUT_PATH = Path(__file__).resolve().parent / "frontend" / "graph.json"

_DEFINITION_RE = re.compile(r"^## Definition\s*$", re.MULTILINE)
_NEXT_H2_RE = re.compile(r"^## ", re.MULTILINE)
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def first_sentence_of_definition(content: str, fallback: str) -> str:
    """First sentence of the node's ``## Definition`` section, else ``fallback``.

    Wikilinks are flattened to their display text and whitespace is collapsed so the
    summary is plain prose suitable for a tooltip / answer line.
    """
    m = _DEFINITION_RE.search(content)
    if not m:
        return fallback
    body = content[m.end():]
    nxt = _NEXT_H2_RE.search(body)
    if nxt:
        body = body[:nxt.start()]
    # [[Target|Alias]] -> Alias ; [[Target]] -> Target
    text = _WIKILINK_RE.sub(lambda mt: mt.group(2) or mt.group(1), body)
    text = " ".join(text.split())  # collapse newlines/indentation
    if not text:
        return fallback
    first = _SENTENCE_SPLIT_RE.split(text, maxsplit=1)[0].strip()
    return first or fallback


def build_graph() -> dict:
    """Parse the dev_graph markdown into a {nodes, edges, meta} payload."""
    nodes = sync.scan_dev_graph()
    name_index = sync.build_name_index(nodes)

    out_nodes: list[dict] = []
    for n in nodes:
        filepath = sync.DEV_GRAPH_DIR.parent / n["filepath"]
        content = filepath.read_text(encoding="utf-8")
        fm = sync.parse_frontmatter(content) or {}
        evidence = fm.get("evidence")
        evidence = [str(e) for e in evidence] if isinstance(evidence, list) else []
        props = n["props"]
        out_nodes.append({
            "id": n["canonical_id"],
            "label": n["label"],
            "name": n["name"],
            "summary": first_sentence_of_definition(content, n["name"]),
            "confidence": props.get("confidence", ""),
            "evidence": evidence,
            "status": props.get("status", n.get("status", "")),
        })

    out_edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    skipped: list[tuple[str, str, str]] = []
    for n in nodes:
        source = n["canonical_id"]
        for rel_type, targets in n["relationships"].items():
            for target in targets:
                cid = sync.resolve_target(target, name_index)
                if cid is None:
                    skipped.append((n["name"], rel_type, target))
                    continue
                key = (source, rel_type, cid)
                if key in seen:
                    continue
                seen.add(key)
                out_edges.append({"source": source, "type": rel_type, "target": cid})

    out_nodes.sort(key=lambda d: d["id"])
    out_edges.sort(key=lambda d: (d["source"], d["type"], d["target"]))

    return {
        "meta": {
            "node_count": len(out_nodes),
            "edge_count": len(out_edges),
            "skipped_edges": len(skipped),
            "source": "dev_graph markdown (sync_to_neo4j parser)",
        },
        "nodes": out_nodes,
        "edges": out_edges,
        "_skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the dev_graph to graph.json")
    parser.add_argument("--stdout", action="store_true", help="print to stdout instead of writing the file")
    parser.add_argument("--out", type=Path, default=OUTPUT_PATH, help="output path (default jarvis/frontend/graph.json)")
    args = parser.parse_args()

    graph = build_graph()
    skipped = graph.pop("_skipped")
    payload = json.dumps(graph, indent=2, ensure_ascii=False)

    if args.stdout:
        # write UTF-8 bytes directly — print() uses the console locale (cp1250 on Windows PowerShell)
        # and would raise UnicodeEncodeError on the '→'/'·' characters in node summaries.
        sys.stdout.buffer.write((payload + "\n").encode("utf-8"))
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {args.out} — {graph['meta']['node_count']} nodes, "
              f"{graph['meta']['edge_count']} edges ({graph['meta']['skipped_edges']} skipped).")

    if skipped:
        print(f"\nSkipped {len(skipped)} unresolvable edge(s) (same as the Neo4j sync):")
        for src, rel, tgt in skipped:
            print(f"  {src} -[{rel}]-> {tgt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
