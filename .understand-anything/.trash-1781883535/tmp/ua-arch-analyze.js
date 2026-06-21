#!/usr/bin/env node
'use strict';

function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];
  if (!inputPath || !outputPath) {
    console.error('Usage: node ua-arch-analyze.js <input.json> <output.json>');
    process.exit(1);
  }
  const fs = require('fs');
  const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const fileNodes = input.fileNodes || [];
  const importEdges = input.importEdges || [];
  const allEdges = input.allEdges || [];

  const idToNode = new Map();
  for (const n of fileNodes) idToNode.set(n.id, n);

  // ---- Common prefix of all file paths ----
  const paths = fileNodes.map((n) => (n.filePath || '').split('/'));
  function commonPrefixSegments(arr) {
    if (arr.length === 0) return [];
    let prefix = arr[0].slice(0, -1); // drop filename
    for (const segs of arr) {
      const dir = segs.slice(0, -1);
      let i = 0;
      while (i < prefix.length && i < dir.length && prefix[i] === dir[i]) i++;
      prefix = prefix.slice(0, i);
      if (prefix.length === 0) break;
    }
    return prefix;
  }
  const prefix = commonPrefixSegments(paths);
  const prefixLen = prefix.length;

  // ---- A. Directory Grouping ----
  const directoryGroups = {};
  function groupOf(filePath) {
    const segs = (filePath || '').split('/');
    const after = segs.slice(prefixLen);
    if (after.length <= 1) return '(root)';
    return after[0];
  }
  for (const n of fileNodes) {
    const g = groupOf(n.filePath);
    (directoryGroups[g] = directoryGroups[g] || []).push(n.id);
  }

  // ---- B. Node Type Grouping ----
  const nodeTypeGroups = {};
  for (const n of fileNodes) {
    (nodeTypeGroups[n.type] = nodeTypeGroups[n.type] || []).push(n.id);
  }

  // ---- C. Import Adjacency: fan-in / fan-out ----
  const fileFanOut = {};
  const fileFanIn = {};
  for (const n of fileNodes) { fileFanOut[n.id] = 0; fileFanIn[n.id] = 0; }
  for (const e of importEdges) {
    if (fileFanOut[e.source] !== undefined) fileFanOut[e.source]++;
    if (fileFanIn[e.target] !== undefined) fileFanIn[e.target]++;
  }

  // group membership lookup
  const idToGroup = new Map();
  for (const [g, ids] of Object.entries(directoryGroups)) for (const id of ids) idToGroup.set(id, g);

  // ---- D. Cross-Category (allEdges between node types) ----
  const idToType = new Map();
  for (const n of fileNodes) idToType.set(n.id, n.type);
  const crossMap = {}; // key fromType|toType|edgeType
  for (const e of allEdges) {
    const ft = idToType.get(e.source);
    const tt = idToType.get(e.target);
    if (!ft || !tt) continue;
    if (ft === tt) continue; // cross-category only
    const k = ft + '|' + tt + '|' + (e.type || 'unknown');
    crossMap[k] = (crossMap[k] || 0) + 1;
  }
  const crossCategoryEdges = Object.entries(crossMap).map(([k, count]) => {
    const [fromType, toType, edgeType] = k.split('|');
    return { fromType, toType, edgeType, count };
  }).sort((a, b) => b.count - a.count);

  // ---- E. Inter-Group Import Frequency (imports only) ----
  const interMap = {};
  for (const e of importEdges) {
    const fg = idToGroup.get(e.source);
    const tg = idToGroup.get(e.target);
    if (!fg || !tg || fg === tg) continue;
    const k = fg + '|' + tg;
    interMap[k] = (interMap[k] || 0) + 1;
  }
  const interGroupImports = Object.entries(interMap).map(([k, count]) => {
    const [from, to] = k.split('|');
    return { from, to, count };
  }).sort((a, b) => b.count - a.count);

  // ---- F. Intra-Group Import Density ----
  const intraGroupDensity = {};
  const groupInternal = {};
  const groupTotal = {};
  for (const g of Object.keys(directoryGroups)) { groupInternal[g] = 0; groupTotal[g] = 0; }
  for (const e of importEdges) {
    const fg = idToGroup.get(e.source);
    const tg = idToGroup.get(e.target);
    if (fg) groupTotal[fg]++;
    if (tg && tg !== fg) groupTotal[tg]++;
    if (fg && tg && fg === tg) { groupInternal[fg]++; }
  }
  for (const g of Object.keys(directoryGroups)) {
    const total = groupTotal[g] || 0;
    const internal = groupInternal[g] || 0;
    intraGroupDensity[g] = {
      internalEdges: internal,
      totalEdges: total,
      density: total > 0 ? +(internal / total).toFixed(3) : 0,
    };
  }

  // ---- G. Directory Pattern Matching ----
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
  ];
  const dirPatternMap = new Map();
  for (const [names, label] of dirPatterns) for (const nm of names) if (!dirPatternMap.has(nm)) dirPatternMap.set(nm, label);

  const patternMatches = {};
  for (const g of Object.keys(directoryGroups)) {
    const lower = g.toLowerCase();
    if (dirPatternMap.has(lower)) patternMatches[g] = dirPatternMap.get(lower);
  }

  // file-level pattern helpers
  function fileLevelPattern(n) {
    const fp = (n.filePath || '');
    const base = fp.split('/').pop();
    if (/(\.test\.|\.spec\.)/.test(base)) return 'test';
    if (/^test_.*\.py$/.test(base)) return 'test';
    if (/_test\.go$/.test(base)) return 'test';
    if (/Test\.java$/.test(base)) return 'test';
    if (/_spec\.rb$/.test(base)) return 'test';
    if (/Test\.php$/.test(base)) return 'test';
    if (/Tests\.cs$/.test(base)) return 'test';
    if (/\.d\.ts$/.test(base)) return 'types';
    if (/\.(graphql|gql|proto)$/.test(base)) return 'types';
    if (/\.sql$/.test(base)) return 'data';
    if (/\.(md|rst)$/.test(base)) return 'documentation';
    if (base === 'Dockerfile' || /^docker-compose/.test(base)) return 'infrastructure';
    if (/\.(tf|tfvars)$/.test(base)) return 'infrastructure';
    if (base === 'Makefile') return 'infrastructure';
    if (base === 'Jenkinsfile' || base === '.gitlab-ci.yml') return 'ci-cd';
    if (/^\.github\/workflows\//.test(fp)) return 'ci-cd';
    return null;
  }

  // ---- H. Deployment Topology ----
  const infraFiles = [];
  let hasDockerfile = false, hasCompose = false, hasK8s = false, hasTerraform = false, hasCI = false;
  for (const n of fileNodes) {
    const fp = n.filePath || '';
    const base = fp.split('/').pop();
    if (base === 'Dockerfile' || /^Dockerfile\./.test(base)) { hasDockerfile = true; infraFiles.push(fp); }
    else if (/^docker-compose.*\.(ya?ml)$/.test(base) || /^docker-compose/.test(base)) { hasCompose = true; infraFiles.push(fp); }
    else if (/\.(tf|tfvars)$/.test(base)) { hasTerraform = true; infraFiles.push(fp); }
    else if (/(^|\/)(k8s|kubernetes|helm|charts)(\/|$)/.test(fp)) { hasK8s = true; infraFiles.push(fp); }
    else if (/(^|\/)\.github\/workflows\//.test(fp) || base === '.gitlab-ci.yml' || base === 'Jenkinsfile') { hasCI = true; infraFiles.push(fp); }
  }
  const deploymentTopology = { hasDockerfile, hasCompose, hasK8s, hasTerraform, hasCI, infraFiles };

  // ---- I. Data Pipeline ----
  const schemaFiles = [], migrationFiles = [], dataModelFiles = [], apiHandlerFiles = [];
  for (const n of fileNodes) {
    const fp = n.filePath || '';
    const base = fp.split('/').pop();
    const tags = (n.tags || []).map((t) => String(t).toLowerCase());
    if (/\.(sql|graphql|gql|proto|prisma)$/.test(base)) schemaFiles.push(fp);
    if (/migrations?\//.test(fp)) migrationFiles.push(fp);
    if (/(^|\/)(models|entities|entity)(\/|$)/.test(fp) || tags.includes('model') || tags.includes('orm')) dataModelFiles.push(fp);
    if (tags.includes('api-handler') || tags.includes('endpoint') || tags.includes('route') || /(^|\/)(routes|api|controllers|endpoints|handlers)(\/|$)/.test(fp)) apiHandlerFiles.push(fp);
  }
  const dataPipeline = { schemaFiles, migrationFiles, dataModelFiles, apiHandlerFiles };

  // ---- J. Documentation Coverage ----
  const groupsWithDocs = {};
  for (const n of fileNodes) {
    if (n.type === 'document' || /\.(md|rst)$/.test((n.filePath || ''))) {
      const g = idToGroup.get(n.id);
      if (g) groupsWithDocs[g] = true;
    }
  }
  const allGroups = Object.keys(directoryGroups);
  const undocumentedGroups = allGroups.filter((g) => !groupsWithDocs[g]);
  const docCoverage = {
    groupsWithDocs: Object.keys(groupsWithDocs).length,
    totalGroups: allGroups.length,
    coverageRatio: allGroups.length ? +(Object.keys(groupsWithDocs).length / allGroups.length).toFixed(3) : 0,
    undocumentedGroups,
  };

  // ---- K. Dependency Direction ----
  const pairNet = {};
  for (const { from, to, count } of interGroupImports) {
    const key = [from, to].sort().join('|');
    pairNet[key] = pairNet[key] || {};
    pairNet[key][from + '>' + to] = count;
  }
  const dependencyDirection = [];
  const seenPairs = new Set();
  for (const { from, to } of interGroupImports) {
    const key = [from, to].sort().join('|');
    if (seenPairs.has(key)) continue;
    seenPairs.add(key);
    const ab = interMap[from + '|' + to] || 0;
    const ba = interMap[to + '|' + from] || 0;
    if (ab >= ba) dependencyDirection.push({ dependent: from, dependsOn: to });
    else dependencyDirection.push({ dependent: to, dependsOn: from });
  }

  // ---- File stats ----
  const filesPerGroup = {};
  for (const [g, ids] of Object.entries(directoryGroups)) filesPerGroup[g] = ids.length;
  const nodeTypeCounts = {};
  for (const [t, ids] of Object.entries(nodeTypeGroups)) nodeTypeCounts[t] = ids.length;

  // file-level pattern matches (collect)
  const fileLevelPatterns = {};
  for (const n of fileNodes) {
    const p = fileLevelPattern(n);
    if (p) fileLevelPatterns[n.id] = p;
  }

  const result = {
    scriptCompleted: true,
    commonPrefix: prefix.join('/'),
    directoryGroups,
    nodeTypeGroups,
    crossCategoryEdges,
    interGroupImports,
    intraGroupDensity,
    patternMatches,
    fileLevelPatterns,
    deploymentTopology,
    dataPipeline,
    docCoverage,
    dependencyDirection,
    fileStats: {
      totalFileNodes: fileNodes.length,
      filesPerGroup,
      nodeTypeCounts,
    },
    fileFanIn,
    fileFanOut,
  };

  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.error('OK: ' + fileNodes.length + ' file nodes, ' + Object.keys(directoryGroups).length + ' groups');
}

try { main(); process.exit(0); }
catch (err) { console.error('FATAL: ' + (err && err.stack ? err.stack : err)); process.exit(1); }
