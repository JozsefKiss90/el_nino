// Builds the architecture-analyzer input JSON from the assembled graph.
const fs = require('fs');
const path = require('path');

const SRC = 'C:/Code/el_nino/.understand-anything/intermediate/assembled-graph.json';
const OUT = 'C:/Code/el_nino/.understand-anything/tmp/ua-arch-input.json';

const d = JSON.parse(fs.readFileSync(SRC, 'utf8'));

const fileLevelTypes = new Set(['file', 'config', 'document', 'service', 'pipeline', 'table', 'schema', 'resource', 'endpoint']);

const fileNodes = d.nodes
  .filter(n => fileLevelTypes.has(n.type))
  .map(n => ({
    id: n.id,
    type: n.type,
    name: n.name,
    filePath: n.filePath || (n.id.includes(':') ? n.id.split(':').slice(1).join(':') : n.id),
    summary: n.summary || '',
    tags: n.tags || []
  }));

const fileNodeIds = new Set(fileNodes.map(n => n.id));

// importEdges: only imports between file-level nodes
const importEdges = d.edges
  .filter(e => e.type === 'imports' && fileNodeIds.has(e.source) && fileNodeIds.has(e.target))
  .map(e => ({ source: e.source, target: e.target, type: e.type }));

// allEdges: all edges where both endpoints are file-level nodes (excludes sub-file edges)
const allEdges = d.edges
  .filter(e => fileNodeIds.has(e.source) && fileNodeIds.has(e.target))
  .map(e => ({ source: e.source, target: e.target, type: e.type }));

const out = { fileNodes, importEdges, allEdges };
fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
console.log('fileNodes:', fileNodes.length);
console.log('importEdges:', importEdges.length);
console.log('allEdges:', allEdges.length);
