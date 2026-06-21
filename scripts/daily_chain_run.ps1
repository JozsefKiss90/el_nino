<#
.SYNOPSIS
  el_nino daily chain run -- thread the latest banked Mr-Ripley snapshot through the Layer-3 chain
  orchestrator and persist the el_nino ledger + portfolio.

.DESCRIPTION
  Mirrors Mr-Ripley/scripts/daily_eod_snapshot.ps1, but ALL changes stay in el_nino (Mr-Ripley is a
  separate repo and is never modified). One run per invocation:

    find latest snapshot_*.json in $SnapshotDir  ->  python -m orchestration.runtime ...  ->  persist

  Execution core: the DETERMINISTIC SimulatedBrokerAdapter (the default port -- NOT the live Alpaca
  broker). Operational status: the operational feed, captured for replay. -FeedSource 'calendar' (the
  default) is the deterministic, credential-free MarketCalendarFeed; -FeedSource 'alpaca' is the live
  paper clock/calendar plug (default-OFF; requires env creds; fail-closed) -- use only after operator
  opt-in. The chain is idempotent on source_snapshot_id, so a missed or duplicate run is safe (no
  double-admit / double-fill).

  Registration of the RECURRING scheduled task is a SEPARATE operator action
  (register_daily_chain_task.ps1). This script performs exactly one run when invoked.

.NOTES
  Sequencing: run AFTER the Mr-Ripley 'MrRipley-Layer2-DailyEOD' 23:00 job (30-min limit) has banked
  the day's snapshot -- e.g. 23:45. Paper-only ALWAYS (ADR-011 section 3). No live-money path.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot           = 'C:\Code\el_nino',
    [string]$Python             = 'C:\Code\el_nino\.venv\Scripts\python.exe',
    [string]$SnapshotDir        = 'C:\Code\Mr-Ripley\runtime\snapshots',
    [string]$Ledger             = 'C:\Code\el_nino\runtime\chain\runtime_ledger.json',
    [string]$Portfolio          = 'C:\Code\el_nino\runtime\chain\portfolio_state.json',
    [string]$OperationalCapture = 'C:\Code\el_nino\runtime\chain\operational_capture.json',
    [ValidateSet('calendar', 'alpaca')]
    [string]$FeedSource         = 'calendar',
    [switch]$GuardFromEnv
)

$ErrorActionPreference = 'Stop'

Set-Location -Path $RepoRoot
$env:PYTHONPATH = Join-Path $RepoRoot 'src'

$logDir   = Join-Path $RepoRoot 'runtime\logs'
$chainDir = Join-Path $RepoRoot 'runtime\chain'
New-Item -ItemType Directory -Force -Path $logDir   | Out-Null
New-Item -ItemType Directory -Force -Path $chainDir | Out-Null

$stamp   = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$logFile = Join-Path $logDir ("daily_chain_run_{0}.log" -f $stamp)

function Note([string]$msg) {
    $line = "{0}  {1}" -f (Get-Date).ToUniversalTime().ToString('o'), $msg
    Add-Content -Path $logFile -Value $line
    Write-Output $line
}

Note ("el_nino daily chain run starting (FeedSource={0}, GuardFromEnv={1})" -f $FeedSource, $GuardFromEnv.IsPresent)
Note "snapshot-dir=$SnapshotDir ledger=$Ledger portfolio=$Portfolio"

$pyArgs = @(
    '-m', 'orchestration.runtime',
    '--snapshot-dir', $SnapshotDir,
    '--ledger', $Ledger,
    '--portfolio', $Portfolio,
    '--operational-feed',
    '--operational-feed-source', $FeedSource,
    '--operational-capture', $OperationalCapture
)
if ($GuardFromEnv) { $pyArgs += '--guard-from-env' }

Note ("invoking: {0} {1}" -f $Python, ($pyArgs -join ' '))
$output = & $Python @pyArgs
$code = $LASTEXITCODE
foreach ($l in $output) { Note "  $l" }
Note "orchestration.runtime exit code = $code"

if ($code -ne 0) {
    Note "FAILED -- non-zero exit; ledger/portfolio left unchanged by the fail-closed shell"
    exit $code
}
Note "OK -- chain run complete"
exit 0
