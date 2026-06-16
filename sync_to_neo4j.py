"""
Dev Graph -> Neo4j Sync Script

Parses all dev_graph markdown files, extracts YAML frontmatter and
relationship sections, then MERGE-syncs to Neo4j as typed nodes and edges.

Aligned with [[Neo4j Export Mapping]] (GOV-005): all 23 content labels, all 17
relationship sections, and ``canonical_id`` as the node primary key (stable across
renames and immune to basename collisions). Relationship targets are wikilink names,
resolved to canonical_ids via a name index (path-qualified ``[[dir/Name]]`` forms are
tolerated by stripping the directory prefix; on a name collision the non-deprecated
node wins).

Usage:
    python dev_graph/sync_to_neo4j.py [--dry-run] [--clear] [--verify-only]

Options:
    --dry-run   Print Cypher statements + the skipped-edge report without a live DB
    --clear     Delete all DevGraph-labeled nodes before syncing

``--dry-run`` does not import or contact Neo4j, so it validates the parse + edge
resolution offline. ``neo4j`` + ``pyyaml`` are only required for a live sync.
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

# --- Configuration ---

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DB = os.environ.get("NEO4J_DATABASE", "neo4j")

# Resolve the dev_graph dir robustly whether this script lives in dev_graph/ (its
# documented home) or at the repo root: scan ONLY dev_graph, never the whole repo
# (which would sweep wiki/ + raw/ + root docs). Override with DEV_GRAPH_DIR env if set.
_here = Path(__file__).resolve().parent
DEV_GRAPH_DIR = Path(
    os.environ.get(
        "DEV_GRAPH_DIR",
        _here if _here.name == "dev_graph" else _here / "dev_graph",
    )
)
STRUCTURAL_FILES = {"CLAUDE", "index", "log", "README"}

# Maps frontmatter `type` values to Neo4j labels (PascalCase). Per GOV-005 — all 23
# content types (the 7 ontology-redesign types architecture/system/capability/interface/
# event/knowledge_asset/pattern are included so their nodes + edges export).
TYPE_TO_LABEL = {
    "module": "Module",
    "file": "File",
    "test": "Test",
    "gate": "Gate",
    "predicate": "Predicate",
    "artifact_schema": "ArtifactSchema",
    "workflow": "Workflow",
    "agent": "Agent",
    "skill": "Skill",
    "decision_record": "DecisionRecord",
    "constraint": "Constraint",
    "api_doc_source": "ApiDocSource",
    "benchmark_result": "BenchmarkResult",
    "context_pack": "ContextPack",
    "governance": "Governance",
    "observability": "Observability",
    "reference": "Reference",
    "architecture": "Architecture",
    "system": "System",
    "capability": "Capability",
    "interface": "Interface",
    "event": "Event",
    "knowledge_asset": "KnowledgeAsset",
    "pattern": "Pattern",
}

# Relationship section headings -> Neo4j relationship types (all 17 per GOV-005).
SECTION_TO_REL = {
    "Depends On": "DEPENDS_ON",
    "Provides": "PROVIDES",
    "Validated By": "VALIDATED_BY",
    "Constrained By": "CONSTRAINED_BY",
    "Supersedes": "SUPERSEDES",
    "Used By": "USED_BY",
    "Produces": "PRODUCES",
    "Consumes": "CONSUMES",
    "Contains": "CONTAINS",
    "Implements": "IMPLEMENTS",
    "Emits": "EMITS",
    "Triggered By": "TRIGGERED_BY",
    "Guards": "GUARDS",
    "Originates From": "ORIGINATES_FROM",
    "Justified By": "JUSTIFIED_BY",
    "Realizes": "REALIZES",
    "Composes": "COMPOSES",
}

# Frontmatter array fields -> Neo4j relationship types
FRONTMATTER_TO_REL = {
    "related_files": "RELATES_TO_FILE",
    "related_tests": "RELATES_TO_TEST",
    "related_constraints": "CONSTRAINED_BY",
    "related_decisions": "DECIDED_BY",
    "depends_on": "DEPENDS_ON",
    "provides": "PROVIDES",
    "covers": "COVERS",
    "supersedes": "SUPERSEDES",
    "superseded_by": "SUPERSEDED_BY",
    "required_for": "REQUIRED_FOR",
    "validated_by": "VALIDATED_BY",
    "consumed_by": "CONSUMED_BY",
    "produced_by": "PRODUCED_BY",
    "owns": "OWNS",
    "used_by": "USED_BY",
}

# --- Parsing ---

WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


def extract_wikilinks(text: str) -> list[str]:
    """Extract wikilink targets from a text block, normalizing .md suffixes."""
    raw = WIKILINK_RE.findall(text)
    # Strip .md suffix since Obsidian page names don't include the extension
    return [t[:-3] if t.endswith(".md") else t for t in raw]


def parse_relationship_sections(content: str) -> dict[str, list[str]]:
    """Parse ## Relationships subsections for wikilinks."""
    relationships: dict[str, list[str]] = {}
    rel_match = re.search(r"^## Relationships\s*$", content, re.MULTILINE)
    if not rel_match:
        return relationships

    rel_text = content[rel_match.end():]
    next_h2 = re.search(r"^## (?!#)", rel_text, re.MULTILINE)
    if next_h2:
        rel_text = rel_text[:next_h2.start()]

    subsections = re.split(r"^### (.+)$", rel_text, flags=re.MULTILINE)
    for i in range(1, len(subsections), 2):
        heading = subsections[i].strip()
        body = subsections[i + 1] if i + 1 < len(subsections) else ""
        links = extract_wikilinks(body)
        if links and heading in SECTION_TO_REL:
            relationships[heading] = links

    return relationships


