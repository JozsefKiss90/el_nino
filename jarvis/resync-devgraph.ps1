# resync-devgraph.ps1 - re-project the dev_graph into EVERY downstream consumer, atomically.
#
# The dev_graph markdown is canonical; Neo4j and the two graph.json copies are rebuildable
# projections of it (ADR-010 §4, PROJECTION_SYNC_PLAN.md Rec 2). Run this after ANY change to
# dev_graph/** so the projections can never half-run onto different versions of the markdown.
# This is the single command behind dev_graph/CLAUDE.md writeback step 10.
#
# Steps (fail-fast - any failure aborts the whole run):
#   1. sync_to_neo4j.py --dry-run   validate the parse offline (no DB needed)
#   2. sync_to_neo4j.py --clear     re-project Neo4j
#   3. export_graph_json.py         re-write BOTH graph.json copies (frontend + hud/public)
#
#   Usage:   powershell -ExecutionPolicy Bypass -File C:\Code\el_nino\jarvis\resync-devgraph.ps1
#   Skip Neo4j (offline; graph.json only):  ... resync-devgraph.ps1 -NoNeo4j
#
# It does NOT rebuild the served HUD bundle - run `cd jarvis\hud; npm run build` if you need
# hud/dist/graph.json refreshed for the single-URL server.
#
# Note on exit codes: sync_to_neo4j.py returns 1 whenever ANY edge is skipped (the 5
# known-unresolvable edges are the normal steady state), so its exit code can't tell "completed
# with skips" from "crashed". We instead key success off the "--- Summary ---" marker it prints
# only on a full run - a parse error or a Neo4j-down failure aborts before that line.

param(
  [switch]$NoNeo4j  # regenerate graph.json only; don't touch Neo4j (useful with no DB up)
)

$ErrorActionPreference = "Stop"
$repo   = Split-Path -Parent $PSScriptRoot          # C:\Code\el_nino
$venvPy = Join-Path $repo ".venv\Scripts\python.exe"
$py     = if (Test-Path $venvPy) { $venvPy } else { "python" }
$sync   = Join-Path $repo "sync_to_neo4j.py"
$export = Join-Path $repo "jarvis\export_graph_json.py"

# Run a sync_to_neo4j.py step. Captures stdout (where "--- Summary ---" lives); stderr flows to the
# console unredirected (so a Python traceback is visible AND so we dodge the PS 5.1 native-stderr
# ErrorRecord quirk). Success = the Summary marker printed; otherwise the run aborted - throw.
function Invoke-SyncStep([string]$label, [string[]]$syncArgs) {
  Write-Host $label -ForegroundColor Cyan
  $out = (& $py $sync @syncArgs | Out-String)
  if ($out -notmatch '---\s*Summary\s*---') {
    Write-Host $out
    throw "$label FAILED - sync did not reach the summary (parse error or Neo4j unreachable; see output above)."
  }
  # Echo only the tail (the summary) - the per-node/edge dump is large and uninteresting on success.
  ($out -split "`r?`n" | Select-Object -Last 14) -join "`n" | Write-Host
}

# Run export_graph_json.py - its exit code IS reliable (0 on success, nonzero only on a real crash).
function Invoke-ExportStep([string]$label) {
  Write-Host $label -ForegroundColor Cyan
  & $py $export
  if ($LASTEXITCODE -ne 0) { throw "$label FAILED (exit $LASTEXITCODE) - see output above." }
}

# 1) Validate the parse offline first - cheap, no DB, catches a broken markdown edit before we --clear.
Invoke-SyncStep "[1/3] Validating dev_graph parse (sync_to_neo4j.py --dry-run)..." @("--dry-run")

# 2) Re-project Neo4j (idempotent MERGE on canonical_id; --clear wipes first). Skippable when no DB.
if ($NoNeo4j) {
  Write-Host "[2/3] Skipping Neo4j re-sync (-NoNeo4j)." -ForegroundColor Yellow
} else {
  if (-not $env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD = "elnino_dev" }   # same default as start.ps1
  Invoke-SyncStep "[2/3] Re-projecting Neo4j (sync_to_neo4j.py --clear)..." @("--clear")
}

# 3) Re-write BOTH graph.json copies from the one parse (frontend/ + hud/public/).
Invoke-ExportStep "[3/3] Re-projecting graph.json (both copies)..."

Write-Host "`nResync complete. All projections rebuilt from dev_graph markdown." -ForegroundColor Green
Write-Host "If the served HUD bundle must be current too: cd jarvis\hud; npm run build" -ForegroundColor DarkGray
