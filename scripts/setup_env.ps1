param()

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent $scriptDir
Set-Location $repoRoot

$venvPath = Join-Path $repoRoot ".venv"
$requirementsPath = Join-Path $repoRoot "requirements.txt"

$python = Get-Command python3.13 -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python 3.13 is required but was not found in PATH."
    exit 1
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment with python3.13..."
    & $python.Source -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists at $venvPath"
}

$activateScript = Join-Path $venvPath "Scripts/Activate.ps1"
. $activateScript

python -m pip install --upgrade pip
python -m pip install -U -r $requirementsPath

$envSample = @(".env.example", ".env_example") |
    ForEach-Object {
        $candidate = Join-Path $repoRoot $_
        if (Test-Path $candidate) { return $candidate }
    } | Select-Object -First 1

if (-not $envSample) {
    Write-Error "Could not find .env.example (or .env_example) to copy from."
    exit 1
}

$envTarget = Join-Path $repoRoot ".env"
if (-not (Test-Path $envTarget)) {
    Copy-Item $envSample $envTarget
    Write-Host "Copied $(Split-Path $envSample -Leaf) to .env"
} else {
    Write-Host ".env already exists, leaving it unchanged"
}

python -m kratos.initmem

Write-Host ""
Write-Host "All set! Run 'langgraph dev --allow-blocking' to start the dev server when you're ready."
