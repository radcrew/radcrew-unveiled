# Run QLoRA training with UTF-8 mode (avoids TRL template read errors on Windows cp1252).
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$here = $PSScriptRoot
$py = Join-Path $here ".venv\Scripts\python.exe"
$script = Join-Path $here "train_qlora.py"

if (-not (Test-Path $py)) {
    Write-Error "Missing $py - create training/.venv and run: pip install -r requirements.txt"
}

& $py $script
