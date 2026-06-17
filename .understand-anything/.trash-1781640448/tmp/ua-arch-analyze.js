#!/usr/bin/env node
'use strict';
// Architecture structural analyzer.
// Usage: node ua-arch-analyze.js <input.json> <output.json>

const fs = require('fs');

function fail(msg) { process.stderr.write(String(msg) + '\n'); process.exit(1); }

const inPath = process.argv[2];
const outPath = process.argv[3];
if (!inPath || !outPath) fail('Usage: node ua-arch-analyze.js <input.json> <output.json>');

let input;
try { input = JSON.parse(fs.readFileSync(inPath, 'utf8')); }
catch (e) { fail('Failed to read/parse input: ' + e.message); }

const fileNodes = input.fileNodes || [];
const importEdges = input.importEdges || [];
const allEdges = input.allEdges || [];

const norm = p => String(p || '').replace(/\\/g, '/');
const byId = new Map();
for (const n of fileNodes) byId.set(n.id, n);

// ---------- A. Directory grouping ----------
const paths = fileNodes.map(n => norm(n.filePath || n.id));

// common path prefix (directory-segment based)
function commonPrefixSegments(list) {
  if (list.length === 0) return '';
  const split = list.map(p => p.split('/'));
  // only consider paths that have at least one dir
  let prefix = split[0].slice(0, -1); // dirs of first
  for (const segs of split) {
    const dirs = segs.slice(0, -1);
    let i = 0;
    while (i < prefix.length && i < dirs.length && prefix[i] === dirs[i]) i++;
    prefix = prefix.slice(0, i);
    if (prefix.length === 0) break;
  }
  return prefix.join('/');
}
const commonPrefix = commonPrefixSegments(paths);

function topGroup(p) {
  let rel = p;
  if (commonPrefix && rel.startsWith(commonPrefix + '/')) rel = rel.slice(commonPrefix.length + 1);
  const segs = rel.split('/');
  if (segs.length > 1) return segs[0];
  return '(root)';
}

const directoryGroups = {};
const nodeGroupMap = new Map(); // id -> group
for (const n of fileNodes) {
  const g = topGroup(norm(n.filePath || n.id));
  (directoryGroups[g] = directoryGroups[g] || []).push(n.id);
  nodeGroupMap.set(n.id, g);
}

// ---------- B. Node type grouping ----------
const nodeTypeGroups = {};
for (const n of fileNodes) {
  (nodeTypeGroups[n.type] = nodeTypeGroups[n.type] || []).push(n.id);
}

// ---------- C. Import adjacency / fan-in / fan-out ----------
const fileFanIn = {};
const fileFanOut = {};
for (const n of fileNodes) { fileFanIn[n.id] = 0; fileFanOut[n.id] = 0; }
for (const e of importEdges) {
  if (fileFanOut[e.source] !== undefined) fileFanOut[e.source]++;
  if (fileFanIn[e.target] !== undefined) fileFanIn[e.target]++;
}

// ---------- D. Cross-category dependency analysis ----------
const crossCatMap = new Map(); // key fromType|toType|edgeType -> count
for (const e of allEdges) {
  const s = byId.get(e.source), t = byId.get(e.target);
  if (!s || !t) continue;
  if (s.type === t.type && s.type === 'file') continue; // skip pure file->file here (covered elsewhere)
  if (s.type === 'file' && t.type === 'file') continue;
  const key = s.type + '|' + t.type + '|' + e.type;
  crossCatMap.set(key, (crossCatMap.get(key) || 0) + 1);
}
const crossCategoryEdges = [...crossCatMap.entries()].map(([k, count]) => {
  const [fromType, toType, edgeType] = k.split('|');
  return { fromType, toType, edgeType, count };
}).sort((a, b) => b.count - a.count);

// ---------- E. Inter-group import frequency ----------
const interMap = new Map(); // from|to -> count
for (const e of importEdges) {
  const gs = nodeGroupMap.get(e.source);
  const gt = nodeGroupMap.get(e.target);
  if (gs === undefined || gt === undefined) continue;
  if (gs === gt) continue;
  const key = gs + '|' + gt;
  interMap.set(key, (interMap.get(key) || 0) + 1);
}
const interGroupImports = [...interMap.entries()].map(([k, count]) => {
  const [from, to] = k.split('|');
  return { from, to, count };
}).sort((a, b) => b.count - a.count);

// ---------- F. Intra-group import density ----------
const intraGroupDensity = {};
const groupTotalEdges = {}; // edges touching a group (import edges)
const groupInternalEdges = {};
for (const g of Object.keys(directoryGroups)) { groupTotalEdges[g] = 0; groupInternalEdges[g] = 0; }
for (const e of importEdges) {
  const gs = nodeGroupMap.get(e.source);
  const gt = nodeGroupMap.get(e.target);
  if (gs !== undefined) groupTotalEdges[gs]++;
  if (gt !== undefined && gt !== gs) groupTotalEdges[gt]++;
  if (gs !== undefined && gs === gt) groupInternalEdges[gs]++;
}
for (const g of Object.keys(directoryGroups)) {
  const total = groupTotalEdges[g];
  const internal = groupInternalEdges[g];
  intraGroupDensity[g] = {
    internalEdges: internal,
    totalEdges: total,
    density: total > 0 ? +(internal / total).toFixed(3) : 0
  };
}

