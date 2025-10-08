# Simple Transcendence Setup Script
Write-Host "🌱 Starting Transcendence Setup..." -ForegroundColor Green

# Check if Python is available
$pythonCheck = & python --version 2>&1
if ($pythonCheck -like "*Python 3.*") {
    Write-Host "✅ Python found: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.11+ required" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
$nodeCheck = & node --version 2>&1
if ($nodeCheck -like "v*") {
    Write-Host "✅ Node.js found: $nodeCheck" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js 18+ required" -ForegroundColor Red
    exit 1
}

Write-Host "🐍 Setting up Python backend..." -ForegroundColor Yellow
Set-Location backend

# Create Python virtual environment
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host "✅ Backend setup complete!" -ForegroundColor Green

Write-Host "⚛️ Setting up React frontend..." -ForegroundColor Yellow
Set-Location ../frontend

# Install npm dependencies
npm install

# Create .env file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host "✅ Frontend setup complete!" -ForegroundColor Green

Write-Host "🎯 Setup complete! Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend/.env with AWS credentials"
Write-Host "2. Run: .\scripts\seed.ps1"
Write-Host "3. Start backend: cd backend && python -m uvicorn app.main:app --reload"
Write-Host "4. Start frontend: cd frontend && npm run dev"

Set-Location ..