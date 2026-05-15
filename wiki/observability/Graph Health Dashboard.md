---
type: observability
domain: observability
created: 2026-05-15
updated: 2026-05-15
status: active
aliases: [Dashboard, Graph Dashboard]
confidence: inferred
tags: []
---

# Graph Health Dashboard

## Metadata Coverage

```dataview
TABLE type, domain, status, updated
FROM "wiki"
WHERE type != null
SORT updated DESC
```

## Pages Missing Frontmatter

```dataview
LIST
FROM "wiki"
WHERE type = null
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```

## Confidence Distribution

```dataview
TABLE length(rows) AS Count
FROM "wiki"
WHERE confidence != null
GROUP BY confidence
```

## Orphan Pages

```dataview
TABLE file.inlinks
FROM "wiki"
WHERE length(file.inlinks) = 0
AND file.name != "index" AND file.name != "log" AND file.name != "CLAUDE"
```

## Weakly Connected Pages

```dataview
TABLE length(file.inlinks) AS Inbound,
       length(file.outlinks) AS Outbound,
       domain
FROM "wiki"
WHERE type != null AND (length(file.inlinks) < 3 OR length(file.outlinks) < 3)
SORT length(file.inlinks) ASC
```

## Stale Pages (>30 days without update)

```dataview
TABLE updated, status, domain
FROM "wiki"
WHERE type != null AND updated != null
AND date(updated) < date(today) - dur(30 days)
AND status = "active"
SORT updated ASC
```

## Ontology Overview (Domain Distribution)

```dataview
TABLE length(rows) AS "Page Count"
FROM "wiki"
WHERE type != null
GROUP BY domain
SORT length(rows) DESC
```

## Type Distribution

```dataview
TABLE length(rows) AS Count
FROM "wiki"
WHERE type != null
GROUP BY type
SORT length(rows) DESC
```

## Stub Tracking

```dataview
TABLE domain, updated
FROM "wiki"
WHERE status = "stub"
SORT domain ASC
```

## Source Coverage

```dataview
TABLE source_file, source_type, date_ingested
FROM "wiki/sources"
WHERE type = "source"
SORT date_ingested DESC
```

## Source Provenance (pages citing each source)

```dataview
TABLE length(file.inlinks) AS "Cited By"
FROM "wiki/sources"
WHERE type = "source"
SORT length(file.inlinks) DESC
```

## Contradiction Registry

```dataview
LIST
FROM "wiki"
WHERE contains(tags, "contradiction")
```

## Recently Updated Notes

```dataview
TABLE file.mtime AS "File Modified", updated AS "Content Updated", type
FROM "wiki"
SORT file.mtime DESC
LIMIT 15
```

## Ingestion Timeline

```dataview
TABLE source_type, date_ingested, status
FROM "wiki/sources"
WHERE type = "source"
SORT date_ingested ASC
```
