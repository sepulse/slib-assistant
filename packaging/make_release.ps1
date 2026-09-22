param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$required = @(
    ".\dist\SLibAssistant.exe",
    ".\dist\SLibUpdater.exe",
    ".\dist\SLibProbe.exe"
)
foreach ($item in $required) {
    if (-not (Test-Path -LiteralPath $item)) {
        throw "Missing build artifact: $item. Run packaging\build.ps1 first."
    }
}

$bundle = Join-Path $ProjectRoot "dist\SLibAssistant-Windows"
if (Test-Path -LiteralPath $bundle) {
    Remove-Item -LiteralPath $bundle -Recurse -Force
}
New-Item -ItemType Directory -Path $bundle | Out-Null

Copy-Item -LiteralPath ".\dist\SLibAssistant.exe" -Destination $bundle
Copy-Item -LiteralPath ".\dist\SLibUpdater.exe" -Destination $bundle
Copy-Item -LiteralPath ".\config\config.example.toml" -Destination $bundle
Copy-Item -LiteralPath ".\packaging\PRE_OFFICE_README.txt" -Destination (Join-Path $bundle "README.txt")

$zip = Join-Path $ProjectRoot "dist\SLibAssistant-Windows.zip"
if (Test-Path -LiteralPath $zip) {
    Remove-Item -LiteralPath $zip -Force
}
Compress-Archive -Path (Join-Path $bundle "*") -DestinationPath $zip -CompressionLevel Optimal

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLowerInvariant()
$checksumPath = "$zip.sha256"
"$hash  SLibAssistant-Windows.zip" | Set-Content -LiteralPath $checksumPath -Encoding ascii

Get-Item -LiteralPath $zip, $checksumPath | Select-Object FullName, Length, LastWriteTime
Write-Output "SHA256 $hash"

$probeBundle = Join-Path $ProjectRoot "dist\SLibProbe-OFFICE-GATE"
if (Test-Path -LiteralPath $probeBundle) {
    Remove-Item -LiteralPath $probeBundle -Recurse -Force
}
New-Item -ItemType Directory -Path $probeBundle | Out-Null
Copy-Item -LiteralPath ".\dist\SLibProbe.exe" -Destination $probeBundle
Copy-Item -LiteralPath ".\packaging\OFFICE_PROBE_README.txt" -Destination (Join-Path $probeBundle "README.txt")
Copy-Item -LiteralPath ".\OFFICE_PROBE_GATE.md" -Destination $probeBundle
$probeZip = Join-Path $ProjectRoot "dist\SLibProbe-OFFICE-GATE.zip"
if (Test-Path -LiteralPath $probeZip) {
    Remove-Item -LiteralPath $probeZip -Force
}
Compress-Archive -Path (Join-Path $probeBundle "*") -DestinationPath $probeZip -CompressionLevel Optimal

$handoffBundle = Join-Path $ProjectRoot "dist\SLibAssistant-OFFICE-HANDOFF"
if (Test-Path -LiteralPath $handoffBundle) {
    Remove-Item -LiteralPath $handoffBundle -Recurse -Force
}
New-Item -ItemType Directory -Path $handoffBundle | Out-Null
Copy-Item -LiteralPath ".\dist\SLibAssistant.exe" -Destination $handoffBundle
Copy-Item -LiteralPath ".\dist\SLibUpdater.exe" -Destination $handoffBundle
Copy-Item -LiteralPath ".\dist\SLibProbe.exe" -Destination $handoffBundle
Copy-Item -LiteralPath ".\config\config.example.toml" -Destination $handoffBundle
Copy-Item -LiteralPath ".\OFFICE_HANDOFF.md" -Destination $handoffBundle
Copy-Item -LiteralPath ".\OFFICE_PROBE_GATE.md" -Destination $handoffBundle
Copy-Item -LiteralPath ".\packaging\OFFICE_PROBE_README.txt" -Destination (Join-Path $handoffBundle "README_FIRST.txt")
$handoffZip = Join-Path $ProjectRoot "dist\SLibAssistant-OFFICE-HANDOFF.zip"
if (Test-Path -LiteralPath $handoffZip) {
    Remove-Item -LiteralPath $handoffZip -Force
}
Compress-Archive -Path (Join-Path $handoffBundle "*") -DestinationPath $handoffZip -CompressionLevel Optimal

Get-Item -LiteralPath $probeZip, $handoffZip | Select-Object FullName, Length, LastWriteTime
