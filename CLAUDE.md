@dev_graph/CLAUDE.md

# el_nino — root memory

The line above imports **`dev_graph/CLAUDE.md`** so it loads at **session start** (not just on-demand
when a `dev_graph/` file is touched). That file is the **authoritative operations manual for all work
under `dev_graph/`** — its ontology, governance, lint, writeback, and Neo4j/MCP rules take precedence
for dev_graph work. Defer to it.

Notes:
- The Mr-Ripley Layer-2 producer is a **separate repository** with its own constitution; it is not
  governed by this file.
- Verify what is loaded with the `/memory` command — both this file and `dev_graph/CLAUDE.md` should
  appear.
