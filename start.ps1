# One-command launcher for VisionFlow on Windows PowerShell.
# Usage:  .\start.ps1            (API :8000 + UI :8501)
#         .\start.ps1 -Reload    (API autoreload)
#         .\start.ps1 -NoUi      (API only)
param(
    [switch]$Reload,
    [switch]$NoUi
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
    $py = $venvPy
} else {
    Write-Host "[VisionFlow] .venv not found, using system python. Run 'python -m venv .venv' first if needed." -ForegroundColor Yellow
    $py = "python"
}

$args = @("run.py")
if ($Reload) { $args += "--reload" }
if ($NoUi)   { $args += "--no-ui" }

& $py @args
