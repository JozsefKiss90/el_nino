#!/usr/bin/env node
"use strict";

const fs = require("fs");

function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];
  if (!inputPath || !outputPath) {
    console.error("Usage: ua-tour-analyze.js <input.json> <output.json>");
    process.exit(1);
  }

  const raw = fs.readFileSync(inputPath, "utf8");
  const data = JSON.parse(raw);
  const nodes = Array.isArray(data.nodes) ? data.nodes : [];
  const edges = Array.isArray(data.edges) ? data.edges : [];
  const layers = Array.isArray(data.layers) ? data.layers : [];

  const nodeById = new Map();
  for (const n of nodes) nodeById.set(n.id, n);

  // Adjacency
  const fanIn = new Map();
  const fanOut = new Map();
  for (const n of nodes) {
    fanIn.set(n.id, 0);
    fanOut.set(n.id, 0);
  }
  // forward edges for imports/calls (BFS)
  const forwardAdj = new Map();
  for (const n of nodes) forwardAdj.set(n.id, []);
  // bidirectional pair detection
  const edgeSet = new Set();
  const adjAll = new Map();
  for (const n of nodes) adjAll.set(n.id, new Set());

  for (const e of edges) {
    if (!nodeById.has(e.source) || !nodeById.has(e.target)) continue;
    fanOut.set(e.source, fanOut.get(e.source) + 1);
    fanIn.set(e.target, fanIn.get(e.target) + 1);
    edgeSet.add(e.source + "||" + e.target + "||" + e.type);
    adjAll.get(e.source).add(e.target);
    adjAll.get(e.target).add(e.source);
    if (e.type === "imports" || e.type === "calls") {
      forwardAdj.get(e.source).push(e.target);
    }
  }

  const nameOf = (id) => (nodeById.get(id) ? nodeById.get(id).name : id);
  const summaryOf = (id) => (nodeById.get(id) ? (nodeById.get(id).summary || "") : "");

  // A. Fan-in ranking
  const fanInRanking = nodes
    .map((n) => ({ id: n.id, fanIn: fanIn.get(n.id), name: n.name }))
    .sort((a, b) => b.fanIn - a.fanIn)
    .slice(0, 20);

  // B. Fan-out ranking
  const fanOutRanking = nodes
    .map((n) => ({ id: n.id, fanOut: fanOut.get(n.id), name: n.name }))
    .sort((a, b) => b.fanOut - a.fanOut)
    .slice(0, 20);

  // Percentile helpers
  const fanOutVals = nodes.map((n) => fanOut.get(n.id)).sort((a, b) => a - b);
  const fanInVals = nodes.map((n) => fanIn.get(n.id)).sort((a, b) => a - b);
  const pct = (arr, p) => {
    if (arr.length === 0) return 0;
    const idx = Math.floor((p / 100) * (arr.length - 1));
    return arr[idx];
  };
  const fanOutTop10 = pct(fanOutVals, 90);
  const fanInBottom25 = pct(fanInVals, 25);

  // C. Entry point candidates
  const codeEntryNames = new Set([
    "index.ts", "index.js", "main.ts", "main.js", "app.ts", "app.js",
    "server.ts", "server.js", "mod.rs", "main.go", "main.py", "main.rs",
    "manage.py", "app.py", "wsgi.py", "asgi.py", "run.py", "__main__.py",
    "Application.java", "Main.java", "Program.cs", "config.ru", "index.php",
    "App.swift", "Application.kt", "main.cpp", "main.c",
  ]);

  function depth(filePath) {
    if (!filePath) return 99;
    const norm = filePath.replace(/\\/g, "/");
    return norm.split("/").length - 1;
  }

  const entryScores = [];
  for (const n of nodes) {
    let score = 0;
    const fp = n.filePath || "";
    const isRootMd = (n.type === "document") && (n.name === "README.md") && depth(fp) === 0;
    if (n.type === "document") {
      if (n.name === "README.md" && depth(fp) === 0) score += 5;
      else if (/\.md$/i.test(n.name) && depth(fp) === 0) score += 2;
    } else {
      if (codeEntryNames.has(n.name)) score += 3;
      if (depth(fp) <= 1) score += 1;
      if (fanOut.get(n.id) >= fanOutTop10 && fanOutTop10 > 0) score += 1;
      if (fanIn.get(n.id) <= fanInBottom25) score += 1;
    }
    if (score > 0) {
      entryScores.push({ id: n.id, score, name: n.name, summary: summaryOf(n.id), type: n.type, filePath: fp });
    }
  }
  entryScores.sort((a, b) => b.score - a.score);
  const entryPointCandidates = entryScores.slice(0, 5).map((e) => ({ id: e.id, score: e.score, name: e.name, summary: e.summary }));

  // D. BFS from top code entry point
  const codeEntries = entryScores.filter((e) => e.type !== "document");
  let startNode = null;
  if (codeEntries.length > 0) startNode = codeEntries[0].id;
  else if (nodes.length > 0) {
    // fallback: highest fan-out non-document
    const cand = nodes.filter((n) => n.type !== "document").sort((a, b) => fanOut.get(b.id) - fanOut.get(a.id));
    startNode = cand.length ? cand[0].id : nodes[0].id;
  }

  const bfsOrder = [];
  const depthMap = {};
  if (startNode) {
    const queue = [[startNode, 0]];
    const seen = new Set([startNode]);
    while (queue.length) {
      const [cur, d] = queue.shift();
      bfsOrder.push(cur);
      depthMap[cur] = d;
      for (const nxt of (forwardAdj.get(cur) || [])) {
        if (!seen.has(nxt)) {
          seen.add(nxt);
          queue.push([nxt, d + 1]);
        }
      }
    }
  }
  const byDepth = {};
  for (const id of bfsOrder) {
    const d = String(depthMap[id]);
    if (!byDepth[d]) byDepth[d] = [];
    byDepth[d].push(id);
  }

  // E. Non-code file inventory
  const inv = { documentation: [], infrastructure: [], data: [], config: [] };
  for (const n of nodes) {
    const rec = { id: n.id, name: n.name, type: n.type, summary: summaryOf(n.id) };
    if (n.type === "document") inv.documentation.push(rec);
    else if (n.type === "service" || n.type === "pipeline" || n.type === "resource") inv.infrastructure.push(rec);
    else if (n.type === "table" || n.type === "schema" || n.type === "endpoint") inv.data.push(rec);
    else if (n.type === "config") inv.config.push(rec);
  }

  // F. Tightly coupled clusters
  // bidirectional pairs over imports/calls
  const directed = new Map(); // "src||tgt" -> set of types
  for (const e of edges) {
    if (e.type !== "imports" && e.type !== "calls") continue;
    const k = e.source + "||" + e.target;
    if (!directed.has(k)) directed.set(k, new Set());
    directed.get(k).add(e.type);
  }
  const seedClusters = [];
  const usedPair = new Set();
  for (const e of edges) {
    if (e.type !== "imports" && e.type !== "calls") continue;
    const fwd = e.source + "||" + e.target;
    const rev = e.target + "||" + e.source;
    if (directed.has(rev)) {
      const pairKey = [e.source, e.target].sort().join("##");
      if (!usedPair.has(pairKey)) {
        usedPair.add(pairKey);
        seedClusters.push(new Set([e.source, e.target]));
      }
    }
  }
  // Expand clusters: add nodes connecting to 2+ members
  for (const cl of seedClusters) {
    let changed = true;
    while (changed && cl.size < 5) {
      changed = false;
      const candidateCount = new Map();
      for (const m of cl) {
        for (const nb of (adjAll.get(m) || [])) {
          if (cl.has(nb)) continue;
          candidateCount.set(nb, (candidateCount.get(nb) || 0) + 1);
        }
      }
      for (const [cand, cnt] of candidateCount) {
        if (cnt >= 2 && cl.size < 5) {
          cl.add(cand);
          changed = true;
        }
      }
    }
  }
  // count edges within cluster
  const clustersOut = seedClusters.map((cl) => {
    const arr = [...cl];
    let ec = 0;
    for (const e of edges) {
      if (cl.has(e.source) && cl.has(e.target)) ec++;
    }
    return { nodes: arr, edgeCount: ec };
  }).sort((a, b) => b.edgeCount - a.edgeCount).slice(0, 10);

  // G. Layers
  const layersOut = {
    count: layers.length,
    list: layers.map((l) => ({ id: l.id, name: l.name, description: l.description })),
  };

  // H. Node summary index
  const nodeSummaryIndex = {};
  for (const n of nodes) {
    nodeSummaryIndex[n.id] = { name: n.name, type: n.type, summary: n.summary || "" };
  }

  const result = {
    scriptCompleted: true,
    entryPointCandidates,
    fanInRanking,
    fanOutRanking,
    bfsTraversal: { startNode, order: bfsOrder, depthMap, byDepth },
    nonCodeFiles: inv,
    clusters: clustersOut,
    layers: layersOut,
    nodeSummaryIndex,
    totalNodes: nodes.length,
    totalEdges: edges.length,
  };

  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log("Analysis complete:", nodes.length, "nodes,", edges.length, "edges. Start node:", startNode);
}

try {
  main();
  process.exit(0);
} catch (err) {
  console.error("FATAL:", err && err.stack ? err.stack : err);
  process.exit(1);
}
