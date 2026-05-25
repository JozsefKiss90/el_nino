---
type: observability
status: active
implementation_status: implemented
canonical: true
created: 2026-05-25
updated: 2026-05-25
confidence: confirmed
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
