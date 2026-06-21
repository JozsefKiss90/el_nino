# `.understand-anything/` — Codebase Knowledge Graph

This folder holds the **Understand-Anything** knowledge graph for `layer3-trading-engine`,
produced by the [`understand-anything`](https://github.com/Egonex-AI/Understand-Anything)
Claude Code plugin (v2.8.0). It powers the interactive architecture dashboard and the
`/understand-*` query commands.

You regenerate it yourself with the plugin's slash commands — you do **not** need anyone to
orchestrate the pipeline by hand.

---

## TL;DR — regenerate the graph

In a Claude Code session **with the working directory at the repo root** (`C:\Code\el_nino`):

```
/understand --full
```

- `/understand` (no flags) = **incremental** update — re-analyzes only files that changed since
  the last build, then recomputes layers + tour. Fast and cheap.
- `/understand --full` = **full rebuild** — re-scans the entire on-disk tree from scratch.

> If your client needs the namespaced form, use `/understand-anything:understand --full`
> (the plugin's commands are namespaced).

When it finishes it writes `knowledge-graph.json`, `meta.json`, and `fingerprints.json` here,
then offers to launch the dashboard.

---

## ⚠️ When you MUST use `--full` instead of incremental

Incremental mode decides what changed via `git diff <last-built-commit>..HEAD --name-only`.
**That only sees committed changes.** It is blind to:

- **untracked files/dirs** (e.g. a brand-new package that hasn't been `git add`ed), and
- **staged-but-uncommitted** files.

So if you've added new code that isn't committed yet, either:

1. `git add` / commit the new work first, **then** run `/understand`, or
2. just run `/understand --full` (scans the on-disk tree directly — always complete).

Rule of thumb: **after adding a whole new subsystem, run `--full`.** For small edits to existing,
committed files, plain `/understand` is enough.

---

## Prerequisites on this machine

| Need | Status here | Notes |
|------|-------------|-------|
| Node.js >= 22 | ✅ v22.14.0 | runs the bundled `.mjs` scripts |
| Python >= 3.10 | ✅ 3.10.x | runs `merge-batch-graphs.py` |
| Plugin core built (`packages/core/dist/`) | ✅ already built | the plugin's own `.mjs` scripts import it |
| `pnpm` | ❌ not installed | only needed to **build the plugin itself**, not to run `/understand` |

If the plugin ever needs rebuilding (e.g. after an update) and `pnpm` is missing, enable it via
corepack instead of installing globally:

```powershell
corepack enable
corepack prepare pnpm@latest --activate
# then, in the plugin root:
#   C:\Users\jozse\.claude\plugins\cache\understand-anything\understand-anything\2.8.0
pnpm install ; pnpm --filter @understand-anything/core build
```

---

## Other useful commands

| Command | What it does |
|---------|--------------|
| `/understand-dashboard` | Launch the interactive web dashboard (graph view, layers, guided tour). |
| `/understand-diff` | Explain what a git diff / PR changed, affected components, and risks. |
| `/understand-explain` | Deep-dive a specific file, function, or module. |
| `/understand-chat` | Ask free-form questions answered from the knowledge graph. |
| `/understand-onboard` | Generate an onboarding guide for new contributors. |
| `/understand-domain` | (Re)build `domain-graph.json` — the business-domain flow graph (separate artifact). |

Useful flags on `/understand`:

- `--full` — force a full rebuild (see above).
- `--review` — run the full LLM graph-reviewer instead of the fast inline validator.
- `--language <code>` — generate summaries/tags/tour in another language (e.g. `--language zh`).
- `--auto-update` / `--no-auto-update` — toggle automatic graph refresh on commit.

---

## What each file here is

| File | Purpose | Safe to delete? |
|------|---------|-----------------|
| `knowledge-graph.json` | **The graph** — nodes, edges, layers, tour. The main artifact. | Regenerable |
| `meta.json` | Last-build commit hash + timestamp + file count. Drives incremental detection. | Regenerable |
| `fingerprints.json` | Per-file structural fingerprints. Lets future commits do cheap incrementals instead of full rebuilds. | Regenerable |
| `config.json` | Plugin settings for this project (currently `outputLanguage: en`). | Keep |
| `.understandignore` | What to exclude from analysis (see below). | Keep |
| `domain-graph.json` | Business-domain flow graph from `/understand-domain` (separate from the main graph). | Regenerable |
| `intermediate/scan-result.json` | Cached file inventory; preserved so incremental runs skip re-scanning. | Regenerable |
| `README.md` | This file. | Keep |

The plugin also creates `intermediate/` and `tmp/` scratch dirs during a run and moves them into a
timestamped `.trash-*/` folder on completion (auto-purged after 7 days). Those are disposable.

---

## Scope: `.understandignore`

This project is configured for **full scope** — all code **and** all documentation/knowledge
corpora are analyzed:

- **Included:** `src/`, `ops/`, `tests/`, `benchmarks/`, `jarvis/`, `scripts/`, `snapshot_sources/`
  AND the markdown corpora `dev_graph/`, `wiki/`, `raw/`, plus root-level `*.md` planning docs.
- **Excluded:** only machine-generated state — `.smart-env/`, `*.ajson`, `.obsidian/`, `.serena/`,
  `.claude/`, `*.env`, and `.understand-anything/` itself (plus built-in defaults like
  `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `*.lock`, images).

Edit `.understandignore` (gitignore syntax) to narrow scope — e.g. uncomment `dev_graph/` and
`wiki/` to analyze code only, which is much faster.

---

## Notes specific to this Windows machine

- The graph build runs many subagents and can take a while on a full rebuild (510 files →
  ~51 analysis batches). Incremental runs are far quicker.
- **Dashboard launch friction:** because `pnpm` isn't installed, `/understand-dashboard` builds the
  viewer via corepack + direct `tsc`/`vite`. A helper script `understand-dashboard.ps1` exists at the
  repo root. If the dashboard won't start, that's where to look (EPERM / ignored-builds workarounds).
- These artifacts are git-tracked in this repo. After regenerating, `git add .understand-anything/`
  to commit the refreshed graph.

---

## Last regeneration (for reference)

- **Project:** `layer3-trading-engine` — autonomous trading engine (Layer 3 / execution)
- **Mode:** full rebuild
- **Files analyzed:** 510 (code 151, docs 327, config 18, markup 6, script 6, infra 2)
- **Graph:** 773 nodes, 1,204 edges, 10 architecture layers, 14-step guided tour
- **Built at commit:** `7124a3a`
- **Date:** 2026-06-19