def parse_dev_graph_file(filepath: Path) -> dict | None:
    """Parse a single dev_graph markdown file into a node dict."""
    content = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    if fm is None or "type" not in fm:
        return None

    name = filepath.stem  # filename without .md
    node_type = fm.get("type", "")
    label = TYPE_TO_LABEL.get(node_type)
    if not label:
        print(f"  SKIP {name}: unknown type '{node_type}'")
        return None

    canonical_id = fm.get("canonical_id")
    if not canonical_id:
        print(f"  SKIP {name}: missing canonical_id")
        return None

    # Collect scalar properties for Neo4j node
    props = {"name": name, "canonical_id": str(canonical_id)}
    scalar_fields = [
        "type", "status", "implementation_status", "canonical",
        "created", "updated", "confidence",
        "module_name", "module_path", "responsibility", "language",
        "file_path", "test_path", "test_type", "gate_id", "gate_scope",
        "blocking", "predicate_id", "predicate_scope", "implemented_in",
        "schema_id", "schema_path", "schema_format", "schema_version",
        "provider", "doc_source", "doc_scope", "freshness_requirement",
        "decision_id", "decision_date", "decision_status",
        "task_id", "task_type", "admissibility_checked",
        "api_provider", "api_version", "doc_url", "retrieval_method",
    ]
    for key in scalar_fields:
        val = fm.get(key)
        if val is not None:
            props[key] = str(val) if not isinstance(val, (str, bool, int, float)) else val

    array_fields = [
        "evidence",  # evidence-class provenance — kept in sync with graph.json so the live Neo4j
                     # path carries the same evidence array as the offline projection (ADR-010 §3)
        "source_paths", "allowed_for_tasks",
        "required_nodes", "required_files", "required_tests", "required_docs",
        "required_artifacts",
    ]
    for key in array_fields:
        val = fm.get(key)
        if val and isinstance(val, list) and any(v for v in val):
            props[key] = [str(v) for v in val if v]

    # Collect relationships from frontmatter arrays
    fm_rels: dict[str, list[str]] = {}
    for fm_key, rel_type in FRONTMATTER_TO_REL.items():
        val = fm.get(fm_key)
        if val and isinstance(val, list):
            targets: list[str] = []
            for item in val:
                if not item:
                    continue
                wl = extract_wikilinks(str(item))
                if wl:
                    targets.extend(wl)
            if targets:
                fm_rels[rel_type] = targets

    section_rels = parse_relationship_sections(content)

    all_rels = dict(fm_rels)
    for heading, targets in section_rels.items():
        rel_type = SECTION_TO_REL[heading]
        existing = set(all_rels.get(rel_type, []))
        existing.update(targets)
        all_rels[rel_type] = list(existing)

    return {
        "name": name,
        "canonical_id": str(canonical_id),
        "label": label,
        "props": props,
        "relationships": all_rels,
        "status": str(fm.get("status", "")),
        "filepath": str(filepath.relative_to(DEV_GRAPH_DIR.parent)),
    }


