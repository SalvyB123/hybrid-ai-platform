# scripts/dev.ps1
Param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 5173
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

function Wait-ForPort {
  param([int]$Port, [int]$Timeout = 30)
  Write-Host "⏳ Waiting for localhost:$Port (timeout $Timeout s)…"
  for ($i = 0; $i -lt $Timeout; $i++) {
    try {
      $resp = Invoke-WebRequest -UseBasicParsing -Method GET "http://localhost:$Port/health" -TimeoutSec 2
      if ($resp.StatusCode -eq 200) {
        Write-Host "✅ localhost:$Port is ready."
        return
      }
    } catch { }
    Start-Sleep -Seconds 1
  }
  throw "Timeout waiting for localhost:$Port"
}

# Migrations
Write-Host "🚀 Running Alembic migrations…"
python -m alembic upgrade head

# Start API (background)
Write-Host "🚀 Starting FastAPI on :$ApiPort…"
$api = Start-Process -PassThru -FilePath python -ArgumentList "-m","uvicorn","src.api.app:app","--reload","--host","0.0.0.0","--port",$ApiPort

try {
  Wait-ForPort -Port $ApiPort -Timeout 30

  # Frontend
  Set-Location "$root/frontend"
  if (-not $env:VITE_API_BASE_URL) {
    $env:VITE_API_BASE_URL = "http://localhost:$ApiPort"
  }
  Write-Host "🚀 Starting frontend (Vite) on :$WebPort…"
  npm run dev
} finally {
  if ($api -and -not $api.HasExited) {
    Write-Host "🧹 Stopping API…"
    Stop-Process -Id $api.Id -Force
  }
}