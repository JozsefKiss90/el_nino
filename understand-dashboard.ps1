# understand-dashboard.ps1
# Relaunch the Understand-Anything dashboard for the el_nino knowledge graph.
# The graph data lives on disk (.understand-anything\knowledge-graph.json + domain-graph.json);
# this just starts the local viewer. The one-time pnpm install + build is already done.
#
# Run it any of these ways:
#   - Right-click this file -> "Run with PowerShell"
#   - In a terminal:  powershell -ExecutionPolicy Bypass -File .\understand-dashboard.ps1
#   - Inside Claude Code:  ! powershell -ExecutionPolicy Bypass -File .\understand-dashboard.ps1
# Stop it with Ctrl+C in the window it opens.

$ErrorActionPreference = "Stop"

# --- Resolve the installed plugin (newest version dir) ---
$pluginBase = "$env:USERPROFILE\.claude\plugins\cache\understand-anything\understand-anything"
if (-not (Test-Path $pluginBase)) {
    Write-Host "ERROR: Understand-Anything plugin not found at $pluginBase" -ForegroundColor Red
    Write-Host "Reinstall it, then re-run /understand in Claude Code to rebuild the graph." -ForegroundColor Yellow
    exit 1
}
$versionDir = Get-ChildItem $pluginBase -Directory |
    Sort-Object { try { [version]$_.Name } catch { [version]"0.0.0" } } -Descending |
    Select-Object -First 1
$dashboard = Join-Path $versionDir.FullName "packages\dashboard"
$viteJs    = Join-Path $dashboard "node_modules\vite\bin\vite.js"

if (-not (Test-Path $viteJs)) {
    Write-Host "ERROR: dashboard not built (vite missing at $viteJs)." -ForegroundColor Red
    Write-Host "The plugin was likely updated. In Claude Code, ask to rebuild: run pnpm install + core build in" -ForegroundColor Yellow
    Write-Host "  $($versionDir.FullName)" -ForegroundColor Yellow
    exit 1
}

# --- Point the viewer at this project's graph, with a stable access token ---
$env:GRAPH_DIR = "C:\Code\el_nino"
$env:UNDERSTAND_ACCESS_TOKEN = "elnino5f3a9c2b1e8d4a769b0c4d2e1f6a8b30"

Write-Host ""
Write-Host "  Starting el_nino dashboard (Ctrl+C to stop)..." -ForegroundColor Cyan
Write-Host "  Open: http://127.0.0.1:5173/?token=$($env:UNDERSTAND_ACCESS_TOKEN)" -ForegroundColor Green
Write-Host "  (It also auto-opens in your browser. Use the Structural <-> Domain toggle in the header.)" -ForegroundColor DarkGray
Write-Host ""

Set-Location $dashboard
node $viteJs --host 127.0.0.1