def scan_dev_graph() -> list[dict]:
    """Scan all markdown files in dev_graph and parse into node dicts."""
    nodes = []
    for md_file in sorted(DEV_GRAPH_DIR.rglob("*.md")):
        if md_file.stem in STRUCTURAL_FILES:
            continue
        node = parse_dev_graph_file(md_file)
        if node:
            nodes.append(node)
    return nodes


def build_name_index(nodes: list[dict]) -> dict[str, str]:
    """Map node name (filename stem) -> canonical_id. On a name collision the
    non-deprecated node wins (so a deprecated duplicate never shadows the live node)."""
    index: dict[str, tuple[str, bool]] = {}
    for n in nodes:
        nm = n["name"]
        cid = n["canonical_id"]
        deprecated = n["status"] == "deprecated"
        if nm not in index or (index[nm][1] and not deprecated):
            index[nm] = (cid, deprecated)
    return {nm: cid for nm, (cid, _dep) in index.items()}


def resolve_target(target: str, name_index: dict[str, str]) -> str | None:
    """Resolve a wikilink target (bare or path-qualified) to a canonical_id."""
    cid = name_index.get(target)
    if cid:
        return cid
    if "/" in target:  # tolerate path-qualified [[dir/Name]] forms
        return name_index.get(target.split("/")[-1])
    return None


# --- Neo4j Sync ---

def build_node_cypher(node: dict) -> tuple[str, dict]:
    """Build a MERGE statement for a single node, keyed on canonical_id (GOV-005)."""
    label = node["label"]
    props = node["props"]

    set_clauses = []
    params = {"cid": node["canonical_id"]}
    for key, val in props.items():
        if key == "canonical_id":
            continue
        param_key = f"p_{key}"
        set_clauses.append(f"n.{key} = ${param_key}")
        params[param_key] = val

    set_str = ", ".join(set_clauses) if set_clauses else "n.canonical_id = $cid"
    cypher = f"MERGE (n:{label}:DevGraph {{canonical_id: $cid}}) SET {set_str}"
    return cypher, params


def build_rel_cypher(source_cid: str, rel_type: str, target_cid: str) -> tuple[str, dict]:
    """Build a MERGE statement for a relationship between two DevGraph nodes (by canonical_id)."""
    cypher = (
        f"MATCH (a:DevGraph {{canonical_id: $source}}) "
        f"MATCH (b:DevGraph {{canonical_id: $target}}) "
        f"MERGE (a)-[r:{rel_type}]->(b)"
    )
    return cypher, {"source": source_cid, "target": target_cid}


