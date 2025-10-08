# 🌱 Transcendence Setup Script - Windows PowerShell
# Automated installation and configuration for local development

Write-Host "🌱 Starting Transcendence Setup..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 11) {
            Write-Host "✅ Python $pythonVersion found" -ForegroundColor Green
        } else {
            Write-Host "❌ Python 3.11+ required, found $pythonVersion" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Could not determine Python version from: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+)") {
        $majorVersion = [int]$matches[1]
        if ($majorVersion -ge 18) {
            Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
        } else {
            Write-Host "❌ Node.js 18+ required, found $nodeVersion" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Could not determine Node.js version from: $nodeVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✅ npm $npmVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm" -ForegroundColor Red
    exit 1
}

Write-Host "`n🐍 Setting up Python backend..." -ForegroundColor Yellow

# Create and activate Python virtual environment
Set-Location backend
if (Test-Path ".venv") {
    Write-Host "🔄 Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}

Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Cyan
python -m venv .venv

Write-Host "🚀 Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "📥 Installing Python dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating backend .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit backend/.env with your AWS credentials" -ForegroundColor Yellow
}

Write-Host "✅ Python backend setup complete!" -ForegroundColor Green

Write-Host "`n⚛️  Setting up React frontend..." -ForegroundColor Yellow
Set-Location ../frontend

Write-Host "📥 Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

# Create environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating frontend .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

Write-Host "✅ React frontend setup complete!" -ForegroundColor Green

Write-Host "`n🎯 Setup Summary:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Python virtual environment created in backend/.venv" -ForegroundColor Green
Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
Write-Host "✅ Environment files created" -ForegroundColor Green

Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend/.env with your AWS Mistral credentials (optional for mock mode)"
Write-Host "2. Run: .\scripts\seed.ps1 to populate sample data"
Write-Host "3. Start backend: cd backend && python -m uvicorn app.main:app --reload --port 8000"
Write-Host "4. Start frontend: cd frontend && npm run dev"
Write-Host "5. Open: http://localhost:5173"

Write-Host "`n🌱 Happy green job hunting!" -ForegroundColor Green

Set-Location ..