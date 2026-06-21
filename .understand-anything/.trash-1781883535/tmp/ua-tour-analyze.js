#!/usr/bin/env node
'use strict';

/*
 * Phase-1 Tour Topology Analyzer.
 * Reads {nodes, edges, layers} JSON, computes structural signals
 * (fan-in/out, entry points, BFS dependency chains, non-code inventory,
 * clusters, layer list, node summary index) and writes results JSON.
 */

const fs = require('fs');
const SEP = String.fromCharCode(0); // null byte: safe key delimiter, never in node ids

function main() {
  const inPath = process.argv[2];
  const outPath = process.argv[3];
  if (!inPath || !outPath) {
    console.error('Usage: node ua-tour-analyze.js <input.json> <output.json>');
    process.exit(1);
  }

  const raw = fs.readFileSync(inPath, 'utf8');
  const data = JSON.parse(raw);
  const nodes = Array.isArray(data.nodes) ? data.nodes : [];
  const edges = Array.isArray(data.edges) ? data.edges : [];
  const layers = Array.isArray(data.layers) ? data.layers : [];

  const nodeById = new Map();
  for (const n of nodes) nodeById.set(n.id, n);

  // ---- Fan-in / Fan-out (distinct neighbours; ignore self & dangling) ----
  const fanInSets = new Map();
  const fanOutSets = new Map();
  for (const n of nodes) {
    fanInSets.set(n.id, new Set());
    fanOutSets.set(n.id, new Set());
  }
  const forwardAdj = new Map(); // imports/calls only, forward direction
  for (const n of nodes) forwardAdj.set(n.id, []);
  const pairCount = new Map();  // undirected key -> edge count
  const directed = new Map();   // directed key -> edge count

  for (const e of edges) {
    const s = e.source, t = e.target;
    if (s === t) continue;
    if (!nodeById.has(s) || !nodeById.has(t)) continue; // dangling -> skip
    fanOutSets.get(s).add(t);
    fanInSets.get(t).add(s);
    if (e.type === 'imports' || e.type === 'calls') {
      forwardAdj.get(s).push(t);
    }
    const dk = s + SEP + t;
    directed.set(dk, (directed.get(dk) || 0) + 1);
    const a = s < t ? s : t;
    const b = s < t ? t : s;
    const pk = a + SEP + b;
    pairCount.set(pk, (pairCount.get(pk) || 0) + 1);
  }

  const fanIn = new Map();
  const fanOut = new Map();
  for (const n of nodes) {
    fanIn.set(n.id, fanInSets.get(n.id).size);
    fanOut.set(n.id, fanOutSets.get(n.id).size);
  }

  const fanInRanking = [...nodes]
    .map(n => ({ id: n.id, fanIn: fanIn.get(n.id), name: n.name }))
    .sort((a, b) => b.fanIn - a.fanIn || a.id.localeCompare(b.id))
    .slice(0, 20);

  const fanOutRanking = [...nodes]
    .map(n => ({ id: n.id, fanOut: fanOut.get(n.id), name: n.name }))
    .sort((a, b) => b.fanOut - a.fanOut || a.id.localeCompare(b.id))
    .slice(0, 20);

  // ---- Entry point candidates ----
  const codeEntryNames = new Set([
    'index.ts', 'index.js', 'main.ts', 'main.js', 'app.ts', 'app.js',
    'server.ts', 'server.js', 'mod.rs', 'main.go', 'main.py', 'main.rs',
    'manage.py', 'app.py', 'wsgi.py', 'asgi.py', 'run.py', '__main__.py',
    'Application.java', 'Main.java', 'Program.cs', 'config.ru', 'index.php',
    'App.swift', 'Application.kt', 'main.cpp', 'main.c',
  ]);

  const fanOutVals = nodes.map(n => fanOut.get(n.id)).sort((a, b) => a - b);
  const fanInVals = nodes.map(n => fanIn.get(n.id)).sort((a, b) => a - b);
  const pct = (arr, p) => {
    if (arr.length === 0) return 0;
    const idx = Math.min(arr.length - 1, Math.floor(p * (arr.length - 1)));
    return arr[idx];
  };
  const fanOutTop10Threshold = pct(fanOutVals, 0.9);
  const fanInBottom25Threshold = pct(fanInVals, 0.25);

  const depthOf = (fp) => {
    if (!fp) return 99;
    return fp.split('/').filter(Boolean).length - 1; // directories above the file
  };

  const entryScores = [];
  for (const n of nodes) {
    let score = 0;
    const fp = n.filePath || '';
    const name = n.name || '';
    if (n.type === 'document') {
      const isRoot = depthOf(fp) === 0;
      if (name.toLowerCase() === 'readme.md' && isRoot) score += 5;
      else if (/\.md$/i.test(name) && isRoot) score += 2;
    } else if (n.type === 'file') {
      if (codeEntryNames.has(name)) score += 3;
      if (depthOf(fp) <= 1) score += 1;
      if (fanOutTop10Threshold > 0 && fanOut.get(n.id) >= fanOutTop10Threshold) score += 1;
      if (fanIn.get(n.id) <= fanInBottom25Threshold) score += 1;
    }
    if (score > 0) {
      entryScores.push({ id: n.id, score, name, type: n.type, summary: n.summary || '' });
    }
  }
  entryScores.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  const entryPointCandidates = entryScores.slice(0, 5);

  // ---- BFS from top CODE entry point (skip documents) ----
  const codeEntries = entryScores.filter(e => e.type === 'file');
  let startNode = null;
  if (codeEntries.length > 0) startNode = codeEntries[0].id;
  else if (nodes.length > 0) startNode = nodes[0].id;

  const order = [];
  const depthMap = {};
  if (startNode) {
    const visited = new Set([startNode]);
    let frontier = [startNode];
    depthMap[startNode] = 0;
    order.push(startNode);
    let depth = 0;
    while (frontier.length > 0) {
      const next = [];
      for (const cur of frontier) {
        for (const t of (forwardAdj.get(cur) || [])) {
          if (!visited.has(t)) {
            visited.add(t);
            depthMap[t] = depth + 1;
            order.push(t);
            next.push(t);
          }
        }
      }
      frontier = next;
      depth += 1;
    }
  }
  const byDepth = {};
  for (const id of order) {
    const d = depthMap[id];
    if (!byDepth[d]) byDepth[d] = [];
    byDepth[d].push(id);
  }

  // ---- Non-code file inventory ----
  const mkEntry = (n) => ({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  const nonCodeFiles = { documentation: [], infrastructure: [], data: [], config: [] };
  for (const n of nodes) {
    if (n.type === 'document') nonCodeFiles.documentation.push(mkEntry(n));
    else if (n.type === 'service' || n.type === 'pipeline' || n.type === 'resource') nonCodeFiles.infrastructure.push(mkEntry(n));
    else if (n.type === 'table' || n.type === 'schema' || n.type === 'endpoint') nonCodeFiles.data.push(mkEntry(n));
    else if (n.type === 'config') nonCodeFiles.config.push(mkEntry(n));
  }

  // ---- Tightly coupled clusters ----
  const seeds = [];
  const seenSeed = new Set();
  for (const dk of directed.keys()) {
    const parts = dk.split(SEP);
    const s = parts[0], t = parts[1];
    const rk = t + SEP + s;
    if (directed.has(rk)) {
      const a = s < t ? s : t;
      const b = s < t ? t : s;
      const key = a + SEP + b;
      if (!seenSeed.has(key)) {
        seenSeed.add(key);
        seeds.push([a, b]);
      }
    }
  }
  const undirNeigh = new Map();
  for (const n of nodes) undirNeigh.set(n.id, new Set());
  for (const pk of pairCount.keys()) {
    const parts = pk.split(SEP);
    const a = parts[0], b = parts[1];
    undirNeigh.get(a).add(b);
    undirNeigh.get(b).add(a);
  }

  const clusters = [];
  const usedNodes = new Set();
  for (const seed of seeds) {
    if (seed.some(id => usedNodes.has(id))) continue;
    const members = new Set(seed);
    let changed = true;
    while (changed && members.size < 5) {
      changed = false;
      const candidateCounts = new Map();
      for (const m of members) {
        for (const nb of undirNeigh.get(m)) {
          if (members.has(nb)) continue;
          candidateCounts.set(nb, (candidateCounts.get(nb) || 0) + 1);
        }
      }
      let best = null, bestC = 0;
      for (const [c, cnt] of candidateCounts) {
        if (cnt >= 2 && cnt > bestC) { best = c; bestC = cnt; }
      }
      if (best) { members.add(best); changed = true; }
    }
    if (members.size >= 2) {
      let edgeCount = 0;
      const arr = [...members];
      for (let i = 0; i < arr.length; i++) {
        for (let j = 0; j < arr.length; j++) {
          if (i === j) continue;
          edgeCount += (directed.get(arr[i] + SEP + arr[j]) || 0);
        }
      }
      for (const id of members) usedNodes.add(id);
      clusters.push({ nodes: arr, edgeCount });
    }
  }
  clusters.sort((a, b) => b.edgeCount - a.edgeCount);
  const topClusters = clusters.slice(0, 10);

  // ---- Layer list ----
  const layerList = layers.map(l => ({ id: l.id, name: l.name, description: l.description }));

  // ---- Node summary index ----
  const nodeSummaryIndex = {};
  for (const n of nodes) {
    nodeSummaryIndex[n.id] = { name: n.name, type: n.type, summary: n.summary || '' };
  }

  const result = {
    scriptCompleted: true,
    entryPointCandidates,
    fanInRanking,
    fanOutRanking,
    bfsTraversal: { startNode, order, depthMap, byDepth },
    nonCodeFiles,
    clusters: topClusters,
    layers: { count: layerList.length, list: layerList },
    nodeSummaryIndex,
    totalNodes: nodes.length,
    totalEdges: edges.length,
  };

  fs.writeFileSync(outPath, JSON.stringify(result, null, 2));
  console.error('Analysis complete: ' + nodes.length + ' nodes, ' + edges.length + ' edges, start=' + startNode);
  process.exit(0);
}

try {
  main();
} catch (err) {
  console.error('FATAL: ' + (err && err.stack ? err.stack : err));
  process.exit(1);
}
