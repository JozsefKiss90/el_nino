# Graph Health Dashboard

## Orphan Pages

```dataview
TABLE file.inlinks
FROM "wiki"
WHERE length(file.inlinks) = 0
```

## Weakly Connected Pages

```dataview
TABLE length(file.inlinks) AS Inbound,
       length(file.outlinks) AS Outbound
FROM "wiki"
WHERE length(file.inlinks) < 3
SORT length(file.inlinks) ASC
```

## Recently Updated Notes

```dataview
TABLE file.mtime AS Updated
FROM "wiki"
SORT file.mtime DESC
LIMIT 20
```
