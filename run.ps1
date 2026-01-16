$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $repo '.venv\Scripts\python.exe'

if (-not (Test-Path $py)) {
  Write-Host "Nao achei o venv em: $py" -ForegroundColor Red
  Write-Host "Crie o venv e instale dependencias:" -ForegroundColor Yellow
  Write-Host "  python -m venv .venv" -ForegroundColor Yellow
  Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
  Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
  exit 1
}

Set-Location $repo
& $py -m streamlit run Home.py
