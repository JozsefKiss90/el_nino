import json, sys, io
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"C:\Code\el_nino\.understand-anything\intermediate"
COMMIT = "f9b1a22ce1edc974bcfe5c3dec4ec6319ffe5019"

def load(name):
    with open(rf"{ROOT}\{name}", encoding="utf-8") as f:
        return json.load(f)

scan = load("scan-result.json")
graph = load("assembled-graph.json")
layers = load("layers.json")
tour = load("tour.json")

# --- project metadata (robust to scan-result layout) ---
proj = scan.get("project", {}) if isinstance(scan.get("project"), dict) else {}
name = proj.get("name") or scan.get("projectName") or "el_nino"
description = proj.get("description") or scan.get("projectDescription") or ""
languages = scan.get("languages") or proj.get("languages") or []
frameworks = scan.get("frameworks") or proj.get("frameworks") or []
# languages may be list of dicts {language,...} or strings
def norm_list(v):
    out = []
    for x in (v or []):
        out.append(x.get("language") or x.get("name") if isinstance(x, dict) else x)
    return [s for s in out if s]
languages = norm_list(languages)
frameworks = norm_list(frameworks)

nodes = graph["nodes"]
edges = graph["edges"]
node_ids = {n["id"] for n in nodes}

KNOWN_PREFIXES = ("file:", "function:", "class:", "module:", "concept:", "config:",
                  "document:", "service:", "table:", "endpoint:", "pipeline:",
                  "schema:", "resource:")

def fix_id(x):
    if isinstance(x, dict):
        x = x.get("id", "")
    if isinstance(x, str) and not x.startswith(KNOWN_PREFIXES) and x:
        return "file:" + x
    return x

# --- normalize layers (already array; unwrap defensively + drop dangling) ---
if isinstance(layers, dict) and "layers" in layers:
    layers = layers["layers"]
layer_dangling = 0
for L in layers:
    if "nodes" in L and "nodeIds" not in L:
        L["nodeIds"] = L.pop("nodes")
    if not L.get("id"):
        L["id"] = "layer:" + (L.get("name", "unnamed").lower().replace(" ", "-"))
    fixed = []
    for nid in L.get("nodeIds", []):
        nid = fix_id(nid)
        if nid in node_ids:
            fixed.append(nid)
        else:
            layer_dangling += 1
    L["nodeIds"] = fixed

# --- normalize tour (already array; rename/convert/drop/sort) ---
if isinstance(tour, dict):
    tour = tour.get("tour") or tour.get("steps") or []
tour_dangling = 0
for s in tour:
    if "nodesToInspect" in s and "nodeIds" not in s:
        s["nodeIds"] = s.pop("nodesToInspect")
    if "whyItMatters" in s and "description" not in s:
        s["description"] = s.pop("whyItMatters")
    fixed = []
    for nid in s.get("nodeIds", []):
        nid = fix_id(nid)
        if nid in node_ids:
            fixed.append(nid)
        else:
            tour_dangling += 1
    s["nodeIds"] = fixed
tour.sort(key=lambda s: s.get("order", 0))

final = {
    "version": "1.0.0",
    "project": {
        "name": name,
        "languages": languages,
        "frameworks": frameworks,
        "description": description,
        "analyzedAt": datetime.now(timezone.utc).isoformat(),
        "gitCommitHash": COMMIT,
    },
    "nodes": nodes,
    "edges": edges,
    "layers": layers,
    "tour": tour,
}

with open(rf"{ROOT}\assembled-graph.json", "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print("ASSEMBLED OK")
print("name:", name)
print("languages:", languages)
print("frameworks:", frameworks)
print("nodes:", len(nodes), "edges:", len(edges), "layers:", len(layers), "tour steps:", len(tour))
print("layer dangling dropped:", layer_dangling, "tour dangling dropped:", tour_dangling)