def sync_to_neo4j(nodes: list[dict], dry_run: bool = False, clear: bool = False) -> int:
    """Sync parsed nodes to Neo4j. Returns the number of skipped (unresolvable) edges."""
    name_index = build_name_index(nodes)

    driver = None
    if not dry_run:
        from neo4j import GraphDatabase  # lazy: only needed for a live sync
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    else:
        print("\n=== DRY RUN — Cypher statements (no DB connection) ===\n")

    try:
        if clear and not dry_run:
            print("Clearing existing DevGraph nodes...")
            with driver.session(database=NEO4J_DB) as session:
                result = session.run("MATCH (n:DevGraph) DETACH DELETE n")
                summary = result.consume()
                print(f"  Deleted {summary.counters.nodes_deleted} nodes, "
                      f"{summary.counters.relationships_deleted} relationships")

        print(f"\n--- Phase 1: Syncing {len(nodes)} nodes ---\n")
        for node in nodes:
            cypher, params = build_node_cypher(node)
            if dry_run:
                print(f"// {node['name']} ({node['canonical_id']} :{node['label']})")
                print(f"{cypher}\n")
            else:
                with driver.session(database=NEO4J_DB) as session:
                    session.run(cypher, params)
                print(f"  MERGE :{node['label']} {node['canonical_id']} ({node['name']})")

        print("\n--- Phase 2: Syncing relationships ---\n")
        rel_count = 0
        skipped: list[tuple[str, str, str]] = []

        for node in nodes:
            source_cid = node["canonical_id"]
            for rel_type, targets in node["relationships"].items():
                for target in targets:
                    target_cid = resolve_target(target, name_index)
                    if target_cid is None:
                        skipped.append((node["name"], rel_type, target))
                        continue
                    cypher, params = build_rel_cypher(source_cid, rel_type, target_cid)
                    if dry_run:
                        print(f"// {node['name']} -[{rel_type}]-> {target} ({target_cid})")
                        print(f"{cypher}\n")
                    else:
                        with driver.session(database=NEO4J_DB) as session:
                            session.run(cypher, params)
                        print(f"  ({node['canonical_id']})-[:{rel_type}]->({target_cid})")
                    rel_count += 1

        print("\n--- Summary ---")
        print(f"  Nodes synced: {len(nodes)}")
        print(f"  Relationships created: {rel_count}")
        if skipped:
            print(f"  Relationships SKIPPED (target not resolvable): {len(skipped)}")
            for src, rel, tgt in skipped:
                print(f"    {src} -[{rel}]-> {tgt} (target not found)")
        else:
            print("  Relationships skipped: 0 (clean — every edge target resolved)")
        return len(skipped)

    finally:
        if driver:
            driver.close()


def verify_graph() -> None:
    """Run verification queries against Neo4j and print results."""
    from neo4j import GraphDatabase  # lazy
    print("\n=== Verification Queries ===\n")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    try:
        with driver.session(database=NEO4J_DB) as session:
            result = session.run(
                "MATCH (n:DevGraph) RETURN labels(n) AS labels, count(n) AS count ORDER BY count DESC"
            )
            print("Node counts by label:")
            total_nodes = 0
            for record in result:
                type_labels = [lbl for lbl in record["labels"] if lbl != "DevGraph"]
                label = type_labels[0] if type_labels else "DevGraph"
                print(f"  :{label} = {record['count']}")
                total_nodes += record["count"]
            print(f"  TOTAL = {total_nodes}")

            result = session.run(
                "MATCH (:DevGraph)-[r]->(:DevGraph) "
                "RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC"
            )
            print("\nRelationship counts by type:")
            total_rels = 0
            for record in result:
                print(f"  {record['rel_type']} = {record['count']}")
                total_rels += record["count"]
            print(f"  TOTAL = {total_rels}")
    finally:
        driver.close()


# --- Main ---

def main() -> int:
    parser = argparse.ArgumentParser(description="Sync dev_graph markdown to Neo4j")
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher without executing")
    parser.add_argument("--clear", action="store_true", help="Clear existing DevGraph nodes first")
    parser.add_argument("--verify-only", action="store_true", help="Only run verification queries")
    args = parser.parse_args()

    if args.verify_only:
        verify_graph()
        return 0

    print(f"Scanning {DEV_GRAPH_DIR} for markdown files...\n")
    nodes = scan_dev_graph()
    print(f"Found {len(nodes)} content nodes\n")

    skipped = sync_to_neo4j(nodes, dry_run=args.dry_run, clear=args.clear)

    if not args.dry_run:
        verify_graph()

    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
