# Start both API and WebUI in separate consoles (PowerShell) using jobs
# Usage: .\start_all.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Start-Job -ScriptBlock { & "$scriptDir\start_api.ps1" }
Start-Job -ScriptBlock { & "$scriptDir\start_webui.ps1" }

Write-Host "Started API and WebUI as background jobs. Use Get-Job to inspect."
