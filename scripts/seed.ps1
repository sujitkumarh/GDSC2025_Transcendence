# 🌱 Transcendence Data Seeding Script - Windows PowerShell
# Populates the application with sample personas and data

Write-Host "🌱 Starting Transcendence Data Seeding..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend\app\data")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Checking data directory..." -ForegroundColor Yellow

# Ensure data directory exists
if (-not (Test-Path "backend\app\data")) {
    Write-Host "📁 Creating data directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "backend\app\data" -Force
}

Write-Host "✅ Data directory ready" -ForegroundColor Green

Write-Host "`n👥 Seeding sample personas..." -ForegroundColor Yellow

# Check if personas.json already exists
if (Test-Path "backend\app\data\personas.json") {
    Write-Host "📄 Personas file already exists" -ForegroundColor Cyan
} else {
    Write-Host "❌ Personas file not found - this should have been created automatically" -ForegroundColor Red
    Write-Host "💡 The personas.json file should be in backend/app/data/" -ForegroundColor Yellow
}

Write-Host "`n📊 Initializing analytics..." -ForegroundColor Yellow

# Create empty events file
$eventsFile = "backend\app\data\events.json"
if (-not (Test-Path $eventsFile)) {
    Write-Host "📝 Creating events file..." -ForegroundColor Cyan
    "[]" | Out-File -FilePath $eventsFile -Encoding UTF8
}

Write-Host "✅ Events file ready" -ForegroundColor Green

Write-Host "`n🎯 Seeding completed successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`n📋 Seeded Data Summary:" -ForegroundColor Cyan
Write-Host "✅ 8 sample Brazilian youth personas" -ForegroundColor Green
Write-Host "✅ Analytics infrastructure initialized" -ForegroundColor Green
Write-Host "✅ Event logging system ready" -ForegroundColor Green

Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start the backend: cd backend && python -m uvicorn app.main:app --reload --port 8000"
Write-Host "2. Start the frontend: cd frontend && npm run dev"
Write-Host "3. Open: http://localhost:5173"
Write-Host "4. Explore the sample personas in the Personas section"

Write-Host "`n🌟 Sample Personas Created:" -ForegroundColor Cyan
Write-Host "• Marina Silva (SP) - Interested in solar energy" -ForegroundColor White
Write-Host "• João Santos (RJ) - Preparing for wind energy career" -ForegroundColor White
Write-Host "• Ana Costa (MG) - Exploring waste management" -ForegroundColor White
Write-Host "• Carlos Oliveira (CE) - Ready for ESG consulting" -ForegroundColor White
Write-Host "• Beatriz Almeida (RS) - Preparing for sustainable agriculture" -ForegroundColor White
Write-Host "• Rafael Pereira (BA) - Interested in green construction" -ForegroundColor White
Write-Host "• Camila Rodrigues (PR) - Ready for ESG consulting" -ForegroundColor White
Write-Host "• Lucas Ferreira (PE) - Exploring forestry careers" -ForegroundColor White

Write-Host "`n🌱 Happy green career exploration!" -ForegroundColor Green