# start.ps1 - bring up the JARVIS HUD at http://127.0.0.1:8000/
#
# The HUD is served by the read-only FastAPI bridge (it mounts the built React dist). This script
# is idempotent: it ensures Neo4j is running, builds the HUD once if needed, then starts the bridge
# in the foreground (Ctrl+C to stop). Nothing here auto-starts on reboot - run it when you want the UI.
#
#   Usage:   powershell -ExecutionPolicy Bypass -File C:\Code\el_nino\jarvis\start.ps1
#   Then:    open http://127.0.0.1:8000/   in Chrome/Edge
#
# Optional: set ANTHROPIC_API_KEY before running to enable the /ask LLM path (otherwise the HUD
# uses the offline graph router, still cited). Set JARVIS_ASK_MODEL to override the model.

$ErrorActionPreference = "Stop"
$repo   = Split-Path -Parent $PSScriptRoot          # C:\Code\el_nino
$venvPy = Join-Path $repo ".venv\Scripts\python.exe"
$backend = Join-Path $repo "jarvis\backend"
$hud     = Join-Path $repo "jarvis\hud"

if (-not (Test-Path $venvPy)) { throw "venv python not found at $venvPy - create it and pip install jarvis\backend\requirements.txt" }

# 1) Neo4j (the graph store). Normally already up via restart:unless-stopped; start it if stopped.
$running = docker ps --filter "name=elnino-neo4j" --format "{{.Names}}"
if (-not $running) {
  Write-Host "[1/3] Starting Neo4j container..." -ForegroundColor Cyan
  docker start elnino-neo4j
  if ($LASTEXITCODE -ne 0) {
    Push-Location (Join-Path $repo "jarvis"); docker compose up -d neo4j; Pop-Location
  }
} else {
  Write-Host "[1/3] Neo4j already running." -ForegroundColor Green
}

# 2) Build the HUD once (the bridge serves jarvis\hud\dist).
if (-not (Test-Path (Join-Path $hud "dist\index.html"))) {
  Write-Host "[2/3] Building the HUD (first run)..." -ForegroundColor Cyan
  Push-Location $hud
  if (-not (Test-Path "node_modules")) { npm install }
  npm run build
  Pop-Location
} else {
  Write-Host "[2/3] HUD already built (jarvis\hud\dist). Rebuild with: cd jarvis\hud; npm run build" -ForegroundColor Green
}

# 3) Bridge (API + static HUD) on :8000, foreground.
Write-Host "[3/3] Starting bridge -> open http://127.0.0.1:8000/  (Ctrl+C to stop)" -ForegroundColor Cyan
$env:NEO4J_PASSWORD = if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD } else { "elnino_dev" }
& $venvPy -m uvicorn app:app --port 8000 --app-dir $backend
