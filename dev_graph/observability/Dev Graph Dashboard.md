---
type: observability
canonical_id: OBS-001
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-06-06
confidence: confirmed
evidence:
  - design
source_paths:
  - "wiki/observability/Graph Health Dashboard.md"
related_files: []
related_tests: []
related_constraints:
  - "[[Frontmatter Required]]"
related_decisions:
  - "[[ADR - Dev Graph Bootstrap]]"
---

# Dev Graph Dashboard

Dataview queries for dev_graph health monitoring. Adapted from `wiki/observability/Graph Health Dashboard.md` patterns.

---

## 1. Node Inventory

```dataview
TABLE type, status, implementation_status, confidence, updated
FROM "dev_graph"
WHERE type != null
SORT updated DESC
```

## 2. Nodes Missing Frontmatter

```dataview
LIST
FROM "dev_graph"
WHERE type = null
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE" AND file.name != "README"
```

## 3. Type Distribution

```dataview
TABLE length(rows) AS Count
FROM "dev_graph"
WHERE type != null
GROUP BY type
SORT length(rows) DESC
```

## 4. Implementation Status Distribution

```dataview
TABLE length(rows) AS Count
FROM "dev_graph"
WHERE implementation_status != null
GROUP BY implementation_status
SORT length(rows) DESC
```

## 5. Confidence Distribution

```dataview
TABLE length(rows) AS Count
FROM "dev_graph"
WHERE confidence != null
GROUP BY confidence
SORT length(rows) DESC
```

## 6. Stale Nodes (>30 days without update)

```dataview
TABLE updated, status, type, implementation_status
FROM "dev_graph"
WHERE type != null AND updated != null
AND date(updated) < date(today) - dur(30 days)
AND status != "deprecated"
SORT updated ASC
```

## 7. Orphan Nodes (0 inbound links)

```dataview
TABLE type, status
FROM "dev_graph"
WHERE type != null
AND length(file.inlinks) = 0
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE" AND file.name != "README"
SORT type ASC
```

## 8. Constraint Coverage (nodes without related_constraints)

```dataview
TABLE type, status
FROM "dev_graph"
WHERE type != null
AND type != "constraint" AND type != "governance" AND type != "observability" AND type != "reference"
AND (related_constraints = null OR length(related_constraints) = 0)
SORT type ASC
```

## 9. Test Coverage (modules/files without related_tests)

```dataview
TABLE implementation_status, confidence
FROM "dev_graph"
WHERE (type = "module" OR type = "file")
AND (related_tests = null OR length(related_tests) = 0)
SORT type ASC
```

## 10. API Doc Freshness

```dataview
TABLE provider, doc_scope, freshness_requirement
FROM "dev_graph/api_docs"
WHERE type = "api_doc_source"
SORT provider ASC
```

## 11. Blocked Nodes

```dataview
TABLE type, implementation_status, updated
FROM "dev_graph"
WHERE status = "blocked" OR implementation_status = "blocked"
SORT updated ASC
```

## 12. Deprecated Decisions

```dataview
TABLE decision_status, decision_date, superseded_by
FROM "dev_graph/decisions"
WHERE type = "decision_record"
AND (decision_status = "superseded" OR decision_status = "deprecated")
SORT decision_date DESC
```

## 13. Canonical ID Coverage

```dataview
TABLE type, canonical_id
FROM "dev_graph"
WHERE type != null AND (canonical_id = null OR canonical_id = "")
```

## 14. Evidence Coverage

```dataview
TABLE type, evidence
FROM "dev_graph"
WHERE type != null AND (evidence = null OR length(evidence) = 0)
SORT type ASC
```

## 15. Pattern Realization Coverage

```dataview
TABLE type, file.name
FROM "dev_graph"
WHERE (type = "module" OR type = "capability")
AND NOT contains(file.content, "### Realizes")
```

## 16. Traceability Gaps (Capabilities without Justified By)

```dataview
TABLE file.name, type
FROM "dev_graph"
WHERE type = "capability"
AND NOT contains(file.content, "### Justified By")
```

## 17. Population Progress

```dataview
TABLE length(rows) AS Count
FROM "dev_graph"
WHERE type != null
GROUP BY type
SORT length(rows) DESC
```

## 18. Population Debt: Systems Without Capabilities

```dataview
TABLE file.name
FROM "dev_graph"
WHERE type = "system"
AND (contains_capabilities = null OR length(contains_capabilities) = 0)
```

## 19. Population Debt: Capabilities Without Modules

```dataview
TABLE file.name, parent_system
FROM "dev_graph"
WHERE type = "capability"
AND (implemented_by = null OR length(implemented_by) = 0)
AND implementation_status != "not-started"
```

## 20. Population Debt: Modules Without Files

```dataview
TABLE file.name
FROM "dev_graph"
WHERE type = "module"
AND (related_files = null OR length(related_files) = 0)
AND implementation_status = "implemented"
```

## 21. Population Debt: Modules Without Tests

```dataview
TABLE implementation_status, related_tests
FROM "dev_graph"
WHERE type = "module"
AND (related_tests = null OR length(related_tests) = 0)
AND implementation_status != "not-started"
SORT file.name ASC
```

---

## Known Distinct Pairs

Pages flagged as potential semantic duplicates but confirmed as legitimately distinct. This list prevents recurring false positives during duplicate detection scans.

<!-- Add entries as: - [[Page A]] / [[Page B]] — reason for distinction -->

## Relationships

### Depends On
- [[REF - Wiki Graph Health Dashboard]]
- [[Frontmatter Required]]

### Provides
- Observability for all dev_graph nodes

### Validated By

### Constrained By

### Supersedes

### Used By
- Per-session lint workflows
- Weekly maintenance workflows
- Monthly audit workflows

### Produces
- Health metrics for dev_graph

### Consumes
- Frontmatter from all dev_graph nodes
