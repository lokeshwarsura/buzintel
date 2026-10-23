# BizIntel AI - Windows Native Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

Write-Host "=== BIZINTEL AI: Windows Native Environment Setup ===" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/5] Checking Python environment..." -ForegroundColor Yellow
$py = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not found in PATH. Please install Python 3.12+ from python.org."
    exit 1
}
Write-Host "Found: $py" -ForegroundColor Green

# 2. Check Node
Write-Host "`n[2/5] Checking Node.js environment..." -ForegroundColor Yellow
$node = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Node.js is not found in PATH. Please install Node.js 20+ from nodejs.org."
    exit 1
}
Write-Host "Found: Node $node" -ForegroundColor Green

# 3. Virtualenv & Dependencies
Write-Host "`n[3/5] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[dev,documents,agents]"

# 4. Database Migrations
Write-Host "`n[4/5] Running database migrations..." -ForegroundColor Yellow
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
.venv\Scripts\alembic.exe upgrade head
Write-Host "Database migrations up to date." -ForegroundColor Green

# 5. Frontend Dependencies & Build
Write-Host "`n[5/5] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location apps\web
npm.cmd install
npm.cmd run build
Pop-Location
Write-Host "Frontend build verified." -ForegroundColor Green

Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "To start the backend API server:" -ForegroundColor White
Write-Host "  .venv\Scripts\uvicorn.exe apps.api.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "`nTo start the frontend development server:" -ForegroundColor White
Write-Host "  cd apps\web; npm.cmd run dev" -ForegroundColor Gray
Write-Host "`nTo run automated test suite:" -ForegroundColor White
Write-Host "  `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; .venv\Scripts\pytest.exe -v" -ForegroundColor Gray
