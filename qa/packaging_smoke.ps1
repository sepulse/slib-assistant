$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$App = ".\dist\SLibAssistant.exe"
$Probe = ".\dist\SLibProbe.exe"
$Updater = ".\dist\SLibUpdater.exe"

if (-not (Test-Path $App)) { throw "Missing SLibAssistant.exe" }
if (-not (Test-Path $Probe)) { throw "Missing SLibProbe.exe" }
if (-not (Test-Path $Updater)) { throw "Missing SLibUpdater.exe" }

$process = Start-Process -FilePath $App -WindowStyle Hidden -PassThru
Start-Sleep -Milliseconds 2500
$appPath = (Resolve-Path $App).Path
$appProcesses = @(Get-Process SLibAssistant -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $appPath })
$appRunning = $appProcesses.Count -gt 0
foreach ($item in $appProcesses) {
    Stop-Process -Id $item.Id -Force
}
if (-not $appRunning) {
    throw "SLibAssistant.exe exited during launch smoke."
}

$probeOutput = Join-Path $Root "qa\evidence\packaging-probe-smoke"
& $Probe --output $probeOutput
$probeExit = $LASTEXITCODE
if ($probeExit -notin @(0, 2)) {
    throw "SLibProbe.exe failed with exit code $probeExit"
}
if (-not (Test-Path (Join-Path $probeOutput "probe.json"))) {
    throw "SLibProbe.exe did not produce probe.json"
}

Write-Output "SLibAssistant launch smoke: PASS"
Write-Output "SLibProbe execution smoke: PASS (exit=$probeExit; 2 means target S-Lib window absent)"
Write-Output "SLibUpdater packaging presence: PASS"
Get-ChildItem $App, $Probe, $Updater | Select-Object Name, Length, LastWriteTime
