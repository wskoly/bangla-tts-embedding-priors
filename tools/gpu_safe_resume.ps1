# At-logon helper (D-052): re-apply GPU limits after a reboot, then resume the C3 queue if it is unfinished.
# Bounded: at most $MaxResumes automatic resumes (counted in runs/auto_resume_count.txt) so a crash loop stops itself.
# One-time registration, in an ADMINISTRATOR PowerShell:
#   Register-ScheduledTask -TaskName tts_gpu_safe_resume -User SYSTEM -RunLevel Highest `
#     -Trigger (New-ScheduledTaskTrigger -AtLogOn) `
#     -Action (New-ScheduledTaskAction -Execute powershell.exe -Argument '-NoProfile -ExecutionPolicy Bypass -File "D:\Personal\Research\tts-research\tools\gpu_safe_resume.ps1"')
# Remove with: Unregister-ScheduledTask -TaskName tts_gpu_safe_resume -Confirm:$false
$ErrorActionPreference = "Continue"
$Root = "D:\Personal\Research\tts-research"
$MaxResumes = 4
$Log = Join-Path $Root "runs\pilot_v8_queue.log"
$Counter = Join-Path $Root "runs\auto_resume_count.txt"

Start-Sleep -Seconds 60  # let the driver, services and the user session come up
& nvidia-smi -pl 250 | Out-Null
& nvidia-smi -lgc 210,2100 | Out-Null

if (-not (Test-Path $Log) -or (Select-String -Path $Log -Pattern "=== done" -Quiet)) { exit 0 }
$n = 0; if (Test-Path $Counter) { $n = [int](Get-Content $Counter) }
if ($n -ge $MaxResumes) { Add-Content $Log "=== auto-resume limit ($MaxResumes) reached $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'); not resuming"; exit 0 }
Set-Content $Counter ($n + 1)
Add-Content $Log "=== auto-resume $($n + 1)/$MaxResumes $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') (limits re-applied: 250 W, 2100 MHz)"
Start-ScheduledTask -TaskName tts_pilot_v8