// ---------- G. Directory & file pattern matching ----------
const dirPatterns = [
  [['routes', 'api', 'controllers', 'endpoints', 'handlers'], 'api'],
  [['services', 'core', 'lib', 'domain', 'logic'], 'service'],
  [['models', 'db', 'data', 'persistence', 'repository', 'entities'], 'data'],
  [['components', 'views', 'pages', 'ui', 'layouts', 'screens'], 'ui'],
  [['middleware', 'plugins', 'interceptors', 'guards'], 'middleware'],
  [['utils', 'helpers', 'common', 'shared', 'tools'], 'utility'],
  [['config', 'constants', 'env', 'settings'], 'config'],
  [['__tests__', 'test', 'tests', 'spec', 'specs'], 'test'],
  [['types', 'interfaces', 'schemas', 'contracts', 'dtos'], 'types'],
  [['hooks'], 'hooks'],
  [['store', 'state', 'reducers', 'actions', 'slices'], 'state'],
  [['assets', 'static', 'public'], 'assets'],
  [['migrations'], 'data'],
  [['management', 'commands'], 'config'],
  [['templatetags'], 'utility'],
  [['signals'], 'service'],
  [['serializers'], 'api'],
  [['cmd'], 'entry'],
  [['internal'], 'service'],
  [['pkg'], 'utility'],
  [['dto', 'request', 'response'], 'types'],
  [['entity'], 'data'],
  [['controller'], 'api'],
  [['routers'], 'api'],
  [['composables'], 'service'],
  [['blueprints'], 'api'],
  [['mailers', 'jobs', 'channels'], 'service'],
  [['bin'], 'entry'],
  [['docs', 'documentation', 'wiki'], 'documentation'],
  [['deploy', 'deployment', 'infra', 'infrastructure'], 'infrastructure'],
  [['.github', '.gitlab', '.circleci'], 'ci-cd'],
  [['k8s', 'kubernetes', 'helm', 'charts'], 'infrastructure'],
  [['terraform', 'tf'], 'infrastructure'],
  [['docker'], 'infrastructure'],
  [['sql', 'database', 'schema'], 'data'],
  [['benchmarks', 'benchmark'], 'test'],
  [['dev_graph'], 'documentation'],
  [['raw'], 'documentation'],
];
const dirLabel = {};
for (const [names, label] of dirPatterns) for (const nm of names) dirLabel[nm] = label;

