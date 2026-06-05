"""
Dev Graph -> Neo4j Sync Script

Parses all dev_graph markdown files, extracts YAML frontmatter and
relationship sections, then MERGE-syncs to Neo4j as typed nodes and edges.

Usage:
    python dev_graph/sync_to_neo4j.py [--dry-run] [--clear]

Options:
    --dry-run   Print Cypher statements without executing
    --clear     Delete all DevGraph-labeled nodes before syncing

Requires:
    pip install neo4j pyyaml
"""

import os
import re
import sys
import yaml
import argparse
from pathlib import Path
from neo4j import GraphDatabase

# --- Configuration ---

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DB = os.environ.get("NEO4J_DATABASE", "neo4j")

DEV_GRAPH_DIR = Path(__file__).parent
STRUCTURAL_FILES = {"CLAUDE", "index", "log", "README"}

# Maps frontmatter `type` values to Neo4j labels (PascalCase)
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
}

# Relationship section headings -> Neo4j relationship types
SECTION_TO_REL = {
    "Depends On": "DEPENDS_ON",
    "Provides": "PROVIDES",
    "Validated By": "VALIDATED_BY",
    "Constrained By": "CONSTRAINED_BY",
    "Supersedes": "SUPERSEDES",
    "Used By": "USED_BY",
    "Produces": "PRODUCES",
    "Consumes": "CONSUMES",
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
    relationships = {}
    # Find the ## Relationships section
    rel_match = re.search(r"^## Relationships\s*$", content, re.MULTILINE)
    if not rel_match:
        return relationships

    rel_text = content[rel_match.end():]
    # Stop at the next ## heading (not ###)
    next_h2 = re.search(r"^## (?!#)", rel_text, re.MULTILINE)
    if next_h2:
        rel_text = rel_text[:next_h2.start()]

    # Parse each ### subsection
    subsections = re.split(r"^### (.+)$", rel_text, flags=re.MULTILINE)
    # subsections[0] is text before first ###, then alternating heading/content
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

    # Collect scalar properties for Neo4j node
    props = {"name": name}
    scalar_fields = [
        "type", "status", "implementation_status", "canonical",
        "created", "updated", "confidence",
        # Domain-specific scalars
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
            # Convert dates to strings for Neo4j
            props[key] = str(val) if not isinstance(val, (str, bool, int, float)) else val

    # Collect array properties (stored as Neo4j string arrays)
    array_fields = [
        "source_paths", "allowed_for_tasks",
        "required_nodes", "required_files", "required_tests", "required_docs",
        "required_artifacts",
    ]
    for key in array_fields:
        val = fm.get(key)
        if val and isinstance(val, list) and any(v for v in val):
            props[key] = [str(v) for v in val if v]

    # Collect relationships from frontmatter arrays
    fm_rels = {}
    for fm_key, rel_type in FRONTMATTER_TO_REL.items():
        val = fm.get(fm_key)
        if val and isinstance(val, list):
            targets = []
            for item in val:
                if not item:
                    continue
                item_str = str(item)
                # Extract wikilink target if wrapped in [[]]
                wl = extract_wikilinks(item_str)
                if wl:
                    targets.extend(wl)
                # Skip plain filesystem paths (not graph references)
            if targets:
                fm_rels[rel_type] = targets

    # Collect relationships from ## Relationships sections
    section_rels = parse_relationship_sections(content)

    # Merge: section relationships augment frontmatter relationships
    all_rels = dict(fm_rels)
    for heading, targets in section_rels.items():
        rel_type = SECTION_TO_REL[heading]
        existing = set(all_rels.get(rel_type, []))
        existing.update(targets)
        all_rels[rel_type] = list(existing)

    return {
        "name": name,
        "label": label,
        "props": props,
        "relationships": all_rels,
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


# --- Neo4j Sync ---

def build_node_cypher(node: dict) -> tuple[str, dict]:
    """Build a MERGE statement for a single node."""
    label = node["label"]
    props = node["props"]

    # Use MERGE on name, then SET all properties
    set_clauses = []
    params = {"name": props["name"]}
    for key, val in props.items():
        if key == "name":
            continue
        param_key = f"p_{key}"
        set_clauses.append(f"n.{key} = ${param_key}")
        params[param_key] = val

    set_str = ", ".join(set_clauses) if set_clauses else "n.name = $name"
    # Every node also gets a :DevGraph label for easy identification
    cypher = f"MERGE (n:{label}:DevGraph {{name: $name}}) SET {set_str}"
    return cypher, params


def build_rel_cypher(source_name: str, rel_type: str, target_name: str) -> tuple[str, dict]:
    """Build a MERGE statement for a relationship between two DevGraph nodes."""
    cypher = (
        f"MATCH (a:DevGraph {{name: $source}}) "
        f"MATCH (b:DevGraph {{name: $target}}) "
        f"MERGE (a)-[r:{rel_type}]->(b)"
    )
    return cypher, {"source": source_name, "target": target_name}


def sync_to_neo4j(nodes: list[dict], dry_run: bool = False, clear: bool = False):
    """Sync parsed nodes to Neo4j."""
    if dry_run:
        print("\n=== DRY RUN — Cypher statements ===\n")

    driver = None if dry_run else GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    try:
        if clear and not dry_run:
            print("Clearing existing DevGraph nodes...")
            with driver.session(database=NEO4J_DB) as session:
                result = session.run("MATCH (n:DevGraph) DETACH DELETE n")
                summary = result.consume()
                print(f"  Deleted {summary.counters.nodes_deleted} nodes, "
                      f"{summary.counters.relationships_deleted} relationships")

        # Phase 1: Create/update nodes
        print(f"\n--- Phase 1: Syncing {len(nodes)} nodes ---\n")
        node_names = {n["name"] for n in nodes}

        for node in nodes:
            cypher, params = build_node_cypher(node)
            if dry_run:
                print(f"// {node['name']} ({node['label']})")
                print(f"{cypher}")
                print(f"// params: {params}\n")
            else:
                with driver.session(database=NEO4J_DB) as session:
                    session.run(cypher, params)
                print(f"  MERGE :{node['label']} {node['name']}")

        # Phase 2: Create relationships
        print(f"\n--- Phase 2: Syncing relationships ---\n")
        rel_count = 0
        skipped = []

        for node in nodes:
            for rel_type, targets in node["relationships"].items():
                for target in targets:
                    if target not in node_names:
                        skipped.append((node["name"], rel_type, target))
                        continue
                    cypher, params = build_rel_cypher(node["name"], rel_type, target)
                    if dry_run:
                        print(f"// {node['name']} -[{rel_type}]-> {target}")
                        print(f"{cypher}\n")
                    else:
                        with driver.session(database=NEO4J_DB) as session:
                            session.run(cypher, params)
                        print(f"  ({node['name']})-[:{rel_type}]->({target})")
                    rel_count += 1

        # Summary
        print(f"\n--- Summary ---")
        print(f"  Nodes synced: {len(nodes)}")
        print(f"  Relationships created: {rel_count}")
        if skipped:
            print(f"  Relationships skipped (target not in dev_graph): {len(skipped)}")
            for src, rel, tgt in skipped:
                print(f"    {src} -[{rel}]-> {tgt} (target not found)")

    finally:
        if driver:
            driver.close()


def verify_graph():
    """Run verification queries against Neo4j and print results."""
    print("\n=== Verification Queries ===\n")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    try:
        with driver.session(database=NEO4J_DB) as session:
            # Node count by label
            result = session.run(
                "MATCH (n:DevGraph) "
                "RETURN labels(n) AS labels, count(n) AS count "
                "ORDER BY count DESC"
            )
            print("Node counts by label:")
            total_nodes = 0
            for record in result:
                # Filter out the 'DevGraph' label to show the type label
                type_labels = [l for l in record["labels"] if l != "DevGraph"]
                label = type_labels[0] if type_labels else "DevGraph"
                print(f"  :{label} = {record['count']}")
                total_nodes += record["count"]
            print(f"  TOTAL = {total_nodes}")

            # Relationship count by type
            result = session.run(
                "MATCH (:DevGraph)-[r]->(:DevGraph) "
                "RETURN type(r) AS rel_type, count(r) AS count "
                "ORDER BY count DESC"
            )
            print("\nRelationship counts by type:")
            total_rels = 0
            for record in result:
                print(f"  {record['rel_type']} = {record['count']}")
                total_rels += record["count"]
            print(f"  TOTAL = {total_rels}")

            # Sample: show all constraint nodes and what they constrain
            result = session.run(
                "MATCH (a:DevGraph)-[:CONSTRAINED_BY]->(c:Constraint:DevGraph) "
                "RETURN a.name AS node, c.name AS constraint "
                "ORDER BY c.name, a.name"
            )
            print("\nConstraint relationships:")
            for record in result:
                print(f"  {record['node']} --CONSTRAINED_BY--> {record['constraint']}")

            # Sample: show decision relationships
            result = session.run(
                "MATCH (a:DevGraph)-[:DECIDED_BY]->(d:DecisionRecord:DevGraph) "
                "RETURN a.name AS node, d.name AS decision "
                "ORDER BY d.name, a.name"
            )
            print("\nDecision relationships:")
            for record in result:
                print(f"  {record['node']} --DECIDED_BY--> {record['decision']}")

    finally:
        driver.close()


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Sync dev_graph markdown to Neo4j")
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher without executing")
    parser.add_argument("--clear", action="store_true", help="Clear existing DevGraph nodes first")
    parser.add_argument("--verify-only", action="store_true", help="Only run verification queries")
    args = parser.parse_args()

    if args.verify_only:
        verify_graph()
        return

    print(f"Scanning {DEV_GRAPH_DIR} for markdown files...\n")
    nodes = scan_dev_graph()
    print(f"Found {len(nodes)} content nodes\n")

    for node in nodes:
        rel_count = sum(len(v) for v in node["relationships"].values())
        print(f"  {node['label']:20s} {node['name']}")
        if rel_count:
            print(f"  {'':20s}   -> {rel_count} relationships")

    sync_to_neo4j(nodes, dry_run=args.dry_run, clear=args.clear)

    if not args.dry_run:
        verify_graph()


if __name__ == "__main__":
    main()
