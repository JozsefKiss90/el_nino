'use strict';
// Generates layers.json from the structural analysis results.
const fs = require('fs');

const RESULTS = 'C:/Code/el_nino/.understand-anything/tmp/ua-arch-results.json';
const INPUT = 'C:/Code/el_nino/.understand-anything/tmp/ua-arch-input.json';
const OUT = 'C:/Code/el_nino/.understand-anything/intermediate/layers.json';

const r = JSON.parse(fs.readFileSync(RESULTS, 'utf8'));
const input = JSON.parse(fs.readFileSync(INPUT, 'utf8'));

const norm = p => String(p || '').replace(/\\/g, '/');
const byId = new Map();
for (const n of input.fileNodes) byId.set(n.id, { ...n, p: norm(n.filePath || n.id) });

const assigned = new Map(); // id -> layerId

function assign(id, layerId) {
  if (!byId.has(id)) return;            // never invent ids
  if (assigned.has(id)) return;         // first match wins
  assigned.set(id, layerId);
}

// Iterate every file node and classify by path/type.
for (const [id, n] of byId) {
  const p = n.p;
  const type = n.type;

  // --- Infrastructure: docker / deploy service nodes ---
  if (type === 'service' || /Dockerfile/.test(p) || /docker-compose/.test(p)) {
    assign(id, 'layer:infrastructure');
    continue;
  }

  // --- Verification: tests + benchmarks (code + fixtures) ---
  if (p.startsWith('tests/') || p.startsWith('benchmarks/')) {
    assign(id, 'layer:verification');
    continue;
  }

  // --- Trading Engine Core: the deterministic Python pipeline under src/ ---
  if (p.startsWith('src/')) {
    assign(id, 'layer:trading-engine');
    continue;
  }

  // --- Data Ingestion: snapshot input adapters ---
  if (p.startsWith('snapshot_sources/')) {
    assign(id, 'layer:data-ingestion');
    continue;
  }

  // --- JARVIS backend / API + tooling (FastAPI, export, sync, hooks, scripts) ---
  if (p.startsWith('jarvis/backend/')) { assign(id, 'layer:jarvis-backend'); continue; }
  if (p === 'jarvis/export_graph_json.py') { assign(id, 'layer:jarvis-backend'); continue; }
  if (p === 'sync_to_neo4j.py') { assign(id, 'layer:jarvis-backend'); continue; }
  if (p.startsWith('jarvis/hooks/')) { assign(id, 'layer:jarvis-backend'); continue; }
  if (/^jarvis\/.*\.ps1$/.test(p)) { assign(id, 'layer:jarvis-backend'); continue; }

  // --- JARVIS frontend / HUD (React + Vite + TS UI) ---
  if (p.startsWith('jarvis/hud/') || p.startsWith('jarvis/frontend/') || p.startsWith('jarvis/sources/')) {
    assign(id, 'layer:jarvis-ui');
    continue;
  }
  // jarvis root config/docs (.env.example, CLAUDE.md, README, roadmaps, docker-compose handled above)
  if (p.startsWith('jarvis/')) {
    if (type === 'config') { assign(id, 'layer:jarvis-backend'); continue; }
    // jarvis markdown docs -> knowledge/docs layer
    assign(id, 'layer:knowledge-docs');
    continue;
  }

  // --- Knowledge & Docs: dev_graph, wiki, raw, root planning markdown ---
  if (p.startsWith('dev_graph/') || p.startsWith('wiki/') || p.startsWith('raw/')) {
    assign(id, 'layer:knowledge-docs');
    continue;
  }

  // --- Root-level files ---
  if (type === 'document') { assign(id, 'layer:knowledge-docs'); continue; }
  if (type === 'config') {
    // .mcp.json, pyproject.toml at root -> project config -> infrastructure (build/tooling)
    assign(id, 'layer:infrastructure');
    continue;
  }

  // Fallback: anything else -> knowledge-docs (should not happen)
  assign(id, 'layer:knowledge-docs');
}

// Build layer objects in dependency order (top -> bottom).
const layerMeta = [
  ['layer:jarvis-ui', 'JARVIS UI Layer',
   'React + TypeScript + Vite HUD frontend (Cytoscape graph views, ops/flow/main panels, hooks, theming) that visualizes the trading system read-only.'],
  ['layer:jarvis-backend', 'JARVIS Backend & Sync Layer',
   'FastAPI/Neo4j read-only backend plus the dev_graph projection tooling (graph export, Neo4j sync, git hooks, launch scripts) serving graph intelligence to the HUD.'],
  ['layer:trading-engine', 'Trading Engine Core',
   'Deterministic Python Layer-3 paper-trading pipeline: snapshot consumer, feature builder, regime classifier, gold decision builder, paper runtime, risk guardrails, supervisor decision engine, and execution.'],
  ['layer:data-ingestion', 'Data Ingestion Layer',
   'Snapshot input adapters and backfill/publisher scripts that source Layer-2 truth data and produce the snapshots the trading engine consumes.'],
  ['layer:verification', 'Verification Layer',
   'pytest suite mirroring the engine modules plus benchmark scenarios and snapshot fixtures that enforce determinism and distribution guarantees.'],
  ['layer:infrastructure', 'Infrastructure & Config',
   'Container definitions (Dockerfile, docker-compose) and root-level project configuration (pyproject.toml, .mcp.json) for building and deploying the system.'],
  ['layer:knowledge-docs', 'Knowledge & Documentation',
   'Markdown corpora and planning artifacts: the dev_graph engineering knowledge graph, the wiki domain corpus, raw research notes, and root-level briefs/audits/ADRs.'],
];

const layers = [];
for (const [lid, name, description] of layerMeta) {
  const nodeIds = [...assigned.entries()].filter(([, v]) => v === lid).map(([k]) => k);
  if (nodeIds.length > 0) layers.push({ id: lid, name, description, nodeIds });
}

// Validation
const total = input.fileNodes.length;
const sum = layers.reduce((a, l) => a + l.nodeIds.length, 0);
const allAssignedIds = new Set([].concat(...layers.map(l => l.nodeIds)));
const missing = input.fileNodes.filter(n => !allAssignedIds.has(n.id)).map(n => n.id);
const inputIds = new Set(input.fileNodes.map(n => n.id));
const invented = [...allAssignedIds].filter(x => !inputIds.has(x));

fs.writeFileSync(OUT, JSON.stringify(layers, null, 2));

console.log('totalFileNodes:', total);
console.log('sumAssigned:', sum);
console.log('layerCount:', layers.length);
console.log('missing:', missing.length, missing.slice(0, 20));
console.log('invented:', invented.length);
console.log('perLayer:');
for (const l of layers) console.log('  ' + l.id + ': ' + l.nodeIds.length);