function fileLevelPattern(p, name) {
  const b = name || p.split('/').pop();
  if (/\.(test|spec)\.[^/]+$/.test(b) || /^test_.+\.py$/.test(b) || /_test\.go$/.test(b) || /Test\.java$/.test(b) || /_spec\.rb$/.test(b) || /Test\.php$/.test(b) || /Tests\.cs$/.test(b)) return 'test';
  if (/\.d\.ts$/.test(b)) return 'types';
  if (b === 'manage.py') return 'entry';
  if (b === 'wsgi.py' || b === 'asgi.py') return 'config';
  if (b === 'main.go' && /(^|\/)cmd\/[^/]+\/main\.go$/.test(p)) return 'entry';
  if ((b === 'main.rs' || b === 'lib.rs') && /(^|\/)src\/(main|lib)\.rs$/.test(p)) return 'entry';
  if (b === 'Application.java' || b === 'Program.cs') return 'entry';
  if (b === 'config.ru') return 'entry';
  if (['Cargo.toml', 'go.mod', 'Gemfile', 'pom.xml', 'build.gradle', 'composer.json', 'pyproject.toml'].includes(b)) return 'config';
  if (b === 'Dockerfile' || /^docker-compose\..*\.(yml|yaml)$/.test(b) || /^docker-compose\.(yml|yaml)$/.test(b)) return 'infrastructure';
  if (/\.(tf|tfvars)$/.test(b)) return 'infrastructure';
  if (/(^|\/)\.github\/workflows\//.test(p) || b === '.gitlab-ci.yml' || b === 'Jenkinsfile') return 'ci-cd';
  if (/\.sql$/.test(b)) return 'data';
  if (/\.(graphql|gql|proto)$/.test(b)) return 'types';
  if (/\.(md|rst)$/.test(b)) return 'documentation';
  if (b === 'Makefile') return 'infrastructure';
  if (b === 'index.ts' || b === 'index.js' || b === '__init__.py') return 'entry';
  return null;
}

const patternMatches = {};
for (const g of Object.keys(directoryGroups)) {
  if (dirLabel[g]) patternMatches[g] = dirLabel[g];
}

// Per-file pattern matches (for nuanced assignment of root files etc.)
const filePatternMatches = {};
for (const n of fileNodes) {
  const p = norm(n.filePath || n.id);
  const fp = fileLevelPattern(p, n.name);
  if (fp) filePatternMatches[n.id] = fp;
}

// ---------- H. Deployment topology ----------
const infraFiles = [];
let hasDockerfile = false, hasCompose = false, hasK8s = false, hasTerraform = false, hasCI = false;
for (const n of fileNodes) {
  const p = norm(n.filePath || n.id);
  const b = n.name || p.split('/').pop();
  if (b === 'Dockerfile' || /Dockerfile/.test(b)) { hasDockerfile = true; infraFiles.push(p); }
  else if (/docker-compose/.test(b)) { hasCompose = true; infraFiles.push(p); }
  else if (/\.(tf|tfvars)$/.test(b)) { hasTerraform = true; infraFiles.push(p); }
  else if (/(^|\/)(k8s|kubernetes|helm|charts)\//.test(p)) { hasK8s = true; infraFiles.push(p); }
  else if (/(^|\/)\.github\/workflows\//.test(p) || b === '.gitlab-ci.yml' || b === 'Jenkinsfile') { hasCI = true; infraFiles.push(p); }
}
const deploymentTopology = { hasDockerfile, hasCompose, hasK8s, hasTerraform, hasCI, infraFiles };

// ---------- I. Data pipeline detection ----------
const schemaFiles = [], migrationFiles = [], dataModelFiles = [], apiHandlerFiles = [];
for (const n of fileNodes) {
  const p = norm(n.filePath || n.id);
  const b = (n.name || '').toLowerCase();
  const tags = (n.tags || []).map(t => String(t).toLowerCase());
  if (/\.(sql|graphql|gql|proto|prisma)$/.test(b) || /schema/.test(b)) schemaFiles.push(p);
  if (/(^|\/)migrations\//.test(p)) migrationFiles.push(p);
  if (/(^|\/)(models|entities|entity)(\/|$)/.test(p) || tags.includes('model') || tags.includes('data-model')) dataModelFiles.push(p);
  if (tags.includes('api-handler') || tags.includes('endpoint') || /(^|\/)(routes|api|controllers|endpoints|handlers)(\/|$)/.test(p)) apiHandlerFiles.push(p);
}
const dataPipeline = { schemaFiles, migrationFiles, dataModelFiles, apiHandlerFiles };

// ---------- J. Documentation coverage ----------
const docNodes = fileNodes.filter(n => n.type === 'document' || /\.(md|rst)$/.test(norm(n.filePath || n.id)));
const groupsWithDocsSet = new Set();
for (const n of docNodes) groupsWithDocsSet.add(nodeGroupMap.get(n.id));
// Also: groups that themselves contain a README
const groupHasReadme = new Set();
for (const n of fileNodes) {
  if (/readme\.md$/i.test(norm(n.filePath || n.id))) groupHasReadme.add(nodeGroupMap.get(n.id));
}
const allGroupKeys = Object.keys(directoryGroups);
const groupsWithDocs = new Set([...groupsWithDocsSet, ...groupHasReadme]);
const undocumentedGroups = allGroupKeys.filter(g => !groupsWithDocs.has(g));
const docCoverage = {
  groupsWithDocs: groupsWithDocs.size,
  totalGroups: allGroupKeys.length,
  coverageRatio: allGroupKeys.length ? +(groupsWithDocs.size / allGroupKeys.length).toFixed(3) : 0,
  undocumentedGroups
};

// ---------- K. Dependency direction ----------
const pairDir = new Map(); // unordered pair -> {a, b, ab, ba}
for (const { from, to, count } of interGroupImports) {
  const key = [from, to].sort().join('||');
  let rec = pairDir.get(key);
  if (!rec) { const [a, b] = [from, to].sort(); rec = { a, b, ab: 0, ba: 0 }; pairDir.set(key, rec); }
  if (from === rec.a && to === rec.b) rec.ab += count; else rec.ba += count;
}
const dependencyDirection = [];
for (const rec of pairDir.values()) {
  if (rec.ab === rec.ba) continue;
  if (rec.ab > rec.ba) dependencyDirection.push({ dependent: rec.a, dependsOn: rec.b });
  else dependencyDirection.push({ dependent: rec.b, dependsOn: rec.a });
}

// ---------- fileStats ----------
const filesPerGroup = {};
for (const g of Object.keys(directoryGroups)) filesPerGroup[g] = directoryGroups[g].length;
const nodeTypeCounts = {};
for (const t of Object.keys(nodeTypeGroups)) nodeTypeCounts[t] = nodeTypeGroups[t].length;

const out = {
  scriptCompleted: true,
  commonPrefix,
  directoryGroups,
  nodeTypeGroups,
  crossCategoryEdges,
  interGroupImports,
  intraGroupDensity,
  patternMatches,
  filePatternMatches,
  deploymentTopology,
  dataPipeline,
  docCoverage,
  dependencyDirection,
  fileStats: {
    totalFileNodes: fileNodes.length,
    filesPerGroup,
    nodeTypeCounts
  },
  fileFanIn,
  fileFanOut
};

try { fs.writeFileSync(outPath, JSON.stringify(out, null, 2)); }
catch (e) { fail('Failed to write output: ' + e.message); }
process.stderr.write('Analysis complete: ' + fileNodes.length + ' file nodes, ' + Object.keys(directoryGroups).length + ' groups\n');
process.exit(0);
