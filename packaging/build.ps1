param([switch]$Clean)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

if ($Clean) {
    if (Test-Path ".\build") { Remove-Item -Recurse -Force ".\build" }
    if (Test-Path ".\dist") { Remove-Item -Recurse -Force ".\dist" }
}

python -m PyInstaller --noconfirm --clean --onefile --windowed --name SLibAssistant --paths src src\slib_assistant\app.py
if ($LASTEXITCODE -ne 0) { throw "SLibAssistant build failed with exit code $LASTEXITCODE" }

python -m PyInstaller --noconfirm --clean --onefile --console --name SLibProbe --paths src --hidden-import pywinauto --hidden-import pywinauto.application src\slib_assistant\slib\probe.py
if ($LASTEXITCODE -ne 0) { throw "SLibProbe build failed with exit code $LASTEXITCODE" }

python -m PyInstaller --noconfirm --clean --onefile --windowed --name SLibUpdater --paths src src\slib_assistant\updater.py
if ($LASTEXITCODE -ne 0) { throw "SLibUpdater build failed with exit code $LASTEXITCODE" }

Get-ChildItem ".\dist\SLibAssistant.exe", ".\dist\SLibProbe.exe", ".\dist\SLibUpdater.exe" | Select-Object Name, Length, LastWriteTime
