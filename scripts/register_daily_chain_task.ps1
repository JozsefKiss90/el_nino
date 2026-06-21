<#
.SYNOPSIS
  Register the el_nino daily chain run as a Windows Scheduled Task (OPERATOR ACTION -- default-OFF).

.DESCRIPTION
  Mirrors Mr-Ripley/scripts/register_daily_task.ps1. Registers a daily task that runs
  scripts\daily_chain_run.ps1 AFTER the Mr-Ripley 'MrRipley-Layer2-DailyEOD' 23:00 job has banked the
  day's snapshot (default 23:45 -- Mr-Ripley's 30-minute limit means it completes by ~23:30).

  THIS IS A DELIBERATE OPERATOR STEP. The chain orchestrator slice wires nothing automatically; the
  recurring task is registered only when the operator explicitly runs this script. Until then the
  daily run is exercised by a single manual invocation of daily_chain_run.ps1.

  The task runs the DETERMINISTIC simulator path (no live broker) with the deterministic calendar feed
  (-FeedSource calendar). Switching the run to the live Alpaca calendar plug or the live paper broker
  is a further, separate operator opt-in (env creds; see daily_chain_run.ps1 / the runbook).

.EXAMPLE
  # Register (operator action):
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\register_daily_chain_task.ps1

.EXAMPLE
  # Inspect / disable / remove:
  Get-ScheduledTaskInfo -TaskName 'ElNino-Chain-DailyRun'
  Disable-ScheduledTask  -TaskName 'ElNino-Chain-DailyRun'
  Unregister-ScheduledTask -TaskName 'ElNino-Chain-DailyRun' -Confirm:$false
#>
[CmdletBinding()]
param(
    [string]$TaskName = 'ElNino-Chain-DailyRun',
    [string]$Script   = 'C:\Code\el_nino\scripts\daily_chain_run.ps1',
    [string]$At       = '11:45PM'
)

$ErrorActionPreference = 'Stop'

$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument ('-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $Script)

$trigger = New-ScheduledTaskTrigger -Daily -At $At

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings `
    -Description ('el_nino: daily chain orchestrator run over the latest banked Mr-Ripley snapshot ' +
                  '(deterministic simulator + operational calendar feed; paper-only). Sequenced after ' +
                  'MrRipley-Layer2-DailyEOD.') `
    -Force | Out-Null

Write-Output "Registered scheduled task '$TaskName' (daily at $At), running: $Script"
Write-Output "Verify with: Get-ScheduledTaskInfo -TaskName '$TaskName'"
